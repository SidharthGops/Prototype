import { Sparkles, Shirt, ScanFace, Waves, SwatchBook } from "lucide-react";

import { cn } from "@/lib/utils";

const items = [
  {
    label: "Virtual Try-On",
    description: "Identity-safe editorial output",
    icon: ScanFace,
    active: true,
  },
  {
    label: "Catalog Generation",
    description: "Campaign-ready product assets",
    icon: Shirt,
  },
  {
    label: "Saree Visualization",
    description: "Regional drape intelligence",
    icon: Waves,
  },
  {
    label: "Textile Visualization",
    description: "Material realism at scale",
    icon: SwatchBook,
  },
];

export function Sidebar() {
  return (
    <aside className="glass-panel hidden rounded-3xl p-4 xl:block">
      <div className="mb-4 px-3">
        <p className="text-xs uppercase tracking-[0.25em] text-white/40">Studio</p>
        <h2 className="mt-2 text-lg font-semibold tracking-[-0.03em] text-white">
          Creative Modules
        </h2>
      </div>

      <div className="space-y-2">
        {items.map((item) => (
          <div
            key={item.label}
            className={cn(
              "rounded-2xl border px-4 py-4 transition",
              item.active
                ? "border-primary/30 bg-primary/10"
                : "border-white/5 bg-white/[0.03]",
            )}
          >
            <div className="flex items-start gap-3">
              <span className="mt-0.5 rounded-2xl border border-white/10 bg-white/5 p-2 text-white/75">
                <item.icon className="h-4 w-4" />
              </span>
              <div>
                <p className="text-sm font-medium text-white">{item.label}</p>
                <p className="mt-1 text-sm leading-6 text-white/50">
                  {item.description}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 rounded-2xl border border-white/5 bg-black/20 p-4">
        <div className="flex items-center gap-2 text-primary">
          <Sparkles className="h-4 w-4" />
          <p className="text-xs uppercase tracking-[0.25em]">Creative direction</p>
        </div>
        <p className="mt-3 text-sm leading-6 text-white/60">
          Built for premium commerce teams shaping fashion imagery with speed,
          control, and editorial polish.
        </p>
      </div>
    </aside>
  );
}
