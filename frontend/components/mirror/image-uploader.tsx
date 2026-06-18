"use client";

import { ImagePlus, UploadCloud, X } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import type { UploadAsset } from "@/types/vton";

interface ImageUploaderProps {
  asset: UploadAsset | null;
  label: string;
  hint: string;
  onChange: (file: File | null) => void;
}

export function ImageUploader({
  asset,
  label,
  hint,
  onChange,
}: ImageUploaderProps) {
  return (
    <label
      className={cn(
        "group block cursor-pointer rounded-[1.75rem] border border-dashed border-white/12 bg-white/[0.03] p-4 transition hover:border-primary/35 hover:bg-white/[0.05]",
        asset && "border-primary/25 bg-primary/5",
      )}
    >
      <input
        type="file"
        accept="image/png,image/jpeg,image/webp"
        className="hidden"
        onChange={(event) => onChange(event.target.files?.[0] ?? null)}
      />

      {asset ? (
        <div className="space-y-4">
          <div className="relative aspect-[4/5] overflow-hidden rounded-[1.4rem]">
            <img
              src={asset.previewUrl}
              alt={label}
              className="h-full w-full object-cover"
            />
          </div>
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="text-sm font-medium text-white">{label} ready</p>
              <p className="text-xs text-white/50">{asset.file.name}</p>
            </div>
            <Button
              type="button"
              variant="ghost"
              size="icon"
              onClick={(event) => {
                event.preventDefault();
                onChange(null);
              }}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>
      ) : (
        <div className="flex aspect-[4/5] flex-col items-center justify-center rounded-[1.4rem] border border-white/8 bg-black/20 px-6 text-center">
          <span className="rounded-full border border-white/10 bg-white/5 p-4 text-primary">
            {label.toLowerCase().includes("person") ? (
              <ImagePlus className="h-6 w-6" />
            ) : (
              <UploadCloud className="h-6 w-6" />
            )}
          </span>
          <p className="mt-5 text-sm font-medium text-white">{label}</p>
          <p className="mt-2 text-sm leading-6 text-white/45">{hint}</p>
        </div>
      )}
    </label>
  );
}
