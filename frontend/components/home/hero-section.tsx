"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, PlayCircle } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export function HeroSection() {
  return (
    <section className="container">
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="glass-panel relative overflow-hidden rounded-[2rem] px-6 py-10 md:px-10 md:py-14"
      >
        <div className="absolute inset-0 bg-hero-noise opacity-70" />
        <div className="relative grid gap-10 lg:grid-cols-[1.15fr_0.85fr] lg:items-end">
          <div>
            <Badge>AI visual commerce</Badge>
            <h1 className="editorial-heading mt-6">
              Luxury-grade product imagery, generated with editorial precision.
            </h1>
            <p className="editorial-subtitle mt-6">
              Build immersive visual shopping experiences across virtual try-on,
              catalog campaigns, saree draping, and textile storytelling.
            </p>

            <div className="mt-8 flex flex-wrap gap-3">
              <Button size="lg" asChild>
                <Link href="/mirror">
                  Start virtual try-on
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </Button>
              <Button size="lg" variant="secondary">
                <PlayCircle className="h-4 w-4" />
                Product walkthrough
              </Button>
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            {[
              ["Identity-safe", "Preserve face fidelity and garment details."],
              ["Cinematic scenes", "Direct the scene with natural-language prompts."],
              ["Scaled output", "Prepare campaign visuals and SKU content faster."],
              ["Luxury finish", "Crafted for premium consumer presentation."],
            ].map(([title, copy], index) => (
              <motion.div
                key={title}
                initial={{ opacity: 0, y: 18 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.1 * (index + 1) }}
                className="rounded-[1.75rem] border border-white/10 bg-black/20 p-5"
              >
                <p className="text-sm font-medium text-white">{title}</p>
                <p className="mt-2 text-sm leading-6 text-white/55">{copy}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.div>
    </section>
  );
}
