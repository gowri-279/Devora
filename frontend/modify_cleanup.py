from pathlib import Path
import re

home = Path('/home/ubuntu/devora-frontend/client/src/pages/Home.tsx')
text = home.read_text()
text = re.sub(r'\n\s*<header className="topbar">.*?</header>', '\n      <button className="mobile-nav-launcher mobile-only" onClick={() => setMobileNav(true)} aria-label="Open navigation"><Menu size={20} /></button>', text, count=1, flags=re.S)
text = text.replace('toast.success("Good job — the next module is unlocked.");', '', 1)
text = text.replace('triggerBob("wrong"); toast("Try again.");', 'triggerBob("wrong");', 1)
home.write_text(text)

bob = Path('/home/ubuntu/devora-frontend/client/src/components/BobAssistant.tsx')
text = bob.read_text()
text = text.replace('<div className="bob-orb-core">{state === "success" ? <span className="bob-happy-eyes"><i /><i /></span> : state === "low" ? <span className="bob-sad-eyes"><i /><i /></span> : <><span /><span /></>}<i className={`bob-smile ${state === "low" ? "sad" : ""}`} /></div>', '<div className="bob-orb-core">{state === "success" ? <span className="bob-happy-eyes"><i /><i /></span> : state === "low" ? <span className="bob-sad-eyes"><i /><i /></span> : <><span /><span /></>}</div>', 1)
bob.write_text(text)
print('updated workspace and Bob cleanup')
