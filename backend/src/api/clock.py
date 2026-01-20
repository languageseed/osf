"""
Network Clock API Endpoints

Provides REST and SSE endpoints for the synchronized network clock.
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from typing import Optional, List
import asyncio
import json

from src.services.network_clock import (
    get_network_clock,
    ClockMode,
    ClockPreset,
    PendingAction,
    PRESET_CONFIG,
)

router = APIRouter(prefix="/network/clock", tags=["Network Clock"])


# =============================================================================
# Request/Response Models
# =============================================================================

class ClockStatusResponse(BaseModel):
    """Current clock status."""
    current_month: int
    mode: str
    preset: str
    interval_seconds: int
    seconds_until_tick: int
    is_processing: bool
    warning_active: bool
    pending_actions_count: int


class PresetInfo(BaseModel):
    """Information about a timing preset."""
    name: str
    interval_seconds: int
    description: str
    warning_seconds: int


class SetPresetRequest(BaseModel):
    """Request to change preset."""
    preset: str


class SetIntervalRequest(BaseModel):
    """Request to set custom interval."""
    seconds: int


class SetModeRequest(BaseModel):
    """Request to change mode."""
    mode: str  # auto, manual, paused


class QueueActionRequest(BaseModel):
    """Request to queue an action."""
    id: str
    user_id: str
    action_type: str
    data: dict
    priority: int = 0


# =============================================================================
# Status Endpoints
# =============================================================================

@router.get("/status", response_model=ClockStatusResponse)
async def get_clock_status():
    """
    Get current network clock status.
    
    Returns the current month, mode, timing configuration,
    and countdown to next tick.
    """
    clock = get_network_clock()
    state = clock.get_state()
    
    return ClockStatusResponse(
        current_month=state.current_month,
        mode=state.mode.value,
        preset=state.preset.value,
        interval_seconds=state.interval_seconds,
        seconds_until_tick=state.seconds_until_tick,
        is_processing=state.is_processing,
        warning_active=state.warning_active,
        pending_actions_count=clock.get_pending_count(),
    )


@router.get("/presets", response_model=List[PresetInfo])
async def get_available_presets():
    """
    Get all available timing presets.
    
    Returns a list of preset configurations that can be applied.
    """
    presets = []
    for preset, config in PRESET_CONFIG.items():
        presets.append(PresetInfo(
            name=preset.value,
            interval_seconds=config["interval_seconds"],
            description=config["description"],
            warning_seconds=config["warning_seconds"],
        ))
    return presets


@router.get("/pending-actions")
async def get_pending_actions():
    """
    Get all pending actions queued for the next tick.
    """
    clock = get_network_clock()
    return {
        "count": clock.get_pending_count(),
        "actions": clock.get_pending_actions(),
        "seconds_until_tick": clock.seconds_until_tick,
    }


# =============================================================================
# Configuration Endpoints
# =============================================================================

@router.post("/preset")
async def set_preset(request: SetPresetRequest):
    """
    Apply a timing preset.
    
    Available presets: test, demo_fast, demo, casual, slow, realtime, daily
    """
    try:
        preset = ClockPreset(request.preset)
    except ValueError:
        valid = [p.value for p in ClockPreset]
        raise HTTPException(400, f"Invalid preset. Valid options: {valid}")
    
    clock = get_network_clock()
    await clock.set_preset(preset)
    
    return {
        "status": "ok",
        "preset": preset.value,
        "interval_seconds": clock.config.interval_seconds,
        "next_tick_in": clock.seconds_until_tick,
    }


@router.post("/interval")
async def set_interval(request: SetIntervalRequest):
    """
    Set a custom tick interval in seconds.
    
    Must be between 10 seconds and 86400 seconds (24 hours).
    """
    clock = get_network_clock()
    
    if request.seconds < clock.config.min_interval:
        raise HTTPException(400, f"Interval must be at least {clock.config.min_interval} seconds")
    if request.seconds > clock.config.max_interval:
        raise HTTPException(400, f"Interval cannot exceed {clock.config.max_interval} seconds")
    
    await clock.set_interval(request.seconds)
    
    return {
        "status": "ok",
        "interval_seconds": request.seconds,
        "next_tick_in": clock.seconds_until_tick,
    }


@router.post("/mode")
async def set_mode(request: SetModeRequest):
    """
    Set the clock mode.
    
    Modes:
    - auto: Automatic ticking on interval
    - manual: Only tick when triggered via API
    - paused: Clock is paused, no ticks
    """
    try:
        mode = ClockMode(request.mode)
    except ValueError:
        valid = [m.value for m in ClockMode]
        raise HTTPException(400, f"Invalid mode. Valid options: {valid}")
    
    clock = get_network_clock()
    await clock.set_mode(mode)
    
    return {
        "status": "ok",
        "mode": mode.value,
        "next_tick_in": clock.seconds_until_tick if mode == ClockMode.AUTO else None,
    }


# =============================================================================
# Control Endpoints
# =============================================================================

@router.post("/start")
async def start_clock():
    """Start the network clock (begins automatic ticking)."""
    clock = get_network_clock()
    await clock.start()
    
    return {
        "status": "started",
        "month": clock.current_month,
        "interval_seconds": clock.config.interval_seconds,
        "next_tick_in": clock.seconds_until_tick,
    }


@router.post("/stop")
async def stop_clock():
    """Stop the network clock completely."""
    clock = get_network_clock()
    await clock.stop()
    
    return {
        "status": "stopped",
        "month": clock.current_month,
    }


@router.post("/pause")
async def pause_clock():
    """Pause the network clock (can be resumed)."""
    clock = get_network_clock()
    await clock.pause()
    
    return {
        "status": "paused",
        "month": clock.current_month,
    }


@router.post("/resume")
async def resume_clock():
    """Resume a paused network clock."""
    clock = get_network_clock()
    await clock.resume()
    
    return {
        "status": "resumed",
        "month": clock.current_month,
        "next_tick_in": clock.seconds_until_tick,
    }


@router.post("/force-tick")
async def force_tick():
    """
    Force an immediate tick (admin only).
    
    Processes all pending actions and advances the month immediately.
    """
    clock = get_network_clock()
    
    if clock.is_processing:
        raise HTTPException(409, "A tick is already being processed")
    
    await clock.force_tick()
    
    return {
        "status": "ok",
        "month": clock.current_month,
        "next_tick_in": clock.seconds_until_tick,
    }


# =============================================================================
# Action Queue Endpoints
# =============================================================================

@router.post("/queue-action")
async def queue_action(request: QueueActionRequest):
    """
    Queue an action for the next tick.
    
    Actions are processed in priority order (highest first) when the month advances.
    """
    clock = get_network_clock()
    
    action = PendingAction(
        id=request.id,
        user_id=request.user_id,
        action_type=request.action_type,
        data=request.data,
        priority=request.priority,
    )
    
    clock.queue_action(action)
    
    return {
        "status": "queued",
        "action_id": action.id,
        "pending_count": clock.get_pending_count(),
        "seconds_until_tick": clock.seconds_until_tick,
    }


@router.delete("/queue-action/{action_id}")
async def remove_action(action_id: str):
    """Remove a pending action from the queue."""
    clock = get_network_clock()
    
    if clock.remove_action(action_id):
        return {"status": "removed", "action_id": action_id}
    else:
        raise HTTPException(404, f"Action {action_id} not found in queue")


@router.delete("/queue-actions")
async def clear_actions():
    """Clear all pending actions from the queue."""
    clock = get_network_clock()
    count = clock.get_pending_count()
    clock.clear_actions()
    
    return {"status": "cleared", "removed_count": count}


# =============================================================================
# Streaming Endpoint
# =============================================================================

@router.get("/stream")
async def clock_stream():
    """
    Server-Sent Events stream for real-time clock updates.
    
    Events:
    - clock_sync: Periodic state sync
    - tick_warning: Warning before tick
    - processing_started: Tick processing begun
    - month_completed: Tick completed
    - config_changed: Configuration changed
    - mode_changed: Mode changed
    """
    clock = get_network_clock()
    queue = clock.subscribe()
    
    async def event_generator():
        try:
            # Send initial state
            yield {
                "event": "clock_sync",
                "data": json.dumps(clock.get_state().to_dict())
            }
            
            while True:
                try:
                    # Wait for events with timeout
                    message = await asyncio.wait_for(queue.get(), timeout=10.0)
                    yield {
                        "event": message["event"],
                        "data": json.dumps(message["data"])
                    }
                except asyncio.TimeoutError:
                    # Send heartbeat/sync
                    yield {
                        "event": "clock_sync",
                        "data": json.dumps(clock.get_state().to_dict())
                    }
                    
        except asyncio.CancelledError:
            pass
        finally:
            clock.unsubscribe(queue)
    
    return EventSourceResponse(event_generator())


# =============================================================================
# Reset Endpoint (Testing)
# =============================================================================

@router.post("/reset")
async def reset_clock(
    month: int = Query(default=1, ge=1, le=1000),
    preset: str = Query(default="demo"),
):
    """
    Reset the network clock to a specific state (for testing).
    
    Clears all pending actions and resets the month counter.
    """
    try:
        preset_enum = ClockPreset(preset)
    except ValueError:
        preset_enum = ClockPreset.DEMO
    
    clock = get_network_clock()
    
    # Stop if running
    await clock.stop()
    
    # Reset state
    clock.current_month = month
    clock.clear_actions()
    await clock.set_preset(preset_enum)
    
    return {
        "status": "reset",
        "month": clock.current_month,
        "preset": preset_enum.value,
        "interval_seconds": clock.config.interval_seconds,
    }
