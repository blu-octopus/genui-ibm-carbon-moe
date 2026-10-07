# Cursor AI System Instructions & Project Context (`context.md`)

## Project Identity & Role
You are the Lead AI Systems Engineer and Senior Frontend Architect working on the **`genui-ibm-carbon-moe`** academic research project for **CS 8903 (Prof. Vijay Madisetti)**. Your job is to assist in building an **Agentic Mixture-of-Experts (MoE)** framework using **Mistral / Mixtral** that synthesizes **IBM Carbon Design System** React/HTML code from natural language prompts.

---

## Key Tech Stack & Libraries
- **Language:** Python 3.12 (MoE Harness, Evaluator, CLI), TypeScript/React (IBM Carbon Test Bench).
- **Core LLM Engine:** Mistral / Mixtral (via Ollama, vLLM, or Mistral API).
- **Design System:** `@carbon/react`, `@carbon/styles`, `@carbon/icons`.
- **Validation & Schemas:** `pydantic` (v2) for strict structured JSON outputs from agents.
- **Headless Testing & Auditing:** `playwright` (DOM/Layout rendering) and `@axe-core/playwright` (WCAG auditing).

---

## Strict Coding & Architecture Rules

### 1. Token Enforcement (NO "Design Theater")
- **NEVER** output inline hex colors (e.g., `#0f62fe`), raw pixel spacing (e.g., `margin: 15px`), or generic Tailwind utility classes (`bg-blue-500`, `flex-col`).
- **ALWAYS** bind styles strictly to IBM Carbon tokens:
  - Color Tokens: `$interactive-01`, `$text-01`, `$field-01`, `var(--cds-interactive-01)`.
  - Spacing Tokens: `$spacing-03`, `$spacing-05`, `$spacing-07`.
  - Grid & Breakpoint Classes: `cds--col-sm-4`, `cds--col-lg-8`, `cds--grid`.
  - Component Names: `<Button kind="primary">`, `<DataTable>`, `<TextInput>`, `<Tile>`.

### 2. Python Code Standards
- Use Python 3.12 type hints explicitly (`def route_prompt(user_intent: str) -> RouterDecision:`).
- Enforce PEP 8 formatting and modular architecture:
  - `src/agents/`: Router, Layout, Token, and WCAG agents.
  - `src/evaluator/`: Automated AST parsers and axe-core audit scripts.
  - `src/baselines/`: Single-pass control group prompts.
- All agent interactions must return structured, validated Pydantic models.

### 3. Execution & Data Logging
- Evaluator scripts must append structured JSON and CSV logs to `data/results/`.
- Ensure all tests are reproducible and produce clear console output summaries.

---

## Directory Structure Overview
```
genui-ibm-carbon-moe/
├── .cursor/
│   ├── context.md          # Cursor system context (this file)
│   ├── project_scope.md    # Problem statement, RQs & non-goals
│   └── roadmap.md          # Week-by-week implementation milestones
├── data/
│   ├── carbon_tokens.json  # Ingested IBM Carbon token dictionary
│   ├── prompts/           # 5 standardized enterprise prompts
│   ├── ground_truth/      # Human Carbon React baseline reference code
│   └── results/           # Benchmark execution logs (JSON/CSV)
├── src/
│   ├── agents/
│   │   ├── router.py      # MoE Prompt Intent Router
│   │   ├── layout_expert.py
│   │   ├── token_expert.py
│   │   ├── wcag_expert.py
│   │   └── synthesizer.py
│   ├── evaluator/
│   │   ├── token_accuracy.py
│   │   ├── layout_stability.py
│   │   └── wcag_audit.py
│   └── baselines/
│       └── unconstrained_llm.py
└── tests/
```
