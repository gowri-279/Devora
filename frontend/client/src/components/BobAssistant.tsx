// Signal Garden style reminder: Bob is the only expressive, stateful glow in the UI. Keep the companion friendly, precise, and visually connected to the dark mineral workspace.
import { useEffect, useMemo, useState } from "react";
import { Check, ChevronDown, Minimize2, Send, Sparkles } from "lucide-react";

type BobState = "idle" | "listening" | "thinking" | "responding" | "low" | "success";

type BobMessage = {
  id: number;
  role: "bob" | "user";
  text: string;
  confidence?: "HIGH" | "MEDIUM" | "LOW";
  source?: string;
  hint?: string;
};

const mockBobService = async (question: string, context: string, admin = false): Promise<BobMessage> => {
  await new Promise((resolve) => setTimeout(resolve, 700));
  const lower = question.toLowerCase();
  if (context.startsWith("Knowledge gap context:")) {
    const uploadedContext = context.replace("Knowledge gap context:", "").trim();
    return { id: Date.now(), role: "bob", text: `For “${question}”, the newly uploaded context (${uploadedContext}) provides the missing project-specific guidance. I’ll use it as the source of truth while we continue refining the implementation together.`, confidence: "HIGH", source: `${uploadedContext} → Knowledge gap resolution` };
  }
  if (admin) {
    if (lower.includes("status") || lower.includes("member") || lower.includes("maya") || lower.includes("sofia") || lower.includes("aarav") || lower.includes("noah")) return { id: Date.now(), role: "bob", text: "Maya is at 40% with Architecture next in her path. Sofia needs focus in Security, while Aarav is progressing steadily. Open Member status for the full module-by-module view.", confidence: "HIGH", source: "team-status.json → Member status" };
    if (lower.includes("next") || lower.includes("plan") || lower.includes("recommend")) return { id: Date.now(), role: "bob", text: "The next useful move is to close the open knowledge gaps, then prioritize Security & Data for anyone below the confidence threshold. I can also summarize a specific member’s route.", confidence: "HIGH", source: "team-plan.json → Next best action" };
    return { id: Date.now(), role: "bob", text: "I can summarize a member’s status, surface open knowledge gaps, or suggest the next best move in the team plan.", confidence: "MEDIUM", source: "team-overview.md → Admin guidance", hint: "Try asking: Which member needs attention next?" };
  }
  if (lower.includes("setup") || lower.includes("install")) {
    return { id: Date.now(), role: "bob", text: "Start with the Local Setup module: clone the repository, install dependencies with pnpm, then copy the example environment file. The module walks through the exact commands for this project.", confidence: "HIGH", source: "local-setup.md → Getting started" };
  }
  if (lower.includes("architecture") || lower.includes("component")) {
    return { id: Date.now(), role: "bob", text: "The web client is split around routes, shared UI primitives, and service boundaries. Read the Architecture module next; it maps the request flow from the page into the knowledge engine.", confidence: "HIGH", source: "architecture.md → Request flow" };
  }
  if (lower.includes("module")) {
    return { id: Date.now(), role: "bob", text: `This screen is currently focused on ${context}. The fastest route is to read the overview, capture the vocabulary, and then use the checkpoint question to test recall.`, confidence: "MEDIUM", source: "onboarding-path.json → Current module" };
  }
  return { id: Date.now(), role: "bob", text: "I found a useful starting point, but not enough grounded context to be fully certain. Try asking about setup, architecture, APIs, or the current module.", confidence: "LOW", source: "Knowledge Engine → Retrieved context", hint: "Try using the project vocabulary from the module title in your question." };
};

export type BobReviewHandoff = { id: string; question: string; uploadedContext: string };

interface BobAssistantProps { context?: string; quizFeedback?: "idle" | "wrong" | "correct"; onStateChange?: (state: BobState) => void; admin?: boolean; reviewHandoff?: BobReviewHandoff | null; }

export default function BobAssistant({ context = "Project Overview", quizFeedback = "idle", onStateChange, admin = false, reviewHandoff = null }: BobAssistantProps) {
  const [open, setOpen] = useState(false);
  const [state, setState] = useState<BobState>("idle");
  const [input, setInput] = useState("");
  const [quizHintShown, setQuizHintShown] = useState(false);
  const [showGreeting, setShowGreeting] = useState(true);
  const [feedbackVisible, setFeedbackVisible] = useState(false);
  const [reviewContext, setReviewContext] = useState<string | null>(null);
  const [messages, setMessages] = useState<BobMessage[]>([
    { id: 1, role: "bob", text: admin ? "Hi Taylor, want a team runthrough?" : "Hi Maya — ready to start onboarding?", confidence: "HIGH", source: admin ? "team-overview.md → Member status" : "project-overview.md → About this project" },
  ]);

  useEffect(() => { onStateChange?.(state); }, [state, onStateChange]);
  useEffect(() => {
    const timer = window.setTimeout(() => setShowGreeting(false), 4200);
    return () => window.clearTimeout(timer);
  }, []);
  useEffect(() => {
    if (!reviewHandoff) return;
    let active = true;
    setOpen(true);
    setInput("");
    setReviewContext(`Knowledge gap · ${reviewHandoff.uploadedContext}`);
    setState("thinking");
    setMessages((current) => [...current, { id: Date.now(), role: "user", text: reviewHandoff.question }]);
    mockBobService(reviewHandoff.question, `Knowledge gap context: ${reviewHandoff.uploadedContext}`, admin).then((response) => {
      if (!active) return;
      setMessages((current) => [...current, response]);
      setState(response.confidence === "LOW" ? "low" : "responding");
      window.setTimeout(() => setState("idle"), 1200);
    });
    return () => { active = false; };
  }, [reviewHandoff]);
  useEffect(() => {
    if (quizFeedback === "wrong") {
      setState("low"); setFeedbackVisible(true); setQuizHintShown(false);
      setMessages((current) => [...current, { id: Date.now(), role: "bob", text: "Oops! Want a hint?", confidence: "LOW", source: "Local Setup checkpoint → quiz feedback" }]);
    }
    if (quizFeedback === "correct") {
      setState("success"); setFeedbackVisible(true); setQuizHintShown(false);
      setMessages((current) => [...current, { id: Date.now(), role: "bob", text: "Good job! Want me to elucidate?", confidence: "HIGH", source: "Local Setup checkpoint → quiz passed" }]);
    }
    const resetTimer = quizFeedback === "wrong" || quizFeedback === "correct" ? window.setTimeout(() => { setState("idle"); setFeedbackVisible(false); }, 2500) : undefined;
    return () => { if (resetTimer) window.clearTimeout(resetTimer); };
  }, [quizFeedback]);
  const statusLabel = useMemo(() => ({ idle: "ready", listening: "listening", thinking: "thinking", responding: "responding", low: "knowledge gap", success: "nice work" }[state]), [state]);

  const toggleBob = () => {
    const nextOpen = !open;
    setOpen(nextOpen);
    if (nextOpen && quizFeedback === "wrong" && !quizHintShown) {
      setMessages((current) => [...current, { id: Date.now(), role: "bob", text: "Here’s a nudge: look for the package manager named in the terminal snippet above. I’ll help with the next question too.", confidence: "HIGH", source: "Local Setup checkpoint → contextual hint" }]);
      setQuizHintShown(true);
    }
  };

  const send = async (value = input) => {
    const question = value.trim();
    if (!question || state === "thinking") return;
    setMessages((current) => [...current, { id: Date.now(), role: "user", text: question }]);
    setInput(""); setState("thinking");
    const response = await mockBobService(question, reviewContext ?? context, admin);
    setMessages((current) => [...current, response]);
    setState(response.confidence === "LOW" ? "low" : "responding");
    window.setTimeout(() => setState("idle"), 1200);
  };

  return <>
    {open && <section className="bob-panel" aria-label="Bob AI assistant">
      <div className="bob-panel-head">
        <div className="bob-identity"><div className="bob-mini-face"><img src="/bob-robot-transparent.png" alt="Bob" /></div><div><strong>Bob</strong><small>Devora assistant · {statusLabel}</small></div></div>
        <button className="icon-btn" onClick={() => setOpen(false)} aria-label="Minimize Bob"><Minimize2 size={16} /></button>
      </div>
      <div className="bob-context"><Sparkles size={14} /> Grounded in <b>{reviewContext ?? context}</b></div>
      <div className="bob-messages">
        {messages.map((message) => <div key={message.id} className={`bob-message ${message.role}`}>
          <p>{message.text}</p>
          {message.confidence && <div className={`confidence ${message.confidence.toLowerCase()}`}><span>{message.confidence === "HIGH" ? <Check size={11} /> : "~"}</span> {message.confidence} confidence <i>{message.source}</i></div>}
          {message.hint && <button className="hint-link" onClick={() => send(message.hint)}>Show a hint <ChevronDown size={13} /></button>}
        </div>)}
        {state === "thinking" && <div className="bob-message bob thinking-dots"><span /><span /><span /></div>}
      </div>
      <div className="bob-suggestions">{admin ? <><button onClick={() => send("Summarize a member status")}>Summarize member status</button><button onClick={() => send("What should we do next in the plan?")}>Next best move</button><button onClick={() => send("Which member needs attention next?")}>Who needs attention?</button></> : <><button onClick={() => send("How do I set this project up?")}>How do I set this up?</button><button onClick={() => send("What does this module do?")}>Explain this module</button></>}</div>
      <form className="bob-composer" onSubmit={(event) => { event.preventDefault(); send(); }}><input value={input} onChange={(event) => { setInput(event.target.value); setState(event.target.value ? "listening" : "idle"); }} placeholder="Ask about the project..." aria-label="Ask Bob a question" /><button type="submit" aria-label="Send question"><Send size={16} /></button></form>
    </section>}
    <button className={`bob-orb ${state} ${open ? "is-open" : ""}`} onClick={toggleBob} aria-label={open ? "Minimize Bob" : "Open Bob assistant"}>
      <div className="bob-orb-core"><span /><span /></div><div className="bob-orb-ring" />
      {(!open || feedbackVisible) && ((showGreeting && state === "idle" && !feedbackVisible) || state !== "idle" || feedbackVisible) && <span className="bob-tooltip">{feedbackVisible ? state === "low" ? "Oops! Want a hint?" : "Good job! Want me to elucidate?" : state === "idle" ? admin ? "Hi Taylor, want a team runthrough?" : "Hey Maya — ready to start onboarding?" : statusLabel}</span>}
    </button>
  </>;
}
