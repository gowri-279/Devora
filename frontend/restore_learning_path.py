from pathlib import Path
import re

path = Path('/home/ubuntu/devora-frontend/client/src/pages/Home.tsx')
text = path.read_text()
text = text.replace('<LearningPath onAssessmentSubmit={submitAssessment}', '<LearningPath onAssessment={() => setView("twin")}')
pattern = r'function LearningPath\([\s\S]*?\n}\n\nfunction AssessmentPanel'
replacement = '''function LearningPath({ onAssessment, modulePlan, selectedModule, setSelectedModule, quizPassed, setQuizPassed, completedModules, setCompletedModules, quizAnswer, setQuizAnswer, showHint, setShowHint, onBobFeedback }: { onAssessment: () => void; modulePlan: ReturnType<typeof personalizeModules>; selectedModule: number; setSelectedModule: (value: number) => void; quizPassed: boolean; setQuizPassed: (value: boolean) => void; completedModules: number[]; setCompletedModules: React.Dispatch<React.SetStateAction<number[]>>; quizAnswer: string | null; setQuizAnswer: (value: string | null) => void; showHint: boolean; setShowHint: (value: boolean) => void; onBobFeedback: (value: "idle" | "wrong" | "correct") => void }) {
  const [started, setStarted] = useState(false);
  const [activeQuestion, setActiveQuestion] = useState(0);
  const [answers, setAnswers] = useState<Record<number, string | null>>({});
  const [notes, setNotes] = useState("");
  const mod = modulePlan[selectedModule] ?? modulePlan[0];
  const questions = [
    { prompt: "Which command installs the project dependencies?", options: ["npm start", "pnpm install", "git pull", "node setup.js"], correct: "pnpm install", explanation: "pnpm install keeps the dependency graph reproducible across the team." },
    { prompt: "Where should local environment values live?", options: ["README.md", ".env.local", "package.json", "src/index.ts"], correct: ".env.local", explanation: "The local environment file keeps machine-specific values out of the shared source." },
  ];
  const question = questions[activeQuestion];
  const triggerBob = (feedback: "wrong" | "correct") => { onBobFeedback("idle"); window.setTimeout(() => onBobFeedback(feedback), 20); };
  const choose = (answer: string) => {
    setAnswers((current) => ({ ...current, [activeQuestion]: answer }));
    setQuizAnswer(answer);
    if (answer === question.correct) {
      triggerBob("correct");
      if (activeQuestion === questions.length - 1) {
        setQuizPassed(true);
        setCompletedModules((current) => current.includes(selectedModule) ? current : [...current, selectedModule]);
      } else {
        window.setTimeout(() => { setActiveQuestion(1); setQuizAnswer(null); }, 500);
      }
    } else {
      setShowHint(false);
      triggerBob("wrong");
    }
  };
  const completed = (index: number) => completedModules.includes(index);
  const locked = (index: number) => index > (completedModules.includes(1) ? 2 : 1);
  return <><div className="page-heading"><div><p className="eyebrow">ONBOARDING / {quizPassed ? "100% COMPLETE" : "72% COMPLETE"}</p><h1>Learning path</h1><p>A guided route through the parts of Atlas Core that matter most to your role.</p></div><div className="progress-summary"><ProgressRing value={quizPassed ? 100 : 72} /><span><strong>{quizPassed ? "5 of 5" : "3 of 5"}</strong><small>modules completed</small></span></div></div><div className={`learning-layout ${started ? "is-reading" : ""}`}><div className="module-list"><div className="eyebrow">YOUR MODULES</div>{modulePlan.map((item, index) => <button key={item.title} className={`module-item ${index === selectedModule ? "selected" : ""} ${locked(index) ? "locked" : ""}`} onClick={() => { if (!locked(index)) { setSelectedModule(index); setStarted(false); setActiveQuestion(0); setQuizAnswer(null); } }}><span className="module-num">{completed(index) ? <Check size={14} /> : locked(index) ? <LockKeyhole size={13} /> : item.tag}</span><span><strong>{item.title}</strong><small>{item.time} · {completed(index) ? "Completed" : locked(index) ? "Locked" : index === selectedModule && started ? "In progress" : "Ready to start"}</small></span><ChevronRight size={15} /></button>)}</div><section className={`module-detail ${started ? "reading-mode" : ""}`}>{!started ? <><div className="module-detail-head"><div><span className="eyebrow seafoam">MODULE {mod.tag} / {completed(selectedModule) ? "COMPLETE" : "READY"}</span><h2>{mod.title}</h2><p>{mod.desc}</p></div><div className="module-time"><Zap size={15} /> {mod.time}</div></div><div className="module-progress"><span style={{ width: completed(selectedModule) ? "100%" : "62%" }} /></div><div className="module-summary"><span className="summary-mark"><BookOpen size={20} /></span><div><span className="eyebrow">MODULE SUMMARY</span><h3>{selectedModule === 1 ? "A calm first step into the codebase." : "Build the context you need."}</h3><p>{selectedModule === 1 ? "Learn the environment contract, the commands the team trusts, and how to verify a clean local session before touching product logic." : mod.desc}</p><div className="summary-meta"><span><Zap size={14} /> {mod.time}</span><span><CircleHelp size={14} /> {selectedModule === 1 ? "2 questions" : "Reading + checkpoint"}</span></div><button className="primary-cta" onClick={() => setStarted(true)}>{completed(selectedModule) ? "Review module" : "Start module"} <ArrowUpRight size={15} /></button></div></div></> : <div className="module-reading-wrap"><div className="module-reading"><div className="reading-toolbar"><button className="text-btn" onClick={() => setStarted(false)}><ChevronRight size={14} className="back-chevron" /> Return to Learning path</button><span className="eyebrow">MODULE {mod.tag} / READING MODE</span></div><div className="module-reading-head"><span className="eyebrow seafoam">ATLAS CORE / LOCAL SETUP</span><h2>{mod.title}</h2><p>Make the first local run feel predictable.</p></div><div className="reading-copy"><p className="lead">The fastest way into Atlas Core is to understand the environment contract before you touch the product logic.</p><p>This module connects the repository shape to a working local session. You will learn the package manager, environment variables, and the commands the team uses to verify a clean setup.</p><div className="command-block"><span>TERMINAL</span><code><i>$</i> pnpm install<br /><i>$</i> pnpm dev</code></div><h3>Before you move on</h3><p>Keep your local values in the environment file, then use the checkpoint below to confirm the two details that make this project predictable.</p></div><div className="quiz-card"><div className="quiz-title"><span className="eyebrow">CHECKPOINT / 0{activeQuestion + 1} OF 02</span><h3>{question.prompt}</h3></div><div className="quiz-options">{question.options.map((answer) => <button key={answer} className={answers[activeQuestion] === answer ? answer === question.correct ? "correct" : "wrong" : ""} onClick={() => choose(answer)}>{answer}<span>{answers[activeQuestion] === answer && (answer === question.correct ? <Check size={15} /> : "×")}</span></button>)}</div>{quizPassed && <button className="primary-cta next-module-btn" onClick={() => { setStarted(false); setSelectedModule(2); setQuizAnswer(null); setShowHint(false); setQuizPassed(false); setActiveQuestion(0); setAnswers({}); }}>Start next module <ArrowUpRight size={15} /></button>}</div>{quizPassed && <div className="assessment-banner"><div><span className="eyebrow seafoam">NEXT / DEVELOPER TWIN</span><h3>Your learning path is ready for a deeper read.</h3><p>Answer five open-ended questions so Bob can update your strengths, gaps, and next best module.</p></div><button className="primary-cta" onClick={onAssessment}><BrainCircuit size={16} /> Open assessment <ArrowUpRight size={15} /></button></div>}</div><aside className="module-notes"><div className="section-head"><div><span className="eyebrow">PRIVATE NOTES</span><h3>Keep a thought here.</h3></div><MoreHorizontal size={17} /></div><textarea value={notes} onChange={(event) => setNotes(event.target.value)} placeholder="Write anything you want to remember..." /><span className="notes-hint">Saved locally in this demo</span></aside></div>}</section></div></>;
}

function AssessmentPanel'''
text, count = re.subn(pattern, replacement, text, count=1)
if count != 1:
    raise RuntimeError('LearningPath restore failed')
path.write_text(text)
print('learning path restored selectively')
