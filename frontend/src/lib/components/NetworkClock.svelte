<script lang="ts">
  /**
   * NetworkClock - Synchronized network time display
   * 
   * Connects to the backend clock service via SSE for real-time updates.
   * Shows current month, countdown to next tick, and pending actions.
   * 
   * Presets:
   * - test: 30s (development)
   * - demo_fast: 2min
   * - demo: 5min (default)
   * - casual: 15min
   * - slow: 30min
   * - realtime: 1hr
   * - daily: 24hr
   */
  
  import { onMount, onDestroy } from 'svelte';
  import { 
    Clock, 
    Calendar, 
    Loader2, 
    Pause, 
    Play, 
    Settings,
    ChevronDown,
    Zap,
    AlertCircle
  } from 'lucide-svelte';
  import { API_V1 } from '$lib/config';
  
  // Props
  interface Props {
    apiBase?: string;
    showControls?: boolean;
    compact?: boolean;
  }
  
  let { 
    apiBase = API_V1,
    showControls = false,
    compact = false
  }: Props = $props();
  
  // Clock state
  let currentMonth = $state(1);
  let secondsUntilTick = $state(0);
  let isProcessing = $state(false);
  let clockMode = $state<'auto' | 'manual' | 'paused'>('auto');
  let preset = $state('demo');
  let intervalSeconds = $state(300);
  let warningActive = $state(false);
  let pendingActionsCount = $state(0);
  let connected = $state(false);
  let error = $state<string | null>(null);
  
  // UI state
  let showPresetMenu = $state(false);
  
  // Event source
  let eventSource: EventSource | null = null;
  let countdownInterval: number | null = null;
  let reconnectTimeout: number | null = null;
  
  // Available presets
  const presets = [
    { id: 'test', label: 'Test (30s)', interval: 30 },
    { id: 'demo_fast', label: 'Demo Fast (2m)', interval: 120 },
    { id: 'demo', label: 'Demo (5m)', interval: 300 },
    { id: 'casual', label: 'Casual (15m)', interval: 900 },
    { id: 'slow', label: 'Slow (30m)', interval: 1800 },
    { id: 'realtime', label: 'Realtime (1h)', interval: 3600 },
  ];
  
  // Format seconds as MM:SS
  function formatTime(seconds: number): string {
    if (seconds <= 0) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }
  
  // Connect to SSE stream
  function connect() {
    if (eventSource) {
      eventSource.close();
    }
    
    error = null;
    
    try {
      eventSource = new EventSource(`${apiBase}/network/clock/stream`);
      
      eventSource.onopen = () => {
        connected = true;
        error = null;
        console.log('[NetworkClock] Connected to clock stream');
      };
      
      eventSource.onerror = (e) => {
        console.error('[NetworkClock] Connection error', e);
        connected = false;
        error = 'Connection lost';
        
        // Reconnect after 5 seconds
        if (reconnectTimeout) clearTimeout(reconnectTimeout);
        reconnectTimeout = setTimeout(() => {
          console.log('[NetworkClock] Attempting reconnect...');
          connect();
        }, 5000) as unknown as number;
      };
      
      eventSource.addEventListener('clock_sync', (e) => {
        const data = JSON.parse(e.data);
        updateState(data);
      });
      
      eventSource.addEventListener('tick_warning', (e) => {
        const data = JSON.parse(e.data);
        warningActive = true;
        secondsUntilTick = data.seconds_until_tick;
        pendingActionsCount = data.pending_actions;
      });
      
      eventSource.addEventListener('processing_started', (e) => {
        const data = JSON.parse(e.data);
        isProcessing = true;
        currentMonth = data.month - 1; // Still on previous month during processing
      });
      
      eventSource.addEventListener('month_completed', (e) => {
        const data = JSON.parse(e.data);
        isProcessing = false;
        currentMonth = data.month;
        secondsUntilTick = data.next_tick_in;
        warningActive = false;
        
        // Dispatch custom event for parent components
        window.dispatchEvent(new CustomEvent('osf:month_completed', { 
          detail: data 
        }));
      });
      
      eventSource.addEventListener('config_changed', (e) => {
        const data = JSON.parse(e.data);
        if (data.preset) preset = data.preset;
        if (data.interval_seconds) intervalSeconds = data.interval_seconds;
        if (data.next_tick_in !== undefined) secondsUntilTick = data.next_tick_in;
      });
      
      eventSource.addEventListener('mode_changed', (e) => {
        const data = JSON.parse(e.data);
        clockMode = data.mode;
        if (data.next_tick_in !== undefined) secondsUntilTick = data.next_tick_in;
      });
      
      eventSource.addEventListener('clock_paused', () => {
        clockMode = 'paused';
      });
      
      eventSource.addEventListener('clock_resumed', (e) => {
        const data = JSON.parse(e.data);
        clockMode = 'auto';
        secondsUntilTick = data.next_tick_in;
      });
      
    } catch (e) {
      console.error('[NetworkClock] Failed to connect', e);
      error = 'Failed to connect';
    }
  }
  
  function updateState(data: any) {
    currentMonth = data.current_month;
    clockMode = data.mode;
    preset = data.preset;
    intervalSeconds = data.interval_seconds;
    isProcessing = data.is_processing;
    secondsUntilTick = data.seconds_until_tick;
    warningActive = data.warning_active;
  }
  
  // API calls
  async function setPreset(presetId: string) {
    try {
      const res = await fetch(`${apiBase}/network/clock/preset`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ preset: presetId })
      });
      if (res.ok) {
        preset = presetId;
        showPresetMenu = false;
      }
    } catch (e) {
      console.error('Failed to set preset', e);
    }
  }
  
  async function togglePause() {
    const endpoint = clockMode === 'paused' ? 'resume' : 'pause';
    try {
      await fetch(`${apiBase}/network/clock/${endpoint}`, { method: 'POST' });
    } catch (e) {
      console.error(`Failed to ${endpoint}`, e);
    }
  }
  
  async function forceTick() {
    try {
      await fetch(`${apiBase}/network/clock/force-tick`, { method: 'POST' });
    } catch (e) {
      console.error('Failed to force tick', e);
    }
  }
  
  onMount(() => {
    connect();
    
    // Local countdown (visual smoothness between SSE updates)
    countdownInterval = setInterval(() => {
      if (secondsUntilTick > 0 && !isProcessing && clockMode === 'auto') {
        secondsUntilTick--;
      }
    }, 1000) as unknown as number;
  });
  
  onDestroy(() => {
    if (eventSource) {
      eventSource.close();
    }
    if (countdownInterval) {
      clearInterval(countdownInterval);
    }
    if (reconnectTimeout) {
      clearTimeout(reconnectTimeout);
    }
  });
</script>

{#if compact}
  <!-- Compact version for headers -->
  <div class="flex items-center gap-3 px-3 py-1.5 bg-slate-800/50 rounded-lg border border-slate-700/50 text-sm">
    <div class="flex items-center gap-1.5">
      <Calendar class="w-3.5 h-3.5 text-slate-400" />
      <span class="text-slate-400">Month</span>
      <span class="font-bold text-blue-400">{currentMonth}</span>
    </div>
    
    <div class="w-px h-4 bg-slate-700"></div>
    
    {#if !connected}
      <div class="flex items-center gap-1.5 text-red-400">
        <AlertCircle class="w-3.5 h-3.5" />
        <span>Offline</span>
      </div>
    {:else if isProcessing}
      <div class="flex items-center gap-1.5 text-emerald-400">
        <Loader2 class="w-3.5 h-3.5 animate-spin" />
        <span>Processing...</span>
      </div>
    {:else if clockMode === 'paused'}
      <div class="flex items-center gap-1.5 text-slate-500">
        <Pause class="w-3.5 h-3.5" />
        <span>Paused</span>
      </div>
    {:else}
      <div class="flex items-center gap-1.5" class:text-amber-400={warningActive} class:text-slate-300={!warningActive}>
        <Clock class="w-3.5 h-3.5" />
        <span class="font-mono">{formatTime(secondsUntilTick)}</span>
      </div>
    {/if}
    
    {#if pendingActionsCount > 0}
      <div class="px-1.5 py-0.5 bg-amber-500/20 rounded text-xs text-amber-400 font-medium">
        {pendingActionsCount} pending
      </div>
    {/if}
  </div>
{:else}
  <!-- Full version with controls -->
  <div class="bg-gradient-to-r from-slate-800 to-slate-800/50 rounded-xl border border-slate-700/50 p-4">
    <div class="flex items-center justify-between gap-4">
      <!-- Month display -->
      <div class="flex items-center gap-4">
        <div class="flex flex-col">
          <span class="text-xs text-slate-500 uppercase tracking-wider">Network Month</span>
          <div class="flex items-center gap-2">
            <Calendar class="w-5 h-5 text-blue-400" />
            <span class="text-2xl font-bold text-white">{currentMonth}</span>
          </div>
        </div>
        
        <div class="w-px h-12 bg-slate-700"></div>
        
        <!-- Countdown / Status -->
        <div class="flex flex-col">
          <span class="text-xs text-slate-500 uppercase tracking-wider">
            {#if isProcessing}
              Status
            {:else if clockMode === 'paused'}
              Paused
            {:else}
              Next Update
            {/if}
          </span>
          
          {#if !connected}
            <div class="flex items-center gap-2 text-red-400">
              <AlertCircle class="w-5 h-5" />
              <span class="text-lg font-medium">Reconnecting...</span>
            </div>
          {:else if isProcessing}
            <div class="flex items-center gap-2 text-emerald-400">
              <Loader2 class="w-5 h-5 animate-spin" />
              <span class="text-lg font-medium">Processing Month {currentMonth + 1}...</span>
            </div>
          {:else if clockMode === 'paused'}
            <div class="flex items-center gap-2 text-slate-400">
              <Pause class="w-5 h-5" />
              <span class="text-lg font-medium">Clock Paused</span>
            </div>
          {:else}
            <div class="flex items-center gap-2" class:text-amber-400={warningActive} class:text-white={!warningActive}>
              <Clock class="w-5 h-5" />
              <span class="text-2xl font-mono font-bold">{formatTime(secondsUntilTick)}</span>
              {#if warningActive}
                <span class="text-xs text-amber-400 animate-pulse">Tick soon!</span>
              {/if}
            </div>
          {/if}
        </div>
      </div>
      
      <!-- Right side: pending + controls -->
      <div class="flex items-center gap-3">
        <!-- Pending actions -->
        {#if pendingActionsCount > 0}
          <div class="flex items-center gap-2 px-3 py-1.5 bg-amber-500/10 border border-amber-500/30 rounded-lg">
            <Zap class="w-4 h-4 text-amber-400" />
            <span class="text-sm font-medium text-amber-400">{pendingActionsCount} pending actions</span>
          </div>
        {/if}
        
        {#if showControls}
          <!-- Preset selector -->
          <div class="relative">
            <button
              onclick={() => showPresetMenu = !showPresetMenu}
              class="flex items-center gap-2 px-3 py-2 bg-slate-700/50 hover:bg-slate-700 rounded-lg text-sm text-slate-300 transition-colors"
            >
              <Settings class="w-4 h-4" />
              <span class="capitalize">{preset.replace('_', ' ')}</span>
              <ChevronDown class="w-4 h-4" />
            </button>
            
            {#if showPresetMenu}
              <div class="absolute top-full right-0 mt-2 w-48 bg-slate-800 border border-slate-700 rounded-lg shadow-xl z-50">
                {#each presets as p}
                  <button
                    onclick={() => setPreset(p.id)}
                    class="w-full px-4 py-2 text-left text-sm hover:bg-slate-700/50 transition-colors first:rounded-t-lg last:rounded-b-lg"
                    class:text-blue-400={preset === p.id}
                    class:text-slate-300={preset !== p.id}
                  >
                    {p.label}
                  </button>
                {/each}
              </div>
            {/if}
          </div>
          
          <!-- Pause/Resume -->
          <button
            onclick={togglePause}
            class="p-2 rounded-lg transition-colors {clockMode === 'paused' ? 'bg-amber-500/20 text-amber-400' : 'bg-slate-700/50 text-slate-300 hover:bg-slate-700'}"
            title={clockMode === 'paused' ? 'Resume' : 'Pause'}
          >
            {#if clockMode === 'paused'}
              <Play class="w-4 h-4" />
            {:else}
              <Pause class="w-4 h-4" />
            {/if}
          </button>
          
          <!-- Force tick -->
          <button
            onclick={forceTick}
            disabled={isProcessing}
            class="px-3 py-2 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 disabled:text-slate-500 text-white text-sm font-medium rounded-lg transition-colors"
            title="Force immediate tick"
          >
            Force Tick
          </button>
        {/if}
      </div>
    </div>
    
    <!-- Progress bar -->
    {#if clockMode === 'auto' && !isProcessing && connected}
      <div class="mt-3 h-1 bg-slate-700 rounded-full overflow-hidden">
        <div 
          class="h-full transition-all duration-1000 ease-linear rounded-full"
          class:bg-amber-500={warningActive}
          class:bg-blue-500={!warningActive}
          style="width: {Math.max(0, 100 - (secondsUntilTick / intervalSeconds) * 100)}%"
        ></div>
      </div>
    {/if}
  </div>
{/if}

<!-- Click outside to close preset menu -->
{#if showPresetMenu}
  <div 
    class="fixed inset-0 z-40" 
    onclick={() => showPresetMenu = false}
    onkeydown={(e) => e.key === 'Escape' && (showPresetMenu = false)}
    role="button"
    tabindex="-1"
  ></div>
{/if}
