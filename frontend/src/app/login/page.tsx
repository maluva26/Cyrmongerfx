"use client";

import { useEffect, useState, type FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import StandaloneHeader from "@/components/StandaloneHeader";
import { useAuth } from "@/lib/auth";
import { api, type AuthSession } from "@/lib/api";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const { setAuth, status } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (status === "authenticated") router.replace("/dashboard");
  }, [router, status]);

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const session = await api.post<AuthSession>("/auth/login", {
        email: email.trim(),
        password,
        admin_only: false,
      });
      setAuth(session.user, session.access);
      router.replace("/dashboard");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Sign in failed. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="mx-auto min-h-screen max-w-sm px-4 py-10 sm:py-16">
      <StandaloneHeader />
      <h1 className="mt-5 text-2xl font-bold">Sign in</h1>
      <form onSubmit={submit} className="mt-4 space-y-3">
        <label className="block space-y-1 text-sm">
          <span>Email</span>
          <input
            className="input"
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
        </label>
        <label className="block space-y-1 text-sm">
          <span>Password</span>
          <input
            className="input"
            type="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </label>
        {error && <p role="alert" className="text-sm text-red-600">{error}</p>}
        <button type="submit" disabled={submitting || status === "loading"} className="btn btn-primary w-full disabled:opacity-60">
          {submitting ? "Signing in..." : status === "loading" ? "Checking session..." : "Sign in"}
        </button>
      </form>
      <p className="mt-4 text-sm text-gray-600">
        No account? <Link href="/register" className="text-brand-600">Create a trader account</Link>
      </p>
      <div className="mt-6 border-t border-[var(--border)] pt-4">
        <p className="text-sm font-medium">Administrator access</p>
        <div className="mt-2 flex flex-wrap gap-x-4 gap-y-2 text-sm">
          <Link href="/admin/login" className="text-brand-600 underline">Admin sign in</Link>
          <Link href="/admin/create-account" className="text-brand-600 underline">Create an admin account</Link>
        </div>
        <p className="mt-2 text-xs text-gray-500">Admin accounts can only be created by an existing administrator.</p>
      </div>
    </main>
  );
}
