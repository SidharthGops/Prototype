import { Sparkles } from "lucide-react";

import { Textarea } from "@/components/ui/textarea";

interface PromptBoxProps {
  value: string;
  onChange: (value: string) => void;
  placeholder: string;
}

export function PromptBox({ value, onChange, placeholder }: PromptBoxProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 text-sm text-white/70">
        <Sparkles className="h-4 w-4 text-primary" />
        Prompt direction
      </div>
      <Textarea
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
      />
    </div>
  );
}
