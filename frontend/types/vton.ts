export type MirrorStage =
  | "idle"
  | "ready"
  | "upload-preview"
  | "loading"
  | "processing"
  | "result"
  | "error";

export interface VtonGeneratePayload {
  person_image: string;
  garment_image: string;
  prompt?: string;
}

export interface VtonGenerateResponse {
  output_image: string;
}

export interface VtonErrorResponse {
  detail: string;
}

export interface UploadAsset {
  file: File;
  previewUrl: string;
  base64: string;
}
