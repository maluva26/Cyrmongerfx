"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth";
import { api } from "@/lib/api";

type Lesson = {
  lesson_id: string;
  title: string;
  category: string;
  order_index: number;
};

type Progress = {
  lessons_total: number;
  lessons_completed: number;
  per_lesson: { lesson_id: string; best_score: string | number; attempts: number }[];
};

export default function LearnPage() {
  const { token, status } = useAuth();
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [progress, setProgress] = useState<Progress | null>(null);
  const [category, setCategory] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    if (status !== "authenticated" || !token) return;
    let active = true;
    setLoading(true);
    setError("");

    Promise.all([
      api.get<Lesson[]>("/lessons", token),
      api.get<Progress>("/progress", token),
    ]).then(([lessonData, progressData]) => {
      if (!active) return;
      setLessons(Array.isArray(lessonData) ? lessonData : []);
      setProgress(progressData);
    }).catch((cause: unknown) => {
      if (active) setError(cause instanceof Error ? cause.message : "Lessons could not be loaded.");
    }).finally(() => {
      if (active) setLoading(false);
    });

    return () => {
      active = false;
    };
  }, [status, token, reloadKey]);

  const categories = useMemo(
    () => Array.from(new Set(lessons.map((lesson) => lesson.category).filter(Boolean))).sort((a, b) => a.localeCompare(b)),
    [lessons],
  );
  const visibleLessons = category ? lessons.filter((lesson) => lesson.category === category) : lessons;
  const progressByLesson = new Map((progress?.per_lesson ?? []).map((item) => [item.lesson_id, item]));

  if (status === "loading") return <p className="mx-auto max-w-5xl px-4 py-8">Checking your session...</p>;
  if (status === "anonymous") {
    return <p className="mx-auto max-w-5xl px-4 py-8">Please <Link href="/login" className="text-brand-600 underline">sign in</Link> to access lessons.</p>;
  }

  return (
    <main className="mx-auto max-w-5xl px-4 py-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Learning Centre</h1>
          <p className="mt-1 text-sm text-gray-600">
            {progress ? `${progress.lessons_completed} of ${progress.lessons_total} lessons passed` : "Browse lessons and check your progress."}
          </p>
        </div>
        <label className="block space-y-1 text-sm">
          <span>Category</span>
          <select className="input w-auto min-w-44" value={category} onChange={(event) => setCategory(event.target.value)}>
            <option value="">All categories</option>
            {categories.map((item) => <option key={item} value={item}>{item}</option>)}
          </select>
        </label>
      </div>

      {error && (
        <div className="mt-5 flex flex-wrap items-center justify-between gap-3 border-y border-red-200 py-3 text-sm text-red-700">
          <p role="alert">{error}</p>
          <button className="btn border border-red-300" onClick={() => setReloadKey((key) => key + 1)}>Retry</button>
        </div>
      )}

      {loading ? (
        <p className="py-10 text-sm text-gray-600" aria-live="polite">Loading lessons...</p>
      ) : !error && visibleLessons.length === 0 ? (
        <p className="py-10 text-sm text-gray-600">
          {lessons.length ? "There are no lessons in this category yet." : "No published lessons are available yet."}
        </p>
      ) : (
        <div className="mt-5 grid gap-3 md:grid-cols-2">
          {visibleLessons.map((lesson) => {
            const lessonProgress = progressByLesson.get(lesson.lesson_id);
            const score = lessonProgress ? Number(lessonProgress.best_score) : null;
            const passed = score !== null && score >= 70;
            return (
              <Link
                key={lesson.lesson_id}
                href={`/learn/${lesson.lesson_id}`}
                className="card block p-4 transition-colors hover:border-brand-400 focus-visible:outline focus-visible:outline-2 focus-visible:outline-brand-600"
              >
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h2 className="font-semibold">{lesson.title}</h2>
                    <p className="mt-1 text-xs capitalize text-gray-500">{lesson.category}</p>
                  </div>
                  <span className={`shrink-0 text-xs ${passed ? "text-green-700" : "text-gray-500"}`}>
                    {passed ? `Passed · ${score}%` : lessonProgress ? `Best · ${score}%` : "Not started"}
                  </span>
                </div>
                {lessonProgress && <p className="mt-3 text-xs text-gray-500">{lessonProgress.attempts} quiz {lessonProgress.attempts === 1 ? "attempt" : "attempts"}</p>}
              </Link>
            );
          })}
        </div>
      )}
    </main>
  );
}
