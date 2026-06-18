interface ImagePreviewProps {
  personImage: string;
  garmentImage: string;
}

export function ImagePreview({ personImage, garmentImage }: ImagePreviewProps) {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      <div className="space-y-3">
        <p className="text-xs uppercase tracking-[0.22em] text-white/40">Person input</p>
        <div className="aspect-[4/5] overflow-hidden rounded-[1.75rem] border border-white/10 bg-black/20">
          <img src={personImage} alt="Person upload preview" className="h-full w-full object-cover" />
        </div>
      </div>
      <div className="space-y-3">
        <p className="text-xs uppercase tracking-[0.22em] text-white/40">Garment input</p>
        <div className="aspect-[4/5] overflow-hidden rounded-[1.75rem] border border-white/10 bg-black/20">
          <img src={garmentImage} alt="Garment upload preview" className="h-full w-full object-cover" />
        </div>
      </div>
    </div>
  );
}
