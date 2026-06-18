import { WandSparkles } from "lucide-react";

import { Button } from "@/components/ui/button";

interface GenerateButtonProps {
  disabled?: boolean;
  loading?: boolean;
  onClick: () => void;
}

export function GenerateButton({
  disabled,
  loading,
  onClick,
}: GenerateButtonProps) {
  return (
    <Button
      size="lg"
      className="w-full"
      disabled={disabled || loading}
      onClick={onClick}
    >
      <WandSparkles className="h-4 w-4" />
      {loading ? "Generating look..." : "Generate editorial shot"}
    </Button>
  );
}
