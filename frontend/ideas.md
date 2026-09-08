# Devora Design Direction

## Three stylistic approaches

### Theme Name: Signal Garden
Very dark, editorial, and futuristic: a quiet command center where learning signals bloom into confident action. Soft spectral color and precise typography make the AI feel intelligent without becoming sci-fi theater.

Probability: 0.07

### Theme Name: Paper Circuit
Warm off-white surfaces, ink-like typography, and technical annotation marks create a tactile handbook for modern engineers. It makes onboarding feel approachable, documented, and human.

Probability: 0.03

### Theme Name: Night Shift Console
High-contrast charcoal surfaces, electric blue controls, and restrained violet state changes create a polished late-night developer workspace. The energy is technical and focused, with Bob as the only living glow.

Probability: 0.09

## Selected approach: Signal Garden

### Design Movement
Neo-editorial product design: Swiss information hierarchy meets observability dashboards, with soft glass surfaces, pin-light gradients, and a quiet sense of scientific instrumentation.

### Core Principles
1. Make progress visible before making it verbose.
2. Use contrast and whitespace to create calm, not emptiness.
3. Let Bob be the only expressive, animated character in the system.
4. Treat every panel as a useful instrument with one obvious next action.

### Color Philosophy
The foundation is midnight ink and mineral slate so dense information remains restful. Devora's ownable color is **luminous seafoam (#8CF7D0)**, used as a signal of movement, completion, and trust. Periwinkle and violet appear only as AI/state accents, while amber is reserved for knowledge gaps and uncertainty. This makes semantic color feel earned rather than decorative.

### Layout Paradigm
A persistent left rail anchors navigation, while the main dashboard uses an asymmetric observability canvas: a wide primary column for the next action and learning path, a narrower right column for team signals and resources, and an unobtrusive floating Bob layer. Content is organized in offset instrument panels rather than a generic centered card grid.

### Signature Elements
- A tiny four-point signal mark that acts as the Devora logo and favicon.
- Fine dotted-grid textures and hairline separators that feel like a technical notebook.
- Bob's state orb, using smooth spectral transitions to communicate idle, thinking, responding, and low confidence.

### Interaction Philosophy
Interactions should feel like instruments responding to input: immediate press feedback, gentle lift on actionable cards, and contextual state changes rather than noisy decoration. The user should always understand what changed and why.

### Animation
Use short ease-out transitions under 280ms for navigation, buttons, and panels. Bob uses a slow breathing animation while idle, a slightly more active orbit while thinking, and a warm flash when a quiz answer is correct or confidence is low. Entrances stagger by 40ms across panels, but reduced-motion users receive static states.

### Typography System
Use **Space Grotesk** for display, labels, and navigation to give the interface a crisp engineering voice. Use **DM Sans** for body copy and longer reading to keep documentation comfortable. Headlines use tight tracking and medium-to-bold weights; metadata is uppercase, letter-spaced, and small; body text stays at 15–16px with generous line height.

### Brand Essence
Devora is the calm AI onboarding system for engineering teams that need every developer to find their footing faster, with project context instead of generic tutorials.

Personality adjectives: **clear, companionable, exact**.

### Brand Voice
Headlines are concise and directional. CTAs sound like confident invitations, not growth-marketing slogans. Microcopy is specific, encouraging, and grounded in the developer's immediate task.

Example lines:
- “Turn unfamiliar code into a path forward.”
- “Bob is ready when the repository gets weird.”

### Wordmark & Logo
The mark is a four-point signal flower: four tapered modules orbiting a small negative-space center, implying a repository being understood from multiple directions. The wordmark is set in Space Grotesk with a custom clipped crossbar on the A; in the UI, the symbol carries the brand so the wordmark can stay quiet.

### Signature Brand Color
**Luminous seafoam — #8CF7D0.** It reads as progress and clarity against midnight ink, and it gives the product a recognizable visual signal without relying on default blue or purple gradients.

## Style Decisions

- Use a dark, mineral foundation with seafoam as the primary action and completion color.
- Keep Bob's glow stateful and restrained; never turn the whole application into a neon surface.
- Prefer asymmetric dashboard compositions over uniform card grids.
- Use Space Grotesk + DM Sans, never Inter, for this experience.
- Use generated Bob artwork only in the landing hero; use CSS/HTML for the persistent orb so it remains crisp and interactive.

## Accepted review amendments

- Bob artwork must be integrated into a dark instrument environment, not read as a pasted rectangular image.
- The landing hero should include an asymmetric cluster of status, repository, progress, and knowledge signals.
- Seafoam #8CF7D0 remains the only dominant luminous color; violet/periwinkle are secondary state accents only.
