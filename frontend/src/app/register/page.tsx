"use client";

import { useEffect, useState, type FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import StandaloneHeader from "@/components/StandaloneHeader";
import { useAuth } from "@/lib/auth";
import { api } from "@/lib/api";

export default function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [acceptedTerms, setAcceptedTerms] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const { status } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (status === "authenticated") router.replace("/dashboard");
  }, [router, status]);

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await api.post("/auth/register", {
        email: email.trim(),
        password,
        full_name: fullName.trim(),
        accepted_terms: acceptedTerms,
        terms_version: "draft-2026-10",
      });
      setSuccess(true);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Account creation failed. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  if (success) {
    return (
      <main className="mx-auto min-h-screen max-w-sm px-4 py-10 sm:py-16">
        <StandaloneHeader />
        <h1 className="mt-5 text-2xl font-bold">Account created</h1>
        <p className="mt-3 text-sm text-gray-600">Sign in to continue to your learning centre and dashboard.</p>
        <Link href="/login" className="btn btn-primary mt-5 w-full">Continue to sign in</Link>
      </main>
    );
  }

  return (
    <main className="mx-auto min-h-screen max-w-sm px-4 py-10 sm:py-16">
      <StandaloneHeader />
      <h1 className="mt-5 text-2xl font-bold">Create account</h1>
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
            autoComplete="new-password"
            minLength={10}
            required
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
          <span className="block text-xs text-gray-500">Use at least 10 characters.</span>
        </label>
        <label className="block space-y-1 text-sm">
          <span>Full name <span className="text-gray-500">(optional)</span></span>
          <input
            className="input"
            autoComplete="name"
            maxLength={120}
            value={fullName}
            onChange={(event) => setFullName(event.target.value)}
          />
        </label>
        <label className="flex items-start gap-2 text-sm">
          <input
            className="mt-1"
            type="checkbox"
            required
            checked={acceptedTerms}
            onChange={(event) => setAcceptedTerms(event.target.checked)}
          />
          <span>I accept the Terms, Privacy Policy and Risk Disclosure.</span>
        </label>
        {error && <p role="alert" className="text-sm text-red-600">{error}</p>}
        <button type="submit" disabled={submitting} className="btn btn-primary w-full disabled:opacity-60">
          {submitting ? "Creating account..." : "Register"}
        </button>
      </form>
      <p className="mt-4 text-sm text-gray-600">
        Already have an account? <Link href="/login" className="text-brand-600">Sign in</Link>
      </p>
      <p className="mt-2 text-xs text-gray-500">
        Educational decision support only. Not financial advice. Trading Forex carries a high risk of loss.
      </p>
    </main>
  );
}
