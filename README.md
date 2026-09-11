# Agentsway — Agentic AI Workflows Lab

A small learning repository for exploring **agentic AI workflows** using the
[OpenAI Agents SDK](https://github.com/openai/openai-agents-python). It shows how to define an
AI agent, give it instructions, and run it — a starting point for experimenting with agentic AI
and AI agents.

## Prerequisites

- Python 3.9+
- An [OpenAI API key](https://platform.openai.com/api-keys)
- (Optional) A [Gemini API key](https://aistudio.google.com/api-keys), if you want to experiment
  with `google-genai` instead of / alongside OpenAI
- A [Google account](https://accounts.google.com/signup) with access to
  [Google Colab](https://colab.research.google.com/), since this lab is designed to be run in a
  Colab notebook

## Running on Google Colab

This lab is meant to be run on [Google Colab](https://colab.research.google.com/) so you don't
need to set up Python locally.

1. Sign in with a Google account and open [colab.research.google.com](https://colab.research.google.com/).
2. Upload and open [notebooks/01_openai_basic_agent.ipynb](notebooks/01_openai_basic_agent.ipynb).
3. Install dependencies by running the first code cell:

   ```python
   %pip install -q openai-agents requests google-genai
   ```

4. Add `OPENAI_API_KEY` to Colab's **Secrets** panel (the key icon in the left sidebar).
5. Run the remaining cells in order.

## Setup (local)

1. **Create and activate a virtual environment**

   ```
   python -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies**

   ```
   pip install -r requirements.txt
   ```

3. **Set your API key**

   ```
   export OPENAI_API_KEY=<your api key>
   ```

4. **Run the agent**

   ```
   python src/workflow.py
   ```

## Project structure

| File | Purpose |
|---|---|
| [notebooks/01_openai_basic_agent.ipynb](notebooks/01_openai_basic_agent.ipynb) | Ready-to-run OpenAI agent notebook |
| [src/workflow.py](src/workflow.py) | Defines and runs the `Learning Assistant` |
| [requirements.txt](requirements.txt) | Python dependencies (`openai-agents`, `requests`, `google-genai`) |

## How it works

[src/workflow.py](src/workflow.py) defines a single agent and runs it synchronously with a sample prompt:

```python
from agents import Agent, Runner

agent = Agent(
    name="Learning Assistant",
    instructions="You are a helpful AI assistant. Explain things about given topic clearly to a beginner."
)

result = Runner.run_sync(
    starting_agent=agent,
    input="Explain University of Colombo School of Computing Master of Business Analytics Program."
)

print(result.final_output)
```

## Refining agent instructions

The `instructions` field is the agent's system prompt — it shapes tone, scope, and behavior.
Start simple, then add guardrails as needed. For example:

**Minimal:**

```python
instructions="You are a helpful AI assistant. Explain things about given topic clearly to a beginner."
```

**With guardrails:**

```python
instructions="""
You are a helpful, accurate, and beginner-friendly AI assistant.

- Explain things clearly and simply.
- Assume the user may be a beginner.
- Use examples when useful.
- Break complex topics into smaller parts.
- Be concise for simple questions.
- Be detailed when needed.
- Never invent facts.
- If unsure, say so clearly.
"""
```

Try editing the `instructions` in [src/workflow.py](src/workflow.py) and re-running to see how the
agent's responses change.

## Next steps

Ideas for extending this lab:

- Swap the `input` prompt to test different topics.
- Add tools/function calls to the agent (see the
  [Agents SDK docs](https://github.com/openai/openai-agents-python)).
- Chain multiple agents together to build a multi-agent workflow.
- Try `google-genai` as an alternative model provider.
