<script lang="ts">
  /**
   * GovernorChat - Interactive chat with the Network Governor AI
   * 
   * Allows users to ask questions about the network between clock ticks.
   * Uses streaming for real-time responses.
   */
  
  import { Send, Bot, User, Loader2, Sparkles } from 'lucide-svelte';
  import { Button } from "$lib/components/ui/button";
  import { API_V1 } from '$lib/config';
  
  // Props
  interface Props {
    apiBase?: string;
    userId?: string;
    compact?: boolean;
    hideHeader?: boolean;
  }
  
  let { 
    apiBase = API_V1,
    userId = undefined,
    compact = false,
    hideHeader = false
  }: Props = $props();
  
  // Chat state
  interface Message {
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
  }
  
  let messages = $state<Message[]>([]);
  let inputValue = $state('');
  let isLoading = $state(false);
  let streamingContent = $state('');
  
  // Suggested prompts
  const suggestions = [
    "How is the network performing?",
    "What properties are available?",
    "Explain how dividends work",
    "What should I invest in?",
  ];
  
  async function sendMessage(content?: string) {
    const message = content || inputValue.trim();
    if (!message || isLoading) return;
    
    // Add user message
    messages = [...messages, {
      role: 'user',
      content: message,
      timestamp: new Date(),
    }];
    
    inputValue = '';
    isLoading = true;
    streamingContent = '';
    
    try {
      // Use streaming endpoint
      const params = new URLSearchParams({ message });
      if (userId) params.append('user_id', userId);
      
      const response = await fetch(`${apiBase}/network/governor/chat/stream?${params}`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      
      if (!reader) {
        throw new Error('No response body');
      }
      
      let fullContent = '';
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.type === 'token' && data.content) {
                fullContent += data.content;
                streamingContent = fullContent;
              } else if (data.type === 'done') {
                // Streaming complete
              } else if (data.type === 'error') {
                throw new Error(data.message);
              }
            } catch (e) {
              // Ignore parse errors for incomplete chunks
            }
          }
        }
      }
      
      // Add assistant message
      messages = [...messages, {
        role: 'assistant',
        content: fullContent || 'I apologize, but I could not generate a response.',
        timestamp: new Date(),
      }];
      
    } catch (error) {
      console.error('Chat error:', error);
      messages = [...messages, {
        role: 'assistant',
        content: `I apologize, but I encountered an error: ${error}. Please try again.`,
        timestamp: new Date(),
      }];
    } finally {
      isLoading = false;
      streamingContent = '';
    }
  }
  
  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }
</script>

<div class="flex flex-col h-full bg-slate-900 {hideHeader ? '' : 'rounded-xl border border-slate-700'} overflow-hidden">
  <!-- Header (optional) -->
  {#if !hideHeader}
  <div class="flex items-center gap-3 px-4 py-3 bg-gradient-to-r from-blue-600/20 to-purple-600/20 border-b border-slate-700">
    <div class="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center">
      <Bot class="w-4 h-4 text-white" />
    </div>
    <div>
      <h3 class="text-sm font-semibold text-white">Network Governor</h3>
      <p class="text-xs text-slate-400">AI-powered network assistant</p>
    </div>
    <div class="ml-auto">
      <span class="flex items-center gap-1 text-xs text-emerald-400">
        <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
        Online
      </span>
    </div>
  </div>
  {/if}
  
  <!-- Messages -->
  <div class="flex-1 overflow-y-auto p-4 space-y-4 min-h-0">
    {#if messages.length === 0}
      <!-- Welcome state -->
      <div class="flex flex-col items-center justify-center h-full py-6">
        <div class="w-14 h-14 mb-4 rounded-full bg-gradient-to-br from-blue-500/20 to-purple-500/20 flex items-center justify-center">
          <Sparkles class="w-7 h-7 text-blue-400" />
        </div>
        <h4 class="text-lg font-medium text-white mb-2">Hello! I'm the Network Governor</h4>
        <p class="text-sm text-slate-400 mb-6 text-center max-w-md px-4">
          Ask me anything about the OSF simulation, properties, investment strategies, or market conditions.
        </p>
        <div class="flex flex-wrap gap-2 justify-center px-4 max-w-lg">
          {#each suggestions as suggestion}
            <button
              onclick={() => sendMessage(suggestion)}
              class="px-4 py-2 text-sm bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg border border-slate-600 transition-colors hover:border-slate-500"
            >
              {suggestion}
            </button>
          {/each}
        </div>
      </div>
    {:else}
      <!-- Message list -->
      {#each messages as message}
        <div class="flex gap-3 {message.role === 'user' ? 'flex-row-reverse' : ''}">
          <div class="w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center {message.role === 'user' ? 'bg-blue-600' : 'bg-gradient-to-br from-blue-500 to-purple-500'}">
            {#if message.role === 'user'}
              <User class="w-4 h-4 text-white" />
            {:else}
              <Bot class="w-4 h-4 text-white" />
            {/if}
          </div>
          <div class="max-w-[80%] px-4 py-2 rounded-2xl {message.role === 'user' ? 'bg-blue-600 text-white rounded-br-md' : 'bg-slate-800 text-slate-200 rounded-bl-md'}">
            <p class="text-sm whitespace-pre-wrap">{message.content}</p>
          </div>
        </div>
      {/each}
      
      <!-- Streaming message -->
      {#if isLoading && streamingContent}
        <div class="flex gap-3">
          <div class="w-8 h-8 rounded-full flex-shrink-0 bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center">
            <Bot class="w-4 h-4 text-white" />
          </div>
          <div class="max-w-[80%] px-4 py-2 rounded-2xl bg-slate-800 text-slate-200 rounded-bl-md">
            <p class="text-sm whitespace-pre-wrap">{streamingContent}<span class="animate-pulse">▋</span></p>
          </div>
        </div>
      {/if}
      
      <!-- Loading indicator -->
      {#if isLoading && !streamingContent}
        <div class="flex gap-3">
          <div class="w-8 h-8 rounded-full flex-shrink-0 bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center">
            <Loader2 class="w-4 h-4 text-white animate-spin" />
          </div>
          <div class="px-4 py-2 rounded-2xl bg-slate-800 text-slate-400 rounded-bl-md">
            <p class="text-sm">Thinking...</p>
          </div>
        </div>
      {/if}
    {/if}
  </div>
  
  <!-- Input -->
  <div class="p-4 border-t border-slate-700 bg-slate-800/80">
    <div class="flex gap-3">
      <input
        type="text"
        bind:value={inputValue}
        onkeydown={handleKeydown}
        placeholder="Ask the Governor about the network, properties, or market..."
        disabled={isLoading}
        class="flex-1 px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50"
      />
      <Button
        onclick={() => sendMessage()}
        disabled={isLoading || !inputValue.trim()}
        class="px-5 py-3"
      >
        {#if isLoading}
          <Loader2 class="w-5 h-5 animate-spin" />
        {:else}
          <Send class="w-5 h-5" />
        {/if}
      </Button>
    </div>
  </div>
</div>
