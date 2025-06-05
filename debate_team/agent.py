from google.adk.agents import Agent, LlmAgent, ParallelAgent, SequentialAgent, LoopAgent
from google.adk.tools import google_search, FunctionTool
from google.adk.tools import ToolContext

GEMINI_MODEL = "gemini-2.5-flash-preview-04-17"

# Tool for transferring back to greeter
def return_to_greeter(tool_context: ToolContext) -> dict:
    """Transfers control back to the DebateTeamGreeter agent.
    
    Returns:
        dict: Confirmation of transfer
    """
    tool_context.actions.transfer_to_agent = "DebateTeamGreeter"
    return {
        "status": "success", 
        "message": "Transferring back to the greeter for the next debate topic."
    }

transfer_tool = FunctionTool(func=return_to_greeter)

# --- 1. RoleAssignmentAgent ---
role_assignment_agent = LlmAgent(
    name="RoleAssignmentAgent",
    model=GEMINI_MODEL,
    instruction="""You define the debate positions for a given topic.

Based on the topic provided ({debate_topic}), your task is to:
1. Analyze the topic and rephrase it into a clear, debatable question if needed
2. Define two distinct positions: Proponent (FOR) and Opponent (AGAINST)  
3. Outline the main argument for each side (1-2 sentences each)

Output Format:
**Debate Question:** [Clear, focused debate question]

**Proponent Position:** [What they argue FOR]
**Proponent Main Argument:** [Their core reasoning]

**Opponent Position:** [What they argue AGAINST]  
**Opponent Main Argument:** [Their core reasoning]

Be clear and balanced in defining both positions.""",
    description="Defines Proponent and Opponent roles and their main arguments for the debate topic.",
    output_key="role_assignments"
)

# --- 2. Research Agents ---
proponent_researcher = LlmAgent(
    name="ProponentResearcher",
    model=GEMINI_MODEL,
    instruction="""You research supporting evidence for the Proponent position in the debate.

Role Assignments: {role_assignments}

Look at the role assignments and find 2-3 strong supporting points, facts, or examples that support the Proponent's stance. Use Google Search to find current, credible information.

Focus on:
- Statistical evidence
- Expert opinions  
- Real-world examples
- Research findings

Summarize your findings concisely but persuasively.""",
    tools=[google_search],
    description="Researches supporting points for the Proponent's stance.",
    output_key="proponent_research_findings"
)

opponent_researcher = LlmAgent(
    name="OpponentResearcher", 
    model=GEMINI_MODEL,
    instruction="""You research supporting evidence for the Opponent position in the debate.

Role Assignments: {role_assignments}

Look at the role assignments and find 2-3 strong supporting points, facts, or examples that support the Opponent's stance. Use Google Search to find current, credible information.

Focus on:
- Statistical evidence
- Expert opinions
- Real-world examples  
- Research findings

Summarize your findings concisely but persuasively.""",
    tools=[google_search],
    description="Researches supporting points for the Opponent's stance.",
    output_key="opponent_research_findings"
)

# --- 3. Parallel Research Coordinator ---
parallel_stance_researcher = ParallelAgent(
    name="ParallelStanceResearcher",
    description="Researches supporting evidence for both debate positions concurrently.",
    sub_agents=[proponent_researcher, opponent_researcher]
)

# --- 4. Debate Round Executor ---
debate_round_executor = LlmAgent(
    name="DebateRoundExecutor",
    model=GEMINI_MODEL,
    instruction="""You are conducting a structured debate with multiple rounds.

Role Assignments: {role_assignments}
Proponent Research: {proponent_research_findings}
Opponent Research: {opponent_research_findings}

Conduct a 3-round debate:

**Round 1 - Proponent Opening:**
Present the main argument FOR the topic using the proponent research. (2-3 sentences)

**Round 2 - Opponent Response:**
Present the main argument AGAINST the topic using the opponent research. (2-3 sentences)

**Round 3 - Proponent Rebuttal:**
Provide a final rebuttal addressing the opponent's concerns. (2-3 sentences)

Format each round clearly and use the research findings to support each position.""",
    description="Conducts the complete debate sequence in structured rounds.",
    output_key="debate_rounds"
)

# --- 6. Debate Summarizer ---
debate_summarizer = LlmAgent(
    name="DebateSummarizerAgent", 
    model=GEMINI_MODEL,
    instruction="""You provide a balanced summary of the entire debate.

Role Assignments: {role_assignments}
Proponent Research: {proponent_research_findings}
Opponent Research: {opponent_research_findings}
Debate Rounds: {debate_rounds}

Review all the information from the debate process to create a comprehensive summary.

Include:
1. **Topic Overview:** Restate the debate question
2. **Key Arguments:** Main points from both Proponent and Opponent
3. **Evidence Presented:** Important facts/research from both sides
4. **Points of Contention:** Where the sides fundamentally disagree
5. **Complexity Note:** Acknowledge the nuanced nature of the issue

After providing your complete summary, use the 'return_to_greeter' tool to transfer control back to the DebateTeamGreeter.

Maintain objectivity and present both sides fairly.""",
    description="Summarizes the entire debate with balanced analysis and returns to greeter.",
    output_key="final_debate_summary",
    tools=[transfer_tool]
)

# --- 5. Sequential Debate Workflow ---
debate_workflow = SequentialAgent(
    name="AIDebateWorkflow",
    description="Executes the complete debate process in sequential order.",
    sub_agents=[
        role_assignment_agent,      # Step 1: Define debate positions  
        parallel_stance_researcher, # Step 2: Research both sides
        debate_round_executor,     # Step 3: Conduct debate rounds
        debate_summarizer          # Step 4: Summarize results
    ]
)

# --- 7. Greeter (Root Agent) ---
root_agent = LlmAgent(
    name="DebateTeamGreeter",
    model=GEMINI_MODEL,
    instruction="""You are the welcoming host for an advanced AI Debate Team.

Your job is to:
1. **If this is a greeting** (like "hello", "hi", "hey", etc.):
   - Warmly introduce yourself and the AI Debate Team
   - Explain the process: "We'll research both sides, conduct a structured debate, and provide a balanced summary"
   - Ask them: "What topic would you like us to debate today?"
   - Output just your greeting and question

2. **If this appears to be a debate topic** (like "renewable energy", "space exploration", etc.):
   - Confirm the topic: "Great! Let's debate: [topic]"
   - Transfer to your sub-agent 'AIDebateWorkflow' to begin the comprehensive analysis
   - The workflow will handle role assignment, research, debate rounds, and summary

3. **If returning after a debate summary**:
   - Thank them for the interesting debate
   - Ask: "Would you like to explore another topic? I'm ready for the next debate!"
   - If they provide a new topic, repeat step 2

Be conversational and helpful. Once you have a clear debate topic, transfer control to AIDebateWorkflow.""",
    description="Greets users, introduces the debate process, transfers to workflow, and handles follow-ups.",
    output_key="debate_topic",
    sub_agents=[debate_workflow]
)