# Research & Engineering Roadmap: Agentic MoE Generative UI Benchmark (`genui-ibm-carbon-moe`)

**Course:** CS 8903 OVM — AI Agents / World Models Research  
**Advisor:** Prof. Vijay K. Madisetti  
**Target Submission:** ACM CHI / DIS / IEEE Access  

---

## Phase 1: Environment & Ground Truth Test Bench Setup (Week 5)
- [ ] **Cursor Workspace Setup:** Initialize Python 3.12 virtualenv, Node.js environment, and install dependencies (`@carbon/react`, `@carbon/styles`, `playwright`, `axe-core`, `pydantic`, `mistralai`).
- [ ] **Carbon Design System Metadata Ingestion:** Parse IBM Carbon Design System token dictionary (`$interactive-01`, `$spacing-05`, `$body-01`, etc.) into a structured JSON index (`data/carbon_tokens.json`).
- [ ] **Define 5 Standardized Enterprise Prompts:**
  1. *Prompt 1 (Data Dashboard):* "Create a responsive travel comparison dashboard with date picker, metric cards, and a filterable data table."
  2. *Prompt 2 (Enterprise Table):* "Generate a data-dense inventory table with pagination, batch actions, and status tag badges."
  3. *Prompt 3 (User Form):* "Build a multi-step user registration form with validation feedback, inline tooltips, and primary/secondary button controls."
  4. *Prompt 4 (Analytics Overview):* "Design an executive KPI card grid with trend indicators, dropdown filters, and accessible icon labels."
  5. *Prompt 5 (Modal Workflow):* "Synthesize a destructive action confirmation modal with clear messaging, warning callout, and focus-trapped action buttons."
- [ ] **Human Baseline Ground Truth:** Construct 5 manual, pixel-perfect IBM Carbon React reference components (`data/ground_truth/`) serving as the evaluation control standard.

---

## Phase 2: Agentic Mixture-of-Experts (MoE) Implementation (Weeks 6–7)
- [ ] **Base Model Integration:** Configure Mistral / Mixtral inference pipeline (via Ollama, vLLM, or Mistral API).
- [ ] **Intent Router Agent (`src/agents/router.py`):** Implement router logic to decompose user prompt intent and dispatch specialized sub-tasks to expert agents.
- [ ] **Expert Agent 1 — Layout & Responsive Structure (`src/agents/layout_expert.py`):**
  - Specialization: DOM hierarchy, flex/grid alignment, responsive breakpoint containers (`cds--col-sm`, `cds--col-lg`).
- [ ] **Expert Agent 2 — Design System Token Binding (`src/agents/token_expert.py`):**
  - Specialization: Strict mapping of raw styles to IBM Carbon CSS/SCSS variables, typography classes, and color tokens. Eliminates "vibe-coded" Tailwind/vanilla CSS.
- [ ] **Expert Agent 3 — Accessibility & WCAG Compliance (`src/agents/wcag_expert.py`):**
  - Specialization: ARIA roles, high-contrast text ratios, keyboard navigation attributes, and screen-reader accessibility labels.
- [ ] **Agentic Synthesizer (`src/agents/synthesizer.py`):** Recombines expert outputs into a clean, compiled React/HTML component.

---

## Phase 3: Automated Evaluation Pipeline & Benchmarking (Weeks 8–9)
- [ ] **Token Accuracy Evaluator (`src/evaluator/token_accuracy.py`):** AST and Regex parser calculating:
  $$\text{Token Accuracy} = \frac{\text{Valid IBM Carbon Tokens Used}}{\text{Total Styling Instructions}} \times 100\%$$
- [ ] **Cross-Device Layout Stability Audit (`src/evaluator/layout_stability.py`):** Playwright automated headless browser test rendering output at Desktop (1440px) vs Mobile (375px) viewports to detect overflow, overlapping elements, or broken grid hierarchies.
- [ ] **WCAG 2.1 AA Audit Harness (`src/evaluator/wcag_audit.py`):** Automated `axe-core` / `pa11y` evaluation measuring accessibility violation counts and contrast compliance.
- [ ] **Baseline Comparison Runner (`src/baselines/unconstrained_llm.py`):** Run the 5 prompts through unconstrained single-pass LLMs (vanilla Mistral, GPT-4o direct prompt) as Control Group vs. MoE system as Treatment Group.
- [ ] **Performance & Efficiency Logging:** Record generation latency (seconds), total tokens consumed, and time saved relative to manual component drafting.

---

## Phase 4: Quantitative Analysis & Overleaf Paper Integration (Weeks 10–12)
- [ ] **Generate Visual Assets & Tables:** Compile CSV logs into box plots and summary tables for Token Accuracy, WCAG Violation Reduction, and Responsive Stability.
- [ ] **Overleaf Section 4 (Experiments & Benchmarking):** Drop empirical results into Overleaf project shared with `madisetti.vj@gmail.com`.
- [ ] **Overleaf Section 5 (Discussion & Contribution Mapping):** Map findings to Research Questions:
  - **C1 → RQ1:** Token Accuracy % improvement.
  - **C2 → RQ2:** Cross-Device Breakpoint Stability.
  - **C3 → RQ3:** WCAG Accessibility violation reduction.
  - **C4 → RQ4:** Latency vs. Quality Trade-off.
- [ ] **Final Submission Checklist:** Run Turnitin/GPTZero compliance checks, finalize AI Use Statement, and submit to target ACM/IEEE venues.
