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

# Tool for ending debate when quality threshold is met
def end_debate(tool_context: ToolContext) -> dict:
    """Signals that the debate should end due to sufficient coverage.
    
    Returns:
        dict: Confirmation of debate termination
    """
    tool_context.actions.escalate = True
    return {
        "status": "debate_ended", 
        "message": "Debate has reached sufficient depth and coverage."
    }

transfer_tool = FunctionTool(func=return_to_greeter)
end_debate_tool = FunctionTool(func=end_debate)

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

# --- 4. Individual Debater Agents for LoopAgent ---
proponent_debater = LlmAgent(
    name="ProponentDebater",
    model=GEMINI_MODEL,
    instruction="""You are the PROPONENT debater in an iterative debate.

**Role Context:**
{role_assignments}

**Your Research:**
{proponent_research_findings}

**Opponent's Research (for context):**
{opponent_research_findings}

**Your Task:**
Make ONE strong argument FOR your position. This is a single round in an ongoing debate.

- Use your research evidence effectively  
- Be persuasive but concise (2-3 sentences)
- Stay focused on your PRO position
- If previous rounds have occurred, build on the discussion naturally

If this feels like an advanced round (after several exchanges) and you believe the key points have been thoroughly covered from both sides, you may call the 'end_debate' tool to conclude the discussion.

Output your argument clearly and persuasively.""",
    description="Makes individual pro arguments in the iterative debate.",
    tools=[end_debate_tool],
    output_key="current_round"
)

opponent_debater = LlmAgent(
    name="OpponentDebater", 
    model=GEMINI_MODEL,
    instruction="""You are the OPPONENT debater in an iterative debate.

**Role Context:**
{role_assignments}

**Your Research:**
{opponent_research_findings}

**Proponent's Research (for context):**
{proponent_research_findings}

**Your Task:**
Make ONE strong argument AGAINST the position. This is a single round in an ongoing debate.

- Use your research evidence strategically
- Be persuasive but concise (2-3 sentences)  
- Stay focused on your AGAINST position
- If previous rounds have occurred, respond to the discussion naturally

If this feels like an advanced round (after several exchanges) and you believe the key points have been thoroughly covered from both sides, you may call the 'end_debate' tool to conclude the discussion.

Output your counter-argument clearly and persuasively.""",
    description="Makes individual opposing arguments in the iterative debate.",
    tools=[end_debate_tool],
    output_key="current_round"
)

# --- 5. LoopAgent for Iterative Debate Rounds ---
iterative_debate_loop = LoopAgent(
    name="IterativeDebateLoop",
    description="Conducts real iterative debate rounds between Proponent and Opponent agents.",
    sub_agents=[proponent_debater, opponent_debater],
    max_iterations=8  # 4 rounds each side (can be dynamic based on complexity)
)

# --- 6. Debate History Aggregator ---
debate_aggregator = LlmAgent(
    name="DebateAggregator",
    model=GEMINI_MODEL,
    instruction="""You compile the iterative debate rounds into a readable format.

**Role Context:**
{role_assignments}

**Research Background:**
Proponent Research: {proponent_research_findings}
Opponent Research: {opponent_research_findings}

**Iterative Rounds:**
{current_round}

**Your Task:**
Format the debate rounds into a clear, readable structure:

**DEBATE ROUNDS:**

**Round 1 - Proponent Opening:**
[First proponent argument]

**Round 1 - Opponent Response:**  
[First opponent argument]

**Round 2 - Proponent:** 
[Second proponent argument]

**Round 2 - Opponent:**
[Second opponent argument]

[Continue for all rounds that occurred...]

Present the rounds chronologically and clearly label each turn.""",
    description="Aggregates the iterative debate rounds into a formatted structure.",
    output_key="debate_rounds"
)

# --- 7. Debate Summarizer ---
debate_summarizer = LlmAgent(
    name="DebateSummarizerAgent", 
    model=GEMINI_MODEL,
    instruction="""You provide a balanced summary of the entire iterative debate.

Role Assignments: {role_assignments}
Proponent Research: {proponent_research_findings}
Opponent Research: {opponent_research_findings}
Debate Rounds: {debate_rounds}

Review all the information from the iterative debate process to create a comprehensive summary.

Include:
1. **Topic Overview:** Restate the debate question
2. **Key Arguments:** Main points from both Proponent and Opponent across all rounds
3. **Evidence Presented:** Important facts/research from both sides
4. **Round Evolution:** How arguments developed through the iterations
5. **Points of Contention:** Where the sides fundamentally disagreed
6. **Debate Quality:** Note the depth achieved through iterative exchange
7. **Complexity Note:** Acknowledge the nuanced nature of the issue

After providing your complete summary, use the 'return_to_greeter' tool to transfer control back to the DebateTeamGreeter.

Maintain objectivity and present both sides fairly.""",
    description="Summarizes the entire iterative debate with balanced analysis and returns to greeter.",
    output_key="final_debate_summary",
    tools=[transfer_tool]
)

# --- 8. Enhanced Sequential Debate Workflow ---
debate_workflow = SequentialAgent(
    name="AIDebateWorkflow",
    description="Executes the complete iterative debate process using LoopAgent for real debate rounds.",
    sub_agents=[
        role_assignment_agent,      # Step 1: Define debate positions  
        parallel_stance_researcher, # Step 2: Research both sides
        iterative_debate_loop,     # Step 3: Conduct REAL iterative debate rounds
        debate_aggregator,         # Step 4: Format the rounds
        debate_summarizer          # Step 5: Summarize results
    ]
)

# --- 9. Greeter (Root Agent) ---
root_agent = LlmAgent(
    name="DebateTeamGreeter",
    model=GEMINI_MODEL,
    instruction="""You are the welcoming host for an advanced AI Debate Team featuring ITERATIVE DEBATE ROUNDS.

Your job is to:
1. **If this is a greeting** (like "hello", "hi", "hey", etc.):
   - Warmly introduce yourself and the AI Debate Team
   - Explain the enhanced process: "We'll research both sides, then conduct REAL iterative debate rounds where our Proponent and Opponent agents engage in back-and-forth discussion, and provide a balanced summary"
   - Ask them: "What topic would you like us to debate today?"
   - Output just your greeting and question

2. **If this appears to be a debate topic** (like "renewable energy", "space exploration", etc.):
   - Confirm the topic: "Excellent! Let's conduct an iterative debate on: [topic]"
   - Transfer to your sub-agent 'AIDebateWorkflow' to begin the comprehensive analysis
   - The workflow will handle role assignment, research, REAL iterative debate rounds, and summary

3. **If returning after a debate summary**:
   - Thank them for the engaging iterative debate
   - Ask: "Would you like to explore another topic? I'm ready for the next iterative debate!"
   - If they provide a new topic, repeat step 2

Be conversational and emphasize the iterative, back-and-forth nature of the debate system. Once you have a clear debate topic, transfer control to AIDebateWorkflow.""",
    description="Greets users, introduces the iterative debate process, transfers to workflow, and handles follow-ups.",
    output_key="debate_topic",
    sub_agents=[debate_workflow]
)