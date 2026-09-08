from pathlib import Path
import re

path = Path('/home/ubuntu/devora-frontend/client/src/pages/Home.tsx')
text = path.read_text()
text = text.replace('<LearningPath onAssessment={() => setView("twin")}', '<LearningPath onAssessmentSubmit={submitAssessment}', 1)
pattern = r'function LearningPath\([\s\S]*?\n}\n\nfunction AssessmentPanel'
match = re.search(pattern, text)
if not match:
    raise RuntimeError('LearningPath block not found')
block = match.group(0)
block = block.replace('function LearningPath({ onAssessment,', 'function LearningPath({ onAssessmentSubmit,', 1)
block = block.replace('onAssessment: () => void;', 'onAssessmentSubmit: (answers: Record<number, string>) => void;', 1)
block = block.replace('  const [notes, setNotes] = useState("");', '  const [notes, setNotes] = useState("");\n  const [assessmentOpen, setAssessmentOpen] = useState(false);\n  const [assessmentAnswers, setAssessmentAnswers] = useState<Record<number, string>>({});', 1)
old_start = '  return <><div className="page-heading">'
new_start = '  return <>{assessmentOpen ? <div className="assessment-inline-shell"><button className="text-btn assessment-back" onClick={() => setAssessmentOpen(false)}><ChevronRight size={14} className="back-chevron" /> Return to Learning path</button><AssessmentPanel answers={assessmentAnswers} setAnswers={setAssessmentAnswers} onSubmit={onAssessmentSubmit} /></div> : <><div className="page-heading">'
if old_start not in block:
    raise RuntimeError('LearningPath return start not found')
block = block.replace(old_start, new_start, 1)
old_end = '</section></div></>;\n}\n\nfunction AssessmentPanel'
new_end = '</section></div></>}</>;\n}\n\nfunction AssessmentPanel'
if old_end not in block:
    raise RuntimeError('LearningPath return end not found')
block = block.replace(old_end, new_end, 1)
block = block.replace('onClick={onAssessment}', 'onClick={() => { setAssessmentAnswers({}); setAssessmentOpen(true); }}', 1)
text = text[:match.start()] + block + text[match.end():]
path.write_text(text)
print('assessment trigger restored')
