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

export default function Page() {
  const [promptId, setPromptId] = useState(PROMPT_IDS[0]);
  const [doc, setDoc] = useState<CarbonDocument | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setError(null);
    fetch(`/api/ground-truth/${promptId}`)
      .then(async (r) => {
        if (!r.ok) throw new Error(await r.text());
        return r.json();
      })
      .then((data) => setDoc(data))
      .catch((e) => setError(String(e)));
  }, [promptId]);

  return (
    <>
      <Header aria-label="Carbon MoE">
        <HeaderName href="/" prefix="IBM">
          Carbon MoE Test Bench
        </HeaderName>
      </Header>
      <Content>
        <label htmlFor="prompt">Ground truth prompt</label>
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
