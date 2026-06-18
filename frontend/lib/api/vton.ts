import { API_BASE_URL } from "@/lib/constants";
import type {
  VtonErrorResponse,
  VtonGeneratePayload,
  VtonGenerateResponse,
} from "@/types/vton";

export async function generateVirtualTryOn(
  payload: VtonGeneratePayload,
): Promise<VtonGenerateResponse> {
  const response = await fetch(`${API_BASE_URL}/vton/generate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    let message = "The generation request failed. Please try again.";

    try {
      const error = (await response.json()) as Partial<VtonErrorResponse>;
      if (typeof error.detail === "string" && error.detail.trim()) {
        message = error.detail;
      }
    } catch {
      message = `Request failed with status ${response.status}.`;
    }

    throw new Error(message);
  }

  return (await response.json()) as VtonGenerateResponse;
}
