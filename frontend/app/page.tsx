'use client';

import { useEffect, useState } from 'react';
import { Content, Header, HeaderName } from '@carbon/react';
import { DynamicCarbonRenderer } from '../components/DynamicCarbonRenderer';
import type { CarbonDocument } from '../components/types';

const PROMPT_IDS = [
  'prompt_01_enterprise_table',
  'prompt_02_registration_form',
  'prompt_03_kpi_grid',
  'prompt_04_destructive_modal',
  'prompt_05_global_shell',
];

type SourceId = 'ground_truth' | 'moe' | 'baseline' | 'design_md';

const SOURCES: { id: SourceId; label: string }[] = [
  { id: 'ground_truth', label: 'Ground truth (human)' },
  { id: 'moe', label: 'MoE / mistral-small-latest' },
  { id: 'baseline', label: 'Baseline unconstrained / mistral' },
  { id: 'design_md', label: 'Baseline + design.md / mistral' },
];

function resultFilename(source: SourceId, promptId: string): string | null {
  if (source === 'moe') {
    return `moe_mistral_mistral-small-latest_${promptId}.json`;
  }
  if (source === 'baseline') {
    return `baseline_mistral_mistral-small-latest_${promptId}.json`;
  }
  if (source === 'design_md') {
    return `baseline_mistral_design_md_mistral-small-latest_${promptId}.json`;
  }
  return null;
}

function sourceFromQuery(): SourceId {
  if (typeof window === 'undefined') return 'ground_truth';
  const q = new URLSearchParams(window.location.search).get('source');
  if (q === 'moe' || q === 'baseline' || q === 'design_md' || q === 'ground_truth') {
    return q;
  }
  // legacy aliases
  if (q === 'moe_small') return 'moe';
  if (q === 'baseline_large') return 'baseline';
  return 'ground_truth';
}

function promptFromQuery(): string {
  if (typeof window === 'undefined') return PROMPT_IDS[0];
  const q = new URLSearchParams(window.location.search).get('prompt');
  if (q && PROMPT_IDS.includes(q)) return q;
  return PROMPT_IDS[0];
}

export default function Page() {
  const [promptId, setPromptId] = useState(PROMPT_IDS[0]);
  const [source, setSource] = useState<SourceId>('ground_truth');
  const [doc, setDoc] = useState<CarbonDocument | null>(null);
  const [meta, setMeta] = useState<string>('');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setPromptId(promptFromQuery());
    setSource(sourceFromQuery());
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    setError(null);
    setDoc(null);
    setMeta('');

    const file = resultFilename(source, promptId);
    const url =
      source === 'ground_truth' || !file
        ? `/api/ground-truth/${promptId}`
        : `/api/results/${file}`;

    fetch(url, { signal: controller.signal })
      .then(async (r) => {
        if (!r.ok) throw new Error(await r.text());
        return r.json();
      })
      .then((data) => {
        if (controller.signal.aborted) return;
        if (data.document?.root) {
          setDoc(data.document as CarbonDocument);
          setMeta(
            [data.system, data.model, data.filename].filter(Boolean).join(' · ') ||
              source,
          );
        } else if (data.root) {
          setDoc(data as CarbonDocument);
          setMeta(source === 'ground_truth' ? 'ground truth' : source);
        } else {
          throw new Error('Response has no Carbon document tree');
        }
      })
      .catch((e) => {
        if (controller.signal.aborted || e?.name === 'AbortError') return;
        setError(String(e));
      });

    return () => controller.abort();
  }, [promptId, source]);

  function updateQuery(nextPrompt: string, nextSource: SourceId) {
    const url = new URL(window.location.href);
    url.searchParams.set('prompt', nextPrompt);
    url.searchParams.set('source', nextSource);
    window.history.replaceState({}, '', url.toString());
  }

  return (
    <>
      <Header aria-label="Carbon MoE">
        <HeaderName href="/" prefix="IBM">
          Carbon MoE Test Bench
        </HeaderName>
      </Header>
      <Content>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', marginBottom: '1rem' }}>
          <label htmlFor="prompt">
            Prompt{' '}
            <select
              id="prompt"
              value={promptId}
              onChange={(e) => {
                const next = e.target.value;
                setPromptId(next);
                updateQuery(next, source);
              }}
            >
              {PROMPT_IDS.map((id) => (
                <option key={id} value={id}>
                  {id}
                </option>
              ))}
            </select>
          </label>
          <label htmlFor="source">
            Source{' '}
            <select
              id="source"
              value={source}
              onChange={(e) => {
                const next = e.target.value as SourceId;
                setSource(next);
                updateQuery(promptId, next);
              }}
            >
              {SOURCES.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.label}
                </option>
              ))}
            </select>
          </label>
        </div>
        {meta && <p data-testid="source-meta">{meta}</p>}
        {error && <p role="alert">{error}</p>}
        {doc && (
          <div data-testid="carbon-canvas">
            <DynamicCarbonRenderer node={doc.root} />
          </div>
        )}
      </Content>
    </>
  );
}
