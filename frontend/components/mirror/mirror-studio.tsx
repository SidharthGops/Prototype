"use client";

import { useEffect, useMemo, useState } from "react";
import { AlertCircle, CheckCircle2, Sparkles } from "lucide-react";

import { Sidebar } from "@/components/layout/sidebar";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { DEFAULT_PROMPT, PROGRESS_STEPS } from "@/lib/constants";
import { base64ToDataUrl, dataUrlToBase64, fileToDataUrl } from "@/lib/file";
import { generateVirtualTryOn } from "@/lib/api/vton";
import type { MirrorStage, UploadAsset } from "@/types/vton";
import { BeforeAfterSlider } from "./before-after-slider";
import { EmptyState } from "./empty-state";
import { GenerateButton } from "./generate-button";
import { ImagePreview } from "./image-preview";
import { ImageUploader } from "./image-uploader";
import { LoadingScreen } from "./loading-screen";
import { PromptBox } from "./prompt-box";
import { ResultCard } from "./result-card";

async function makeUploadAsset(file: File): Promise<UploadAsset> {
  const previewUrl = URL.createObjectURL(file);
  const dataUrl = await fileToDataUrl(file);

  return {
    file,
    previewUrl,
    base64: dataUrlToBase64(dataUrl),
  };
}

export function MirrorStudio() {
  const [personAsset, setPersonAsset] = useState<UploadAsset | null>(null);
  const [garmentAsset, setGarmentAsset] = useState<UploadAsset | null>(null);
  const [prompt, setPrompt] = useState(DEFAULT_PROMPT);
  const [stage, setStage] = useState<MirrorStage>("idle");
  const [progress, setProgress] = useState(0);
  const [progressIndex, setProgressIndex] = useState(0);
  const [resultImage, setResultImage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [compareEnabled, setCompareEnabled] = useState(false);
  const [seedNotes, setSeedNotes] = useState("Luxury editorial lighting, clean pose, premium background.");
  const [referenceMood, setReferenceMood] = useState("Quiet luxury, cinematic realism, brand campaign polish.");

  const isReady = Boolean(personAsset && garmentAsset);

  useEffect(() => {
    return () => {
      if (personAsset?.previewUrl) {
        URL.revokeObjectURL(personAsset.previewUrl);
      }
      if (garmentAsset?.previewUrl) {
        URL.revokeObjectURL(garmentAsset.previewUrl);
      }
    };
  }, [personAsset, garmentAsset]);

  useEffect(() => {
    if (stage !== "loading" && stage !== "processing") {
      return;
    }

    const interval = window.setInterval(() => {
      setProgress((current) => {
        const next = Math.min(current + Math.random() * 12 + 6, 92);
        setProgressIndex(Math.min(PROGRESS_STEPS.length - 1, Math.floor(next / 22)));
        return next;
      });
      setStage("processing");
    }, 900);

    return () => window.clearInterval(interval);
  }, [stage]);

  const previewStage = useMemo<MirrorStage>(() => {
    if (resultImage) {
      return "result";
    }
    if (error) {
      return "error";
    }
    if (stage === "loading" || stage === "processing") {
      return stage;
    }
    if (isReady) {
      return "upload-preview";
    }
    return "idle";
  }, [error, isReady, resultImage, stage]);

  async function handleAssetChange(
    setter: (asset: UploadAsset | null) => void,
    existingAsset: UploadAsset | null,
    otherAsset: UploadAsset | null,
    file: File | null,
  ) {
    if (existingAsset?.previewUrl) {
      URL.revokeObjectURL(existingAsset.previewUrl);
    }

    if (!file) {
      setter(null);
      setResultImage(null);
      setError(null);
      setCompareEnabled(false);
      setStage(otherAsset ? "ready" : "idle");
      return;
    }

    const asset = await makeUploadAsset(file);
    setter(asset);
    setError(null);
    setResultImage(null);
    setCompareEnabled(false);
    setStage("ready");
  }

  async function handleGenerate() {
    if (!personAsset || !garmentAsset) {
      return;
    }

    setError(null);
    setResultImage(null);
    setCompareEnabled(false);
    setProgress(12);
    setProgressIndex(0);
    setStage("loading");

    try {
      const response = await generateVirtualTryOn({
        person_image: personAsset.base64,
        garment_image: garmentAsset.base64,
        prompt: `${prompt}\n\nDirection: ${seedNotes}\nMood: ${referenceMood}`,
      });

      setProgress(100);
      setProgressIndex(PROGRESS_STEPS.length - 1);
      setResultImage(base64ToDataUrl(response.output_image));
      setStage("result");
    } catch (requestError) {
      setStage("error");
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Something went wrong while generating the try-on image.",
      );
    }
  }

  function handleDownload() {
    if (!resultImage) {
      return;
    }

    const link = document.createElement("a");
    link.href = resultImage;
    link.download = `atelier-vision-look-${Date.now()}.png`;
    link.click();
  }

  return (
    <section className="container">
      <div className="mb-8">
        <p className="text-xs uppercase tracking-[0.25em] text-white/40">Mirror MVP</p>
        <h1 className="mt-3 text-4xl font-semibold tracking-[-0.05em] text-white md:text-6xl">
          Direct your try-on like a fashion campaign.
        </h1>
        <p className="mt-4 max-w-3xl text-sm leading-7 text-white/55 md:text-base">
          Upload a person and garment image, steer the visual tone with a prompt,
          and generate a polished editorial composition through the VTON backend.
        </p>
      </div>

      <div className="grid gap-6 xl:grid-cols-[280px_minmax(0,1fr)]">
        <Sidebar />

        <div className="panel-grid">
          <Card className="rounded-[2rem] p-6 md:p-7">
            <CardHeader className="border-b border-white/8 pb-6">
              <CardTitle>Creative inputs</CardTitle>
              <CardDescription>
                Curate the subject, garment, and visual mood for the generated frame.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6 pt-6">
              <div className="grid gap-4 sm:grid-cols-2">
                <ImageUploader
                  asset={personAsset}
                  label="Person Image Upload"
                  hint="Use a clear portrait or full-body fashion image."
                  onChange={(file) =>
                    void handleAssetChange(setPersonAsset, personAsset, garmentAsset, file)
                  }
                />
                <ImageUploader
                  asset={garmentAsset}
                  label="Garment Image Upload"
                  hint="Use a garment cutout or clean catalog shot."
                  onChange={(file) =>
                    void handleAssetChange(setGarmentAsset, garmentAsset, personAsset, file)
                  }
                />
              </div>

              <PromptBox
                value={prompt}
                onChange={setPrompt}
                placeholder={DEFAULT_PROMPT}
              />

              <Accordion type="single" collapsible defaultValue="advanced">
                <AccordionItem value="advanced">
                  <AccordionTrigger>Advanced settings</AccordionTrigger>
                  <AccordionContent className="space-y-4">
                    <div>
                      <label className="mb-2 block text-sm text-white/60">
                        Scene notes
                      </label>
                      <Input
                        value={seedNotes}
                        onChange={(event) => setSeedNotes(event.target.value)}
                        placeholder="Lighting, framing, and environment cues"
                      />
                    </div>
                    <div>
                      <label className="mb-2 block text-sm text-white/60">
                        Mood reference
                      </label>
                      <Input
                        value={referenceMood}
                        onChange={(event) => setReferenceMood(event.target.value)}
                        placeholder="Brand tone or campaign mood"
                      />
                    </div>
                  </AccordionContent>
                </AccordionItem>
              </Accordion>

              <GenerateButton
                disabled={!isReady}
                loading={stage === "loading" || stage === "processing"}
                onClick={() => void handleGenerate()}
              />

              <div className="flex items-center gap-2 rounded-2xl border border-white/8 bg-black/20 px-4 py-3 text-sm text-white/55">
                {isReady ? (
                  <>
                    <CheckCircle2 className="h-4 w-4 text-primary" />
                    Inputs are ready for generation.
                  </>
                ) : (
                  <>
                    <Sparkles className="h-4 w-4 text-primary" />
                    Upload both images to enable generation.
                  </>
                )}
              </div>
            </CardContent>
          </Card>

          <Card className="rounded-[2rem] p-6 md:p-7">
            <CardHeader className="border-b border-white/8 pb-6">
              <CardTitle>Preview & output</CardTitle>
              <CardDescription>
                Review the inputs, monitor generation progress, and export the final result.
              </CardDescription>
            </CardHeader>
            <CardContent className="pt-6">
              {previewStage === "idle" && <EmptyState />}

              {previewStage === "upload-preview" && personAsset && garmentAsset && (
                <ImagePreview
                  personImage={personAsset.previewUrl}
                  garmentImage={garmentAsset.previewUrl}
                />
              )}

              {(previewStage === "loading" || previewStage === "processing") && (
                <LoadingScreen
                  progress={progress}
                  label={previewStage === "loading" ? "Uploading" : "Processing"}
                  message={PROGRESS_STEPS[progressIndex]}
                />
              )}

              {previewStage === "error" && (
                <div className="flex min-h-[520px] flex-col items-center justify-center rounded-[2rem] border border-destructive/20 bg-destructive/10 px-8 text-center">
                  <AlertCircle className="h-8 w-8 text-destructive" />
                  <h3 className="mt-5 text-2xl font-semibold text-white">
                    The generation could not be completed
                  </h3>
                  <p className="mt-3 max-w-md text-sm leading-7 text-white/65">
                    {error}
                  </p>
                </div>
              )}

              {previewStage === "result" && resultImage && personAsset && (
                <div className="space-y-6">
                  <ResultCard
                    image={resultImage}
                    onDownload={handleDownload}
                    onRegenerate={() => void handleGenerate()}
                    onToggleCompare={() => setCompareEnabled((value) => !value)}
                    compareEnabled={compareEnabled}
                  />

                  {compareEnabled && (
                    <BeforeAfterSlider
                      before={personAsset.previewUrl}
                      after={resultImage}
                    />
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </section>
  );
}
