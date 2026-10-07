'use client';

import { useEffect, useState } from 'react';
import { Content, Header, HeaderName } from '@carbon/react';
import { DynamicCarbonRenderer } from '../components/DynamicCarbonRenderer';
import type { CarbonDocument } from '../components/types';

const PROMPT_IDS = [
  'prompt_01_travel_dashboard',
  'prompt_02_inventory_table',
  'prompt_03_registration_form',
  'prompt_04_kpi_grid',
  'prompt_05_destructive_modal',
];

type SourceId = 'ground_truth' | 'moe_small' | 'baseline_large';

const SOURCES: { id: SourceId; label: string; resultFile?: string }[] = [
  { id: 'ground_truth', label: 'Ground truth' },
  {
    id: 'moe_small',
    label: 'MoE / mistral-small-latest',
    resultFile: 'moe_mistral_mistral-small-latest_prompt_01_travel_dashboard.json',
  },
  {
    id: 'baseline_large',
    label: 'Baseline / mistral-large-latest',
    resultFile: 'baseline_mistral_mistral-large-latest_prompt_01_travel_dashboard.json',
  },
];

export default function Page() {
  const [promptId, setPromptId] = useState(PROMPT_IDS[0]);
  const [source, setSource] = useState<SourceId>('ground_truth');
  const [doc, setDoc] = useState<CarbonDocument | null>(null);
  const [meta, setMeta] = useState<string>('');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setError(null);
    setDoc(null);
    setMeta('');

    const selected = SOURCES.find((s) => s.id === source);
    const isDashboardCompare =
      promptId === 'prompt_01_travel_dashboard' && source !== 'ground_truth';

    const url =
      source === 'ground_truth' || !isDashboardCompare
        ? `/api/ground-truth/${promptId}`
        : `/api/results/${selected?.resultFile}`;

    if (source !== 'ground_truth' && promptId !== 'prompt_01_travel_dashboard') {
      setError(
        'MoE/baseline compare sources are available for prompt_01_travel_dashboard only. Showing ground truth instead.',
      );
    }

    fetch(url)
      .then(async (r) => {
        if (!r.ok) throw new Error(await r.text());
        return r.json();
      })
      .then((data) => {
        if (data.document?.root) {
          setDoc(data.document as CarbonDocument);
          setMeta(
            [data.system, data.model, data.filename].filter(Boolean).join(' · ') ||
              'ground truth',
          );
        } else if (data.root) {
          setDoc(data as CarbonDocument);
          setMeta('ground truth');
        } else {
          throw new Error('Response has no Carbon document tree');
        }
      })
      .catch((e) => setError(String(e)));
  }, [promptId, source]);

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
              onChange={(e) => setPromptId(e.target.value)}
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
              onChange={(e) => setSource(e.target.value as SourceId)}
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
