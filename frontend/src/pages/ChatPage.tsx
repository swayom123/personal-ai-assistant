import React, { useState, useEffect, useRef } from 'react';
import {
  Send,
  Plus,
  Trash2,
  Cpu,
  Bot,
  User,
  Sparkles,
  Search,
  MessageSquare,
  Copy,
  Check,
  AlertTriangle,
  Radio,
} from 'lucide-react';
import { apiService } from '../services/api';
import { ChatMessage, ConversationItem, ModelInfo } from '../types/api';

export const ChatPage: React.FC = () => {
  const [conversations, setConversations] = useState<ConversationItem[]>([]);
  const [activeConvId, setActiveConvId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamBuffer, setStreamBuffer] = useState('');
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [activeProvider, setActiveProvider] = useState<string>('auto');
  const [useStreamMode, setUseStreamMode] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const [errorBanner, setErrorBanner] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Load models on mount
  useEffect(() => {
    apiService
      .getModels()
      .then((res) => {
        setModels(res.models);
        setActiveProvider(res.active_provider);
        const defaultM = res.models.find((m) => m.is_default) || res.models[0];
        if (defaultM) setSelectedModel(defaultM.id);
      })
      .catch((err) => console.error('Failed to load models:', err));

    loadConversations();
  }, []);

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamBuffer]);

  const loadConversations = async () => {
    try {
      const list = await apiService.listConversations();
      setConversations(list);
      if (list.length > 0 && !activeConvId) {
        selectConversation(list[0].id);
      }
    } catch (err) {
      console.error('Failed to load conversations:', err);
    }
  };

  const selectConversation = async (id: string) => {
    setActiveConvId(id);
    setErrorBanner(null);
    try {
      const detail = await apiService.getConversation(id);
      setMessages(detail.messages);
    } catch (err) {
      console.error(`Failed to load conversation ${id}:`, err);
    }
  };

  const handleNewConversation = async () => {
    try {
      const newConv = await apiService.createConversation('New Chat');
      setConversations([newConv, ...conversations]);
      setActiveConvId(newConv.id);
      setMessages([]);
    } catch (err) {
      console.error('Failed to create conversation:', err);
    }
  };

  const handleDeleteConversation = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await apiService.deleteConversation(id);
      const remaining = conversations.filter((c) => c.id !== id);
      setConversations(remaining);
      if (activeConvId === id) {
        if (remaining.length > 0) {
          selectConversation(remaining[0].id);
        } else {
          setActiveConvId(null);
          setMessages([]);
        }
      }
    } catch (err) {
      console.error('Failed to delete conversation:', err);
    }
  };

  const handleSend = async (overridePrompt?: string) => {
    const textToSend = overridePrompt || inputMessage;
    if (!textToSend.trim() || isStreaming) return;

    setErrorBanner(null);
    const userMsg: ChatMessage = { role: 'user', content: textToSend };
    setMessages((prev) => [...prev, userMsg]);
    setInputMessage('');

    if (useStreamMode) {
      setIsStreaming(true);
      setStreamBuffer('');

      await apiService.streamChatMessage(
        {
          message: textToSend,
          conversation_id: activeConvId || undefined,
          model: selectedModel || undefined,
        },
        {
          onMeta: (meta) => {
            if (!activeConvId) {
              setActiveConvId(meta.conversation_id);
              loadConversations();
            }
          },
          onChunk: (chunk) => {
            setStreamBuffer((prev) => prev + chunk);
          },
          onDone: (fullContent) => {
            setMessages((prev) => [...prev, { role: 'assistant', content: fullContent }]);
            setStreamBuffer('');
            setIsStreaming(false);
            loadConversations();
          },
          onError: (err) => {
            setErrorBanner(err.message);
            setIsStreaming(false);
            setStreamBuffer('');
          },
        }
      );
    } else {
      setIsStreaming(true);
      try {
        const response = await apiService.sendChatMessage({
          message: textToSend,
          conversation_id: activeConvId || undefined,
          model: selectedModel || undefined,
        });

        if (!activeConvId) {
          setActiveConvId(response.conversation_id);
          loadConversations();
        }
        setMessages((prev) => [...prev, response.message]);
      } catch (err: unknown) {
        setErrorBanner(err instanceof Error ? err.message : 'Chat request failed');
      } finally {
        setIsStreaming(false);
      }
    }
  };

  const handleCopy = (content: string, index: number) => {
    navigator.clipboard.writeText(content);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const filteredConversations = conversations.filter((c) =>
    c.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const quickStarters = [
    'Explain the AI assistant architecture pipeline',
    'Write a TypeScript function to debounce an API call',
    'What models and providers are currently active?',
  ];

  return (
    <div className="h-[calc(100vh-8rem)] flex rounded-2xl border border-border bg-surface overflow-hidden shadow-2xl">
      {/* Conversations Sidebar */}
      <div className="w-72 border-r border-border bg-background flex flex-col justify-between shrink-0">
        <div className="p-4 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-text-primary flex items-center gap-2">
              <MessageSquare className="w-4 h-4 text-primary" />
              Conversations
            </h3>
            <button
              onClick={handleNewConversation}
              className="p-1.5 rounded-lg bg-primary/15 text-primary hover:bg-primary/25 border border-primary/30 transition-all"
              title="New Conversation"
            >
              <Plus className="w-4 h-4" />
            </button>
          </div>

          {/* Search bar */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-text-muted" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search chats..."
              className="w-full bg-surface border border-border rounded-lg pl-8 pr-3 py-1.5 text-xs text-text-primary placeholder-text-muted outline-none focus:border-primary"
            />
          </div>

          {/* Conversations list */}
          <div className="space-y-1 overflow-y-auto max-h-[calc(100vh-21rem)] pr-1">
            {filteredConversations.length === 0 ? (
              <div className="text-center py-6 text-xs text-text-muted">
                No conversations found.
              </div>
            ) : (
              filteredConversations.map((conv) => (
                <div
                  key={conv.id}
                  onClick={() => selectConversation(conv.id)}
                  className={`group flex items-center justify-between p-2.5 rounded-lg cursor-pointer transition-all text-xs ${
                    activeConvId === conv.id
                      ? 'bg-primary/15 text-text-primary border-l-2 border-primary font-medium'
                      : 'text-text-secondary hover:bg-surface-elevated hover:text-text-primary'
                  }`}
                >
                  <span className="truncate pr-2">{conv.title}</span>
                  <button
                    onClick={(e) => handleDeleteConversation(conv.id, e)}
                    className="opacity-0 group-hover:opacity-100 p-1 hover:text-red-400 rounded transition-opacity"
                    title="Delete conversation"
                  >
                    <Trash2 className="w-3 h-3" />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Provider info pill */}
        <div className="p-3 border-t border-border bg-surface text-xs font-mono space-y-1">
          <div className="flex justify-between items-center text-text-muted">
            <span>Provider:</span>
            <span className="text-primary uppercase font-bold text-[11px]">{activeProvider}</span>
          </div>
          <div className="flex justify-between items-center text-text-muted">
            <span>Streaming:</span>
            <span className={useStreamMode ? 'text-emerald-400' : 'text-text-muted'}>
              {useStreamMode ? 'SSE Enabled' : 'Buffered'}
            </span>
          </div>
        </div>
      </div>

      {/* Main Chat Interface */}
      <div className="flex-1 flex flex-col justify-between bg-surface-subtle min-w-0">
        {/* Top Control Bar */}
        <div className="h-14 border-b border-border bg-surface px-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-1.5 rounded-lg bg-primary/10 text-primary border border-primary/20">
              <Bot className="w-4 h-4" />
            </div>
            <div>
              <div className="text-sm font-semibold text-text-primary">Aether AI Engine</div>
              <div className="text-[10px] font-mono text-text-muted">
                {activeConvId ? `Active Session: ${activeConvId.slice(0, 8)}...` : 'New Session'}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {/* Stream toggle */}
            <label className="hidden sm:flex items-center gap-2 text-xs font-mono text-text-secondary cursor-pointer">
              <Radio className={`w-3.5 h-3.5 ${useStreamMode ? 'text-emerald-400' : 'text-text-muted'}`} />
              <span>Stream</span>
              <input
                type="checkbox"
                checked={useStreamMode}
                onChange={(e) => setUseStreamMode(e.target.checked)}
                className="accent-primary"
              />
            </label>

            {/* Model Selector */}
            <div className="flex items-center gap-2">
              <Cpu className="w-3.5 h-3.5 text-primary" />
              <select
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="bg-background border border-border rounded-lg px-2.5 py-1 text-xs text-primary font-mono outline-none focus:border-primary"
              >
                {models.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.name} ({m.provider})
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Error Banner */}
        {errorBanner && (
          <div className="p-3 bg-red-500/15 border-b border-red-500/30 text-red-400 text-xs font-mono flex items-center justify-between px-6">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 shrink-0" />
              <span>{errorBanner}</span>
            </div>
            <button onClick={() => setErrorBanner(null)} className="hover:text-white text-xs">
              Dismiss
            </button>
          </div>
        )}

        {/* Messages Stream */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 && !streamBuffer ? (
            <div className="h-full flex flex-col items-center justify-center text-center space-y-5 max-w-lg mx-auto py-12">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-primary to-accent-violet p-0.5 flex items-center justify-center shadow-lg shadow-primary/25">
                <div className="w-full h-full bg-background rounded-[14px] flex items-center justify-center">
                  <Sparkles className="w-6 h-6 text-primary" />
                </div>
              </div>
              <div>
                <h3 className="text-lg font-bold text-text-primary">Aether Central AI Core</h3>
                <p className="text-xs text-text-secondary mt-1">
                  Type your prompt below to interact directly with the LLM engine pipeline.
                </p>
              </div>

              {/* Starter chips */}
              <div className="w-full space-y-2 pt-2">
                {quickStarters.map((starter) => (
                  <button
                    key={starter}
                    onClick={() => handleSend(starter)}
                    className="w-full text-left p-2.5 rounded-xl bg-surface border border-border hover:border-primary/50 text-xs text-text-secondary hover:text-text-primary transition-all flex items-center justify-between group"
                  >
                    <span>{starter}</span>
                    <Send className="w-3 h-3 text-primary opacity-0 group-hover:opacity-100 transition-opacity" />
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <>
              {messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex gap-3.5 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  {msg.role === 'assistant' && (
                    <div className="w-8 h-8 rounded-lg bg-primary/20 border border-primary/30 flex items-center justify-center shrink-0 text-primary">
                      <Bot className="w-4 h-4" />
                    </div>
                  )}

                  <div
                    className={`max-w-2xl rounded-2xl p-4 text-xs leading-relaxed space-y-2 ${
                      msg.role === 'user'
                        ? 'bg-primary text-white shadow-md shadow-primary/10'
                        : 'bg-surface border border-border text-text-primary shadow-sm'
                    }`}
                  >
                    <div className="flex items-center justify-between text-[10px] font-mono opacity-60">
                      <span>{msg.role === 'user' ? 'You' : 'Aether'}</span>
                      {msg.role === 'assistant' && (
                        <button
                          onClick={() => handleCopy(msg.content, idx)}
                          className="hover:opacity-100 flex items-center gap-1"
                        >
                          {copiedIndex === idx ? (
                            <Check className="w-3 h-3 text-emerald-400" />
                          ) : (
                            <Copy className="w-3 h-3" />
                          )}
                          <span>{copiedIndex === idx ? 'Copied' : 'Copy'}</span>
                        </button>
                      )}
                    </div>
                    <div className="whitespace-pre-wrap font-sans text-sm">{msg.content}</div>
                  </div>

                  {msg.role === 'user' && (
                    <div className="w-8 h-8 rounded-lg bg-surface-elevated border border-border flex items-center justify-center shrink-0 text-text-secondary">
                      <User className="w-4 h-4" />
                    </div>
                  )}
                </div>
              ))}

              {/* Streaming token buffer */}
              {isStreaming && streamBuffer && (
                <div className="flex gap-3.5 justify-start">
                  <div className="w-8 h-8 rounded-lg bg-primary/20 border border-primary/30 flex items-center justify-center shrink-0 text-primary">
                    <Bot className="w-4 h-4 animate-pulse" />
                  </div>
                  <div className="max-w-2xl rounded-2xl p-4 text-xs leading-relaxed space-y-2 bg-surface border border-border text-text-primary shadow-sm">
                    <div className="text-[10px] font-mono text-emerald-400 flex items-center gap-1.5">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
                      Streaming response...
                    </div>
                    <div className="whitespace-pre-wrap font-sans text-sm">{streamBuffer}</div>
                  </div>
                </div>
              )}

              {/* Loading spinner before tokens arrive */}
              {isStreaming && !streamBuffer && (
                <div className="flex gap-3.5 items-center text-xs font-mono text-text-muted p-2">
                  <div className="w-2 h-2 rounded-full bg-primary animate-ping" />
                  <span>Aether is processing prompt context...</span>
                </div>
              )}
            </>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <div className="p-4 bg-surface border-t border-border">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex items-end gap-3 max-w-4xl mx-auto"
          >
            <div className="flex-1 rounded-xl bg-background border border-border focus-within:border-primary transition-all p-2 flex items-center">
              <textarea
                ref={textareaRef}
                rows={1}
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                placeholder="Type your message... (Enter to send, Shift+Enter for newline)"
                className="w-full bg-transparent border-none outline-none text-xs text-text-primary placeholder-text-muted resize-none max-h-32 px-2"
              />
            </div>
            <button
              type="submit"
              disabled={!inputMessage.trim() || isStreaming}
              className="p-3 rounded-xl bg-primary hover:bg-primary-hover disabled:opacity-40 text-white transition-all shadow-md shadow-primary/20 shrink-0"
              title="Send Message"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
