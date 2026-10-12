"use client";

import { useEffect, useRef, useState } from "react";
import DOMPurify from "dompurify";
import Image from "next/image";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { api } from "@/lib/api";

type QuizOption = { option_id: string; text: string };
type Question = {
  question_id: string;
  prompt: string;
  options: QuizOption[];
  image_url?: string | null;
  image_alt?: string | null;
};
type LearningMaterial = {
  resource_id: string;
  title: string;
  kind: "VIDEO" | "LINK" | "FILE";
  url: string;
  original_filename: string;
  content_type: string;
  size_bytes: number;
  download_url: string | null;
  youtube_embed_url: string | null;
};
type Lesson = { lesson_id: string; title: string; category: string; body: string; resources: LearningMaterial[]; questions: Question[] };
type QuestionResult = {
  question_id: string;
  correct: boolean;
  correct_option_id: string;
  explanation: string;
};
type QuizResult = { score: number | string; per_question: QuestionResult[] };

function shuffle<T>(items: T[]): T[] {
  const shuffled = [...items];
  for (let index = shuffled.length - 1; index > 0; index -= 1) {
    const swapIndex = Math.floor(Math.random() * (index + 1));
    [shuffled[index], shuffled[swapIndex]] = [shuffled[swapIndex], shuffled[index]];
  }
  return shuffled;
}

function randomizeQuiz(lesson: Lesson): Lesson {
  return {
    ...lesson,
    questions: shuffle(lesson.questions).map((question) => ({
      ...question,
      options: shuffle(question.options),
    })),
  };
}

function formatFileSize(sizeBytes: number): string {
  if (sizeBytes < 1024 * 1024) return `${Math.max(1, Math.round(sizeBytes / 1024))} KB`;
  return `${(sizeBytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function LessonPage() {
  const params = useParams<{ lessonId: string | string[] }>();
  const lessonId = Array.isArray(params.lessonId) ? params.lessonId[0] : params.lessonId;
  const { token, status } = useAuth();
  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [result, setResult] = useState<QuizResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [materialError, setMaterialError] = useState("");
  const [openingMaterialId, setOpeningMaterialId] = useState<string | null>(null);
  const startedAt = useRef(Date.now());
  const answeredCount = lesson?.questions.filter((question) => Boolean(answers[question.question_id])).length ?? 0;

  useEffect(() => {
    if (status !== "authenticated" || !token || !lessonId) return;
    let active = true;
    setLoading(true);
    setError("");
    setLesson(null);
    setAnswers({});
    setResult(null);
    setMaterialError("");

    api.get<Lesson>(`/lessons/${encodeURIComponent(lessonId)}`, token).then((data) => {
      if (active) {
        setLesson(randomizeQuiz(data));
        startedAt.current = Date.now();
      }
    }).catch((cause: unknown) => {
      if (active) setError(cause instanceof Error ? cause.message : "This lesson could not be loaded.");
    }).finally(() => {
      if (active) setLoading(false);
    });

    return () => {
      active = false;
    };
  }, [status, token, lessonId]);

  const submit = async () => {
    if (!token || !lessonId || !lesson) return;
    if (lesson.questions.length === 0) {
      setError("This lesson does not have a quiz yet.");
      return;
    }
    if (lesson.questions.some((question) => !answers[question.question_id])) {
      setError("Answer every question before submitting.");
      return;
    }

    setSubmitting(true);
    setError("");
    try {
      const response = await api.post<QuizResult>(
        `/lessons/${encodeURIComponent(lessonId)}/quiz`,
        { answers, duration_seconds: Math.floor((Date.now() - startedAt.current) / 1000) },
        token,
      );
      setResult(response);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Your answers could not be submitted.");
    } finally {
      setSubmitting(false);
    }
  };

  const downloadMaterial = async (material: LearningMaterial) => {
    if (!token || !material.download_url) return;
    setOpeningMaterialId(material.resource_id);
    setMaterialError("");
    try {
      const blob = await api.download(material.download_url, token);
      const objectUrl = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = objectUrl;
      link.download = material.original_filename || material.title;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.setTimeout(() => URL.revokeObjectURL(objectUrl), 60_000);
    } catch (cause) {
      setMaterialError(cause instanceof Error ? cause.message : "This learning file could not be downloaded.");
    } finally {
      setOpeningMaterialId(null);
    }
  };

  if (status === "loading") return <p className="mx-auto max-w-3xl px-4 py-8">Checking your session...</p>;
  if (status === "anonymous") {
    return <p className="mx-auto max-w-3xl px-4 py-8">Please <Link href="/login" className="text-brand-600 underline">sign in</Link> to access lessons.</p>;
  }

  return (
    <main className="mx-auto max-w-3xl px-4 py-6">
      <Link href="/learn" className="text-sm text-brand-600">Back to lessons</Link>
      {loading ? (
        <p className="py-10 text-sm text-gray-600" aria-live="polite">Loading lesson...</p>
      ) : error && !lesson ? (
        <div className="mt-5 border-y border-red-200 py-4 text-sm text-red-700">
          <p role="alert">{error}</p>
          <Link href="/learn" className="mt-3 inline-block underline">Return to lessons</Link>
        </div>
      ) : lesson ? (
        <>
          <header className="mt-4 border-b border-[var(--border)] pb-4">
            <p className="text-xs capitalize text-gray-500">{lesson.category}</p>
            <h1 className="mt-1 text-2xl font-bold">{lesson.title}</h1>
          </header>

          <article
            className="prose mt-5 max-w-none dark:prose-invert"
            dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(lesson.body, { USE_PROFILES: { html: true } }) }}
          />

          {lesson.resources.length > 0 && (
            <section className="mt-8 border-t border-[var(--border)] pt-5" aria-labelledby="materials-heading">
              <h2 id="materials-heading" className="text-lg font-semibold">Learning materials</h2>
              {materialError && <p role="alert" className="mt-3 text-sm text-red-600">{materialError}</p>}
              <div className="mt-4 space-y-5">
                {lesson.resources.map((material) => (
                  <div key={material.resource_id} className="border-b border-[var(--border)] pb-5 last:border-b-0">
                    <p className="font-medium">{material.title}</p>
                    {material.kind === "VIDEO" && material.youtube_embed_url ? (
                      <iframe
                        className="mt-3 aspect-video w-full max-w-2xl border-0"
                        src={material.youtube_embed_url}
                        title={material.title}
                        referrerPolicy="strict-origin-when-cross-origin"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                        allowFullScreen
                      />
                    ) : material.kind === "LINK" ? (
                      <a
                        className="mt-2 inline-block text-sm text-brand-600 underline"
                        href={material.url}
                        target="_blank"
                        rel="noreferrer"
                      >
                        Open learning link
                      </a>
                    ) : material.kind === "FILE" ? (
                      <div className="mt-2 flex flex-wrap items-center gap-3">
                        <span className="text-sm text-gray-600">
                          {material.original_filename || "Learning file"} {material.size_bytes > 0 ? `(${formatFileSize(material.size_bytes)})` : ""}
                        </span>
                        <button
                          type="button"
                          onClick={() => void downloadMaterial(material)}
                          disabled={openingMaterialId === material.resource_id || !material.download_url}
                          className="btn border border-[var(--border)] disabled:cursor-not-allowed disabled:opacity-50"
                        >
                          {openingMaterialId === material.resource_id ? "Downloading..." : "Download file"}
                        </button>
                      </div>
                    ) : null}
                  </div>
                ))}
              </div>
            </section>
          )}

          <section className="mt-8 border-t border-[var(--border)] pt-5" aria-labelledby="quiz-heading">
            <div className="flex flex-wrap items-baseline justify-between gap-2">
              <h2 id="quiz-heading" className="text-lg font-semibold">Knowledge check</h2>
              {lesson.questions.length > 0 && <p className="text-xs text-gray-500">{lesson.questions.length} questions · pass mark 70%</p>}
            </div>

            {error && lesson && <p role="alert" className="mt-3 text-sm text-red-600">{error}</p>}

            {lesson.questions.length === 0 ? (
              <p className="mt-4 text-sm text-gray-600">A quiz is not available for this lesson yet.</p>
            ) : result ? (
              <div className="mt-4 space-y-3">
                <div className="flex flex-wrap items-baseline justify-between gap-2">
                  <p className="font-semibold">Score: {Number(result.score).toFixed(0)}%</p>
                  <p className={`text-sm ${Number(result.score) >= 70 ? "text-green-700" : "text-red-700"}`}>
                    {Number(result.score) >= 70 ? "Lesson passed" : "Try again to pass"}
                  </p>
                </div>
                {result.per_question.map((item) => {
                  const question = lesson.questions.find((entry) => entry.question_id === item.question_id);
                  const correctOption = question?.options.find((option) => option.option_id === item.correct_option_id);
                  return (
                    <div key={item.question_id} className="border-t border-[var(--border)] py-3">
                      <p className={`text-sm font-medium ${item.correct ? "text-green-700" : "text-red-700"}`}>
                        {item.correct ? "Correct" : "Incorrect"}: {question?.prompt}
                      </p>
                      {!item.correct && correctOption && <p className="mt-1 text-sm">Correct answer: {correctOption.text}</p>}
                      {item.explanation && <p className="mt-1 text-sm text-gray-600">{item.explanation}</p>}
                    </div>
                  );
                })}
                <button
                  type="button"
                  className="btn border border-[var(--border)]"
                  onClick={() => {
                    setAnswers({});
                    setResult(null);
                    setError("");
                    setLesson((current) => current ? randomizeQuiz(current) : current);
                    startedAt.current = Date.now();
                  }}
                >
                  Retake quiz
                </button>
              </div>
            ) : (
              <div className="mt-4 space-y-3">
                {lesson.questions.map((question, index) => (
                  <fieldset key={question.question_id} className="card p-4">
                    <legend className="font-medium">{index + 1}. {question.prompt}</legend>
                    <div className={`mt-3 grid gap-3 ${question.image_url ? "grid-cols-[5rem_minmax(0,1fr)] sm:grid-cols-[9rem_minmax(0,1fr)] sm:gap-4" : "grid-cols-1"}`}>
                      {question.image_url && (
                        <Image
                          src={question.image_url}
                          alt={question.image_alt ?? "Illustrative photo for this question"}
                          width={320}
                          height={220}
                          sizes="(max-width: 640px) 5rem, 9rem"
                          className="h-20 w-full rounded-sm object-cover sm:h-28"
                        />
                      )}
                      <div className="min-w-0 space-y-2">
                        {question.options.map((option) => (
                          <label key={option.option_id} className="flex cursor-pointer items-start gap-2 text-sm">
                            <input
                              className="mt-0.5"
                              type="radio"
                              name={question.question_id}
                              value={option.option_id}
                              checked={answers[question.question_id] === option.option_id}
                              onChange={() => setAnswers((current) => ({ ...current, [question.question_id]: option.option_id }))}
                            />
                            <span>{option.text}</span>
                          </label>
                        ))}
                      </div>
                    </div>
                  </fieldset>
                ))}
                <div className="flex flex-wrap items-center gap-3">
                  <button
                    type="button"
                    onClick={submit}
                    disabled={submitting || answeredCount < lesson.questions.length}
                    className="btn btn-primary disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {submitting ? "Submitting..." : "Submit answers"}
                  </button>
                  <span className="text-xs text-gray-500" aria-live="polite">
                    {answeredCount} of {lesson.questions.length} answered
                  </span>
                </div>
              </div>
            )}
          </section>
        </>
      ) : null}
    </main>
  );
}
