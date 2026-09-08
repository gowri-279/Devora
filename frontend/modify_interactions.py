from pathlib import Path

path = Path('/home/ubuntu/devora-frontend/client/src/pages/Home.tsx')
text = path.read_text()
old = '<div className="quiz-feedback wrong-feedback"><strong>Try again — you got this!</strong><button onClick={() => setShowHint(true)}>Want a hint?</button></div>}{showHint && <div className="quiz-feedback hint-feedback"><Sparkles size={15} /><span>{activeQuestion === 0 ? "Look for the package manager named in the terminal snippet above." : "Keep machine-specific values out of shared source files."}</span></div>}{quizPassed && <div className="quiz-feedback correct-feedback"><Check size={15} /><span><strong>Good job.</strong> Both questions are complete and the next module is unlocked.</span></div>}'
new = '<div className="quiz-feedback hint-feedback hidden-feedback"><Sparkles size={15} /><span>{activeQuestion === 0 ? "Look for the package manager named in the terminal snippet above." : "Keep machine-specific values out of shared source files."}</span></div>}{quizPassed && <button className="primary-cta next-module-btn" onClick={() => { setStarted(false); setSelectedModule(2); setQuizAnswer(null); setShowHint(false); }}>Start next module <ArrowUpRight size={15} /></button>}'
if old not in text:
    raise SystemExit('quiz feedback target not found')
text = text.replace(old, new, 1)
text = text.replace('<i className="bob-smile" />', '<i className={state === "low" ? "bob-smile sad" : "bob-smile"} />', 1) if False else text
path.write_text(text)
print('updated quiz presentation')
