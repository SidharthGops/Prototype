import { cn } from "@/lib/utils";

export function Progress({
  value,
  className,
}: {
  value: number;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "h-2 w-full overflow-hidden rounded-full bg-white/10 ring-1 ring-white/10",
        className,
      )}
    >
      <div
        className="h-full rounded-full bg-[linear-gradient(90deg,rgba(255,231,190,0.45),rgba(224,182,106,0.95),rgba(255,244,220,0.65))] transition-all duration-500"
        style={{ width: `${Math.max(6, Math.min(100, value))}%` }}
      />
    </div>
  );
}
