import { Sparkle } from "lucide-react";

export function EmptyState() {
  return (
    <div className="flex min-h-[520px] flex-col items-center justify-center rounded-[2rem] border border-dashed border-white/10 bg-black/20 px-8 text-center">
      <span className="rounded-full border border-white/10 bg-white/5 p-4 text-primary">
        <Sparkle className="h-7 w-7" />
      </span>
      <h3 className="mt-6 text-2xl font-semibold tracking-[-0.03em] text-white">
        Your editorial preview will appear here
      </h3>
      <p className="mt-3 max-w-md text-sm leading-7 text-white/50">
        Upload a model image and a garment, shape the mood with a prompt, and
        generate a premium try-on scene.
      </p>
    </div>
  );
}
