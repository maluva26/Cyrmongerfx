"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth";
import { api } from "@/lib/api";

type Entry = { entry_id: string; notes: string; created_at: string };

export default function JournalPage() {
  const { token, status } = useAuth();
  const [entries, setEntries] = useState<Entry[]>([]);
  const [notes, setNotes] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      setEntries(await api.get<Entry[]>("/journal", token));
      setError("");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Journal entries could not be loaded.");
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    void load();
  }, [load]);

  const add = async () => {
    if (!token || !notes.trim()) return;
    setSaving(true);
    setError("");
    try {
      await api.post("/journal", { notes: notes.trim() }, token);
      setNotes("");
      await load();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Journal entry could not be saved.");
    } finally {
      setSaving(false);
    }
  };

  if (status === "loading") return <p className="p-4">Checking your session...</p>;
  if (status === "anonymous") {
    return <p className="p-4">Please <Link href="/login" className="text-brand-600 underline">sign in</Link>.</p>;
  }

  return (
    <main className="mx-auto max-w-3xl px-4 py-6">
      <h1 className="text-2xl font-bold">My Journal</h1>
      <p className="text-xs text-gray-500">Personal notes, not a broker statement.</p>
      <textarea
        className="input mt-3"
        rows={3}
        maxLength={5000}
        aria-label="Journal notes"
        placeholder="Write notes..."
        value={notes}
        onChange={(event) => setNotes(event.target.value)}
      />
      <button onClick={add} disabled={saving || !notes.trim()} className="btn btn-primary mt-2 disabled:opacity-50">
        {saving ? "Saving..." : "Save entry"}
      </button>
      {error && <p role="alert" className="mt-2 text-sm text-red-600">{error}</p>}
      <div className="mt-5 space-y-2">
        {loading ? <p className="text-sm text-gray-500">Loading entries...</p> : entries.length === 0 ? (
          <p className="text-sm text-gray-500">No journal entries yet.</p>
        ) : entries.map((entry) => (
          <article key={entry.entry_id} className="card p-3 text-sm">
            <p className="whitespace-pre-wrap">{entry.notes}</p>
            <time className="mt-2 block text-xs text-gray-500" dateTime={entry.created_at}>
              {new Date(entry.created_at).toLocaleString()}
            </time>
          </article>
        ))}
      </div>
    </main>
  );
}
