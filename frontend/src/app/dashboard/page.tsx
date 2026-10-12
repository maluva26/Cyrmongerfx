"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth";
import { api } from "@/lib/api";

type Kpi = { lessons_completed: number; lessons_total: number; average_quiz_score: number; analyses_this_month: number };

export default function HomePage() {
  const { token } = useAuth();
  const [data, setData] = useState<{ kpis: Kpi } | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) return;
    api.get("/dashboard", token).then(setData).catch((e) => setError(e.message));
  }, [token]);

  if (!token) return <p className="p-4">Please sign in.</p>;
  if (error) return <p className="p-4 text-red-600">{error}</p>;
  if (!data) return <p className="p-4">Loading...</p>;

  return (
    <div className="mx-auto max-w-5xl px-4 py-6">
      <h1 className="text-2xl font-bold">Home</h1>
      <div className="mt-4 grid grid-cols-2 gap-3 md:grid-cols-4">
        {[
          ["Lessons completed", `${data.kpis.lessons_completed}/${data.kpis.lessons_total}`],
          ["Avg quiz score", `${data.kpis.average_quiz_score}%`],
          ["Analyses this month", data.kpis.analyses_this_month],
        ].map(([k, v]) => (
          <div key={k as string} className="card p-4">
            <div className="text-xs text-gray-500">{k}</div>
            <div className="text-xl font-semibold">{v}</div>
          </div>
        ))}
      </div>
      <div className="mt-6">
        <h2 className="font-semibold">Quick actions</h2>
        <div className="mt-2 flex flex-wrap gap-2">
          <Link href="/analyze" className="btn btn-primary">Analyze chart</Link>
          <Link href="/learn" className="btn border border-[var(--border)]">Learn</Link>
          <Link href="/risk" className="btn border border-[var(--border)]">Risk calculator</Link>
          <Link href="/journal" className="btn border border-[var(--border)]">Journal</Link>
        </div>
      </div>
    </div>
  );
}
