import { Search as SearchIcon } from "lucide-react";
import type { InputHTMLAttributes, TextareaHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

const field = "w-full rounded-sm border bg-surface px-3 text-sm text-ink placeholder:text-muted transition-[border,box-shadow] duration-[var(--motion-fast)] hover:border-[hsl(var(--line-strong))] focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/15 disabled:cursor-not-allowed disabled:bg-raised disabled:text-muted";
export function Input({ className, ...props }: InputHTMLAttributes<HTMLInputElement>) { return <input className={cn(field, "h-9", className)} {...props} />; }
export function Textarea({ className, ...props }: TextareaHTMLAttributes<HTMLTextAreaElement>) { return <textarea className={cn(field, "min-h-24 py-2.5", className)} {...props} />; }
export function Search({ className, ...props }: InputHTMLAttributes<HTMLInputElement>) { return <label className={cn("relative block", className)}><SearchIcon aria-hidden className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted" /><input type="search" className={cn(field, "h-9 pl-9")} {...props} /></label>; }
