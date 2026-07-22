"use client";

import { AnimatePresence, LayoutGroup, motion, useReducedMotion } from "framer-motion";
import { useForm } from "react-hook-form";
import { type FocusEvent, type KeyboardEvent, type ReactNode, useState } from "react";
import { Footline } from "./footer";
import { Locus, type LocusSuggestion } from "./locus";

type Phase = "arrival" | "access" | "intention" | "workspace";
type EnvironmentId = "documents" | "graph" | "search" | "notes" | "study" | "flashcards" | "quiz" | "analytics";
type AccessValues = { email: string; password: string };

const environments: { id: EnvironmentId; title: string; prompt: string; suggestions: LocusSuggestion[] }[] = [
  { id: "documents", title: "Documents", prompt: "Import knowledge…", suggestions: [{ label: "Architecture notes", detail: "recent material" }, { label: "Bring in a source", detail: "start with a document" }, { label: "Open retrieval design", detail: "knowledge base" }] },
  { id: "graph", title: "Knowledge Graph", prompt: "Explore connections…", suggestions: [{ label: "Authentication", detail: "24 relationships" }, { label: "Open a concept", detail: "knowledge graph" }, { label: "Trace a connection", detail: "relationship path" }] },
  { id: "search", title: "Search", prompt: "Find meaning…", suggestions: [{ label: "Retrieval strategy", detail: "12 supporting passages" }, { label: "Find a concept", detail: "across knowledge" }, { label: "Compare sources", detail: "evidence first" }] },
  { id: "notes", title: "Studio", prompt: "Develop a thought…", suggestions: [{ label: "Working note", detail: "continue writing" }, { label: "Start a synthesis", detail: "from connected material" }, { label: "Capture an idea", detail: "private draft" }] },
  { id: "study", title: "Study", prompt: "Continue learning…", suggestions: [{ label: "Retrieval foundations", detail: "next material" }, { label: "Resume session", detail: "18 minutes remaining" }, { label: "Review key concepts", detail: "spaced practice" }] },
  { id: "flashcards", title: "Flashcards", prompt: "Generate recall…", suggestions: [{ label: "Retrieval foundations", detail: "12 new cards" }, { label: "Review due cards", detail: "6 ready" }, { label: "Build a recall set", detail: "from a source" }] },
  { id: "quiz", title: "Quiz", prompt: "Test understanding…", suggestions: [{ label: "Retrieval foundations", detail: "8 questions" }, { label: "Build a short quiz", detail: "from current knowledge" }, { label: "Review an attempt", detail: "evidence included" }] },
  { id: "analytics", title: "Analytics", prompt: "Inspect progress…", suggestions: [{ label: "Learning continuity", detail: "last 30 days" }, { label: "Inspect recall", detail: "structured measures" }, { label: "Review activity", detail: "knowledge work" }] },
];

const transition = { duration: 0.46, ease: [0.22, 1, 0.36, 1] as const };

export function ExperienceFlow() {
  const [phase, setPhase] = useState<Phase>("arrival");
  const [activeIndex, setActiveIndex] = useState(0);
  const [chosen, setChosen] = useState<EnvironmentId>("documents");
  const reduceMotion = useReducedMotion();
  const choose = (index: number) => { setActiveIndex(index); setChosen(environments[index].id); setPhase("workspace"); };

  return <LayoutGroup id="kogniq-flow"><main className="min-h-dvh overflow-hidden bg-canvas"><AnimatePresence mode="sync" initial={false}>
    {phase === "arrival" && <Arrival onEnter={() => setPhase("access")} reduceMotion={reduceMotion} />}
    {phase === "access" && <Access onContinue={() => setPhase("intention")} reduceMotion={reduceMotion} />}
    {phase === "intention" && <Intention activeIndex={activeIndex} onActiveChange={setActiveIndex} onSelect={choose} reduceMotion={reduceMotion} />}
    {phase === "workspace" && <Workspace environment={environments.find((item) => item.id === chosen)!} onLeave={() => setPhase("intention")} reduceMotion={reduceMotion} />}
  </AnimatePresence></main></LayoutGroup>;
}

function Arrival({ onEnter, reduceMotion }: { onEnter: () => void; reduceMotion: boolean | null }) {
  return <motion.section key="arrival" initial={false} exit={reduceMotion ? undefined : { opacity: 0.98 }} className="arrival-field relative grid min-h-dvh place-items-center overflow-hidden bg-[hsl(var(--night))] text-[hsl(var(--night-ink))]">
    <button onClick={onEnter} className="group relative px-8 py-6 text-left focus-visible:outline-offset-8" aria-label="Enter Kogniq">
      <motion.span layoutId="kogniq-word" initial={reduceMotion ? false : { filter: "blur(1.1px)", letterSpacing: "-0.035em", opacity: 0.9 }} animate={{ filter: "blur(0px)", letterSpacing: "-0.075em", opacity: 1 }} transition={{ duration: reduceMotion ? 0 : 1.05, ease: [0.2, 0.75, 0.25, 1] }} className="kogniq-word text-[clamp(3.2rem,10vw,7rem)]">Kogniq</motion.span><span aria-hidden className="ml-1 inline-block h-[.82em] w-px translate-y-[.08em] bg-current align-baseline opacity-70 [animation:locus-idle_2.2s_cubic-bezier(.45,0,.55,1)_infinite]" />
    </button>
  </motion.section>;
}

function Access({ onContinue, reduceMotion }: { onContinue: () => void; reduceMotion: boolean | null }) {
  const { handleSubmit, register, watch } = useForm<AccessValues>({ defaultValues: { email: "", password: "" } });
  const [emailFocused, setEmailFocused] = useState(false);
  const email = watch("email");
  const showPassword = emailFocused || email.length > 0;
  const focusEmail = (event: FocusEvent<HTMLInputElement>) => { setEmailFocused(true); };
  return <motion.section key="access" initial={false} exit={reduceMotion ? undefined : { opacity: 0.99 }} transition={transition} className="relative flex min-h-dvh flex-col bg-[hsl(var(--night))] px-6 py-7 text-[hsl(var(--night-ink))] sm:px-10 sm:py-9">
    <motion.div layoutId="kogniq-word" transition={transition} className="kogniq-word text-[clamp(1.9rem,4vw,3.25rem)]">Kogniq</motion.div>
    <div className="mx-auto flex w-full max-w-6xl flex-1 items-center py-16 sm:py-20">
      <form onSubmit={handleSubmit(onContinue)} className="w-full max-w-2xl tracking-[-0.035em]" aria-label="Begin a Kogniq session">
        <p className="text-[clamp(2rem,4.5vw,4.8rem)] font-medium leading-[.98]">Build knowledge.</p><p className="mt-3 text-[clamp(1.25rem,2.3vw,2rem)] text-[hsl(var(--night-ink)/.82)]">Connect ideas.</p><p className="mt-1 text-[clamp(1.25rem,2.3vw,2rem)] text-[hsl(var(--night-ink)/.82)]">Understand concepts.</p>
        <div className="mt-14 max-w-md space-y-0 sm:mt-20"><label className="group block"><span className="sr-only">Email address</span><span aria-hidden className="mr-3 inline-block h-[1.05em] w-px translate-y-[.14em] bg-[hsl(var(--night-ink)/.64)] [animation:locus-idle_2.2s_cubic-bezier(.45,0,.55,1)_infinite] group-focus-within:bg-[hsl(var(--night-ink))]" /><input type="email" autoComplete="email" required placeholder="email" className="w-[calc(100%-1.25rem)] border-b border-transparent bg-transparent py-2 text-[clamp(1.15rem,2vw,1.45rem)] outline-none placeholder:text-[hsl(var(--night-muted))] focus:border-[hsl(var(--night-ink)/.7)] focus-visible:text-white" {...register("email")} onFocus={focusEmail} /></label>
          <motion.div initial={false} animate={{ height: showPassword ? "auto" : 0, opacity: showPassword ? 1 : 0, marginTop: showPassword ? 12 : 0 }} transition={{ duration: reduceMotion ? 0 : 0.2, ease: [0.22, 1, .36, 1] }} className="overflow-hidden"><label className="block"><span className="sr-only">Password</span><input type="password" autoComplete="current-password" required tabIndex={showPassword ? 0 : -1} aria-hidden={!showPassword} placeholder="password" className="w-full border-b border-transparent bg-transparent py-2 text-[clamp(1.15rem,2vw,1.45rem)] outline-none placeholder:text-[hsl(var(--night-muted))] focus:border-[hsl(var(--night-ink)/.7)] focus-visible:text-white" {...register("password")} /></label></motion.div>
          <motion.div initial={false} animate={{ height: showPassword ? "auto" : 0, opacity: showPassword ? 1 : 0, marginTop: showPassword ? 22 : 0 }} transition={{ duration: reduceMotion ? 0 : 0.2, ease: [0.22, 1, .36, 1] }} className="overflow-hidden"><button type="submit" className="text-[clamp(1rem,1.7vw,1.2rem)] text-[hsl(var(--night-ink)/.75)] outline-none transition-colors hover:text-white focus-visible:text-white">Continue.</button></motion.div>
        </div>
        <div className="mt-20 text-[clamp(1rem,1.55vw,1.2rem)] leading-8 text-[hsl(var(--night-muted))]"><p>Upload documents.</p><p>Generate learning.</p><p>Search meaning.</p></div>
      </form>
    </div>
    <Footline night />
  </motion.section>;
}

function Intention({ activeIndex, onActiveChange, onSelect, reduceMotion }: { activeIndex: number; onActiveChange: (index: number) => void; onSelect: (index: number) => void; reduceMotion: boolean | null }) {
  const move = (amount: number) => onActiveChange((activeIndex + amount + environments.length) % environments.length);
  const keyDown = (event: KeyboardEvent<HTMLDivElement>) => { if (event.key === "ArrowDown" || event.key.toLowerCase() === "j") { event.preventDefault(); move(1); } if (event.key === "ArrowUp" || event.key.toLowerCase() === "k") { event.preventDefault(); move(-1); } if (event.key === "Enter") { event.preventDefault(); onSelect(activeIndex); } };
  const adjust = (index: number) => { if (index === activeIndex) onSelect(index); else onActiveChange(index); };
  return <motion.section key="intention" initial={reduceMotion ? false : { opacity: 0.96 }} animate={{ opacity: 1 }} transition={transition} className="flex min-h-dvh flex-col bg-[hsl(var(--night))] px-6 py-7 text-[hsl(var(--night-ink))] sm:px-10 sm:py-9"><div className="flex flex-1 items-center justify-center"><div role="listbox" aria-label="What would you like to work on today?" tabIndex={0} onKeyDown={keyDown} onWheel={(event) => { event.preventDefault(); move(event.deltaY > 0 ? 1 : -1); }} className="w-full max-w-xl outline-none"><p className="sr-only" aria-live="polite">{environments[activeIndex].title} selected. Press Enter to continue.</p><div className="relative h-[32rem] overflow-hidden">{environments.map((item, index) => { let offset = index - activeIndex; if (offset > environments.length / 2) offset -= environments.length; if (offset < -environments.length / 2) offset += environments.length; const depth = Math.min(Math.abs(offset), 4); return <motion.button key={item.id} role="option" aria-selected={index === activeIndex} onClick={() => adjust(index)} animate={{ y: offset * 62 - 28, opacity: [1, .54, .24, .09, 0][depth], scale: [1, .92, .82, .74, .7][depth], filter: reduceMotion ? "none" : `blur(${[0, .35, 1, 1.7, 2.4][depth]}px)` }} transition={{ duration: reduceMotion ? 0 : 0.26, ease: [0.22, 1, .36, 1] }} className="absolute left-0 top-1/2 h-14 w-full origin-center text-center text-[clamp(1.35rem,3.5vw,3.25rem)] font-medium tracking-[-.055em] outline-none focus-visible:text-accent">{index === activeIndex && <span aria-hidden className="absolute -left-3 top-1/2 h-[.82em] w-px -translate-y-1/2 bg-current" />}{item.title}</motion.button>; })}</div></div></div><Footline night /></motion.section>;
}

function Workspace({ environment, onLeave, reduceMotion }: { environment: (typeof environments)[number]; onLeave: () => void; reduceMotion: boolean | null }) {
  const [context, setContext] = useState<string | null>(null);
  return <motion.section key="workspace" initial={reduceMotion ? false : { opacity: 0.97 }} animate={{ opacity: 1 }} transition={transition} className="flex min-h-dvh flex-col bg-canvas px-6 py-7 sm:px-10 sm:py-9"><button onClick={onLeave} aria-label="Choose another environment" className="w-fit text-left text-[clamp(1.45rem,2.5vw,2.3rem)] font-medium tracking-[-.05em] text-ink outline-none hover:text-accent focus-visible:text-accent">{context ? `${environment.title} / ${context}` : environment.title}</button><div className="flex flex-1 flex-col py-14"><Locus prompt={context ? `Explore ${context.toLowerCase()}…` : environment.prompt} suggestions={environment.suggestions} onSelect={(item) => setContext(item.label)} className="mx-auto w-full max-w-6xl" /><AnimatePresence mode="wait">{context && <motion.div key={`${environment.id}-${context}`} initial={reduceMotion ? false : { opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={reduceMotion ? undefined : { opacity: 0, y: -4 }} transition={transition} className="mx-auto mt-14 w-full max-w-6xl"><WorkspaceGeometry environment={environment.id} context={context} /></motion.div>}</AnimatePresence></div><Footline /></motion.section>;
}

function WorkspaceGeometry({ environment, context }: { environment: EnvironmentId; context: string }) {
  const contents: Record<EnvironmentId, ReactNode> = {
    documents: <article className="mx-auto max-w-[48rem]"><p className="font-mono text-[10px] uppercase tracking-[.12em] text-muted">source-aware reading</p><h2 className="mt-5 text-[clamp(1.8rem,3vw,3rem)] font-medium tracking-[-.055em]">{context}</h2><div className="mt-10 grid gap-10 md:grid-cols-[1fr_9rem]"><div className="space-y-6 text-[1.08rem] leading-8 text-ink"><p>Knowledge becomes useful when its structure remains visible. Read with enough space to think, then return to the source without losing the thread.</p><p>Related material stays at the margin, present but never competing with the line in front of you.</p></div><aside className="border-l pl-4 font-mono text-[10px] leading-5 text-muted">SOURCE 01<br />ARCHITECTURE<br /><br />RELATED<br />RETRIEVAL</aside></div></article>,
    graph: <div className="relative min-h-[26rem] overflow-hidden" role="img" aria-label={`Relationship view for ${context}`}><svg viewBox="0 0 1000 420" className="h-full min-h-[26rem] w-full" fill="none"><path d="M120 250 C280 90 410 360 560 190 S780 110 900 240" stroke="currentColor" className="text-line" strokeWidth="1" /><path d="M120 250 C330 320 460 90 720 290" stroke="currentColor" className="text-line" strokeWidth="1" /><circle cx="120" cy="250" r="7" className="fill-accent" /><circle cx="370" cy="178" r="5" className="fill-ink" /><circle cx="560" cy="190" r="9" className="fill-accent" /><circle cx="720" cy="290" r="5" className="fill-ink" /><circle cx="900" cy="240" r="6" className="fill-ink" /></svg><p className="absolute left-[11%] top-[64%] text-sm">{context}</p><p className="absolute left-[54%] top-[38%] text-sm text-muted">related concept</p></div>,
    search: <section className="max-w-4xl"><p className="font-mono text-[10px] uppercase tracking-[.12em] text-muted">12 supporting passages</p><div className="mt-7 divide-y"><Evidence title={context} source="Architecture notes" text="The retrieved material makes the relationship explicit, preserving the source and the reason it is relevant." /><Evidence title="Related evidence" source="System overview" text="A result is not a destination. It is a claim with the material needed to inspect it." /><Evidence title="Connected context" source="Retrieval design" text="Meaning appears in the relation between passages, terms, and the questions brought to them." /></div></section>,
    notes: <article className="mx-auto max-w-[42rem]"><p className="font-mono text-[10px] text-muted">PRIVATE DRAFT</p><h2 className="mt-8 text-[clamp(2rem,4vw,4rem)] font-medium leading-[1.02] tracking-[-.06em]">{context}</h2><p className="mt-10 text-xl leading-9 text-muted">Begin with the idea. Connected knowledge will make itself available when it is needed.</p></article>,
    study: <article className="mx-auto max-w-xl text-center"><p className="font-mono text-[10px] uppercase tracking-[.12em] text-muted">continue learning</p><h2 className="mt-8 text-[clamp(2.2rem,4.5vw,4.7rem)] font-medium leading-[1.03] tracking-[-.065em]">{context}</h2><p className="mx-auto mt-8 max-w-md text-lg leading-8 text-muted">One concept, enough space, and a clear next step.</p><p className="mt-14 text-sm text-ink">Begin when you are ready.</p></article>,
    flashcards: <article className="mx-auto max-w-2xl py-8"><p className="font-mono text-[10px] uppercase tracking-[.12em] text-muted">active recall</p><p className="mt-12 text-[clamp(2rem,4.5vw,4.5rem)] font-medium leading-[1.05] tracking-[-.06em]">What makes a retrieved passage useful?</p><p className="mt-16 border-t pt-5 text-sm text-muted">Reveal the reasoning when you are ready.</p></article>,
    quiz: <article className="mx-auto max-w-2xl"><p className="font-mono text-[10px] uppercase tracking-[.12em] text-muted">question 01</p><h2 className="mt-8 text-[clamp(1.9rem,3.6vw,3.6rem)] font-medium leading-[1.08] tracking-[-.055em]">{context}</h2><div className="mt-12 space-y-0"><Answer label="A" text="It contains the most text." /><Answer label="B" text="It preserves evidence for the current question." /><Answer label="C" text="It is the newest available source." /></div></article>,
    analytics: <section className="max-w-4xl"><div className="flex items-end justify-between border-b pb-4"><div><p className="font-mono text-[10px] uppercase tracking-[.12em] text-muted">last 30 days</p><h2 className="mt-3 text-[clamp(1.8rem,3vw,3rem)] font-medium tracking-[-.055em]">{context}</h2></div><p className="font-mono text-xs text-muted">quietly improving</p></div><table className="mt-8 w-full text-left"><tbody><Metric name="Learning sessions" value="14" detail="deliberate returns" /><Metric name="Recall reviewed" value="86%" detail="evidence-based" /><Metric name="Knowledge connected" value="42" detail="relationships explored" /></tbody></table></section>,
  };
  return contents[environment];
}

function Evidence({ title, source, text }: { title: string; source: string; text: string }) { return <article className="py-5"><div className="flex flex-wrap items-baseline justify-between gap-2"><h3 className="text-base font-medium">{title}</h3><span className="font-mono text-[10px] text-muted">{source}</span></div><p className="mt-2 max-w-2xl text-sm leading-6 text-muted">{text}</p></article>; }
function Answer({ label, text }: { label: string; text: string }) { return <button className="flex w-full gap-5 border-b py-4 text-left text-base transition-colors hover:text-accent focus-visible:text-accent"><span className="font-mono text-xs text-muted">{label}</span>{text}</button>; }
function Metric({ name, value, detail }: { name: string; value: string; detail: string }) { return <tr className="border-b"><th scope="row" className="py-5 text-left text-sm font-normal">{name}</th><td className="py-5 text-right text-2xl font-medium tracking-[-.04em]">{value}</td><td className="hidden py-5 pl-6 text-right font-mono text-[10px] text-muted sm:table-cell">{detail}</td></tr>; }
