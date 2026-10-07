# Project Scope & Research Specification (`project_scope.md`)

## 1. Problem Statement
Current Generative UI (GenUI) tools default to generic, unconstrained "vibe-coded" CSS/Tailwind or raw HTML. They fail to enforce enterprise brand identity, ignore strict tokenized design systems (such as the IBM Carbon Design System), break responsive layout structures across device breakpoints, and violate WCAG 2.1 AA accessibility guidelines. This "design theater" results in non-compliant software that requires expensive manual refactoring by frontend engineers.

## 2. Proposed Research Solution
An **Agentic Mixture-of-Experts (MoE)** framework utilizing **Mistral / Mixtral** foundational models and the **IBM Carbon Design System**. A central Router Agent decomposes natural language user intent and orchestrates specialized expert agents (Layout Expert, Token Mapping Expert, WCAG Accessibility Expert) to synthesize enterprise-compliant, token-bound UI components.

---

## 3. In-Scope vs. Out-of-Scope

### In-Scope
- **Design System:** IBM Carbon Design System (React components and SCSS token variables).
- **Component Domain:** Enterprise data tables, metric dashboards, multi-step forms, user settings, and modal workflows.
- **Model Architecture:** Agentic MoE harness using Mistral/Mixtral base models.
- **Evaluation Benchmark:** Quantitative head-to-head comparison between Agentic MoE generated code vs. Unconstrained Single-Pass LLM generated code vs. Human Ground Truth baselines.
- **Metrics:** Token Accuracy %, Cross-Device Layout Stability Index, WCAG 2.1 AA Violation Count, Generation Latency (seconds).

### Out-of-Scope (Non-Goals)
- Training foundational LLM neural network weights from scratch (this is a harness & systems routing contribution).
- Commercial product development / deployment of a SaaS web app.
- Fullstack backend database integration or API server generation (focus is strictly frontend UI component synthesis & token compliance).

---

## 4. Research Questions (RQs) & Mapped Contributions (Cs)

| Research Question (RQ) | Mapped Contribution (C) | Primary Metric |
| :--- | :--- | :--- |
| **RQ1 (Token Accuracy):** To what extent does an Agentic MoE framework enforce strict IBM Carbon design token binding compared to unconstrained baseline LLMs? | **C1:** Empirical proof that specialized token routing eliminates hallucinated vanilla styles and achieves >90% token adherence. | Token Accuracy % (AST/Regex Parser) |
| **RQ2 (Cross-Device Layout Stability):** How reliably does specialized layout routing preserve DOM hierarchy and component alignment across desktop (1440px) and mobile (375px) viewports? | **C2:** A quantitative benchmark verifying responsive breakpoint stability in AI-synthesized UIs. | DOM Overlap & Overflow Count (Playwright) |
| **RQ3 (Accessibility Compliance):** Does dedicating an expert agent to WCAG rules significantly reduce automated accessibility violations in generated code? | **C3:** Framework demonstrating autonomous WCAG 2.1 AA compliance enforcement in GenUI outputs. | Violations Count (axe-core audit score) |
| **RQ4 (Efficiency Trade-Offs):** What is the trade-off in generation latency and token overhead when using an Agentic MoE harness versus a single-pass LLM prompt? | **C4:** Cost-benefit analysis of multi-agent orchestration for enterprise design compliance. | Generation Latency (s) & Token Overhead |
