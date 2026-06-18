export const DEFAULT_PROMPT =
  "Generate a cinematic fashion editorial shot. Preserve identity and garment details. Create a luxurious and visually appealing scene.";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "/api";

export const PROGRESS_STEPS = [
  "Preparing assets",
  "Preserving subject identity",
  "Rendering garment drape",
  "Composing editorial lighting",
  "Finalizing high-fidelity output",
] as const;
