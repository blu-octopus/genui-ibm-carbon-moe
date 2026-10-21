# IBM Carbon Design Context (Control Saturation Document)

Research control document for **context-window-saturated** single-pass baselines in `genui-ibm-carbon-moe`. Paste this entire file into the model context, then append the short enterprise test prompt at the bottom.

This document is **not** injected into the Agentic MoE treatment path. MoE experts receive only a compact token allowlist plus a short user prompt.

---

## 1. Non-negotiable principles (no Design Theater)

1. Use **only** IBM Carbon React components (`@carbon/react`) and Carbon design tokens.
2. **Never** use:
   - Hex colors (`#0f62fe`, `#fff`, …)
   - Raw pixel spacing (`margin: 15px`, `padding: 10px`)
   - `rgb()` / `rgba()`
   - Tailwind / utility classes (`bg-blue-500`, `flex-col`, `rounded-xl`)
   - Inline style objects (`style={{ ... }}`)
3. Prefer semantic Carbon props: `Button kind="primary"`, `Tag type="green"`, `Column sm={4} lg={4}`.
4. Bind emphasis colors to tokens: `$interactive-01`, `$support-success`, `$support-warning`, `$support-error`, `$text-01`, `$ui-background`.
5. Spacing must use the Carbon spacing scale (`$spacing-03` … `$spacing-07`), never ad-hoc pixels.
6. Typography must use Carbon type tokens (`$heading-03`, `$label-01`, `$body-01`, …), never raw `font-size: 24px`.

---

## 2. Allowed color tokens

`$interactive-01`, `$interactive-02`, `$ui-01`, `$ui-02`, `$ui-03`, `$ui-background`, `$text-01`, `$text-02`, `$text-03`, `$text-04`, `$field-01`, `$field-02`, `$support-error`, `$support-success`, `$support-warning`, `$support-info`, `$link-01`, `$icon-01`, `$icon-02`, `$border-subtle-01`, `$focus`, `$overlay-01`

CSS variables (when needed): `--cds-interactive`, `--cds-text-primary`, `--cds-text-secondary`, `--cds-layer`, `--cds-field`, `--cds-support-error`, `--cds-support-success`, `--cds-support-warning`, `--cds-focus`, `--cds-background`

---

## 3. Allowed spacing tokens

`$spacing-01` … `$spacing-13` (prefer `$spacing-03`, `$spacing-05`, `$spacing-07` for UI density)

---

## 4. Allowed typography tokens

`$heading-01` … `$heading-07`, `$body-compact-01`, `$body-compact-02`, `$body-01`, `$body-02`, `$label-01`, `$label-02`, `$helper-text-01`, `$code-01`, `$code-02`

---

## 5. Layout / grid (responsive)

- Structure pages with `Grid` + `Column` (or `Stack` for vertical rhythm).
- Set responsive props on `Column`: `sm`, `md`, `lg` (and `xlg` / `max` when needed).
- Desktop target **1440px**; mobile target **375px**. Two-column forms must collapse to one column on `sm`.
- Prefer Carbon grid classes when expressing CSS: `cds--grid`, `cds--row`, `cds--col-sm-4`, `cds--col-lg-8`, `cds--col-lg-16`.

---

## 6. Allowed components (subset)

`Grid`, `Column`, `Stack`, `Button`, `TextInput`, `TextArea`, `Dropdown`, `Select`, `SelectItem`, `DatePicker`, `DatePickerInput`, `Checkbox`, `Tag`, `Tile`, `Search`, `DataTable`, `Table`, `TableHead`, `TableRow`, `TableHeader`, `TableBody`, `TableCell`, `Pagination`, `Modal`, `ModalHeader`, `ModalBody`, `ModalFooter`, `InlineNotification`, `Form`, `FormGroup`, `ProgressIndicator`, `ProgressStep`, `Link`, `Heading`, `Layer`, `Tooltip`

Button kinds: `primary`, `secondary`, `tertiary`, `ghost`, `danger`, `danger--tertiary`, `danger--ghost`  
Tag types: `green`, `red`, `blue`, `teal`, `gray`, `cool-gray`, `warm-gray`, …

---

## 7. Accessibility (WCAG 2.1 AA expectations)

- Every interactive control needs an accessible name: `labelText`, `ariaLabel`, `titleText`, or visible label.
- Tables: real header cells; batch checkboxes need `aria-label`.
- Modals: treat as dialogs (`aria-modal` semantics via Carbon `Modal`); danger actions use `kind="danger"`.
- Do not rely on color alone for status—pair Tags with clear text (`Active`, `Pending`, `Suspended`).
- Keep focus order logical; do not invent custom focus traps outside Carbon Modal.

---

## 8. Few-shot exemplars (bad → good)

### Buttons

**Bad (vibe-coded):**
```jsx
<button style={{ backgroundColor: '#0f62fe', padding: '10px' }}>Save</button>
```

**Good (token-bound Carbon):**
```jsx
<Button kind="primary">Save</Button>
```

### Status tags

**Bad:**
```jsx
<span style={{ color: '#24a148' }}>Active</span>
```

**Good:**
```jsx
<Tag type="green">Active</Tag>
```

### Form spacing / layout

**Bad:**
```jsx
<div style={{ display: 'flex', gap: '16px', marginBottom: '24px' }}>...</div>
```

**Good:**
```jsx
<Grid>
  <Column sm={4} md={4} lg={8}><TextInput id="company" labelText="Company Name" /></Column>
  <Column sm={4} md={4} lg={8}><TextInput id="email" labelText="Admin Email" invalid invalidText="Enter a valid email" /></Column>
</Grid>
```

### KPI value hierarchy

**Bad:** `<h1 style={{ fontSize: '32px' }}>$1.2M</h1>`  
**Good:** `<Heading props={{ token: "$heading-03", text: "$1.2M" }} />` (or Carbon type token on a Heading node in JSON IR)

### Destructive modal

**Bad:** custom red `<div className="modal">` with hex background  
**Good:** Carbon `Modal` + `InlineNotification kind="error"` + `Button kind="danger"` (disabled until confirm text matches)

---

## 9. Output format for this benchmark harness

When generating for this repo’s evaluators, prefer a single JSON object:

```json
{
  "document": {
    "id": "prompt_id_here",
    "root": {
      "type": "Grid",
      "props": {},
      "children": []
    }
  }
}
```

Each node: `{ "type": "<CarbonComponent>", "props": {}, "children": [] }`.  
Put visible strings in props (`labelText`, `text`, `ariaLabel`, table `headers`/`rows`). Do not emit markdown fences.

---

## 10. Reminder

Append the **specific enterprise test prompt** after this document. Follow Carbon strictly. If a requested visual cannot be expressed with tokens, remap to the nearest Carbon token and state that remapping in `notes` if your schema allows it.
