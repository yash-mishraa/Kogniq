"use client";

import { useQueryClient } from "@tanstack/react-query";
import { LayoutGroup, motion, useReducedMotion } from "framer-motion";
import { type FormEvent, useState } from "react";
import { ApiRequestError, ragApi, type SessionUser } from "@/lib/rag/api";
import { Footline } from "./footer";

type Mode = "login" | "register";

const transition = { duration: 0.35, ease: [0.22, 1, 0.36, 1] as const };

/**
 * Editorial entry experience for Kogniq: direct access to sign-in or
 * account registration, optimized for desktop and mobile touch devices.
 */
export function EntryExperience() {
  const reduceMotion = useReducedMotion();

  return (
    <LayoutGroup id="kogniq-entry">
      <main className="min-h-dvh overflow-x-hidden bg-canvas">
        <Access reduceMotion={reduceMotion} />
      </main>
    </LayoutGroup>
  );
}

function Access({ reduceMotion }: { reduceMotion: boolean | null }) {
  const queryClient = useQueryClient();
  const [mode, setMode] = useState<Mode>("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (pending) return;
    setPending(true);
    setError(null);
    try {
      const form = event.currentTarget;
      const formData = new FormData(form);
      const formEmail = (formData.get("email") as string) || email;
      const formPassword = (formData.get("password") as string) || password;
      const trimmed = formEmail.trim().toLowerCase();
      const user =
        mode === "register"
          ? await ragApi.register(trimmed, formPassword, trimmed.split("@")[0] || "Researcher")
          : await ragApi.login(trimmed, formPassword);
      queryClient.setQueryData<SessionUser>(["session"], user);
      queryClient.removeQueries({
        predicate: (query) => query.queryKey[0] !== "session",
      });
    } catch (caught) {
      setError(authMessage(caught));
      setPending(false);
    }
  };

  const switchMode = () => {
    setMode((current) => (current === "login" ? "register" : "login"));
    setError(null);
  };

  return (
    <motion.section
      key="access"
      initial={false}
      exit={reduceMotion ? undefined : { opacity: 0.99 }}
      transition={transition}
      className="relative flex min-h-dvh flex-col bg-canvas px-5 py-6 text-ink sm:px-10 sm:py-9 select-none sm:select-auto"
    >
      <span className="kogniq-word block w-fit text-[clamp(1.9rem,4vw,3.25rem)] select-none">
        Kogniq
      </span>

      <div className="mx-auto flex w-full max-w-6xl flex-1 items-center py-8 sm:py-16">
        <form
          onSubmit={submit}
          className="w-full max-w-2xl tracking-[-0.035em]"
          aria-label={mode === "login" ? "Sign in to Kogniq" : "Create a Kogniq account"}
        >
          <h1 className="text-[clamp(2rem,4.5vw,4.8rem)] font-medium leading-[0.98]">
            Build knowledge.
          </h1>
          <p className="mt-3 text-[clamp(1.25rem,2.3vw,2rem)] text-ink/80">Connect ideas.</p>
          <p className="mt-1 text-[clamp(1.25rem,2.3vw,2rem)] text-ink/80">
            Understand concepts.
          </p>
          <p className="mt-6 font-mono text-[10px] uppercase tracking-[0.18em] text-muted">
            {mode === "login"
              ? "Retrieval-grounded research console"
              : "New account · retrieval-grounded research console"}
          </p>

          <div className="mt-10 max-w-md space-y-6 sm:mt-14">
            <label className="group block">
              <span className="sr-only">Email address</span>
              <div className="flex items-center border-b border-line/60 focus-within:border-ink transition-colors pb-1">
                <span
                  aria-hidden
                  className="mr-3 inline-block h-[1.05em] w-px translate-y-[0.05em] bg-ink/60 [animation:locus-idle_2.2s_cubic-bezier(.45,0,.55,1)_infinite] group-focus-within:bg-ink shrink-0"
                />
                <input
                  type="email"
                  name="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  placeholder="email"
                  className="w-full bg-transparent py-2.5 text-[clamp(1.15rem,2vw,1.45rem)] text-ink outline-none placeholder:text-muted focus-visible:text-ink select-text"
                />
              </div>
            </label>

            <label className="group block">
              <span className="sr-only">Password</span>
              <div className="flex items-center border-b border-line/60 focus-within:border-ink transition-colors pb-1">
                <span
                  aria-hidden
                  className="mr-3 inline-block h-[1.05em] w-px translate-y-[0.05em] bg-ink/60 [animation:locus-idle_2.2s_cubic-bezier(.45,0,.55,1)_infinite] group-focus-within:bg-ink shrink-0"
                />
                <input
                  type="password"
                  name="password"
                  autoComplete={mode === "login" ? "current-password" : "new-password"}
                  required
                  minLength={mode === "register" ? 8 : undefined}
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder={mode === "register" ? "password · 8 characters minimum" : "password"}
                  className="w-full bg-transparent py-2.5 text-[clamp(1.15rem,2vw,1.45rem)] text-ink outline-none placeholder:text-muted focus-visible:text-ink select-text"
                />
              </div>
            </label>

            <div className="pt-2">
              <button
                type="submit"
                disabled={pending}
                className="inline-flex min-h-[44px] items-center text-[clamp(1rem,1.7vw,1.2rem)] font-medium text-ink transition-colors hover:text-ink/80 focus-visible:outline-none disabled:opacity-50 cursor-pointer"
              >
                {pending ? "Signing in…" : mode === "register" ? "Create account →" : "Continue →"}
              </button>
              {error ? (
                <p
                  role="alert"
                  className="mt-3 max-w-sm font-mono text-[11px] leading-5 text-danger"
                >
                  {error}
                </p>
              ) : null}
            </div>
          </div>

          <div className="mt-14 text-[clamp(1rem,1.55vw,1.2rem)] leading-8 text-muted">
            <p>Upload documents.</p>
            <p>Inspect retrieval.</p>
            <p>Answer with sources.</p>
          </div>
        </form>
      </div>

      <div className="flex flex-wrap items-end justify-between gap-4 border-t border-line/60 pt-5">
        <div>
          <button
            type="button"
            onClick={switchMode}
            className="inline-flex min-h-[44px] items-center font-mono text-[11px] uppercase tracking-[0.16em] text-muted underline-offset-4 transition-colors hover:text-ink hover:underline cursor-pointer"
          >
            {mode === "login" ? "New here? Create an account." : "Already have an account? Sign in."}
          </button>
        </div>
        <Footline />
      </div>
    </motion.section>
  );
}

function authMessage(error: unknown): string {
  if (error instanceof ApiRequestError) {
    if (error.status === 401) {
      if (error.code === "user_not_found") {
        return "No account found with this email. Click 'Create an account' below to sign up.";
      }
      return "Incorrect email or password. Please try again.";
    }
    if (error.status === 400 && error.code === "invalid_credentials") {
      return "Incorrect password. Please try again.";
    }
    if (error.status === 409) return "An account with that email already exists. Click 'Sign in' below.";
    if (error.status === 422) {
      return "Enter a valid email and a password of at least 8 characters.";
    }
    return error.message;
  }
  return error instanceof Error ? error.message : "Could not reach Kogniq.";
}
