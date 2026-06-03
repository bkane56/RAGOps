"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/", label: "Overview" },
  { href: "/documents", label: "Documents" },
  { href: "/ask", label: "Ask" },
  { href: "/compare", label: "Compare" },
  { href: "/evaluation", label: "Evaluation" },
  { href: "/settings", label: "Settings" },
  { href: "/about", label: "About" },
];

export function Nav() {
  const pathname = usePathname();
  return (
    <nav className="border-b border-slate-800 bg-panel px-4 py-3">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center gap-4">
        <Link href="/" className="text-lg font-semibold text-white">
          RAGOps
        </Link>
        <ul className="flex flex-wrap gap-3 text-sm">
          {links.map((link) => (
            <li key={link.href}>
              <Link
                href={link.href}
                className={
                  pathname === link.href
                    ? "text-accent font-medium"
                    : "text-muted hover:text-white"
                }
              >
                {link.label}
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </nav>
  );
}
