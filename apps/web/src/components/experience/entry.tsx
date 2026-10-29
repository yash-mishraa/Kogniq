"use client";

import { useQueryClient } from "@tanstack/react-query";
import { AnimatePresence, LayoutGroup, motion, useReducedMotion } from "framer-motion";
import { type FormEvent, useState } from "react";
import { ApiRequestError, ragApi, type SessionUser } from "@/lib/rag/api";
import { Footline } from "./footer";

type Phase = "arrival" | "access";
type Mode = "login" | "register";

const transition = { duration: 0.46, ease: [0.22, 1, 0.36, 1] as const };

/**
 * The recovered Kogniq entry experience: Arrival, then the editorial Access
 * form. Authentication is wired to the live RAG session API rather than the
 * historical mock provider. Presentation and motion follow the original
 * `experience-flow.tsx` implementation.
 */
export function EntryExperience() {
  const [phase, setPhase] = useState<Phase>("arrival");
  const reduceMotion = useReducedMotion();

  return (
    <LayoutGroup id="kogniq-entry">
      <main className="min-h-dvh overflow-hidden bg-canvas">
        <AnimatePresence mode="sync" initial={false}>
          {phase === "arrival" ? (
            <Arrival
              key="arrival"
              reduceMotion={reduceMotion}
              onEnter={() => setPhase("access")}
            />
          ) : (
            <Access key="access" reduceMotion={reduceMotion} />
          )}
        </AnimatePresence>
      </main>
    </LayoutGroup>
  );
}

function Arrival({
  onEnter,
  reduceMotion,
}: {
  onEnter: () => void;
  reduceMotion: boolean | null;
}) {
  return (
    <motion.section
      key="arrival"
      initial={false}
      exit={reduceMotion ? undefined : { opacity: 0.98 }}
      className="arrival-field relative grid min-h-dvh place-items-center overflow-hidden bg-canvas text-ink"
    >
      <h1 className="sr-only">Kogniq</h1>
      <button
        type="button"
        onClick={onEnter}
        aria-label="Enter Kogniq"
        className="group relative px-8 py-6 text-left outline-none focus-visible:outline-offset-8"
      >
        <motion.span
          layoutId="kogniq-word"
          initial={
            reduceMotion
              ? false
              : { filter: "blur(1.1px)", letterSpacing: "-0.035em", opacity: 0.9 }
          }
          animate={{ filter: "blur(0px)", letterSpacing: "-0.075em", opacity: 1 }}
          transition={{ duration: reduceMotion ? 0 : 1.05, ease: [0.2, 0.75, 0.25, 1] }}
          className="kogniq-word text-[clamp(3.2rem,10vw,7rem)]"
        >
          Kogniq
        </motion.span>
        <span
          aria-hidden
          className="ml-1 inline-block h-[0.82em] w-px translate-y-[0.08em] bg-current align-baseline opacity-70 [animation:locus-idle_2.2s_cubic-bezier(.45,0,.55,1)_infinite]"
        />
      </button>
      <p className="absolute bottom-8 left-1/2 -translate-x-1/2 font-mono text-[10px] uppercase tracking-[0.24em] text-muted">
        Tap to begin
      </p>
    </motion.section>
  );
}

function Access({ reduceMotion }: { reduceMotion: boolean | null }) {
  const queryClient = useQueryClient();
  const [mode, setMode] = useState<Mode>("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [emailFocused, setEmailFocused] = useState(false);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const showPassword = emailFocused || email.length > 0;

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
      className="relative flex min-h-dvh flex-col bg-canvas px-5 py-6 text-ink sm:px-10 sm:py-9"
    >
      <motion.span
        layoutId="kogniq-word"
        transition={transition}
        className="kogniq-word block w-fit text-[clamp(1.9rem,4vw,3.25rem)]"
      >
        Kogniq
      </motion.span>

      <div className="mx-auto flex w-full max-w-6xl flex-1 items-center py-8 sm:py-20">
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

          <div className="mt-12 max-w-md sm:mt-16">
            <label className="group block">
              <span className="sr-only">Email address</span>
              <span
                aria-hidden
                className="mr-3 inline-block h-[1.05em] w-px translate-y-[0.14em] bg-ink/60 [animation:locus-idle_2.2s_cubic-bezier(.45,0,.55,1)_infinite] group-focus-within:bg-ink"
              />
              <input
                type="email"
                name="email"
                autoComplete="email"
                required
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                onFocus={() => setEmailFocused(true)}
                placeholder="email"
                className="w-[calc(100%-1.25rem)] border-b border-transparent bg-transparent py-2 text-[clamp(1.15rem,2vw,1.45rem)] text-ink outline-none placeholder:text-muted focus:border-ink/70 focus-visible:text-ink"
              />
            </label>

            <motion.div
              initial={false}
              animate={{
                height: showPassword ? "auto" : 0,
                opacity: showPassword ? 1 : 0,
                marginTop: showPassword ? 12 : 0,
              }}
              transition={{ duration: reduceMotion ? 0 : 0.2, ease: [0.22, 1, 0.36, 1] }}
              className="overflow-hidden"
            >
              <label className="block">
                <span className="sr-only">Password</span>
                <input
                  type="password"
                  name="password"
                  autoComplete={mode === "login" ? "current-password" : "new-password"}
                  required
                  minLength={mode === "register" ? 8 : undefined}
                  tabIndex={showPassword ? 0 : -1}
                  aria-hidden={!showPassword}
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder={mode === "register" ? "password · 8 characters minimum" : "password"}
                  className="w-full border-b border-transparent bg-transparent py-2 text-[clamp(1.15rem,2vw,1.45rem)] text-ink outline-none placeholder:text-muted focus:border-ink/70 focus-visible:text-ink"
                />
              </label>
            </motion.div>

            <motion.div
              initial={false}
              animate={{
                height: showPassword ? "auto" : 0,
                opacity: showPassword ? 1 : 0,
                marginTop: showPassword ? 22 : 0,
              }}
              transition={{ duration: reduceMotion ? 0 : 0.2, ease: [0.22, 1, 0.36, 1] }}
              className="overflow-hidden"
            >
              <button
                type="submit"
                disabled={pending}
                className="text-[clamp(1rem,1.7vw,1.2rem)] text-ink/75 outline-none transition-colors hover:text-ink focus-visible:text-ink disabled:opacity-50"
              >
                {pending ? "Continue…" : "Continue."}
              </button>
              {error ? (
                <p
                  role="alert"
                  className="mt-4 max-w-sm font-mono text-[11px] leading-5 text-danger"
                >
                  {error}
                </p>
              ) : null}
            </motion.div>
          </div>

          <div className="mt-16 text-[clamp(1rem,1.55vw,1.2rem)] leading-8 text-muted">
            <p>Upload documents.</p>
            <p>Inspect retrieval.</p>
            <p>Answer with sources.</p>
          </div>
        </form>
      </div>

      <div className="flex flex-wrap items-end justify-between gap-4 border-t border-line/60 pt-5">
        <div className="space-y-2">
          <button
            type="button"
            onClick={switchMode}
            className="font-mono text-[10px] uppercase tracking-[0.16em] text-muted underline-offset-4 transition-colors hover:text-ink hover:underline"
          >
            {mode === "login" ? "New here? Create an account." : "Already have an account? Sign in."}
          </button>
          <button
            type="button"
            onClick={() => {
              setEmail("admin@kogniq.ai");
              setPassword("password");
              setMode("login");
              setError(null);
            }}
            className="font-mono text-[10px] text-muted transition-colors hover:text-ink cursor-pointer text-left"
          >
            Demo · admin@kogniq.ai / password
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
