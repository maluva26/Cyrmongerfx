function CreditIcon({ name }: { name: "name" | "role" | "phone" | "email" | "portfolio" }) {
  const common = {
    "aria-hidden": true as const,
    className: "h-4 w-4 shrink-0",
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 1.8,
    strokeLinecap: "round" as const,
    strokeLinejoin: "round" as const,
  };

  switch (name) {
    case "name": return <svg {...common}><circle cx="12" cy="8" r="4" /><path d="M4 21a8 8 0 0 1 16 0" /></svg>;
    case "role": return <svg {...common}><rect x="3" y="7" width="18" height="13" rx="2" /><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M3 12h18M10 12v2h4v-2" /></svg>;
    case "phone": return <svg {...common}><path d="M5 3h4l2 5-3 2a15 15 0 0 0 6 6l2-3 5 2v4a2 2 0 0 1-2 2A17 17 0 0 1 3 5a2 2 0 0 1 2-2Z" /></svg>;
    case "email": return <svg {...common}><rect x="3" y="5" width="18" height="14" rx="2" /><path d="m4 7 8 6 8-6" /></svg>;
    case "portfolio": return <svg {...common}><rect x="3" y="7" width="18" height="14" rx="2" /><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M3 12h18M10 12v2h4v-2" /></svg>;
  }
}

export default function CreditsPage() {
  const year = new Date().getFullYear();

  return (
    <main className="mx-auto max-w-4xl px-4 py-6">
      <header>
        <h1 className="text-2xl font-bold">Credits</h1>
        <p className="mt-1 text-sm text-gray-600">About the developer and copyright information.</p>
      </header>

      <section className="mt-7 border-t border-[var(--border)] py-5" aria-labelledby="developer-heading">
        <h2 id="developer-heading" className="text-lg font-semibold">About the Developer</h2>
        <dl className="mt-4 grid gap-x-6 gap-y-4 sm:grid-cols-[180px_1fr]">
          <dt className="flex items-center gap-2 text-sm text-gray-500"><CreditIcon name="name" />Name</dt>
          <dd className="font-medium">Malvern Pondeka</dd>

          <dt className="flex items-center gap-2 text-sm text-gray-500"><CreditIcon name="role" />Role</dt>
          <dd>Software developer and system analyst</dd>

          <dt className="flex items-center gap-2 text-sm text-gray-500"><CreditIcon name="phone" />Phone</dt>
          <dd><a className="text-brand-600 underline" href="tel:0789733173">0789733173</a></dd>

          <dt className="flex items-center gap-2 text-sm text-gray-500"><CreditIcon name="email" />Email</dt>
          <dd><a className="text-brand-600 underline" href="mailto:Maluvaths@gmail.com">Maluvaths@gmail.com</a></dd>

          <dt className="flex items-center gap-2 text-sm text-gray-500"><CreditIcon name="portfolio" />Portfolio</dt>
          <dd>
            <a className="text-brand-600 underline" href="https://malvernpondeka.netlify.app/" target="_blank" rel="noreferrer">
              malvernpondeka.netlify.app
            </a>
          </dd>
        </dl>
      </section>

      <footer className="mt-5 border-t border-[var(--border)] py-5 text-sm text-gray-600">
        <p>Developed by Malvern Pondeka.</p>
        <p className="mt-1">© {year} Cyrmonger Algo Fx. All rights reserved.</p>
      </footer>
    </main>
  );
}
