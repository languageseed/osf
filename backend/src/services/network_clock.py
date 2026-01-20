"""
OSF Network Clock - Synchronized Time Management

Manages network-wide time progression for the simulation.
All users see the same clock, all actions queue for the same tick.

Configuration Modes:
- TEST: Fast ticks (30s) for development
- DEMO: Medium ticks (2-5 min) for live demos  
- CASUAL: Slow ticks (10-30 min) for casual play
- REALTIME: Very slow (1 hour+) for long-term simulation
- MANUAL: No auto-tick, admin triggers manually
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional, Callable, Awaitable, Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum
import structlog
import json

logger = structlog.get_logger()


class ClockMode(str, Enum):
    """Clock operation modes."""
    AUTO = "auto"       # Automatic ticking on interval
    MANUAL = "manual"   # Manual tick only (admin triggers)
    PAUSED = "paused"   # Temporarily paused


class ClockPreset(str, Enum):
    """Pre-configured timing presets."""
    TEST = "test"           # 30 seconds - for development
    DEMO_FAST = "demo_fast" # 2 minutes - fast demo
    DEMO = "demo"           # 5 minutes - standard demo
    CASUAL = "casual"       # 15 minutes - casual play
    SLOW = "slow"           # 30 minutes - relaxed pace
    REALTIME = "realtime"   # 1 hour - long-term sim
    DAILY = "daily"         # 24 hours - real calendar mapping


# Preset configurations
PRESET_CONFIG: Dict[ClockPreset, Dict[str, Any]] = {
    ClockPreset.TEST: {
        "interval_seconds": 30,
        "description": "Fast ticks for testing (30s)",
        "warning_seconds": 10,  # Warn users before tick
    },
    ClockPreset.DEMO_FAST: {
        "interval_seconds": 120,  # 2 minutes
        "description": "Fast demo mode (2 min)",
        "warning_seconds": 30,
    },
    ClockPreset.DEMO: {
        "interval_seconds": 300,  # 5 minutes
        "description": "Standard demo mode (5 min)",
        "warning_seconds": 60,
    },
    ClockPreset.CASUAL: {
        "interval_seconds": 900,  # 15 minutes
        "description": "Casual play (15 min)",
        "warning_seconds": 120,
    },
    ClockPreset.SLOW: {
        "interval_seconds": 1800,  # 30 minutes
        "description": "Relaxed pace (30 min)",
        "warning_seconds": 300,
    },
    ClockPreset.REALTIME: {
        "interval_seconds": 3600,  # 1 hour
        "description": "Real-time simulation (1 hour)",
        "warning_seconds": 600,
    },
    ClockPreset.DAILY: {
        "interval_seconds": 86400,  # 24 hours
        "description": "Daily ticks (24 hours)",
        "warning_seconds": 3600,
    },
}


@dataclass
class ClockConfig:
    """Clock configuration settings."""
    preset: ClockPreset = ClockPreset.DEMO
    interval_seconds: int = 300
    warning_seconds: int = 60
    mode: ClockMode = ClockMode.AUTO
    
    # Limits
    min_interval: int = 10       # Minimum 10 seconds (for testing)
    max_interval: int = 86400    # Maximum 24 hours
    
    # Features
    auto_start: bool = True
    broadcast_warnings: bool = True
    allow_user_speedup: bool = False  # Can users vote to speed up?
    
    @classmethod
    def from_preset(cls, preset: ClockPreset) -> "ClockConfig":
        """Create config from a preset."""
        preset_data = PRESET_CONFIG.get(preset, PRESET_CONFIG[ClockPreset.DEMO])
        return cls(
            preset=preset,
            interval_seconds=preset_data["interval_seconds"],
            warning_seconds=preset_data["warning_seconds"],
        )
    
    def to_dict(self) -> dict:
        return {
            "preset": self.preset.value,
            "interval_seconds": self.interval_seconds,
            "warning_seconds": self.warning_seconds,
            "mode": self.mode.value,
            "min_interval": self.min_interval,
            "max_interval": self.max_interval,
            "auto_start": self.auto_start,
            "broadcast_warnings": self.broadcast_warnings,
            "allow_user_speedup": self.allow_user_speedup,
        }


@dataclass
class ClockState:
    """Current clock state."""
    current_month: int
    mode: ClockMode
    preset: ClockPreset
    interval_seconds: int
    last_tick: datetime
    next_tick: datetime
    is_processing: bool
    seconds_until_tick: int
    warning_active: bool
    
    def to_dict(self) -> dict:
        return {
            "current_month": self.current_month,
            "mode": self.mode.value,
            "preset": self.preset.value,
            "interval_seconds": self.interval_seconds,
            "last_tick": self.last_tick.isoformat(),
            "next_tick": self.next_tick.isoformat(),
            "is_processing": self.is_processing,
            "seconds_until_tick": self.seconds_until_tick,
            "warning_active": self.warning_active,
        }


@dataclass
class PendingAction:
    """An action queued for the next tick."""
    id: str
    user_id: str
    action_type: str
    data: dict
    timestamp: datetime = field(default_factory=datetime.utcnow)
    priority: int = 0  # Higher = processed first
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "action_type": self.action_type,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority,
        }


class NetworkClock:
    """
    Synchronized network time manager.
    
    Features:
    - Configurable tick intervals with presets
    - Automatic and manual modes
    - Warning broadcasts before ticks
    - Action queue for batch processing
    - SSE broadcasting to all clients
    """
    
    def __init__(self, config: Optional[ClockConfig] = None):
        self.config = config or ClockConfig.from_preset(ClockPreset.DEMO)
        self.current_month = 1
        self.is_processing = False
        self.last_tick = datetime.utcnow()
        
        # Action queue
        self.pending_actions: List[PendingAction] = []
        
        # Callbacks
        self._on_tick: Optional[Callable[[List[PendingAction]], Awaitable[dict]]] = None
        self._on_broadcast: Optional[Callable[[str, dict], Awaitable[None]]] = None
        
        # Internal state
        self._task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()
        self._subscribers: List[asyncio.Queue] = []
        
        logger.info("network_clock_initialized", config=self.config.to_dict())
    
    # =========================================================================
    # Properties
    # =========================================================================
    
    @property
    def next_tick(self) -> datetime:
        """When the next tick will occur."""
        return self.last_tick + timedelta(seconds=self.config.interval_seconds)
    
    @property
    def seconds_until_tick(self) -> int:
        """Seconds remaining until next tick."""
        delta = self.next_tick - datetime.utcnow()
        return max(0, int(delta.total_seconds()))
    
    @property
    def warning_active(self) -> bool:
        """Whether we're in the warning period before a tick."""
        return self.seconds_until_tick <= self.config.warning_seconds
    
    @property
    def mode(self) -> ClockMode:
        return self.config.mode
    
    # =========================================================================
    # State
    # =========================================================================
    
    def get_state(self) -> ClockState:
        """Get current clock state."""
        return ClockState(
            current_month=self.current_month,
            mode=self.config.mode,
            preset=self.config.preset,
            interval_seconds=self.config.interval_seconds,
            last_tick=self.last_tick,
            next_tick=self.next_tick,
            is_processing=self.is_processing,
            seconds_until_tick=self.seconds_until_tick,
            warning_active=self.warning_active,
        )
    
    def get_pending_actions(self) -> List[dict]:
        """Get all pending actions."""
        return [a.to_dict() for a in self.pending_actions]
    
    def get_pending_count(self) -> int:
        """Get count of pending actions."""
        return len(self.pending_actions)
    
    # =========================================================================
    # Configuration
    # =========================================================================
    
    async def set_preset(self, preset: ClockPreset):
        """Apply a timing preset."""
        self.config = ClockConfig.from_preset(preset)
        self.last_tick = datetime.utcnow()  # Reset timer
        
        await self._broadcast("config_changed", {
            "preset": preset.value,
            "interval_seconds": self.config.interval_seconds,
            "next_tick_in": self.seconds_until_tick,
        })
        
        logger.info("clock_preset_changed", preset=preset.value)
    
    async def set_interval(self, seconds: int):
        """Set custom tick interval."""
        seconds = max(self.config.min_interval, min(self.config.max_interval, seconds))
        self.config.interval_seconds = seconds
        self.config.preset = ClockPreset.DEMO  # Custom = no preset
        self.last_tick = datetime.utcnow()  # Reset timer
        
        await self._broadcast("config_changed", {
            "interval_seconds": seconds,
            "next_tick_in": self.seconds_until_tick,
        })
        
        logger.info("clock_interval_changed", seconds=seconds)
    
    async def set_mode(self, mode: ClockMode):
        """Change clock mode."""
        old_mode = self.config.mode
        self.config.mode = mode
        
        if mode == ClockMode.AUTO and old_mode != ClockMode.AUTO:
            self.last_tick = datetime.utcnow()  # Reset timer on resume
        
        await self._broadcast("mode_changed", {
            "mode": mode.value,
            "next_tick_in": self.seconds_until_tick if mode == ClockMode.AUTO else None,
        })
        
        logger.info("clock_mode_changed", mode=mode.value)
    
    # =========================================================================
    # Lifecycle
    # =========================================================================
    
    async def start(self):
        """Start the clock tick loop."""
        if self._task is not None:
            return
        
        self.config.mode = ClockMode.AUTO
        self._task = asyncio.create_task(self._tick_loop())
        
        await self._broadcast("clock_started", {
            "month": self.current_month,
            "interval_seconds": self.config.interval_seconds,
            "next_tick_in": self.seconds_until_tick,
        })
        
        logger.info("network_clock_started", 
                   interval=self.config.interval_seconds,
                   preset=self.config.preset.value)
    
    async def stop(self):
        """Stop the clock tick loop."""
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        
        self.config.mode = ClockMode.PAUSED
        
        await self._broadcast("clock_stopped", {"month": self.current_month})
        logger.info("network_clock_stopped")
    
    async def pause(self):
        """Pause the clock (can be resumed)."""
        self.config.mode = ClockMode.PAUSED
        await self._broadcast("clock_paused", {"month": self.current_month})
        logger.info("network_clock_paused")
    
    async def resume(self):
        """Resume a paused clock."""
        self.config.mode = ClockMode.AUTO
        self.last_tick = datetime.utcnow()
        
        await self._broadcast("clock_resumed", {
            "month": self.current_month,
            "next_tick_in": self.seconds_until_tick,
        })
        logger.info("network_clock_resumed")
    
    # =========================================================================
    # Actions
    # =========================================================================
    
    def queue_action(self, action: PendingAction):
        """Queue an action for the next tick."""
        self.pending_actions.append(action)
        logger.info("action_queued", 
                   action_id=action.id,
                   action_type=action.action_type,
                   user_id=action.user_id)
    
    def remove_action(self, action_id: str) -> bool:
        """Remove a pending action (if not yet processed)."""
        for i, action in enumerate(self.pending_actions):
            if action.id == action_id:
                self.pending_actions.pop(i)
                logger.info("action_removed", action_id=action_id)
                return True
        return False
    
    def clear_actions(self):
        """Clear all pending actions."""
        count = len(self.pending_actions)
        self.pending_actions = []
        logger.info("actions_cleared", count=count)
    
    # =========================================================================
    # Tick Processing
    # =========================================================================
    
    async def force_tick(self):
        """Force an immediate tick (admin only)."""
        logger.info("force_tick_requested")
        await self._process_tick()
    
    async def _tick_loop(self):
        """Main tick loop."""
        warning_sent = False
        
        while True:
            try:
                if self.config.mode == ClockMode.PAUSED:
                    await asyncio.sleep(1)
                    continue
                
                if self.config.mode == ClockMode.MANUAL:
                    await asyncio.sleep(1)
                    continue
                
                seconds_left = self.seconds_until_tick
                
                # Send warning if approaching tick
                if (self.config.broadcast_warnings and 
                    seconds_left <= self.config.warning_seconds and 
                    not warning_sent and
                    not self.is_processing):
                    
                    await self._broadcast("tick_warning", {
                        "seconds_until_tick": seconds_left,
                        "pending_actions": len(self.pending_actions),
                    })
                    warning_sent = True
                
                # Time to tick?
                if seconds_left <= 0 and not self.is_processing:
                    await self._process_tick()
                    warning_sent = False
                
                # Broadcast sync periodically
                await asyncio.sleep(min(5, max(1, seconds_left // 10)))
                await self._broadcast_sync()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("tick_loop_error", error=str(e))
                await asyncio.sleep(5)
    
    async def _process_tick(self):
        """Process a single tick."""
        async with self._lock:
            if self.is_processing:
                logger.warning("tick_already_processing")
                return
            self.is_processing = True
        
        try:
            next_month = self.current_month + 1
            
            # Notify start
            await self._broadcast("processing_started", {
                "month": next_month,
                "pending_actions": len(self.pending_actions),
            })
            
            logger.info("tick_processing_started",
                       month=next_month,
                       pending_actions=len(self.pending_actions))
            
            # Process the tick
            result = {}
            if self._on_tick:
                # Sort actions by priority (highest first)
                actions = sorted(self.pending_actions, key=lambda a: -a.priority)
                result = await self._on_tick(actions)
            
            # Update state
            self.current_month = next_month
            self.last_tick = datetime.utcnow()
            self.pending_actions = []  # Clear queue
            
            # Notify completion
            await self._broadcast("month_completed", {
                "month": self.current_month,
                "next_tick_in": self.seconds_until_tick,
                "result": result,
            })
            
            logger.info("tick_processing_completed", month=self.current_month)
            
        except Exception as e:
            logger.error("tick_processing_failed", error=str(e))
            await self._broadcast("processing_failed", {
                "month": self.current_month + 1,
                "error": str(e),
            })
        
        finally:
            self.is_processing = False
    
    # =========================================================================
    # Broadcasting
    # =========================================================================
    
    def subscribe(self) -> asyncio.Queue:
        """Subscribe to clock events."""
        queue = asyncio.Queue()
        self._subscribers.append(queue)
        return queue
    
    def unsubscribe(self, queue: asyncio.Queue):
        """Unsubscribe from clock events."""
        if queue in self._subscribers:
            self._subscribers.remove(queue)
    
    async def _broadcast(self, event: str, data: dict):
        """Broadcast event to all subscribers."""
        message = {"event": event, "data": data, "timestamp": datetime.utcnow().isoformat()}
        
        # Internal subscribers
        for queue in self._subscribers:
            try:
                queue.put_nowait(message)
            except asyncio.QueueFull:
                pass
        
        # External callback
        if self._on_broadcast:
            try:
                await self._on_broadcast(event, data)
            except Exception as e:
                logger.error("broadcast_callback_error", error=str(e))
    
    async def _broadcast_sync(self):
        """Broadcast current state to all subscribers."""
        await self._broadcast("clock_sync", self.get_state().to_dict())
    
    # =========================================================================
    # Callbacks
    # =========================================================================
    
    def on_tick(self, callback: Callable[[List[PendingAction]], Awaitable[dict]]):
        """Register tick processing callback."""
        self._on_tick = callback
    
    def on_broadcast(self, callback: Callable[[str, dict], Awaitable[None]]):
        """Register broadcast callback."""
        self._on_broadcast = callback


# =============================================================================
# Singleton Instance
# =============================================================================

_network_clock: Optional[NetworkClock] = None


def get_network_clock() -> NetworkClock:
    """Get the singleton network clock instance."""
    global _network_clock
    if _network_clock is None:
        # Default to DEMO preset, can be changed via API
        _network_clock = NetworkClock(ClockConfig.from_preset(ClockPreset.DEMO))
    return _network_clock


def init_network_clock(preset: ClockPreset = ClockPreset.DEMO) -> NetworkClock:
    """Initialize the network clock with a specific preset."""
    global _network_clock
    _network_clock = NetworkClock(ClockConfig.from_preset(preset))
    return _network_clock


def reset_network_clock():
    """Reset the network clock (for testing)."""
    global _network_clock
    _network_clock = None
