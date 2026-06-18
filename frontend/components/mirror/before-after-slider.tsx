"use client";

import { useState } from "react";

interface BeforeAfterSliderProps {
  before: string;
  after: string;
}

export function BeforeAfterSlider({ before, after }: BeforeAfterSliderProps) {
  const [position, setPosition] = useState(52);

  return (
    <div className="space-y-4">
      <div className="relative aspect-[4/5] overflow-hidden rounded-[1.75rem] border border-white/10 bg-black/20">
        <img src={before} alt="Before try-on" className="absolute inset-0 h-full w-full object-cover" />
        <div className="absolute inset-0 overflow-hidden" style={{ width: `${position}%` }}>
          <img src={after} alt="After try-on" className="h-full w-full object-cover" />
        </div>
        <div className="absolute inset-y-0" style={{ left: `${position}%` }}>
          <div className="h-full w-px bg-white/80" />
          <div className="absolute left-1/2 top-1/2 flex h-10 w-10 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full border border-white/20 bg-black/50 text-xs text-white">
            ↔
          </div>
        </div>
      </div>
      <input
        type="range"
        min={0}
        max={100}
        value={position}
        onChange={(event) => setPosition(Number(event.target.value))}
        className="w-full accent-[rgb(225,191,127)]"
      />
    </div>
  );
}
