# genui-ibm-carbon-moe

Agentic Mixture-of-Experts (MoE) research harness that **governs** IBM Carbon UI as validated JSON, then **ships** `@carbon/react` TSX. Built for CS 8903 (Prof. Vijay Madisetti).

## Setup

```bash
python3.12 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env        # add MISTRAL_API_KEY (and OPENAI_API_KEY for GPT-4o baseline)
pytest
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## CLI

```bash
python -m src.main synthesize-gt
python -m src.main grade-gt
python -m src.main run-moe --prompt-id prompt_01_enterprise_table --dry-run
python -m src.main run-moe --prompt-id prompt_01_enterprise_table
python -m src.main run-baseline --provider mistral --prompt-id prompt_01_enterprise_table
python -m src.main run-baseline --provider mistral --prompt-id prompt_01_enterprise_table --context design
python -m src.main run-baseline --provider gpt4o --prompt-id prompt_01_enterprise_table
python scripts/run_bench_matrix.py   # all 5 prompts x baseline/design.md/MoE
```

Prompts: `data/prompts/prompts.md` + `prompts.json`. Design saturation doc: `data/design.md`.

## API keys

- **Mistral (required):** https://console.mistral.ai → API keys  
- **OpenAI (GPT-4o baseline only):** https://platform.openai.com/api-keys  

Never commit `.env`.
