/**
 * AIAssistant.jsx — Chat interface powered by FleetBot (Claude).
 * History is stored in React state per session — not persisted to DB.
 */

import { useState, useRef, useEffect } from "react";
import Layout from "../components/Layout";
import api from "../api";

const SUGGESTIONS = [
  "Which trucks need an oil change?",
  "Are there any overdue maintenance items?",
  "Summarize all open incidents",
  "Which drivers are on duty right now?",
  "What routes are scheduled for today?",
  "Are any driver documents expiring soon?",
  "What did we spend on fuel and repairs this month?",
  "Which trucks are in the best shape?",
];

export default function AIAssistant() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function send(text) {
    if (!text.trim() || loading) return;
    const userMsg = { role: "user", content: text };
    const next = [...messages, userMsg];
    setMessages(next);
    setInput("");
    setLoading(true);

    try {
      const res = await api.post("/ai/chat", {
        message: text,
        history: messages, // prior history, not including this message
      });
      setMessages([...next, { role: "assistant", content: res.data.response }]);
    } catch {
      setMessages([...next, { role: "assistant", content: "Sorry, I couldn't reach the AI assistant. Please check that ANTHROPIC_API_KEY is configured." }]);
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(e) {
    e.preventDefault();
    send(input);
  }

  return (
    <Layout>
      <div className="max-w-3xl mx-auto flex flex-col h-[calc(100vh-8rem)] md:h-[calc(100vh-4rem)]">
        <div className="mb-4">
          <h1 className="text-2xl font-bold text-gray-900">AI Assistant</h1>
          <p className="text-sm text-gray-500">FleetBot — Ask anything about your fleet</p>
        </div>

        {/* Chat area */}
        <div className="flex-1 overflow-y-auto space-y-4 pb-4">
          {/* Welcome */}
          {messages.length === 0 && (
            <div className="text-center py-10">
              <div className="text-5xl mb-3">🤖</div>
              <h2 className="text-lg font-semibold text-gray-800 mb-1">Hi, I'm FleetBot</h2>
              <p className="text-sm text-gray-500 mb-6">I have live access to your entire fleet — ask me anything.</p>
              <div className="flex flex-col gap-2 max-w-xs mx-auto">
                {SUGGESTIONS.map((s) => (
                  <button
                    key={s}
                    onClick={() => send(s)}
                    className="text-left text-sm text-[#3aa3a8] bg-[#68ccd1]/10 hover:bg-[#68ccd1]/20 px-4 py-2.5 rounded-xl transition-colors"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Messages */}
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              {msg.role === "assistant" && (
                <div className="w-7 h-7 rounded-full bg-[#68ccd1] flex items-center justify-center text-white text-xs mr-2 mt-1 shrink-0">
                  🤖
                </div>
              )}
              <div
                className={`max-w-[80%] px-4 py-3 rounded-2xl text-sm whitespace-pre-wrap ${
                  msg.role === "user"
                    ? "bg-[#68ccd1] text-white rounded-br-md"
                    : "bg-white border border-gray-200 text-gray-800 rounded-bl-md"
                }`}
              >
                {msg.content}
              </div>
            </div>
          ))}

          {/* Loading indicator */}
          {loading && (
            <div className="flex justify-start">
              <div className="w-7 h-7 rounded-full bg-[#68ccd1] flex items-center justify-center text-white text-xs mr-2 mt-1 shrink-0">
                🤖
              </div>
              <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-md px-4 py-3">
                <div className="flex gap-1 items-center">
                  <span className="w-2 h-2 bg-gray-300 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                  <span className="w-2 h-2 bg-gray-300 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                  <span className="w-2 h-2 bg-gray-300 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                </div>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input bar */}
        <form onSubmit={handleSubmit} className="flex gap-2 pt-3 border-t border-gray-200 bg-gray-50">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about your fleet…"
            disabled={loading}
            className="flex-1 border border-gray-300 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-[#68ccd1] disabled:opacity-60"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="bg-[#68ccd1] hover:bg-[#4db8be] text-white font-semibold px-4 py-3 rounded-xl text-sm transition-colors disabled:opacity-40"
          >
            Send
          </button>
        </form>
      </div>
    </Layout>
  );
}
