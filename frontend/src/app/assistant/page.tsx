"use client";
import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth";
import { api } from "@/lib/api";

type Msg = { role: string; content: string; blocked: boolean };

export default function AssistantPage() {
  const { token } = useAuth();
  const [convId, setConvId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const send = async () => {
    if (!input.trim() || !token) return;
    setLoading(true); setError("");
    try {
      const data = await api.post("/assistant/chat", { conversation_id: convId, message: input }, token);
      setConvId(data.conversation_id);
      setMessages((m) => [...m, { role: "user", content: input, blocked: false }, { role: "assistant", content: data.reply, blocked: data.blocked }]);
      setInput("");
    } catch (err: any) { setError(err.message); }
    setLoading(false);
  };

  return (
    <div className="mx-auto max-w-3xl px-4 py-6">
      <h1 className="text-2xl font-bold">AI Assistant</h1>
      <p className="text-xs text-gray-500">Educational only. Not financial advice.</p>
      <div className="mt-4 h-[50vh] overflow-y-auto rounded border p-3">
        {messages.map((m, i) => (
          <div key={i} className={`mb-2 ${m.role === "user" ? "text-right" : "text-left"}`}>
            <span className={`inline-block rounded px-2 py-1 text-sm ${m.role === "user" ? "bg-brand-100" : "bg-gray-100"}`}>
              {m.content}
              {m.blocked && <span className="ml-1 text-xs text-red-600">[blocked]</span>}
            </span>
          </div>
        ))}
      </div>
      {error && <p className="mt-1 text-red-600">{error}</p>}
      <div className="mt-2 flex gap-2">
        <input className="input flex-1" value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => e.key === "Enter" && send()} />
        <button onClick={send} disabled={loading} className="btn btn-primary">{loading ? "..." : "Send"}</button>
      </div>
    </div>
  );
}
