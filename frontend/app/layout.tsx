import type { Metadata } from "next";
import type { ReactNode } from "react";

import { Shell } from "@/components/layout/shell";

import "./globals.css";

export const metadata: Metadata = {
  title: "Atelier Vision",
  description:
    "Premium AI visual commerce platform for editorial try-on, catalog generation, and luxury retail storytelling.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body>
        <Shell>{children}</Shell>
      </body>
    </html>
  );
}
