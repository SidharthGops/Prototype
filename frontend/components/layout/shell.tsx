import type { ReactNode } from "react";

import { Navbar } from "@/components/layout/navbar";

export function Shell({ children }: { children: ReactNode }) {
  return (
    <div className="relative min-h-screen overflow-hidden">
      <div className="absolute inset-x-0 top-[-220px] h-[420px] bg-[radial-gradient(circle,rgba(216,177,104,0.18),transparent_55%)] blur-3xl" />
      <Navbar />
      <main className="pb-16 pt-10">{children}</main>
    </div>
  );
}
