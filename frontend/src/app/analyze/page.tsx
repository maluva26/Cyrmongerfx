"use client";
import { useState } from "react";
import Image from "next/image";
import { useAuth } from "@/lib/auth";
import { api } from "@/lib/api";

type AnalysisResult = {
  analysis_id: string;
  signal_category: string;
  overall_confidence: number | null;
  explanation: string;
  detections: { label: string; confidence: number; box: number[] }[];
  is_demo_model: boolean;
  disclaimer: string;
};

export default function AnalyzePage() {
  const { token } = useAuth();
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const onFile = (f: File) => {
    setError("");
    setResult(null);
    if (!["image/png", "image/jpeg", "image/webp"].includes(f.type)) {
      setFile(null);
      setPreview(null);
      setError("Choose a PNG, JPEG, or WebP image.");
      return;
    }
    if (f.size > 2 * 1024 * 1024) {
      setFile(null);
      setPreview(null);
      setError("The image must be 2 MB or smaller.");
      return;
    }
    setFile(f);
    const reader = new FileReader();
    reader.onload = () => {
      if (typeof reader.result === "string") setPreview(reader.result);
      else setError("The image preview could not be loaded.");
    };
    reader.onerror = () => {
      setFile(null);
      setPreview(null);
      setError("The image preview could not be loaded.");
    };
    reader.readAsDataURL(f);
  };

  const compress = (file: File) => {
    return new Promise<Blob>((resolve, reject) => {
      const image = new window.Image();
      const source = URL.createObjectURL(file);
      const releaseSource = () => URL.revokeObjectURL(source);
      image.onload = () => {
        try {
          const canvas = document.createElement("canvas");
          const max = 1280;
          const scale = Math.min(1, max / Math.max(image.naturalWidth, image.naturalHeight));
          canvas.width = Math.max(1, Math.round(image.naturalWidth * scale));
          canvas.height = Math.max(1, Math.round(image.naturalHeight * scale));
          const context = canvas.getContext("2d");
          if (!context) throw new Error("This browser could not process the image.");
          context.drawImage(image, 0, 0, canvas.width, canvas.height);
          canvas.toBlob((blob) => {
            releaseSource();
            if (blob) resolve(blob);
            else reject(new Error("The image could not be prepared for analysis."));
          }, "image/webp", 0.8);
        } catch (cause) {
          releaseSource();
          reject(cause);
        }
      };
      image.onerror = () => {
        releaseSource();
        reject(new Error("This file is not a readable image."));
      };
      image.src = source;
    });
  };

  const submit = async () => {
    if (!file || !token) return;
    setLoading(true); setError(""); setResult(null);
    try {
      const blob = await compress(file);
      const form = new FormData();
      form.append("image", blob, "chart.webp");
      const data = await api.upload<AnalysisResult>("/charts/analyze", form, token);
      setResult(data);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Analysis failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-4xl px-4 py-6">
      <h1 className="text-2xl font-bold">Analyze Chart</h1>
      {result?.is_demo_model && <p className="mt-2 rounded bg-yellow-100 p-2 text-sm text-yellow-800">DEMO MODEL: results are simulated</p>}
      <div className="mt-4">
        <input
          type="file"
          accept="image/png,image/jpeg,image/webp"
          aria-label="Choose a chart image"
          onChange={(event) => {
            const selected = event.currentTarget.files?.[0];
            if (selected) onFile(selected);
            event.currentTarget.value = "";
          }}
        />
        {preview && (
          <div className="relative mt-2 h-64 w-full">
            <Image src={preview} alt="Selected chart preview" fill unoptimized sizes="(max-width: 768px) 100vw, 768px" className="object-contain" />
          </div>
        )}
        <button onClick={submit} disabled={loading || !file} className="btn btn-primary mt-2">{loading ? "Analyzing..." : "Analyze"}</button>
      </div>
      {error && <p className="mt-2 text-red-600">{error}</p>}
      {result && (
        <div className="mt-6 space-y-3">
          <div className="card p-4">
            <p className="font-semibold">Signal: {result.signal_category}</p>
            <p className="text-sm text-gray-500">Confidence: {typeof result.overall_confidence === "number" ? result.overall_confidence.toFixed(4) : "N/A"}</p>
            <p className="mt-2 text-sm">{result.explanation}</p>
            <p className="mt-2 text-xs text-gray-500">{result.disclaimer}</p>
          </div>
          {result.detections.length > 0 && (
            <div className="space-y-2">
              {result.detections.map((d) => (
                <div key={d.label} className="card p-3">
                  <span className="text-sm font-medium">{d.label.replace(/_/g, " ")}</span>
                  <div className="h-2 rounded bg-gray-200">
                    <div className="h-2 rounded bg-brand-500" style={{ width: `${d.confidence * 100}%` }} />
                  </div>
                  <span className="text-xs text-gray-500">{(d.confidence * 100).toFixed(1)}%</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
