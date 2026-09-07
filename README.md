# BA2105 — Agentic AI Workflows Lab

A small learning repository for exploring **agentic AI workflows** using the
[OpenAI Agents SDK](https://github.com/openai/openai-agents-python). It shows how to define an
AI agent, give it instructions, and run it — a starting point for experimenting with agentic AI
and AI agents.

## Prerequisites

- Python 3.9+
- An [OpenAI API key](https://platform.openai.com/api-keys)
- (Optional) A [Gemini API key](https://aistudio.google.com/api-keys), if you want to experiment
  with `google-genai` instead of / alongside OpenAI

## Setup

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
   python workflow.py
   ```

## Project structure

| File | Purpose |
|---|---|
| [workflow.py](workflow.py) | Defines and runs the `BA2105 Agent` |
| [requirements.txt](requirements.txt) | Python dependencies (`openai-agents`, `requests`, `google-genai`) |

## How it works

[workflow.py](workflow.py) defines a single agent and runs it synchronously with a sample prompt:

```python
from agents import Agent, Runner

ba2105_agent = Agent(
    name="BA2105 Agent",
    instructions="You are a helpful AI assistant. Explain things about given topic clearly to a beginner."
)

result = Runner.run_sync(
    starting_agent=ba2105_agent,
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

Try editing the `instructions` in [workflow.py](workflow.py) and re-running to see how the
agent's responses change.

## Next steps

Ideas for extending this lab:

- Swap the `input` prompt to test different topics.
- Add tools/function calls to the agent (see the
  [Agents SDK docs](https://github.com/openai/openai-agents-python)).
- Chain multiple agents together to build a multi-agent workflow.
- Try `google-genai` as an alternative model provider.
