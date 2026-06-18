import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

const links = [
  { href: "/", label: "Home" },
  { href: "/mirror", label: "Mirror" },
  { href: "#features", label: "Capabilities" },
];

export function Navbar() {
  return (
    <header className="sticky top-0 z-50">
      <div className="container pt-6">
        <div className="glass-panel flex items-center justify-between rounded-full px-5 py-3">
          <Link href="/" className="flex items-center gap-3">
            <span className="flex h-10 w-10 items-center justify-center rounded-full border border-primary/20 bg-primary/10 text-xs font-semibold tracking-[0.25em] text-primary">
              AV
            </span>
            <div>
              <p className="text-sm font-semibold tracking-[0.18em] text-white">
                Atelier Vision
              </p>
              <p className="text-xs text-white/45">AI visual commerce platform</p>
            </div>
          </Link>

          <nav className="hidden items-center gap-1 md:flex">
            {links.map((link) => (
              <Button key={link.href} variant="ghost" asChild>
                <Link href={link.href}>{link.label}</Link>
              </Button>
            ))}
          </nav>

          <div className="flex items-center gap-3">
            <Badge className="hidden sm:inline-flex">Dark editorial UI</Badge>
            <Button asChild>
              <Link href="/mirror">Launch Mirror</Link>
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
}
