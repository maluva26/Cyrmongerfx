"use client";

import { useState, type ReactNode } from "react";
import Image from "next/image";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { api } from "@/lib/api";
import ThemeToggle from "@/components/ThemeToggle";

const NAV = [
  { href: "/dashboard", label: "Home", icon: "home", roles: ["TRADER", "ADMIN"] },
  { href: "/analyze", label: "Analyze", icon: "analyze", roles: ["TRADER", "ADMIN"] },
  { href: "/learn", label: "Learn", icon: "learn", roles: ["TRADER", "ADMIN"] },
  { href: "/chat", label: "Forex Chat", icon: "chat", roles: ["TRADER", "ADMIN"] },
  { href: "/classes", label: "Classes", icon: "classes", roles: ["TRADER", "ADMIN"] },
  { href: "/risk", label: "Risk", icon: "risk", roles: ["TRADER", "ADMIN"] },
  { href: "/journal", label: "Journal", icon: "journal", roles: ["TRADER", "ADMIN"] },
  { href: "/reports", label: "Reports", icon: "reports", roles: ["TRADER", "ADMIN"] },
  { href: "/assistant", label: "Assistant", icon: "assistant", roles: ["TRADER", "ADMIN"] },
  { href: "/credits", label: "Credits", icon: "credits", roles: ["TRADER", "ADMIN"] },
  { href: "/profile", label: "Profile", icon: "profile", roles: ["TRADER", "ADMIN"] },
  { href: "/admin", label: "Admin", icon: "admin", roles: ["ADMIN"] },
];

function NavIcon({ name }: { name: string }) {
  const common = {
    "aria-hidden": true as const,
    width: 20,
    height: 20,
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 1.8,
    strokeLinecap: "round" as const,
    strokeLinejoin: "round" as const,
  };

  switch (name) {
    case "home": return <svg {...common}><path d="m3 10 9-7 9 7" /><path d="M5 9v12h14V9M9 21v-7h6v7" /></svg>;
    case "analyze": return <svg {...common}><path d="M3 17 9 11l4 4 8-9" /><path d="M15 6h6v6" /><path d="M4 21h16" /></svg>;
    case "learn": return <svg {...common}><path d="m3 7 9-4 9 4-9 4-9-4Z" /><path d="M5 9v6c4 3 10 3 14 0V9" /><path d="M21 7v7" /></svg>;
    case "chat": return <svg {...common}><path d="M4 5h16v10H8l-4 4V5Z" /><path d="M8 9h8M8 12h5" /></svg>;
    case "classes": return <svg {...common}><path d="M4 5h16v12H4z" /><path d="M8 21h8M12 17v4" /><path d="M8 9h8M8 12h5" /></svg>;
    case "risk": return <svg {...common}><path d="M12 3 20 6v5c0 5-3.4 8.2-8 10-4.6-1.8-8-5-8-10V6l8-3Z" /><path d="m9 12 2 2 4-4" /></svg>;
    case "journal": return <svg {...common}><path d="M6 4h14v17H6a3 3 0 0 1 0-6h14" /><path d="M6 4a3 3 0 0 0-3 3v11" /><path d="M10 8h6M10 12h6" /></svg>;
    case "reports": return <svg {...common}><path d="M5 3h10l4 4v14H5z" /><path d="M14 3v5h5M8 16v-3M12 16V9M16 16v-5" /></svg>;
    case "assistant": return <svg {...common}><path d="M12 3a8 8 0 0 0-8 8v7a2 2 0 0 0 2 2h2v-7H5" /><path d="M12 3a8 8 0 0 1 8 8v7a2 2 0 0 1-2 2h-2v-7h3" /><path d="M9 21h4" /></svg>;
    case "credits": return <svg {...common}><circle cx="12" cy="12" r="9" /><path d="M12 11v5M12 8h.01" /></svg>;
    case "profile": return <svg {...common}><circle cx="12" cy="8" r="4" /><path d="M4 21a8 8 0 0 1 16 0" /></svg>;
    case "admin": return <svg {...common}><path d="M12 3 20 7v5c0 4.5-3.2 7.5-8 9-4.8-1.5-8-4.5-8-9V7l8-4Z" /><path d="M12 8v4M12 16h.01" /></svg>;
    default: return null;
  }
}

export default function AppNav({ children }: { children: ReactNode }) {
  const { user, token, status, clear } = useAuth();
  const [signingOut, setSigningOut] = useState(false);
  const [error, setError] = useState("");
  const path = usePathname();
  const router = useRouter();
  const isStandalonePage = ["/login", "/register", "/admin/login", "/admin/create-account"].includes(path);
  const authenticated = status === "authenticated" && Boolean(user);
  const items = NAV.filter((item) => (user?.role ? item.roles.includes(user.role) : false));

  const signOut = async () => {
    setError("");
    setSigningOut(true);
    try {
      await api.post("/auth/logout", {}, token);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Sign out failed. Please try again.");
      return;
    } finally {
      setSigningOut(false);
    }
    clear();
    router.replace("/login");
  };

  const renderItem = (item: (typeof NAV)[number], mobile = false) => {
    const active = path === item.href || path.startsWith(`${item.href}/`);
    return (
      <Link
        key={item.href}
        href={item.href}
        aria-current={active ? "page" : undefined}
        title={mobile ? item.label : undefined}
        className={`flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors ${
          active ? "bg-sky-50 font-semibold text-sky-800 dark:bg-sky-950 dark:text-sky-200" : "text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-700 dark:hover:text-white"
        } ${mobile ? "min-w-16 flex-col gap-1 px-2 py-1 text-[11px]" : ""}`}
      >
        <NavIcon name={item.icon} />
        <span>{item.label}</span>
      </Link>
    );
  };

  const showNavigation = authenticated && !isStandalonePage;

  return (
    <>
      {showNavigation && (
        <aside className="fixed inset-y-0 left-0 z-30 hidden w-64 flex-col border-r border-[var(--border)] bg-[var(--background)] px-4 py-5 md:flex">
          <Link href="/" aria-label="Cyrmonger Algo Fx home" className="mb-7 flex h-16 items-center rounded-md bg-white px-3">
            <Image src="/brand/primary-logo.png" width={1186} height={316} alt="Cyrmonger Algo Fx" priority className="h-auto w-full" />
          </Link>
          <nav aria-label="Main navigation" className="flex-1 space-y-1">
            {items.map((item) => renderItem(item))}
          </nav>
          <div className="border-t border-[var(--border)] pt-4">
            <ThemeToggle />
            <p className="truncate px-2 pt-2 text-xs text-gray-500 dark:text-gray-400">{user?.email}</p>
            {error && <p role="alert" className="mt-2 px-2 text-xs text-red-600">{error}</p>}
            <button type="button" onClick={() => void signOut()} disabled={signingOut} className="mt-3 flex w-full items-center gap-3 rounded-md px-3 py-2 text-left text-sm text-gray-600 hover:bg-gray-100 disabled:opacity-50 dark:text-gray-300 dark:hover:bg-gray-700">
              <svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M10 17l5-5-5-5M15 12H3" /><path d="M12 3h6a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-6" /></svg>
              {signingOut ? "Signing out..." : "Sign out"}
            </button>
          </div>
        </aside>
      )}

      {showNavigation && (
        <header className="sticky top-0 z-30 border-b border-[var(--border)] bg-[var(--background)] md:hidden">
          <div className="flex items-center justify-between gap-3 px-4 py-3">
            <Link href="/" aria-label="Cyrmonger Algo Fx home" className="flex min-w-0 items-center gap-2">
              <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-white p-1">
                <Image src="/brand/app-mark.png" width={479} height={530} alt="" className="h-full w-full object-contain" />
              </span>
              <span className="text-xs font-bold leading-tight text-brand-600">Cyrmonger Algo Fx</span>
            </Link>
            <div className="flex items-center gap-2">
              <ThemeToggle showLabel={false} />
              <button type="button" onClick={() => void signOut()} disabled={signingOut} className="text-sm text-gray-600 disabled:opacity-50 dark:text-gray-300">
                {signingOut ? "Signing out..." : "Sign out"}
              </button>
            </div>
          </div>
          <nav aria-label="Main navigation" className="flex gap-1 overflow-x-auto border-t border-[var(--border)] px-2 py-2">
            {items.map((item) => renderItem(item, true))}
          </nav>
          {error && <p role="alert" className="px-4 pb-2 text-xs text-red-600">{error}</p>}
        </header>
      )}

      <div className={showNavigation ? "min-h-screen md:pl-64" : "min-h-screen"}>{children}</div>
    </>
  );
}
