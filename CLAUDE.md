# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Streamlit-based marketing campaign generator that creates, translates, and evaluates marketing content using Azure OpenAI. The application generates marketing campaigns using templates, translates them into multiple languages, and evaluates translation quality using the G-Eval framework.

## Common Commands

### Development

```bash
# Install dependencies
poetry install

# Run the application
poetry run streamlit run Home.py

# Activate virtual environment (if needed)
source .venv/bin/activate  # Unix/macOS
.venv\Scripts\activate     # Windows
```

### Testing

No test framework is currently configured in this project.

## Architecture

### Multi-Agent System

The application uses a **LangGraph-based state machine** architecture with three specialized agents:

1. **ContentGenerationAgent** (`agents/content_generation_agent.py`)
   - Generates English marketing content from user queries and templates
   - Uses Retrieval-Augmented Generation (RAG) with Milvus vector database
   - Retrieves similar campaigns to provide context
   - Incorporates audience targeting (name + description)
   - State flow: `generate_content` (single node graph)

2. **TranslationAgent** (`agents/translation_agent.py`)
   - Implements a **Reflection Pattern** with three-node workflow
   - State flow: `translate_content` → `criticize_translation` → `reflect_on_translation`
   - Each translation is criticized and then refined based on feedback
   - Supports multiple target languages simultaneously

3. **EvaluationAgent** (`agents/evaluation_agent.py`)
   - Uses DeepEval G-Eval framework for translation quality assessment
   - Supports 13 evaluation metrics (accuracy, fluency, cultural appropriateness, etc.)
   - Metrics configurable per evaluation

### Data Storage Architecture

**MongoDB** - Document storage for:
- Campaigns (localized content + liquid templates)
- Content templates (HTML templates with example queries)
- Audiences (name + description)

**Milvus** - Vector database for:
- Campaign embeddings (1536-dimensional vectors from Azure OpenAI)
- Similarity search for RAG context retrieval
- Uses IVF_FLAT index with L2 metric

### State Management

All agents share `AgentState` (`agents/agent_state.py`) containing:
- `messages`: conversation history
- `initial_english_content`: generated English content (JSON)
- `translations`: dict of language code → translated JSON
- `criticisms`: feedback on translations
- `evaluation`: evaluation results per language
- `content_template`: Liquid template + items schema
- `selected_languages`: target languages for translation
- `selected_audience_name` / `selected_audience_description`: targeting info

### Template System

Uses **Liquid templates** (`python-liquid` package) to generate HTML from JSON content:
- Templates stored in MongoDB `content_templates` collection
- Each template has: `name`, `liquid_template`, `items` (schema), `example_query`
- Content is generated as JSON, then applied to Liquid template to produce HTML

### Repository Pattern

- `CampaignRepository` (`repositories/campaign_repository.py`)
  - Dual storage: MongoDB for campaigns, Milvus for embeddings
  - `save_campaign()`: saves to both databases
  - `search_similar_campaigns()`: vector similarity search with threshold (default 0.5)
  - `get_campaigns()`: retrieves all campaigns

- `AudienceRepository` (`repositories/audience_repository.py`)
  - MongoDB CRUD operations for audience management

## Key Files

- `Home.py` - Main Streamlit application with 4 tabs: Create New, Campaigns, Audiences, Prompts
- `agents/agent_state.py` - Shared state schema for all agents (TypedDict)
- `utils/azure_openai_utils.py` - Azure OpenAI client and embedding generation
- `utils/deepeval_azure_openai.py` - Azure OpenAI wrapper for DeepEval
- `utils/mongodb_utils.py` - MongoDB client utilities
- `utils/llm_queries.py` - Default prompts for system, translation, criticism, and reflection
- `campaign.py` / `audience.py` - Data models

## Environment Variables

Required in `.env`:

```env
# OpenAI API Configuration
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_MODEL=gpt-4o-mini

# Language Configuration
LANGUAGES=uk-UA,pl-PL,kk-KZ,es-ES,zh-CN,fr-FR,de-DE,hi-IN,ar-SA,pt-BR,ru-RU,ja-JP,ko-KR,it-IT,tr-TR
DEFAULT_LANGUAGES=uk-UA

# Database Connections
CONNECTION_STRING_MONGO=mongodb://team-099:password@localhost:27017/team-099
CONNECTION_STRING_MILVUS=http://user:password@localhost:19530/database
```

## Important Implementation Details

### Content Generation Flow

1. User enters query + selects template + audience
2. Query is formatted with template structure and audience context
3. ContentGenerationAgent retrieves similar campaigns (if context enabled)
4. Azure OpenAI generates JSON content matching template schema
5. JSON is applied to Liquid template → English HTML

### Translation Flow

1. English JSON content is sent to TranslationAgent
2. **Translate**: content translated to all selected languages
3. **Criticize**: translations evaluated for issues
4. **Reflect**: translations improved based on criticism
5. Final translations applied to Liquid template → multilingual HTML

### Evaluation Flow

1. Each translation is wrapped in `LLMTestCase` (input=translation query, actual_output=translation)
2. Selected G-Eval metrics are applied to each translation
3. Each metric returns score (0-1) and reason
4. Results displayed with color coding (green ≥0.7, red <0.7)

## Output Formats

The application supports exporting campaigns in:
- **HTML**: directly rendered in Streamlit
- **PDF**: generated via `weasyprint` from HTML
- **DOCX**: converted from PDF using `pdf2docx`

## Code Conventions

- All agents use structured logging (`logging` module)
- Error handling with try-except blocks and logged tracebacks
- Streamlit session state for persistence across reruns
- Agent methods return state dicts that update shared `AgentState`
- JSON responses from LLM are cleaned (strip ```json markers)
