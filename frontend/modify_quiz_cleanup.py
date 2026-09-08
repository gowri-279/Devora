from pathlib import Path

home = Path('/home/ubuntu/devora-frontend/client/src/pages/Home.tsx')
text = home.read_text()
text = text.replace('  const [quizPassed, setQuizPassed] = useState(false);', '  const [quizPassed, setQuizPassed] = useState(false);\n  const [completedModules, setCompletedModules] = useState<number[]>([0]);', 1)
text = text.replace('setQuizPassed={setQuizPassed} quizAnswer={quizAnswer}', 'setQuizPassed={setQuizPassed} completedModules={completedModules} setCompletedModules={setCompletedModules} quizAnswer={quizAnswer}', 1)
text = text.replace('function LearningPath({ selectedModule, setSelectedModule, quizPassed, setQuizPassed, quizAnswer, setQuizAnswer, showHint, setShowHint, onBobFeedback }: { selectedModule: number; setSelectedModule: (value: number) => void; quizPassed: boolean; setQuizPassed: (value: boolean) => void; quizAnswer: string | null; setQuizAnswer: (value: string | null) => void; showHint: boolean; setShowHint: (value: boolean) => void; onBobFeedback: (value: "idle" | "wrong" | "correct") => void }) {', 'function LearningPath({ selectedModule, setSelectedModule, quizPassed, setQuizPassed, completedModules, setCompletedModules, quizAnswer, setQuizAnswer, showHint, setShowHint, onBobFeedback }: { selectedModule: number; setSelectedModule: (value: number) => void; quizPassed: boolean; setQuizPassed: (value: boolean) => void; completedModules: number[]; setCompletedModules: (value: number[]) => void; quizAnswer: string | null; setQuizAnswer: (value: string | null) => void; showHint: boolean; setShowHint: (value: boolean) => void; onBobFeedback: (value: "idle" | "wrong" | "correct") => void }) {', 1)
text = text.replace('if (activeQuestion === questions.length - 1) { setQuizPassed(true); toast.success("Good job — the next module is unlocked."); }', 'if (activeQuestion === questions.length - 1) { setQuizPassed(true); setCompletedModules((current) => current.includes(selectedModule) ? current : [...current, selectedModule]); toast.success("Good job — the next module is unlocked."); }', 1)
text = text.replace('  const completed = (index: number) => index === 0 || (index === 1 && quizPassed);\n  const locked = (index: number) => index > (quizPassed ? 2 : 1);', '  const completed = (index: number) => completedModules.includes(index);\n  const locked = (index: number) => index > (completedModules.includes(1) ? 2 : 1);', 1)
text = text.replace('setStarted(false); setSelectedModule(2); setQuizAnswer(null); setShowHint(false);', 'setStarted(false); setSelectedModule(2); setQuizAnswer(null); setShowHint(false); setQuizPassed(false); setActiveQuestion(0); setAnswers({});', 1)
text = text.replace('<div className="quiz-feedback hint-feedback hidden-feedback"><Sparkles size={15} /><span>{activeQuestion === 0 ? "Look for the package manager named in the terminal snippet above." : "Keep machine-specific values out of shared source files."}</span></div>}', '}', 1)
text = text.replace('toast("Try again — Bob has a hint when you need it.");', 'toast("Try again.");', 1)
home.write_text(text)

bob = Path('/home/ubuntu/devora-frontend/client/src/components/BobAssistant.tsx')
text = bob.read_text()
text = text.replace('    if (quizFeedback === "wrong") {\n      setState("low"); setQuizHintShown(false);', '    if (quizFeedback === "wrong") {\n      setState("low"); setQuizHintShown(false);', 1)
text = text.replace('    if (quizFeedback === "correct") {\n      setState("success"); setQuizHintShown(false);', '    if (quizFeedback === "correct") {\n      setState("success"); setQuizHintShown(false);', 1)
old = '  }, [quizFeedback]);'
new = '    const resetTimer = quizFeedback === "wrong" || quizFeedback === "correct" ? window.setTimeout(() => setState("idle"), 2500) : undefined;\n    return () => { if (resetTimer) window.clearTimeout(resetTimer); };\n  }, [quizFeedback]);'
text = text.replace(old, new, 1)
text = text.replace('{state === "success" ? <span className="bob-happy-eyes">&gt;&lt;</span> : state === "low" ? <span className="bob-sad-eyes">•  •</span> : <><span /><span /></>}<i className={`bob-smile ${state === "low" ? "sad" : ""}`} />', '{state === "success" ? <span className="bob-happy-eyes"><i /><i /></span> : state === "low" ? <span className="bob-sad-eyes"><i /><i /></span> : <><span /><span /></>}<i className={`bob-smile ${state === "low" ? "sad" : ""}`} />', 1)
bob.write_text(text)
print('updated quiz cleanup')
