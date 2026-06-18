import { Download, RefreshCcw, SplitSquareVertical } from "lucide-react";

import { Button } from "@/components/ui/button";

interface ResultCardProps {
  image: string;
  onDownload: () => void;
  onRegenerate: () => void;
  onToggleCompare: () => void;
  compareEnabled: boolean;
}

export function ResultCard({
  image,
  onDownload,
  onRegenerate,
  onToggleCompare,
  compareEnabled,
}: ResultCardProps) {
  return (
    <div className="space-y-5">
      <div className="aspect-[4/5] overflow-hidden rounded-[2rem] border border-white/10 bg-black/20">
        <img src={image} alt="Generated try-on result" className="h-full w-full object-cover" />
      </div>

      <div className="flex flex-wrap gap-3">
        <Button variant="secondary" onClick={onDownload}>
          <Download className="h-4 w-4" />
          Download image
        </Button>
        <Button variant="outline" onClick={onRegenerate}>
          <RefreshCcw className="h-4 w-4" />
          Regenerate
        </Button>
        <Button variant={compareEnabled ? "default" : "ghost"} onClick={onToggleCompare}>
          <SplitSquareVertical className="h-4 w-4" />
          Compare before/after
        </Button>
      </div>
    </div>
  );
}
