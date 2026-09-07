from agents import Agent, Runner

ba2105_agent = Agent(
    name="BA2105 Agent",
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
)

result = Runner.run_sync(
    starting_agent=ba2105_agent,
    input="Explain Univesity of Colombo School of Computing Master of Business Analytics Program."
)

print(result.final_output)
