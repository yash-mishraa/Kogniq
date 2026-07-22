import { cva, type VariantProps } from "class-variance-authority";
import type { ButtonHTMLAttributes, ReactNode } from "react";
import { cn } from "@/lib/utils";

const buttonVariants = cva("inline-flex h-9 items-center justify-center gap-2 whitespace-nowrap rounded-sm px-3 text-sm font-medium transition-colors duration-[var(--motion-fast)] disabled:pointer-events-none disabled:opacity-45", {
  variants: {
    variant: {
      primary: "bg-accent text-accent-ink hover:brightness-95",
      secondary: "border bg-surface text-ink hover:bg-raised",
      ghost: "text-muted hover:bg-raised hover:text-ink",
      danger: "bg-danger text-white hover:brightness-95",
    },
    size: { sm: "h-8 px-2.5 text-xs", md: "h-9 px-3", lg: "h-10 px-4" },
  },
  defaultVariants: { variant: "primary", size: "md" },
});

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement>, VariantProps<typeof buttonVariants> { children: ReactNode }
export function Button({ className, variant, size, type = "button", ...props }: ButtonProps) { return <button type={type} className={cn(buttonVariants({ variant, size }), className)} {...props} />; }

export function IconButton({ label, className, children, ...props }: Omit<ButtonProps, "children"> & { label: string; children: ReactNode }) {
  return <button type="button" aria-label={label} title={label} className={cn("inline-flex size-9 items-center justify-center rounded-sm text-muted transition-colors hover:bg-raised hover:text-ink disabled:pointer-events-none disabled:opacity-45", className)} {...props}>{children}</button>;
}
