"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth";
import { api } from "@/lib/api";

type ActivityReport = {
  quiz: { avg_score: number | string | null; count: number };
  lessons_completed: number;
  journal_entries: number;
  analyses_by_signal: { signal_category: string | null; count: number }[];
  analyses_by_pattern: { "detections__label": string | null; count: number }[];
};
type ExportFormat = "csv" | "pdf";

export default function ReportsPage() {
  const { token, status } = useAuth();
  const [data, setData] = useState<ActivityReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [exporting, setExporting] = useState<ExportFormat | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    if (status !== "authenticated" || !token) return;
    let active = true;
    setLoading(true);
    setData(null);
    setError("");

    api.get<ActivityReport>("/activity", token).then((report) => {
      if (active) setData(report);
    }).catch((cause: unknown) => {
      if (active) setError(cause instanceof Error ? cause.message : "The report could not be loaded.");
    }).finally(() => {
      if (active) setLoading(false);
    });

    return () => {
      active = false;
    };
  }, [status, token, reloadKey]);

  const exportReport = async (format: ExportFormat) => {
    if (!token) return;
    setError("");
    setExporting(format);
    try {
      const file = await api.download(`/activity/export?format=${format}`, token);
      const objectUrl = URL.createObjectURL(file);
      const link = document.createElement("a");
      link.href = objectUrl;
      link.download = `activity-report.${format}`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.setTimeout(() => URL.revokeObjectURL(objectUrl), 1000);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : `The ${format.toUpperCase()} export failed.`);
    } finally {
      setExporting(null);
    }
  };

  if (status === "loading") return <p className="mx-auto max-w-5xl px-4 py-8">Checking your session...</p>;
  if (status === "anonymous") {
    return <p className="mx-auto max-w-5xl px-4 py-8">Please <Link href="/login" className="text-brand-600 underline">sign in</Link> to view reports.</p>;
  }

  return (
    <main className="mx-auto max-w-5xl px-4 py-6">
      <header className="flex flex-wrap items-end justify-between gap-3 border-b border-[var(--border)] pb-4">
        <div>
          <h1 className="text-2xl font-bold">Reports</h1>
          <p className="mt-1 text-sm text-gray-600">A summary of your activity on this platform.</p>
        </div>
        <div className="flex gap-2">
          <button type="button" onClick={() => void exportReport("csv")} disabled={!data || exporting !== null} className="btn border border-[var(--border)] disabled:opacity-50">
            {exporting === "csv" ? "Preparing CSV..." : "Export CSV"}
          </button>
          <button type="button" onClick={() => void exportReport("pdf")} disabled={!data || exporting !== null} className="btn border border-[var(--border)] disabled:opacity-50">
            {exporting === "pdf" ? "Preparing PDF..." : "Export PDF"}
          </button>
        </div>
      </header>

      {error && (
        <div className="mt-4 flex flex-wrap items-center justify-between gap-3 border-y border-red-200 py-3 text-sm text-red-700">
          <p role="alert">{error}</p>
          {!data && <button type="button" onClick={() => setReloadKey((key) => key + 1)} className="btn border border-red-300">Retry</button>}
        </div>
      )}

      {loading ? (
        <p className="py-10 text-sm text-gray-600" aria-live="polite">Loading report...</p>
      ) : data ? (
        <>
          <section className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4" aria-label="Report summary">
            <div className="card p-4">
              <p className="text-xs text-gray-500">Average quiz score</p>
              <p className="mt-1 text-xl font-semibold">
                {data.quiz.avg_score === null ? "N/A" : `${Number(data.quiz.avg_score).toFixed(1)}%`}
              </p>
            </div>
            <div className="card p-4">
              <p className="text-xs text-gray-500">Quiz attempts</p>
              <p className="mt-1 text-xl font-semibold">{data.quiz.count}</p>
            </div>
            <div className="card p-4">
              <p className="text-xs text-gray-500">Lessons completed</p>
              <p className="mt-1 text-xl font-semibold">{data.lessons_completed}</p>
            </div>
            <div className="card p-4">
              <p className="text-xs text-gray-500">Journal entries</p>
              <p className="mt-1 text-xl font-semibold">{data.journal_entries}</p>
            </div>
          </section>

          <section className="mt-7 grid gap-8 md:grid-cols-2">
            <div>
              <h2 className="font-semibold">Analyses by signal</h2>
              {data.analyses_by_signal.length ? (
                <ul className="mt-2 divide-y divide-[var(--border)] border-y border-[var(--border)]">
                  {data.analyses_by_signal.map((row) => (
                    <li key={row.signal_category ?? "unclassified"} className="flex justify-between gap-3 py-2 text-sm">
                      <span>{row.signal_category ?? "Unclassified"}</span><span>{row.count}</span>
                    </li>
                  ))}
                </ul>
              ) : <p className="mt-2 text-sm text-gray-500">No chart analyses in this report.</p>}
            </div>
            <div>
              <h2 className="font-semibold">Detected patterns</h2>
              {data.analyses_by_pattern.length ? (
                <ul className="mt-2 divide-y divide-[var(--border)] border-y border-[var(--border)]">
                  {data.analyses_by_pattern.map((row, index) => (
                    <li key={`${row["detections__label"] ?? "unclassified"}-${index}`} className="flex justify-between gap-3 py-2 text-sm">
                      <span>{row["detections__label"]?.replace(/_/g, " ") ?? "Unclassified"}</span><span>{row.count}</span>
                    </li>
                  ))}
                </ul>
              ) : <p className="mt-2 text-sm text-gray-500">No detected patterns in this report.</p>}
            </div>
          </section>
          <p className="mt-8 border-t border-[var(--border)] pt-3 text-xs text-gray-500">
            This report summarizes platform activity. It is not a broker statement or a guarantee of performance.
          </p>
        </>
      ) : null}
    </main>
  );
}
