"use client";

import { useState, type FormEvent } from "react";
import Link from "next/link";
import StandaloneHeader from "@/components/StandaloneHeader";
import { useAuth } from "@/lib/auth";
import { api } from "@/lib/api";

export default function AdminCreateAccountPage() {
  const { user, token, status, clear } = useAuth();
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [createdEmail, setCreatedEmail] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const signOut = async () => {
    try {
      await api.post("/auth/logout", {}, token);
    } finally {
      clear();
    }
  };

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!token) return;
    setError("");
    setSubmitting(true);
    try {
      const created = await api.post<{ email: string }>("/auth/admin-accounts", {
        email: email.trim(),
        full_name: fullName.trim(),
        password,
      }, token);
      setCreatedEmail(created.email);
      setEmail("");
      setFullName("");
      setPassword("");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "The administrator account could not be created.");
    } finally {
      setSubmitting(false);
    }
  };

  if (status === "loading") {
    return <main className="mx-auto min-h-screen max-w-sm px-4 py-10"><StandaloneHeader /><p className="mt-5 text-sm text-gray-600">Checking your session...</p></main>;
  }

  if (status !== "authenticated" || user?.role !== "ADMIN") {
    return (
      <main className="mx-auto min-h-screen max-w-sm px-4 py-10 sm:py-16">
        <StandaloneHeader />
        <h1 className="mt-5 text-2xl font-bold">Create admin account</h1>
        <p className="mt-3 text-sm text-gray-600">An existing administrator must be signed in to create another admin account.</p>
        <div className="mt-5 flex flex-wrap gap-4 text-sm">
          <Link href="/admin/login" className="text-brand-600 underline">Admin sign in</Link>
          <Link href="/login" className="text-brand-600 underline">Trader sign in</Link>
        </div>
        {status === "authenticated" && user?.role !== "ADMIN" && (
          <button type="button" onClick={() => void signOut()} className="btn btn-primary mt-5 w-full">Sign out first</button>
        )}
      </main>
    );
  }

  return (
    <main className="mx-auto min-h-screen max-w-sm px-4 py-10 sm:py-16">
      <StandaloneHeader />
      <h1 className="mt-5 text-2xl font-bold">Create admin account</h1>
      <p className="mt-1 text-sm text-gray-600">Signed in as {user.email}. New admins can manage learning content.</p>
      {createdEmail ? (
        <div className="mt-5 border-y border-green-200 py-4">
          <p className="text-sm font-medium text-green-800">Administrator account created for {createdEmail}.</p>
          <button type="button" onClick={() => setCreatedEmail("")} className="mt-3 text-sm text-brand-600 underline">Create another admin account</button>
          <Link href="/admin" className="mt-3 block text-sm text-brand-600 underline">Open content management</Link>
        </div>
      ) : (
        <form onSubmit={submit} className="mt-5 space-y-3">
          <label className="block space-y-1 text-sm">
            <span>Email</span>
            <input className="input" type="email" autoComplete="email" required value={email} onChange={(event) => setEmail(event.target.value)} />
          </label>
          <label className="block space-y-1 text-sm">
            <span>Full name</span>
            <input className="input" autoComplete="name" maxLength={120} value={fullName} onChange={(event) => setFullName(event.target.value)} />
          </label>
          <label className="block space-y-1 text-sm">
            <span>Temporary password</span>
            <input className="input" type="password" autoComplete="new-password" minLength={10} required value={password} onChange={(event) => setPassword(event.target.value)} />
            <span className="block text-xs text-gray-500">At least 10 characters and must meet the password rules.</span>
          </label>
          {error && <p role="alert" className="text-sm text-red-600">{error}</p>}
          <button type="submit" disabled={submitting} className="btn btn-primary w-full disabled:opacity-60">
            {submitting ? "Creating account..." : "Create admin account"}
          </button>
        </form>
      )}
      <p className="mt-5 text-sm text-gray-600"><Link href="/admin/login" className="text-brand-600 underline">Admin sign in</Link></p>
    </main>
  );
}
