# Agentsway — Agentic AI Workflows Lab

A small, notebook-first learning lab for building agentic AI workflows with the
[OpenAI Agents SDK](https://github.com/openai/openai-agents-python). Work through the notebooks
in order to learn basic agents, web-search tools, agent tool calls, multi-agent workflows, and
audio generation with either OpenAI or Gemini.

## What you will build

| Notebook | Concept | What it does |
|---|---|---|
| [01_openai_basic_agent.ipynb](notebooks/01_openai_basic_agent.ipynb) | Basic OpenAI agent | Defines a beginner-friendly assistant with an explicit `gpt-5-mini` model setting. |
| [02_gemini_basic_agent.ipynb](notebooks/02_gemini_basic_agent.ipynb) | Basic Gemini agent | Runs the same assistant pattern with Gemini through its OpenAI-compatible API. |
| [03_direct_web_research.ipynb](notebooks/03_direct_web_research.ipynb) | Direct function call | Calls DuckDuckGo search directly, shows the results, then asks an agent to summarize them. |
| [04_agent_tool_call_web_research.ipynb](notebooks/04_agent_tool_call_web_research.ipynb) | Agent tool call | Gives the agent an annotated `search_web` tool and lets it decide when to call it. |
| [05_news_brief_workflow.ipynb](notebooks/05_news_brief_workflow.ipynb) | Multi-agent workflow | Searches news, filters it with an editor agent, writes a news script, creates audio, and downloads it. |

## Prerequisites

- Python 3.9+ for local execution, or a Google account for
  [Google Colab](https://colab.research.google.com/)
- An [OpenAI API key](https://platform.openai.com/api-keys) for OpenAI notebooks
- A [Gemini API key](https://aistudio.google.com/api-keys) for Gemini notebooks

You need only the key for the provider you select. Never add API keys directly to a notebook or
commit them to the repository.

## Run the notebooks in Google Colab

1. Open the desired notebook from the `notebooks/` folder in
   [Google Colab](https://colab.research.google.com/).
2. Add the API key to Colab Secrets, as described below.
3. Run the dependency-install cell.
4. In notebooks 03–05, select the provider in the configuration cell. The model names are shown
   there: `gpt-5-mini` for OpenAI agents and `gemini-2.5-flash` for Gemini agents.
5. Run the remaining cells from top to bottom.

### Add an API key to Colab Secrets

Colab Secrets stores the key outside the notebook file, so it is not exposed when you share or
commit the notebook.

1. Create an API key, if you do not already have one:

   - [Create an OpenAI API key](https://platform.openai.com/api-keys)
   - [Create a Gemini API key](https://aistudio.google.com/api-keys)

2. In Colab, click the 🔑 **Secrets** icon in the left sidebar.
3. Click **Add new secret**.
4. Enter the exact secret name required by your selected provider:

   - `OPENAI_API_KEY` for notebook 01, or when `PROVIDER = "openai"`
   - `GEMINI_API_KEY` for notebook 02, or when `PROVIDER = "gemini"`

5. Paste the API key into the **Value** field and enable notebook access for that secret.
6. Run the notebook's configuration cell. It reads the key securely with
   `google.colab.userdata`.

Never paste an API key into a code or text cell, and never commit a key to GitHub. If a key is
accidentally exposed, revoke it from the provider dashboard and create a replacement. See
[Google's Colab Secrets authentication guide](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Authentication.ipynb)
for screenshots and the same setup flow.

### News workflow output

Notebook 05 starts with a runnable Mermaid diagram explaining the flow:

`topic → DuckDuckGo news search → editor agent → script writer agent → TTS → audio download`

Its selected provider is used for both the agents and speech:

- OpenAI creates `news_brief.mp3` with `gpt-4o-mini-tts`.
- Gemini creates `news_brief.wav` with native Gemini TTS.

Run the final download cell to save the generated audio file. When sharing the briefing, disclose
that the voice is AI-generated.

## Run the basic example locally

The local script is the simplest OpenAI example.

1. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set your OpenAI API key:

   ```bash
   export OPENAI_API_KEY="your-api-key"
   ```

4. Run the workflow:

   ```bash
   python src/workflow.py
   ```

## Project structure

| Path | Purpose |
|---|---|
| `notebooks/` | Colab-ready learning workflows, ordered from basic to advanced. |
| `src/workflow.py` | A minimal local Learning Assistant example. |
| `requirements.txt` | Dependencies: `openai-agents`, `requests`, `google-genai`, and `ddgs`. |

## Key ideas

- **Instructions:** define the agent's role, constraints, and response style.
- **Direct function calls:** your Python code calls a tool, inspects the result, then passes it to an agent.
- **Agent tool calls:** the agent invokes an annotated function itself during a run.
- **Multi-agent workflows:** focused agents pass work from one stage to the next.
- **Provider selection:** the same workflow can use OpenAI or Gemini models through one configuration setting.

## Next steps

- Change the questions and news topic to explore different use cases.
- Compare direct tool calls with agent-selected tool calls in notebooks 03 and 04.
- Adjust the editor and writer instructions in notebook 05 and observe how the final briefing changes.
- Add another specialized agent, such as a fact checker or headline writer, to the news workflow.
