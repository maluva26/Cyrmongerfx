"use client";

import { useEffect, useState, type FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import StandaloneHeader from "@/components/StandaloneHeader";
import { useAuth } from "@/lib/auth";
import { api, type AuthSession } from "@/lib/api";

export default function AdminLoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const { user, token, status, setAuth, clear } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (status === "authenticated" && user?.role === "ADMIN") router.replace("/dashboard");
  }, [router, status, user?.role]);

  const signOutCurrentUser = async () => {
    try {
      await api.post("/auth/logout", {}, token);
      clear();
      setError("");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Sign out failed. Please try again.");
    }
  };

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const session = await api.post<AuthSession>("/auth/login", { email: email.trim(), password, admin_only: true });
      setAuth(session.user, session.access);
      router.replace("/dashboard");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Admin sign in failed. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  if (status === "loading") {
    return <main className="mx-auto min-h-screen max-w-sm px-4 py-10"><StandaloneHeader /><p className="mt-5 text-sm text-gray-600">Checking your session...</p></main>;
  }

  if (status === "authenticated" && user?.role !== "ADMIN") {
    return (
      <main className="mx-auto min-h-screen max-w-sm px-4 py-10 sm:py-16">
        <StandaloneHeader />
        <h1 className="mt-5 text-2xl font-bold">Admin sign in</h1>
        <p className="mt-3 text-sm text-gray-600">You are signed in as a trader. Sign out to use a separate administrator account.</p>
        <button type="button" onClick={() => void signOutCurrentUser()} className="btn btn-primary mt-5 w-full">Sign out</button>
        {error && <p role="alert" className="mt-3 text-sm text-red-600">{error}</p>}
      </main>
    );
  }

  return (
    <main className="mx-auto min-h-screen max-w-sm px-4 py-10 sm:py-16">
      <StandaloneHeader />
      <h1 className="mt-5 text-2xl font-bold">Admin sign in</h1>
      <p className="mt-1 text-sm text-gray-600">Use your administrator account to manage learning content.</p>
      <form onSubmit={submit} className="mt-5 space-y-3">
        <label className="block space-y-1 text-sm">
          <span>Email</span>
          <input className="input" type="email" autoComplete="username" required value={email} onChange={(event) => setEmail(event.target.value)} />
        </label>
        <label className="block space-y-1 text-sm">
          <span>Password</span>
          <input className="input" type="password" autoComplete="current-password" required value={password} onChange={(event) => setPassword(event.target.value)} />
        </label>
        {error && <p role="alert" className="text-sm text-red-600">{error}</p>}
        <button type="submit" disabled={submitting} className="btn btn-primary w-full disabled:opacity-60">
          {submitting ? "Signing in..." : "Sign in as admin"}
        </button>
      </form>
      <div className="mt-5 border-t border-[var(--border)] pt-4 text-sm text-gray-600">
        <p>Need an administrator account?</p>
        <Link href="/admin/create-account" className="mt-1 inline-block text-brand-600 underline">Create one with an existing admin</Link>
      </div>
      <p className="mt-4 text-sm text-gray-600"><Link href="/login" className="text-brand-600 underline">Return to trader sign in</Link></p>
    </main>
  );
}
