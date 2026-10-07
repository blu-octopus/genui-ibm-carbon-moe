# Standardized Enterprise Prompts & Benchmark Methodology

Canonical prompt set and run methodology for the `genui-ibm-carbon-moe` Agentic MoE vs. unconstrained baseline evaluation (CS 8903 / Prof. Madisetti). Use this document when assembling control and treatment runs so results stay academically rigorous and reproducible.

Harness IDs currently wired in [`prompts.json`](prompts.json) may differ until a later sync pass. Prefer the exact prompt wording below for paper-facing experiments.

---

## Benchmark Methodology

### 1. Use the API (highly recommended)

Running tests via a Python script against the OpenAI (GPT-4o) or Mistral API is the gold standard.

- **Stateless by default:** API calls have no memory of past interactions. Each run is a blank slate.
- **Reproducibility:** Set `temperature=0` (or use a fixed `seed`). This forces the model toward its most deterministic answer rather than randomly varying output. Reviewers look for this to ensure the benchmark is stable.

### 2. If using the web interface (fallback)

If the control group must use a web chat UI, sanitize the environment to prevent cross-contamination:

- **Turn memory off:** Disable memory entirely in settings.
- **Clear custom instructions:** Remove hidden background instructions (e.g., “Always write clean code”) that could unfairly advantage the control group.
- **New chat per test:** Open a brand-new chat for every prompt. Do not run Test 2 in the same chat as Test 1, or the model will reuse prior component context.

### 3. Assembling the control prompt

For the control group, do not send only the short test prompt. Simulate the “context window saturation” the research argues against:

1. Paste the massive design context (e.g. `design.md` or [`data/carbon_tokens.json`](../carbon_tokens.json)) into the prompt.
2. Append the specific test instructions at the very bottom.
3. Send that single large block to the baseline model in one shot.

### 4. Assembling the treatment (MoE) run

For the MoE framework, feed the **exact same short test prompt** to the supervisor / router agent. It dispatches Layout, Token, and WCAG experts and does **not** stuff the whole token dictionary into step one.

---

## Standardized Enterprise Prompts

Five prompts designed to stress-test baseline and MoE models. Each is written as a developer or product manager would type it, with structural complexity and specific UI states. RQ mappings support Section 4 (Experiments & Benchmarking).

### 1. The Enterprise Data Table

**The Prompt:**

> Create a React data table for managing enterprise users. It needs columns for User Name, Role, Account Status, and Last Login. Include a checkbox column on the far left for batch selection. At the top right above the table, add a search input field. At the bottom, include a pagination component displaying '1-10 of 100 items'. The 'Status' column should use colored tag components (e.g., Active, Pending, Suspended).

**What it tests:**

- **Tokens (RQ1):** Mapping specific UI states (Active/Pending) to semantic color tokens (e.g., `$support-success`, `$support-warning`) rather than hallucinated hex codes.
- **Accessibility (RQ3):** Proper `aria-labels` on checkboxes, semantic `<th>` and `<td>` structures, and focus states for the search input.

### 2. Multi-Step Registration Form with Validation

**The Prompt:**

> Build a two-column registration form for a new cloud tenant. The fields should include Company Name, Admin Email, Password, and a dropdown select menu for Industry. Include inline validation error messages under the Email and Password fields showing an invalid state. At the bottom right, place a secondary 'Cancel' button and a primary 'Create Account' button.

**What it tests:**

- **Layout Stability (RQ2):** Verifying the 2-column grid collapses gracefully into a 1-column stack on mobile viewports (375px).
- **Tokens (RQ1):** Strict adherence to form spacing scales (e.g., `$spacing-05` between fields) and error text color tokens.

### 3. Analytics KPI Overview Card Grid

**The Prompt:**

> Design a responsive dashboard widget containing four KPI cards arranged in a grid. Each card displays a top-left title (e.g., 'Total Revenue'), a large numeric value in the center, and a small percentage indicator at the bottom (green for an upward trend, red for a downward trend) next to an arrow icon. The grid should display 4 columns on desktop screens and 1 column on mobile.

**What it tests:**

- **Tokens (RQ1):** Typographic hierarchy using strict scale tokens (e.g., `$expressive-heading-03` for the numbers, `$label-01` for the title) instead of raw pixel sizes.
- **Layout Stability (RQ2):** Flexbox or CSS Grid breakpoint enforcement.

### 4. Destructive Action Confirmation Modal

**The Prompt:**

> Create a modal dialog asking the user to confirm the deletion of a database cluster. The modal must have a prominent red warning header. The body text should explain the action is irreversible and include a text input field requiring the user to type the exact cluster name to enable confirmation. Include two buttons at the bottom: a secondary 'Cancel' button and a disabled danger 'Delete Cluster' button.

**What it tests:**

- **Tokens (RQ1):** Proper use of danger tokens (e.g., `$button-danger-primary`) and modal overlay opacity tokens.
- **Accessibility (RQ3):** Focus trapping within the modal, `aria-modal="true"`, and proper contrast for disabled button states.

### 5. High-Level Global Shell & Navigation

**The Prompt:**

> Build the top-level shell for a system monitoring dashboard. It should feature a collapsible left-hand side navigation menu containing 4 link items. The main content area should have a global top header containing a logo placeholder on the left, and a user profile avatar with a notification bell icon on the right. Below the top header, include a blank main content area with a 3-tier breadcrumb trail at the top.

**What it tests:**

- **Layout Stability (RQ2):** Complex z-index layering (ensuring the side nav sits correctly under/over the header) and viewport-height calculations.
- **Tokens (RQ1):** Large-scale background color tokens (e.g., `$ui-background`) and layout margin tokens.
