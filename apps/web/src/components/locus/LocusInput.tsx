"use client";

import { forwardRef, type InputHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

export const LocusInput = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement>>(function LocusInput({ className, ...props }, ref) {
  return <input ref={ref} className={cn("locus-input", className)} {...props} />;
});
