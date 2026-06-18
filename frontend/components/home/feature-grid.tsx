"use client";

import { motion } from "framer-motion";
import { ArrowUpRight, ScanFace, Shirt, SwatchBook, Waves } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const features = [
  {
    title: "Virtual Try-On",
    copy: "Transform product photography into premium try-on imagery with controlled styling and preserved identity.",
    icon: ScanFace,
  },
  {
    title: "Catalog Generation",
    copy: "Generate launch-ready SKU visuals, hero product shots, and branded ecommerce compositions at scale.",
    icon: Shirt,
  },
  {
    title: "Saree Visualization",
    copy: "Preview drape, mood, and environment treatments tailored to premium South Asian fashion storytelling.",
    icon: Waves,
  },
  {
    title: "Textile Visualization",
    copy: "Explore weave, sheen, and texture in immersive compositions that make materials feel tactile online.",
    icon: SwatchBook,
  },
];

export function FeatureGrid() {
  return (
    <section id="features" className="container mt-10 md:mt-16">
      <div className="mb-8 flex items-end justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-white/40">Capabilities</p>
          <h2 className="mt-3 text-3xl font-semibold tracking-[-0.04em] text-white md:text-5xl">
            Built like a design studio, not a dashboard.
          </h2>
        </div>
        <p className="hidden max-w-md text-sm leading-7 text-white/55 lg:block">
          Each workflow is modular, API-driven, and designed for future expansion
          without compromising the premium customer-facing feel.
        </p>
      </div>

      <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
        {features.map((feature, index) => (
          <motion.div
            key={feature.title}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.3 }}
            transition={{ duration: 0.5, delay: index * 0.08 }}
          >
            <Card className="group h-full min-h-72 transition hover:border-primary/25 hover:bg-white/[0.07]">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <span className="rounded-2xl border border-white/10 bg-white/5 p-3 text-primary">
                    <feature.icon className="h-5 w-5" />
                  </span>
                  <ArrowUpRight className="h-4 w-4 text-white/30 transition group-hover:text-primary" />
                </div>
                <CardTitle className="mt-10">{feature.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>{feature.copy}</CardDescription>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
