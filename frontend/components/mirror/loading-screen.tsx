"use client";

import { motion } from "framer-motion";

import { Progress } from "@/components/ui/progress";

interface LoadingScreenProps {
  progress: number;
  label: string;
  message: string;
}

export function LoadingScreen({
  progress,
  label,
  message,
}: LoadingScreenProps) {
  return (
    <div className="flex min-h-[520px] flex-col justify-center rounded-[2rem] border border-white/10 bg-[radial-gradient(circle_at_top,rgba(216,177,104,0.16),transparent_40%),rgba(255,255,255,0.03)] p-8">
      <div className="max-w-lg">
        <div className="inline-flex rounded-full border border-primary/20 bg-primary/10 px-3 py-1 text-xs uppercase tracking-[0.28em] text-primary">
          {label}
        </div>
        <h3 className="mt-6 text-3xl font-semibold tracking-[-0.04em] text-white">
          Generating your cinematic try-on frame
        </h3>
        <p className="mt-4 text-sm leading-7 text-white/55">{message}</p>
        <Progress value={progress} className="mt-8" />
        <div className="mt-3 flex items-center justify-between text-xs uppercase tracking-[0.22em] text-white/40">
          <span>Generation progress</span>
          <span>{Math.round(progress)}%</span>
        </div>
      </div>

      <div className="mt-12 grid gap-4 md:grid-cols-3">
        {[0, 1, 2].map((item) => (
          <motion.div
            key={item}
            animate={{ opacity: [0.35, 0.8, 0.35] }}
            transition={{ duration: 1.8, repeat: Number.POSITIVE_INFINITY, delay: item * 0.2 }}
            className="aspect-[4/5] rounded-[1.75rem] border border-white/10 bg-[linear-gradient(115deg,rgba(255,255,255,0.08),rgba(255,255,255,0.02),rgba(255,255,255,0.08))] bg-[length:200%_100%] p-3"
          >
            <div className="h-full rounded-[1.25rem] bg-black/20" />
          </motion.div>
        ))}
      </div>
    </div>
  );
}
