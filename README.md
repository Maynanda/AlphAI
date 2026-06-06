# Arlo — AlphaAI

Arlo — AlphaAI is a personal, locally-run AI coaching tool that helps technical professionals get promoted to DS/AI Lead by transforming daily work into visible leadership communication and building consistent leadership habits.

## Core Features

1. **Four Leadership Blocks**: Progress, Current Focus, Risks, and Support Needed. The single source of truth for communication.
2. **Arlo Chat Agent**: Conversational interface to create projects, log activities, update blocks, and generate drafts.
3. **Daily Flow**: Guided morning intentions and EOD reflection.
4. **Team Unblocking & Feedback**: Document team impact and capture stakeholder feedback.
5. **Continuous Communication Generator**: BLUF-format drafts generated automatically for activities, risks, unblock actions, and reports.
6. **Local LLM & RAG**: Privacy-first, local inference using PyTorch, HuggingFace Transformers, and ChromaDB.

## Repository Structure

```
arlo/
  ├── core/            # Database schema, config, pydantic models, and prompt templates
  ├── features/        # Business logic modules per feature
  ├── services/        # Infrastructure and external wrappers (LLM, RAG, Email, parser)
  └── ui/              # Streamlit entry point, page modules, and reusable components
```

## Setup & Running Locally

1. **Clone the repository** (if you haven't already).
2. **Set up a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the Streamlit application**:
   ```bash
   streamlit run arlo/ui/app.py
   ```

All data will be stored locally in `./data/`. Please ensure this folder is backed up regularly.
