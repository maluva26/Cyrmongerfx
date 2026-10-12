"use client";

import Link from "next/link";
import { useAuth } from "@/lib/auth";

const channels = [
  {
    name: "Google Classroom",
    label: "Open class",
    href: process.env.NEXT_PUBLIC_GOOGLE_CLASSROOM_URL || "https://classroom.google.com/c/ODkxNjQzNzk3OTk3?cjc=bn7mnd3n",
    tone: "border-emerald-200 bg-emerald-50 text-emerald-800",
    icon: "classroom",
  },
  {
    name: "WhatsApp",
    label: "Join group",
    href: process.env.NEXT_PUBLIC_WHATSAPP_CLASS_URL || "https://whatsapp.com/channel/0029VbE0ExPKWEKhyVpPeP1X",
    tone: "border-green-200 bg-green-50 text-green-800",
    icon: "whatsapp",
  },
  {
    name: "Telegram",
    label: "Open channel",
    href: process.env.NEXT_PUBLIC_TELEGRAM_CLASS_URL || "https://t.me/cyrmonger",
    tone: "border-sky-200 bg-sky-50 text-sky-800",
    icon: "telegram",
  },
  {
    name: "Discord",
    label: "Join server",
    href: process.env.NEXT_PUBLIC_DISCORD_CLASS_URL || "https://discord.gg/cgKBF8yzq",
    tone: "border-indigo-200 bg-indigo-50 text-indigo-800",
    icon: "discord",
  },
];

function ChannelIcon({ name }: { name: string }) {
  const shared = { "aria-hidden": true as const, viewBox: "0 0 48 48", fill: "none" };

  if (name === "classroom") {
    return (
      <svg {...shared} className="h-7 w-7" xmlns="http://www.w3.org/2000/svg">
        <rect x="5" y="8" width="38" height="29" rx="3" fill="#188038" />
        <path d="M10 13h28v18H10z" fill="#34A853" />
        <circle cx="17" cy="19" r="3" fill="#FBBC04" />
        <circle cx="24" cy="17" r="3.5" fill="#4285F4" />
        <circle cx="31" cy="19" r="3" fill="#EA4335" />
        <path d="M12 28c.7-3 2.4-4.5 5-4.5s4.3 1.5 5 4.5M19 28c.7-3.8 2.3-5.8 5-5.8s4.3 2 5 5.8m0 0c.7-3 2.4-4.5 5-4.5s4.3 1.5 5 4.5" stroke="#fff" strokeWidth="1.8" strokeLinecap="round" />
        <path d="M20 37v4m8-4v4m-10 0h12" stroke="#188038" strokeWidth="3" strokeLinecap="round" />
      </svg>
    );
  }

  if (name === "whatsapp") {
    return (
      <svg {...shared} className="h-7 w-7" xmlns="http://www.w3.org/2000/svg">
        <path d="M24 5a18 18 0 0 0-15.4 27.3L6 42l10-2.5A18 18 0 1 0 24 5Z" fill="#25D366" />
        <path d="M18.1 15.3c-.5-1.1-1-1.1-1.5-1.1h-1.2c-.4 0-1 .2-1.5.7s-2 1.9-2 4.6 2 5.4 2.3 5.8 3.8 6.1 9.4 8.3c4.7 1.9 5.7 1.5 6.7 1.4s3.3-1.4 3.8-2.7.5-2.4.4-2.7-.6-.4-1.2-.7-3.3-1.6-3.8-1.8-.9-.3-1.3.3-1.5 1.8-1.9 2.2-.7.5-1.3.2a15.5 15.5 0 0 1-4.5-2.8 16.8 16.8 0 0 1-3.1-3.8c-.3-.6 0-.9.3-1.2l.9-1c.3-.4.4-.7.6-1.1s.1-.8 0-1.1l-1.9-4.5Z" fill="#fff" />
      </svg>
    );
  }

  if (name === "telegram") {
    return (
      <svg {...shared} className="h-7 w-7" xmlns="http://www.w3.org/2000/svg">
        <circle cx="24" cy="24" r="20" fill="#229ED9" />
        <path d="m12 23.2 22-8.5c1-.4 1.8.2 1.5 1.7l-3.7 17.4c-.3 1.2-1 1.5-2.1.9l-6-4.4-2.9 2.8c-.3.3-.6.6-1.2.6l.4-6.2 11.3-10.2c.5-.4-.1-.7-.7-.3L16.7 26.1l-5.9-1.8c-1.3-.4-1.3-1.3 1.2-2.1Z" fill="#fff" />
      </svg>
    );
  }

  return (
    <svg {...shared} className="h-7 w-7" xmlns="http://www.w3.org/2000/svg">
      <rect x="4" y="7" width="40" height="34" rx="12" fill="#5865F2" />
      <path d="M15 16.5c5.8-2.3 12.2-2.3 18 0 2 2.8 3.3 6.4 3.7 10.8-2.1 2.4-4.3 3.9-6.8 4.7l-1.5-2.4c1-.4 1.8-.9 2.7-1.5-4.4 2-9.8 2-14.2 0 .8.6 1.7 1.1 2.7 1.5l-1.5 2.4c-2.5-.8-4.7-2.3-6.8-4.7.4-4.4 1.7-8 3.7-10.8Z" fill="#fff" />
      <circle cx="19" cy="25" r="2" fill="#5865F2" />
      <circle cx="29" cy="25" r="2" fill="#5865F2" />
    </svg>
  );
}

const sessions = [
  { title: "Beginner Forex Foundations", time: "Mondays", format: "Google Classroom" },
  { title: "Market Structure Live Review", time: "Wednesdays", format: "Discord" },
  { title: "Weekend Trade Recap", time: "Saturdays", format: "Telegram" },
];

export default function ClassesPage() {
  const { status } = useAuth();

  if (status === "loading") return <p className="mx-auto max-w-5xl px-4 py-8">Checking your session...</p>;
  if (status === "anonymous") {
    return <p className="mx-auto max-w-5xl px-4 py-8">Please <Link href="/login" className="text-brand-600 underline">sign in</Link> to open classes.</p>;
  }

  return (
    <main className="mx-auto max-w-5xl px-4 py-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Online Classes</h1>
          <p className="mt-1 text-sm text-gray-600">Google Classroom, WhatsApp, Telegram and Discord.</p>
        </div>
        <span className="rounded-full border border-[var(--border)] px-3 py-1 text-xs font-semibold text-gray-600">Community learning</span>
      </div>

      <section className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {channels.map((channel) => (
          <a
            key={channel.name}
            href={channel.href}
            target="_blank"
            rel="noreferrer"
            className="card p-4 transition-colors hover:border-brand-400 focus-visible:outline focus-visible:outline-2 focus-visible:outline-brand-600"
          >
            <div className={`flex h-11 w-11 items-center justify-center rounded-md border ${channel.tone}`}>
              <ChannelIcon name={channel.icon} />
            </div>
            <h2 className="mt-4 font-semibold">{channel.name}</h2>
            <p className="mt-1 text-sm text-gray-600">{channel.label}</p>
          </a>
        ))}
      </section>

      <section className="mt-7">
        <h2 className="font-semibold">Class Rooms</h2>
        <div className="mt-3 divide-y divide-[var(--border)] border-y border-[var(--border)]">
          {sessions.map((session) => (
            <div key={session.title} className="grid gap-2 py-4 sm:grid-cols-[1fr_auto_auto] sm:items-center">
              <p className="font-medium">{session.title}</p>
              <p className="text-sm text-gray-600">{session.time}</p>
              <p className="text-sm text-gray-600">{session.format}</p>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
