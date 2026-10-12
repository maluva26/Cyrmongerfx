/* eslint-disable @next/next/no-img-element */
"use client";

import Link from "next/link";
import { FormEvent, useCallback, useEffect, useRef, useState } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";

type ChatMessage = {
  message_id: string;
  author_id: string | null;
  author_name: string;
  body: string;
  image_url: string | null;
  is_demo: boolean;
  created_at: string;
};

const ALLOWED_IMAGE_TYPES = ["image/png", "image/jpeg", "image/webp"];
const MAX_IMAGE_BYTES = 2 * 1024 * 1024;

function formatTime(value: string) {
  return new Intl.DateTimeFormat(undefined, { hour: "2-digit", minute: "2-digit" }).format(new Date(value));
}

export default function ForexChatPage() {
  const { token, user, status } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [body, setBody] = useState("");
  const [image, setImage] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");
  const bottomRef = useRef<HTMLDivElement | null>(null);

  const loadMessages = useCallback(async (silent = false) => {
    if (!token) return;
    if (!silent) setLoading(true);
    try {
      const data = await api.get<ChatMessage[]>("/community/messages", token);
      setMessages(Array.isArray(data) ? data : []);
      setError("");
    } catch (cause) {
      if (!silent) setError(cause instanceof Error ? cause.message : "Chat messages could not be loaded.");
    } finally {
      if (!silent) setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    if (status !== "authenticated" || !token) return;
    void loadMessages();
    const timer = window.setInterval(() => void loadMessages(true), 5000);
    return () => window.clearInterval(timer);
  }, [loadMessages, status, token]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages.length]);

  useEffect(() => {
    return () => {
      if (preview?.startsWith("blob:")) URL.revokeObjectURL(preview);
    };
  }, [preview]);

  const chooseImage = (file: File | undefined) => {
    setError("");
    if (!file) return;
    if (!ALLOWED_IMAGE_TYPES.includes(file.type)) {
      setError("Choose a PNG, JPEG, or WebP image.");
      return;
    }
    if (file.size > MAX_IMAGE_BYTES) {
      setError("Image must be 2 MB or smaller.");
      return;
    }
    if (preview?.startsWith("blob:")) URL.revokeObjectURL(preview);
    setImage(file);
    setPreview(URL.createObjectURL(file));
  };

  const clearImage = () => {
    if (preview?.startsWith("blob:")) URL.revokeObjectURL(preview);
    setImage(null);
    setPreview(null);
  };

  const sendMessage = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!token || sending || (!body.trim() && !image)) return;
    setSending(true);
    setError("");
    try {
      const form = new FormData();
      form.append("body", body.trim());
      if (image) form.append("image", image);
      const message = await api.upload<ChatMessage>("/community/messages", form, token);
      setMessages((current) => [...current, message]);
      setBody("");
      clearImage();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Message could not be sent.");
    } finally {
      setSending(false);
    }
  };

  if (status === "loading") return <p className="mx-auto max-w-5xl px-4 py-8">Checking your session...</p>;
  if (status === "anonymous") {
    return <p className="mx-auto max-w-5xl px-4 py-8">Please <Link href="/login" className="text-brand-600 underline">sign in</Link> to open Forex Chat.</p>;
  }

  return (
    <main className="mx-auto flex h-[calc(100vh-4.75rem)] max-w-5xl flex-col px-4 py-5 md:h-screen md:py-6">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[var(--border)] pb-4">
        <div>
          <h1 className="text-2xl font-bold">Forex Chat</h1>
          <p className="mt-1 text-sm text-gray-600">Live community room for traders online 24/7.</p>
        </div>
        <div className="rounded-full border border-green-200 bg-green-50 px-3 py-1 text-xs font-semibold text-green-700">
          Live
        </div>
      </div>

      {error && <p role="alert" className="mt-3 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}

      <section className="mt-4 min-h-0 flex-1 overflow-y-auto pr-1" aria-live="polite">
        {loading ? (
          <p className="py-10 text-sm text-gray-600">Loading chat...</p>
        ) : messages.length === 0 ? (
          <p className="py-10 text-sm text-gray-600">No messages yet.</p>
        ) : (
          <div className="space-y-3">
            {messages.map((message) => {
              const mine = Boolean(user?.user_id && message.author_id === user.user_id);
              return (
                <article key={message.message_id} className={`flex ${mine ? "justify-end" : "justify-start"}`}>
                  <div className={`max-w-[82%] rounded-lg px-3 py-2 shadow-sm md:max-w-[68%] ${
                    mine ? "bg-brand-600 text-white" : "border border-[var(--border)] bg-[var(--surface)]"
                  }`}>
                    <div className={`mb-1 flex items-center justify-between gap-3 text-[11px] ${
                      mine ? "text-sky-100" : "text-gray-500"
                    }`}>
                      <span className="font-semibold">{mine ? "You" : message.author_name}</span>
                      <span>{formatTime(message.created_at)}</span>
                    </div>
                    {message.image_url && (
                      <img
                        src={message.image_url}
                        alt=""
                        className="mb-2 max-h-72 w-full rounded-md object-cover"
                      />
                    )}
                    {message.body && <p className="whitespace-pre-wrap break-words text-sm leading-relaxed">{message.body}</p>}
                  </div>
                </article>
              );
            })}
            <div ref={bottomRef} />
          </div>
        )}
      </section>

      <form onSubmit={sendMessage} className="mt-4 border-t border-[var(--border)] pt-3">
        {preview && (
          <div className="mb-3 flex items-center gap-3">
            <img src={preview} alt="Selected upload" className="h-16 w-16 rounded-md object-cover" />
            <button type="button" onClick={clearImage} className="btn border border-[var(--border)]">Remove</button>
          </div>
        )}
        <div className="flex items-end gap-2">
          <label className="btn shrink-0 cursor-pointer border border-[var(--border)]" title="Attach picture">
            <span aria-hidden="true">+</span>
            <input
              type="file"
              accept="image/png,image/jpeg,image/webp"
              className="sr-only"
              onChange={(event) => {
                chooseImage(event.currentTarget.files?.[0]);
                event.currentTarget.value = "";
              }}
            />
          </label>
          <textarea
            className="input min-h-11 flex-1 resize-none"
            rows={1}
            value={body}
            placeholder="Message Forex Chat"
            onChange={(event) => setBody(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                event.currentTarget.form?.requestSubmit();
              }
            }}
          />
          <button type="submit" disabled={sending || (!body.trim() && !image)} className="btn btn-primary shrink-0 disabled:opacity-50">
            {sending ? "Sending" : "Send"}
          </button>
        </div>
      </form>
    </main>
  );
}
