import Image from "next/image";
import Link from "next/link";
import ThemeToggle from "@/components/ThemeToggle";

export default function StandaloneHeader() {
  return (
    <header className="flex items-center justify-between gap-3">
      <Link href="/" aria-label="Cyrmonger Algo Fx home" className="flex w-32 items-center rounded-md bg-white p-1.5 sm:w-40">
        <Image src="/brand/primary-logo.png" width={1186} height={316} alt="Cyrmonger Algo Fx" priority className="h-auto w-full" />
      </Link>
      <ThemeToggle />
    </header>
  );
}
