# Coursework 01: Agentic AI Workflow Case Study

## Objective

Identify a real, low-risk workplace process that could be improved with an agentic AI workflow. Analyse the current process, design the workflow, define its agents and prompts, and build a small prototype if practical.

This case study will be the foundation for Coursework 02: a research paper about the proposed solution.

## Learning outcomes

- Identify a suitable workplace use case for agentic AI.
- Distinguish a manual process from an agentic workflow.
- Define focused agent roles, tools, prompts, and handoffs.
- Identify human review and approval points.
- Communicate an AI workflow with diagrams and a written proposal.

## Choose a use case

Choose one narrow, repetitive, low-risk process from a real setting you know: your workplace, office, internship, volunteer role, family business, or student organization. If you do not have access to such a setting, use a realistic office scenario that you can describe clearly. Do not use confidential or personal data in your report or prototype.

Suitable examples:

- Weekly competitor or industry-news research and summaries
- Categorizing support tickets and drafting responses for human review
- Extracting information from invoices, forms, or reports
- Turning meeting notes into action items and follow-up drafts
- Checking documents against an internal checklist or policy
- Preparing internal knowledge briefs from trusted sources

Avoid high-risk autonomous decisions involving hiring, employee performance, medical care, legal advice, lending, pricing, or customer approvals. These workflows must retain human oversight.

## Report requirements

Submit a 4–6 page report in Markdown, PDF, or document format using these headings.

### 1. Use-case overview

- Workplace context and the problem to solve
- Users or teams affected
- Why the use case matters
- Expected benefits: time saved, quality, consistency, or cost

### 2. Current manual process

Describe the trigger, inputs, people involved, steps, outputs, and pain points. Include a simple current-state process diagram.

### 3. Proposed agentic workflow

Explain which steps are automated, assisted, or kept manual. Identify inputs, outputs, workflow triggers, human review points, limitations, and expected failure cases. Include a proposed workflow diagram.

Mermaid, draw.io, and Excalidraw are all acceptable diagram tools.

### 4. Agent design

Define each agent in a table.

| Agent | Responsibility | Input | Output | Tools or data needed | Human review? |
|---|---|---|---|---|---|
| Research Agent | Finds credible sources | Topic | Source list | Web search | No |
| Review Agent | Checks relevance and risk | Source list | Approved brief | Policy checklist | Yes |

Use focused roles. A good workflow normally has 2–5 agents rather than one agent attempting every task.

### 5. Prompts and tools

Provide the system prompt for at least two proposed agents. Each prompt must define its role, goal, inputs, decision rules, safety boundaries, and output format.

List the tools or data sources each agent needs, such as web search, a knowledge base, email, document retrieval, a calculator, or a database. Explain when each tool may be used.

### 6. Prototype or pseudocode

If possible, build a small proof of concept using a notebook, Python script, or no-code tool. Use public or mock data; real company-system access is not required.

If a prototype is not practical, provide pseudocode or a detailed sequence showing how agents and tools interact.

### 7. Risks, ethics, and evaluation

Discuss privacy, confidential data, access control, incorrect outputs, bias, human escalation, estimated cost, technical limitations, and how success would be measured.

Possible measures include time saved, accuracy, user satisfaction, or reduced repeated work.

## Submission

Submit:

1. A 4–6 page case-study report.
2. Current-state and proposed-workflow diagrams.
3. An optional prototype notebook, script, or pseudocode file.

Do not submit API keys, confidential documents, customer data, employee data, or internal information you are not authorized to share.

## Assessment rubric

| Criterion | Marks |
|---|---:|
| Clear and valuable use-case selection | 15 |
| Accurate analysis of the current manual process | 15 |
| Agentic workflow design and human-review points | 25 |
| Agent roles, prompts, and tool design | 20 |
| Risk, privacy, ethics, and evaluation plan | 15 |
| Prototype, pseudocode, and report clarity | 10 |
| **Total** | **100** |

## Before submitting

- Is the process specific enough for a short report?
- Does each agent have one clear responsibility?
- Are important decisions reviewed by a person?
- Do prompts define accuracy, boundaries, and output format?
- Have you removed confidential and personal information?
