"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";
import Image from "next/image";
import Link from "next/link";
import { useAuth } from "@/lib/auth";
import { api } from "@/lib/api";

type Option = { option_id: string; text: string; is_correct: boolean };
type Question = {
  question_id: string;
  prompt: string;
  explanation: string;
  order_index: number;
  options: Option[];
  image_url?: string | null;
  image_alt?: string | null;
};
type MaterialKind = "VIDEO" | "LINK" | "FILE";
type LearningMaterial = {
  resource_id: string;
  title: string;
  kind: MaterialKind;
  url: string;
  original_filename: string;
  content_type: string;
  size_bytes: number;
  order_index: number;
  download_url: string | null;
  youtube_embed_url: string | null;
};
type Lesson = {
  lesson_id: string;
  title: string;
  template_key: string | null;
  category: string;
  body: string;
  order_index: number;
  status: "DRAFT" | "PUBLISHED" | "ARCHIVED";
  resources: LearningMaterial[];
  questions: Question[];
};
type ModuleTemplate = {
  key: string;
  title: string;
  category: string;
  summary: string;
  lesson_id: string | null;
  status: Lesson["status"] | null;
  question_count: number;
};
type OptionDraft = { text: string; is_correct: boolean };

const emptyOptions: OptionDraft[] = [
  { text: "", is_correct: true },
  { text: "", is_correct: false },
];

export default function AdminPage() {
  const { user, token, status } = useAuth();
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [moduleTemplates, setModuleTemplates] = useState<ModuleTemplate[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [title, setTitle] = useState("");
  const [category, setCategory] = useState("");
  const [body, setBody] = useState("");
  const [orderIndex, setOrderIndex] = useState("0");
  const [prompt, setPrompt] = useState("");
  const [explanation, setExplanation] = useState("");
  const [options, setOptions] = useState<OptionDraft[]>(emptyOptions);
  const [materialKind, setMaterialKind] = useState<MaterialKind>("VIDEO");
  const [materialTitle, setMaterialTitle] = useState("");
  const [materialUrl, setMaterialUrl] = useState("");
  const [materialFile, setMaterialFile] = useState<File | null>(null);
  const [materialFileInputKey, setMaterialFileInputKey] = useState(0);
  const [loading, setLoading] = useState(false);
  const [savingLesson, setSavingLesson] = useState(false);
  const [savingQuestion, setSavingQuestion] = useState(false);
  const [savingMaterial, setSavingMaterial] = useState(false);
  const [removingMaterialId, setRemovingMaterialId] = useState<string | null>(null);
  const [creatingTemplateKey, setCreatingTemplateKey] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const selectedLesson = lessons.find((lesson) => lesson.lesson_id === selectedId) ?? null;

  const resetMaterialForm = () => {
    setMaterialKind("VIDEO");
    setMaterialTitle("");
    setMaterialUrl("");
    setMaterialFile(null);
    setMaterialFileInputKey((current) => current + 1);
  };

  const loadLessons = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const [data, templateData] = await Promise.all([
        api.get<Lesson[]>("/admin/lessons", token),
        api.get<{ modules: ModuleTemplate[] }>("/admin/lesson-templates", token),
      ]);
      setLessons(Array.isArray(data) ? data : []);
      setModuleTemplates(Array.isArray(templateData.modules) ? templateData.modules : []);
      setError("");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Lessons could not be loaded.");
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    if (status === "authenticated" && user?.role === "ADMIN") void loadLessons();
  }, [loadLessons, status, user?.role]);

  const startNewLesson = () => {
    setSelectedId(null);
    setTitle("");
    setCategory("");
    setBody("");
    setOrderIndex("0");
    setPrompt("");
    setExplanation("");
    setOptions(emptyOptions);
    resetMaterialForm();
    setError("");
    setMessage("");
  };

  const selectLesson = (lesson: Lesson) => {
    setSelectedId(lesson.lesson_id);
    setTitle(lesson.title);
    setCategory(lesson.category);
    setBody(lesson.body);
    setOrderIndex(String(lesson.order_index));
    setPrompt("");
    setExplanation("");
    setOptions(emptyOptions);
    resetMaterialForm();
    setError("");
    setMessage("");
  };

  const saveLesson = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!token) return;
    setSavingLesson(true);
    setError("");
    setMessage("");
    const payload = {
      title: title.trim(),
      category: category.trim(),
      body: body.trim(),
      order_index: Number(orderIndex),
    };
    try {
      const saved = selectedId
        ? await api.patch<Lesson>(`/admin/lessons/${selectedId}`, payload, token)
        : await api.post<Lesson>("/admin/lessons", payload, token);
      setSelectedId(saved.lesson_id);
      setMessage(selectedId ? "Lesson changes saved." : "Draft created. Add a quiz before publishing.");
      await loadLessons();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Lesson could not be saved.");
    } finally {
      setSavingLesson(false);
    }
  };

  const saveQuestion = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!token || !selectedLesson) return;
    setSavingQuestion(true);
    setError("");
    setMessage("");
    try {
      await api.post(`/admin/lessons/${selectedLesson.lesson_id}/questions`, {
        prompt: prompt.trim(),
        explanation: explanation.trim(),
        order_index: selectedLesson.questions.length,
        options: options.map((option) => ({ ...option, text: option.text.trim() })),
      }, token);
      setPrompt("");
      setExplanation("");
      setOptions(emptyOptions);
      setMessage("Question added.");
      await loadLessons();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Question could not be added.");
    } finally {
      setSavingQuestion(false);
    }
  };

  const saveMaterial = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!token || !selectedLesson) return;
    if (materialKind === "FILE" && !materialFile) {
      setError("Choose a file to upload.");
      return;
    }

    setSavingMaterial(true);
    setError("");
    setMessage("");
    try {
      const path = `/admin/lessons/${selectedLesson.lesson_id}/materials`;
      if (materialKind === "FILE") {
        const formData = new FormData();
        formData.append("title", materialTitle.trim());
        formData.append("kind", materialKind);
        formData.append("order_index", String(selectedLesson.resources.length));
        formData.append("file", materialFile as File);
        await api.upload(path, formData, token);
      } else {
        await api.post(path, {
          title: materialTitle.trim(),
          kind: materialKind,
          url: materialUrl.trim(),
          order_index: selectedLesson.resources.length,
        }, token);
      }
      resetMaterialForm();
      setMessage(materialKind === "VIDEO" ? "YouTube video added." : materialKind === "LINK" ? "Learning link added." : "Learning file uploaded.");
      await loadLessons();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "The learning material could not be added.");
    } finally {
      setSavingMaterial(false);
    }
  };

  const removeMaterial = async (material: LearningMaterial) => {
    if (!token || !selectedLesson) return;
    setRemovingMaterialId(material.resource_id);
    setError("");
    setMessage("");
    try {
      await api.delete(
        `/admin/lessons/${selectedLesson.lesson_id}/materials?resource_id=${encodeURIComponent(material.resource_id)}`,
        token,
      );
      setMessage("Learning material removed.");
      await loadLessons();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "The learning material could not be removed.");
    } finally {
      setRemovingMaterialId(null);
    }
  };

  const createStarterModule = async (module: ModuleTemplate) => {
    if (!token || creatingTemplateKey) return;
    setCreatingTemplateKey(module.key);
    setError("");
    setMessage("");
    try {
      const response = await api.post<{ lesson: Lesson }>("/admin/lesson-templates", { key: module.key }, token);
      await loadLessons();
      selectLesson(response.lesson);
      setMessage(module.lesson_id ? "Module opened." : "Module draft is ready with 10 questions.");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "The module could not be created.");
    } finally {
      setCreatingTemplateKey(null);
    }
  };

  const changeStatus = async (action: "publish" | "archive") => {
    if (!token || !selectedLesson) return;
    setError("");
    setMessage("");
    try {
      await api.post(`/admin/lessons/${selectedLesson.lesson_id}/${action}`, {}, token);
      setMessage(action === "publish" ? "Lesson published." : "Lesson archived.");
      await loadLessons();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : `Lesson could not be ${action}ed.`);
    }
  };

  const updateOption = (index: number, text: string) => {
    setOptions((current) => current.map((option, i) => i === index ? { ...option, text } : option));
  };

  const markCorrect = (index: number) => {
    setOptions((current) => current.map((option, i) => ({ ...option, is_correct: i === index })));
  };

  if (status === "loading") return <p className="p-4">Checking your session...</p>;
  if (status === "anonymous") {
    return <p className="p-4">Please <Link href="/login" className="text-brand-600 underline">sign in</Link>.</p>;
  }
  if (user?.role !== "ADMIN") return <p className="p-4">Admin access required.</p>;

  return (
    <main className="mx-auto max-w-6xl px-4 py-6">
      <header className="flex flex-wrap items-end justify-between gap-3 border-b border-[var(--border)] pb-4">
        <div>
          <h1 className="text-2xl font-bold">Learning content</h1>
          <p className="mt-1 text-sm text-gray-600">Forex education curriculum</p>
        </div>
        <button type="button" onClick={startNewLesson} className="btn btn-primary">New lesson</button>
      </header>

      <section className="mt-5" aria-labelledby="starter-modules-heading">
        <div className="flex flex-wrap items-baseline justify-between gap-2 border-b border-[var(--border)] pb-2">
          <h2 id="starter-modules-heading" className="text-lg font-semibold">Starter modules</h2>
          <span className="text-xs text-gray-500">10-question quiz per module</span>
        </div>
        {loading && moduleTemplates.length === 0 ? (
          <p className="py-3 text-sm text-gray-500">Loading modules...</p>
        ) : (
          <ul className="divide-y divide-[var(--border)]">
            {moduleTemplates.map((module) => (
              <li key={module.key} className="flex flex-wrap items-center justify-between gap-3 py-3">
                <div className="min-w-0 flex-1">
                  <p className="font-medium">{module.title}</p>
                  <p className="mt-0.5 text-sm text-gray-600">{module.summary}</p>
                  {module.lesson_id && (
                    <p className="mt-1 text-xs text-gray-500">
                      {module.status} · {module.question_count} questions
                    </p>
                  )}
                </div>
                <button
                  type="button"
                  onClick={() => void createStarterModule(module)}
                  disabled={Boolean(creatingTemplateKey) || loading}
                  className="btn border border-[var(--border)] disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {creatingTemplateKey === module.key ? "Adding..." : module.lesson_id ? "Open module" : "Add module"}
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>

      {(error || message) && (
        <p role={error ? "alert" : "status"} className={`mt-3 text-sm ${error ? "text-red-600" : "text-green-700"}`}>
          {error || message}
        </p>
      )}

      <div className="mt-5 grid gap-6 md:grid-cols-[15rem_minmax(0,1fr)]">
        <aside aria-label="Lessons">
          <h2 className="mb-2 text-sm font-semibold">All lessons</h2>
          {loading ? <p className="text-sm text-gray-500">Loading...</p> : lessons.length === 0 ? (
            <p className="text-sm text-gray-500">No lessons created yet.</p>
          ) : (
            <ul className="divide-y divide-[var(--border)] border-y border-[var(--border)]">
              {lessons.map((lesson) => (
                <li key={lesson.lesson_id}>
                  <button
                    type="button"
                    onClick={() => selectLesson(lesson)}
                    aria-current={selectedId === lesson.lesson_id ? "true" : undefined}
                    className={`w-full py-3 text-left ${selectedId === lesson.lesson_id ? "text-brand-700" : "text-[var(--foreground)]"}`}
                  >
                    <span className="block font-medium">{lesson.title}</span>
                    <span className="mt-1 block text-xs text-gray-500">{lesson.status} · {lesson.questions.length} questions</span>
                  </button>
                </li>
              ))}
            </ul>
          )}
          {error && <button type="button" onClick={() => void loadLessons()} className="mt-3 text-sm text-brand-600 underline">Retry loading</button>}
        </aside>

        <div className="min-w-0 space-y-7">
          <section aria-labelledby="lesson-details-heading">
            <h2 id="lesson-details-heading" className="text-lg font-semibold">
              {selectedId ? "Lesson details" : "New lesson draft"}
            </h2>
            <form onSubmit={saveLesson} className="mt-3 grid gap-3 sm:grid-cols-2">
              <label className="block space-y-1 text-sm">
                <span>Title</span>
                <input className="input" required maxLength={200} value={title} onChange={(event) => setTitle(event.target.value)} />
              </label>
              <label className="block space-y-1 text-sm">
                <span>Category</span>
                <input className="input" required maxLength={80} value={category} onChange={(event) => setCategory(event.target.value)} />
              </label>
              <label className="block space-y-1 text-sm sm:col-span-2">
                <span>Lesson content</span>
                <textarea className="input" required rows={8} value={body} onChange={(event) => setBody(event.target.value)} />
              </label>
              <label className="block space-y-1 text-sm">
                <span>Display order</span>
                <input className="input" type="number" min={0} step={1} required value={orderIndex} onChange={(event) => setOrderIndex(event.target.value)} />
              </label>
              <div className="flex items-end">
                <button type="submit" disabled={savingLesson} className="btn btn-primary disabled:opacity-50">
                  {savingLesson ? "Saving..." : "Save draft"}
                </button>
              </div>
            </form>
          </section>

          {selectedLesson && (
            <>
              <section className="border-t border-[var(--border)] pt-5" aria-labelledby="quiz-questions-heading">
                <div className="flex flex-wrap items-baseline justify-between gap-2">
                  <h2 id="quiz-questions-heading" className="text-lg font-semibold">Quiz questions</h2>
                  <span className="text-xs text-gray-500">Exactly one correct option per question</span>
                </div>
                {selectedLesson.questions.length > 0 && (
                  <ol className="mt-3 space-y-2">
                    {selectedLesson.questions.map((question, index) => (
                      <li key={question.question_id} className="card p-3 text-sm">
                        <div className={`grid gap-3 ${question.image_url ? "grid-cols-[5rem_minmax(0,1fr)] sm:grid-cols-[8rem_minmax(0,1fr)]" : "grid-cols-1"}`}>
                          {question.image_url && (
                            <Image
                              src={question.image_url}
                              alt={question.image_alt ?? "Illustrative photo for this question"}
                              width={288}
                              height={192}
                              sizes="(max-width: 640px) 5rem, 8rem"
                              className="h-20 w-full rounded-sm object-cover sm:h-24"
                            />
                          )}
                          <div className="min-w-0">
                            <p className="font-medium">{index + 1}. {question.prompt}</p>
                            <ul className="mt-2 space-y-1 text-gray-600">
                              {question.options.map((option) => (
                                <li key={option.option_id}>{option.is_correct ? "Correct: " : ""}{option.text}</li>
                              ))}
                            </ul>
                          </div>
                        </div>
                      </li>
                    ))}
                  </ol>
                )}

                {selectedLesson.status === "PUBLISHED" ? (
                  <p className="mt-3 text-sm text-gray-600">Archive this lesson before changing its quiz.</p>
                ) : (
                  <form onSubmit={saveQuestion} className="mt-4 space-y-3 border-t border-[var(--border)] pt-4">
                    <label className="block space-y-1 text-sm">
                      <span>Question</span>
                      <textarea className="input" rows={2} required maxLength={2000} value={prompt} onChange={(event) => setPrompt(event.target.value)} />
                    </label>
                    <div className="space-y-2">
                      <p className="text-sm font-medium">Answer options</p>
                      {options.map((option, index) => (
                        <div key={index} className="flex flex-wrap items-center gap-2">
                          <input
                            type="radio"
                            name="correct-option"
                            aria-label={`Mark option ${index + 1} as correct`}
                            checked={option.is_correct}
                            onChange={() => markCorrect(index)}
                          />
                          <input
                            className="input min-w-0 flex-1"
                            aria-label={`Option ${index + 1}`}
                            required
                            maxLength={1000}
                            value={option.text}
                            onChange={(event) => updateOption(index, event.target.value)}
                          />
                          {options.length > 2 && (
                            <button type="button" onClick={() => setOptions((current) => current.filter((_, i) => i !== index))} className="text-xs text-red-700">
                              Remove
                            </button>
                          )}
                        </div>
                      ))}
                      <button type="button" onClick={() => setOptions((current) => [...current, { text: "", is_correct: false }])} className="text-sm text-brand-600 underline">
                        Add option
                      </button>
                    </div>
                    <label className="block space-y-1 text-sm">
                      <span>Explanation shown after submission</span>
                      <textarea className="input" rows={2} required maxLength={4000} value={explanation} onChange={(event) => setExplanation(event.target.value)} />
                    </label>
                    <button type="submit" disabled={savingQuestion} className="btn btn-primary disabled:opacity-50">
                      {savingQuestion ? "Adding..." : "Add question"}
                    </button>
                  </form>
                )}
              </section>

              <section className="border-t border-[var(--border)] pt-5" aria-labelledby="learning-materials-heading">
                <div className="flex flex-wrap items-baseline justify-between gap-2">
                  <h2 id="learning-materials-heading" className="text-lg font-semibold">Learning materials</h2>
                  <span className="text-xs text-gray-500">YouTube videos, HTTPS links, and course files</span>
                </div>

                {selectedLesson.resources.length > 0 && (
                  <ul className="mt-3 divide-y divide-[var(--border)] border-y border-[var(--border)]">
                    {selectedLesson.resources.map((material) => (
                      <li key={material.resource_id} className="flex flex-wrap items-center justify-between gap-3 py-3 text-sm">
                        <div className="min-w-0 flex-1">
                          <p className="font-medium">{material.title}</p>
                          <p className="mt-0.5 text-xs text-gray-500">
                            {material.kind === "VIDEO" ? "YouTube video" : material.kind === "LINK" ? "Learning link" : material.original_filename || "Learning file"}
                          </p>
                        </div>
                        {selectedLesson.status !== "PUBLISHED" && (
                          <button
                            type="button"
                            onClick={() => void removeMaterial(material)}
                            disabled={removingMaterialId === material.resource_id}
                            className="text-xs text-red-700 disabled:opacity-50"
                          >
                            {removingMaterialId === material.resource_id ? "Removing..." : "Remove"}
                          </button>
                        )}
                      </li>
                    ))}
                  </ul>
                )}

                {selectedLesson.status === "PUBLISHED" ? (
                  <p className="mt-3 text-sm text-gray-600">Archive this lesson before changing its materials.</p>
                ) : (
                  <form onSubmit={saveMaterial} className="mt-4 grid gap-3 sm:grid-cols-2">
                    <label className="block space-y-1 text-sm">
                      <span>Material type</span>
                      <select className="input" value={materialKind} onChange={(event) => setMaterialKind(event.target.value as MaterialKind)}>
                        <option value="VIDEO">YouTube video</option>
                        <option value="LINK">HTTPS learning link</option>
                        <option value="FILE">Upload PDF or document</option>
                      </select>
                    </label>
                    <label className="block space-y-1 text-sm">
                      <span>Title</span>
                      <input className="input" required maxLength={200} value={materialTitle} onChange={(event) => setMaterialTitle(event.target.value)} />
                    </label>
                    {materialKind === "FILE" ? (
                      <label className="block space-y-1 text-sm sm:col-span-2">
                        <span>File</span>
                        <input
                          key={materialFileInputKey}
                          className="block w-full text-sm"
                          type="file"
                          required
                          accept=".pdf,.txt,.csv,.doc,.docx,.ppt,.pptx,.xls,.xlsx"
                          onChange={(event) => setMaterialFile(event.target.files?.[0] ?? null)}
                        />
                        <span className="block text-xs text-gray-500">PDF, text, spreadsheet, presentation, or Word document up to 10 MB.</span>
                      </label>
                    ) : (
                      <label className="block space-y-1 text-sm sm:col-span-2">
                        <span>{materialKind === "VIDEO" ? "YouTube video link" : "HTTPS learning link"}</span>
                        <input
                          className="input"
                          type="url"
                          required
                          maxLength={500}
                          placeholder={materialKind === "VIDEO" ? "https://www.youtube.com/watch?v=..." : "https://example.com/material"}
                          value={materialUrl}
                          onChange={(event) => setMaterialUrl(event.target.value)}
                        />
                      </label>
                    )}
                    <div className="sm:col-span-2">
                      <button type="submit" disabled={savingMaterial} className="btn btn-primary disabled:opacity-50">
                        {savingMaterial ? "Adding..." : materialKind === "FILE" ? "Upload material" : "Add material"}
                      </button>
                    </div>
                  </form>
                )}
              </section>

              <section className="flex flex-wrap gap-2 border-t border-[var(--border)] pt-5" aria-label="Publishing">
                {selectedLesson.status === "PUBLISHED" ? (
                  <button type="button" onClick={() => void changeStatus("archive")} className="btn border border-[var(--border)]">Archive lesson</button>
                ) : (
                  <button
                    type="button"
                    onClick={() => void changeStatus("publish")}
                    disabled={selectedLesson.questions.length === 0}
                    className="btn btn-primary disabled:opacity-50"
                  >
                    Publish lesson
                  </button>
                )}
              </section>
            </>
          )}
        </div>
      </div>
    </main>
  );
}
