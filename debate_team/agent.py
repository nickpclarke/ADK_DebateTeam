# =============================================================================
# AI DEBATE TEAM - Multi-Agent System using Google Agent Development Kit (ADK)
# =============================================================================
# This file demonstrates advanced ADK patterns including:
# - Sequential Agents (step-by-step workflow)
# - Parallel Agents (concurrent execution)
# - Loop Agents (iterative back-and-forth interaction)
# - Function Tools (custom capabilities for agents)
# - Agent-to-Agent transfers and escalation
# =============================================================================

# --- IMPORTS ---
# These imports bring in the core ADK classes and tools we need
from google.adk.agents import Agent, LlmAgent, ParallelAgent, SequentialAgent, LoopAgent
# Agent: Base class for all agents
# LlmAgent: An agent powered by Large Language Models (like Gemini)
# ParallelAgent: Runs multiple sub-agents simultaneously 
# SequentialAgent: Runs sub-agents one after another in order
# LoopAgent: Runs sub-agents in a loop for iterative interactions

from google.adk.tools import google_search, FunctionTool
# google_search: Built-in tool that lets agents search Google
# FunctionTool: Wrapper to turn Python functions into agent tools

from google.adk.tools import ToolContext
# ToolContext: Special object passed to tool functions that provides
# agent control capabilities like transfers and escalation

# --- CONFIGURATION ---
# This constant defines which AI model our agents will use
# Gemini 2.5 Flash is Google's latest fast language model
GEMINI_MODEL = "gemini-2.5-flash-preview-04-17"

# --- CUSTOM TOOL FUNCTIONS ---
# In ADK, we can create custom tools by writing Python functions
# These functions get special powers through the ToolContext parameter

def return_to_greeter(tool_context: ToolContext) -> dict:
    """
    Custom tool that transfers control back to the DebateTeamGreeter agent.
    
    This demonstrates ADK's agent transfer capability - agents can hand off
    control to other agents in the system.
    
    Args:
        tool_context (ToolContext): Special ADK object that provides agent
                                   control capabilities like transfers
    
    Returns:
        dict: Status message confirming the transfer
        
    ADK Pattern Note:
        - tool_context.actions.transfer_to_agent = "AgentName" causes a transfer
        - The named agent must exist in the current agent's sub_agents
    """
    # This line tells ADK to transfer control to the DebateTeamGreeter agent
    tool_context.actions.transfer_to_agent = "DebateTeamGreeter"
    
    # Return a dictionary with status information
    # Tools should always return structured data (dict/list/str)
    return {
        "status": "success", 
        "message": "Transferring back to the greeter for the next debate topic."
    }

def end_debate(tool_context: ToolContext) -> dict:
    """
    Custom tool that signals the debate should end due to sufficient coverage.
    
    This demonstrates ADK's escalation capability - agents can signal that
    a loop or process should terminate early.
    
    Args:
        tool_context (ToolContext): Special ADK object that provides agent
                                   control capabilities like escalation
    
    Returns:
        dict: Status message confirming the debate termination
        
    ADK Pattern Note:
        - tool_context.actions.escalate = True breaks out of LoopAgent iterations
        - This is how agents can intelligently end iterative processes
    """
    # This line tells ADK to escalate (end the current loop/process)
    tool_context.actions.escalate = True
    
    # Return confirmation that the debate has ended
    return {
        "status": "debate_ended", 
        "message": "Debate has reached sufficient depth and coverage."
    }

# --- TOOL CREATION ---
# Convert our Python functions into ADK tools that agents can use
# FunctionTool wraps a Python function and makes it available to agents
transfer_tool = FunctionTool(func=return_to_greeter)
end_debate_tool = FunctionTool(func=end_debate)

# Tool for transferring to the debate workflow
def start_debate_workflow(tool_context: ToolContext) -> dict:
    """Transfers control to the AIDebateWorkflow to begin the debate process.
    
    Returns:
        dict: Confirmation of transfer to debate workflow
    """
    tool_context.actions.transfer_to_agent = "AIDebateWorkflow"
    return {
        "status": "success", 
        "message": "Transferring to the debate workflow to begin analysis."
    }

start_workflow_tool = FunctionTool(func=start_debate_workflow)

# =============================================================================
# AGENT DEFINITIONS
# =============================================================================
# Each agent is an LlmAgent with specific instructions and capabilities
# The instruction field is like a detailed prompt that defines the agent's role

# --- 1. ROLE ASSIGNMENT AGENT ---
# This agent analyzes a debate topic and defines clear positions for both sides
role_assignment_agent = LlmAgent(
    # Name: Unique identifier for this agent in the system
    name="RoleAssignmentAgent",
    
    # Model: Which AI model to use (defined in our constant above)
    model=GEMINI_MODEL,
    
    # Instruction: The "prompt" that defines this agent's behavior and role
    # {debate_topic} is a template variable that gets filled in at runtime
    instruction="""You define the debate positions for a given topic.

You will receive a debate topic from the previous agent. Your task is to:
1. Analyze the topic and rephrase it into a clear, debatable question if needed
2. Define two distinct positions: Proponent (FOR) and Opponent (AGAINST)  
3. Outline the main argument for each side (1-2 sentences each)

The debate topic will be provided in the conversation context from the previous agent interaction.

<br><br>

## 📋 **DEBATE SETUP**

<br>

**Debate Topic:** [Restate the topic clearly]<br>
**Debate Question:** [Clear, focused debate question]<br><br>

**Proponent Position:** [What they argue FOR]<br>
**Proponent Main Argument:** [Their core reasoning]<br><br>

**Opponent Position:** [What they argue AGAINST]<br>  
**Opponent Main Argument:** [Their core reasoning]<br><br>

Be clear and balanced in defining both positions.<br><br>""",
    
    # Description: Human-readable description of what this agent does
    description="Defines Proponent and Opponent roles and their main arguments for the debate topic.",
    
    # Output_key: This is crucial! It defines what variable name this agent's
    # output will be stored under for use by other agents in the workflow
    output_key="role_assignments"
)

# --- 2. RESEARCH AGENTS ---
# These agents use Google Search to find supporting evidence for each debate position
# Notice how they reference {role_assignments} - this comes from the agent above

proponent_researcher = LlmAgent(
    name="ProponentResearcher",
    model=GEMINI_MODEL,
    
    # This instruction shows how agents can reference outputs from previous agents
    # {role_assignments} gets filled with the output from role_assignment_agent
    instruction="""You research supporting evidence for the Proponent position in the debate.

Role Assignments: {role_assignments}

Look at the role assignments and find 2-3 strong supporting points, facts, or examples that support the Proponent's stance. Use Google Search to find current, credible information.

<br><br>

## 🟢 **PROPONENT RESEARCH FINDINGS**

<br>

Focus on:
- Statistical evidence<br>
- Expert opinions<br>  
- Real-world examples<br>
- Research findings<br><br>

Summarize your findings concisely but persuasively.<br><br>  

### 📚 **Key Reference Articles (List of Key Sources):**<br>
For each significant article/document used:<br>
* <a href="[Full URL]" target="_blank">[Article Title]</a><br><br>""",
    
    # Tools: List of tools this agent can use
    # google_search is a built-in ADK tool for web searches
    tools=[google_search],
    
    description="Researches supporting points for the Proponent's stance.",
    
    # This agent's output will be available as {proponent_research_findings}
    output_key="proponent_research_findings"
)

opponent_researcher = LlmAgent(
    name="OpponentResearcher", 
    model=GEMINI_MODEL,
    
    # Nearly identical to proponent_researcher but focuses on the opposing side
    instruction="""You research supporting evidence for the Opponent position in the debate.

Role Assignments: {role_assignments}

Look at the role assignments and find 2-3 strong supporting points, facts, or examples that support the Opponent's stance. Use Google Search to find current, credible information.

<br><br>

## 🔴 **OPPONENT RESEARCH FINDINGS**

<br>

Focus on:
- Statistical evidence<br>
- Expert opinions<br>
- Real-world examples<br>  
- Research findings<br><br>

Summarize your findings concisely but persuasively.<br><br>  

### 📚 **Key Reference Articles (List of Key Sources):**<br>
For each significant article/document used:<br>
* <a href="[Full URL]" target="_blank">[Article Title]</a><br><br>""",
    
    # Same tools as proponent_researcher
    tools=[google_search],
    
    description="Researches supporting points for the Opponent's stance.",
    
    # This agent's output will be available as {opponent_research_findings}
    output_key="opponent_research_findings"
)

# --- 3. PARALLEL RESEARCH COORDINATOR ---
# ParallelAgent runs multiple sub-agents at the same time (concurrently)
# This is more efficient than running researchers one after another
parallel_stance_researcher = ParallelAgent(
    name="ParallelStanceResearcher",
    description="Researches supporting evidence for both debate positions concurrently.",
    
    # Sub_agents: List of agents to run in parallel
    # Both researchers will run simultaneously, saving time
    sub_agents=[proponent_researcher, opponent_researcher]
    
    # ADK Pattern Note: ParallelAgent collects outputs from all sub-agents
    # So we'll have both {proponent_research_findings} and {opponent_research_findings}
    # available to subsequent agents in the workflow
)

# --- 4. INDIVIDUAL DEBATER AGENTS FOR LOOP ITERATION ---
# These agents will engage in back-and-forth debate rounds
# They're designed to work within a LoopAgent for iterative interaction

proponent_debater = LlmAgent(
    name="ProponentDebater",
    model=GEMINI_MODEL,
    
    # This instruction shows how agents can access multiple previous outputs
    # Notice {role_assignments}, {proponent_research_findings}, and {opponent_research_findings}
    instruction="""You are the PROPONENT debater in an iterative debate.

**Role Context:**
{role_assignments}

**Your Research:**
{proponent_research_findings}

**Opponent's Research (for context):**
{opponent_research_findings}

**Your Task:**
Make ONE strong argument FOR your position. This is a single round in an ongoing debate.

**IMPORTANT:** Start your response with "🟢 **PROPONENT:**" to clearly identify your role.

- Use your research evidence effectively  
- Be persuasive but concise (2-3 sentences)
- Stay focused on your PRO position
- If previous rounds have occurred, build on the discussion naturally

If this feels like an advanced round (after several exchanges) and you believe the key points have been thoroughly covered from both sides, you may call the 'end_debate' tool to conclude the discussion.

Format:
<br><br>  
🟢 **PROPONENT:**<br>  
[Your clear, persuasive argument]<br><br>""",
    
    description="Makes individual pro arguments in the iterative debate.",
    
    # This agent can use the end_debate tool to terminate the loop early
    tools=[end_debate_tool],
    
    # All debater outputs use the same key - this creates a conversation thread
    output_key="current_round"
)

opponent_debater = LlmAgent(
    name="OpponentDebater", 
    model=GEMINI_MODEL,
    
    # Similar to proponent_debater but argues the opposing position
    instruction="""You are the OPPONENT debater in an iterative debate.

**Role Context:**
{role_assignments}

**Your Research:**
{opponent_research_findings}

**Proponent's Research (for context):**
{proponent_research_findings}

**Your Task:**
Make ONE strong argument AGAINST the position. This is a single round in an ongoing debate.

**IMPORTANT:** Start your response with "🔴 **OPPONENT:**" to clearly identify your role.

- Use your research evidence strategically
- Be persuasive but concise (2-3 sentences)  
- Stay focused on your AGAINST position
- If previous rounds have occurred, respond to the discussion naturally

If this feels like an advanced round (after several exchanges) and you believe the key points have been thoroughly covered from both sides, you may call the 'end_debate' tool to conclude the discussion.

Format:
<br><br>   
🔴 **OPPONENT:**<br>      
[Your clear, persuasive counter-argument]<br><br>""",
    
    description="Makes individual opposing arguments in the iterative debate.",
    
    # Both debaters can end the debate when they feel it's complete
    tools=[end_debate_tool],
    
    # Same output_key as proponent - creates a shared conversation thread
    output_key="current_round"
)

# --- 5. LOOP AGENT FOR ITERATIVE DEBATE ROUNDS ---
# LoopAgent repeatedly cycles through its sub-agents until stopped
# This creates the back-and-forth debate dynamic
iterative_debate_loop = LoopAgent(
    name="IterativeDebateLoop",
    description="Conducts real iterative debate rounds between Proponent and Opponent agents.",
    
    # Sub_agents: The agents that will alternate in the loop
    # Order matters! Proponent goes first, then Opponent, then repeat
    sub_agents=[proponent_debater, opponent_debater],
    
    # Max_iterations: Safety limit to prevent infinite loops
    # With 2 agents, this allows 4 rounds each (8 total exchanges)
    max_iterations=8
    
    # ADK Pattern Note: LoopAgent will continue until:
    # 1. max_iterations is reached, OR
    # 2. An agent calls tool_context.actions.escalate = True (our end_debate tool)
)

# --- 6. DEBATE STRATEGIC ANALYST ---
# This agent provides deep analysis of the debate performance and strategy instead of just regurgitating rounds
debate_aggregator = LlmAgent(
    name="DebateStrategicAnalyst",
    model=GEMINI_MODEL,
    
    # This agent analyzes the debate rounds for strategic insights and quality assessment
    instruction="""You are a strategic debate analyst providing deep insights into the iterative debate performance.

**Available Information:**
Role Context: {role_assignments}
Proponent Research: {proponent_research_findings}
Opponent Research: {opponent_research_findings}
Debate Rounds: {current_round}

**Your Analysis Task:**<br>
Provide a strategic analysis of the debate performance with these key insights:<br><br>

<br><br> 🎯 **STRATEGIC DEBATE ANALYSIS**

<br>

### **1. Argument Strength Assessment**<br>
- Rate each side's strongest and weakest arguments (1-10 scale)<br>
- Identify which evidence was most/least compelling<br>
- Note any logical fallacies or reasoning gaps<br><br>

### **2. Tactical Performance**<br>
- **Proponent Strategy:** How effectively did they advance their position?<br>
- **Opponent Strategy:** How well did they counter and create doubt?<br>
- **Missed Opportunities:** What stronger arguments could each side have made?<br><br>

### **3. Evidence Utilization**<br>
- Which research findings were used most effectively?<br>
- What supporting evidence went unused?<br>
- Were there any unsupported claims?<br><br>

### **4. Debate Flow & Momentum**<br>
- **Opening Round:** Who established stronger initial framing?<br>
- **Middle Rounds:** Where did momentum shift and why?<br>
- **Closing Rounds:** Who delivered more compelling final arguments?<br><br>

### **5. Critical Turning Points**<br>
- Identify 1-2 moments that changed the debate trajectory<br>
- Explain what made these exchanges particularly effective<br><br>

### **6. Debate Quality Metrics**<br>
- **Depth:** How thoroughly were key issues explored? (1-10)<br>
- **Nuance:** Did arguments acknowledge complexity? (1-10)<br>
- **Civility:** Professional tone and respectful disagreement? (1-10)<br>
- **Innovation:** Any surprising or creative arguments? (1-10)<br><br>

### **7. Strategic Recommendations**<br>
- What would strengthen the Proponent's case in future debates?<br>
- How could the Opponent improve their counter-arguments?<br>
- What additional evidence or angles would be valuable?<br><br>

**Format Guidelines:**<br>
- Use clear headings with emojis for readability<br>
- Include specific examples from the debate rounds<br>
- Provide numerical ratings where indicated<br>
- Be objective but insightful - help users understand argumentation effectiveness<br>
- Focus on strategic analysis, not just content repetition<br><br>""",
    
    description="Analyzes debate strategy, argument strength, and provides tactical insights rather than just reformatting rounds.",
    
    # Output becomes available as {debate_analysis} for the final summary
    output_key="debate_analysis"
)

# --- 7. DEBATE SUMMARIZER ---
# The final agent that creates a comprehensive summary and returns control
debate_summarizer = LlmAgent(
    name="DebateSummarizerAgent", 
    model=GEMINI_MODEL,
    
    # This agent has access to ALL previous outputs from the entire workflow
    instruction="""You are the final judge who declares the debate winner and provides conclusive takeaways.

Based on the strategic analysis provided, your job is to make the FINAL CALL and provide decisive conclusions - NOT to repeat the detailed analysis.<br><br>

Available Information:<br>
- Role Assignments: {role_assignments}<br>
- Strategic Analysis: {debate_analysis}<br><br>

<br><br> 🏆 **FINAL DEBATE JUDGMENT**

<br>

Your task is to provide a crisp, decisive conclusion:<br><br>

### **🥇 DEBATE WINNER**<br>
**Winner:** [Proponent OR Opponent]<br>
**Margin of Victory:** [Decisive/Clear/Narrow]<br>
**Key Reason for Victory:** [1-2 sentences explaining why they won]<br><br>

### **⚡ DECISIVE MOMENTS**<br>
**Game-Changer:** [The single most impactful argument or exchange]<br>
**Turning Point:** [When momentum shifted decisively]<br><br>

### **🎯 PERFORMANCE GRADES**<br>
**Proponent Overall:** [A-F grade] - [One sentence why]<br>
**Opponent Overall:** [A-F grade] - [One sentence why]<br><br>

### **💡 KEY TAKEAWAYS**<br>
**For the Topic:** [What did this debate reveal about the issue?]<br>
**For Future Debaters:** [One key lesson for improving arguments]<br>
**Most Compelling Evidence:** [What research/data was most persuasive?]<br><br>

### **🔥 DEBATE HIGHLIGHTS**<br>
**Best Proponent Moment:** [Their strongest argument]<br>
**Best Opponent Moment:** [Their strongest counter]<br>
**Missed Opportunity:** [What could have changed the outcome?]<br><br>

**JUDGE'S FINAL VERDICT:** [2-3 sentences wrapping up why this winner deserved victory and what made this debate valuable]<br><br>

**Important:** Be decisive! Make clear judgments based on the strategic analysis. Don't hedge or repeat analysis - provide conclusions and call a winner!<br><br>

After providing your judgment, use the 'return_to_greeter' tool to transfer control back to the DebateTeamGreeter.<br><br>""",
    
    description="Final judge who declares the debate winner and provides decisive conclusions without repeating analysis.",
    
    output_key="final_debate_summary",
    
    # This agent uses the transfer tool to return control to the greeter
    tools=[transfer_tool]
)

# --- 8. ENHANCED SEQUENTIAL DEBATE WORKFLOW ---
# SequentialAgent runs sub-agents one after another in a specific order
# This creates our main debate pipeline
debate_workflow = SequentialAgent(
    name="AIDebateWorkflow",
    description="Executes the complete iterative debate process using LoopAgent for real debate rounds.",
    
    # Sub_agents: The complete workflow pipeline in order
    sub_agents=[
        role_assignment_agent,      # Step 1: Define debate positions  
        parallel_stance_researcher, # Step 2: Research both sides (in parallel)
        iterative_debate_loop,     # Step 3: Conduct iterative debate rounds
        debate_aggregator,         # Step 4: Analyze debate strategy and effectiveness
        debate_summarizer          # Step 5: Create final summary integrating strategic insights
    ]
    
    # ADK Pattern Note: Each agent in the sequence has access to outputs
    # from all previous agents through template variables like {role_assignments}
)

# --- 9. GREETER (ROOT AGENT) ---
# This is the main entry point - the agent users interact with first
# It handles greetings, topic collection, and workflow coordination
root_agent = LlmAgent(
    name="DebateTeamGreeter",
    model=GEMINI_MODEL,
    
    # Tools: The greeter can use the start_workflow_tool to transfer to the debate team
    tools=[start_workflow_tool],
    
    # This instruction handles multiple conversation states and demonstrates
    # agent transfer patterns
    instruction="""You are the welcoming host for an advanced AI Debate Team featuring ITERATIVE DEBATE ROUNDS.

Your job is to identify debate topics and initiate the debate workflow. Be flexible with user input:

**TOPIC DETECTION AND HANDLING:**

1. **If this is a greeting** (like "hello", "hi", "hey", etc.):
   - Warmly introduce yourself and the AI Debate Team
   - Explain the process: "We'll research both sides, then conduct REAL iterative debate rounds where our Proponent and Opponent agents engage in back-and-forth discussion, and provide a balanced summary"
   - Ask them: "What topic would you like us to debate today?"
   - Output just your greeting and question (do NOT transfer yet)

2. **If you can identify ANY debate topic** from the input (regardless of how it's phrased):
   - Extract the core topic from their message  
   - Say: "Excellent! Let's conduct an iterative debate on: [TOPIC]"
   - Output the topic on the final line for capture
   - Use the 'start_debate_workflow' tool to transfer to the debate team

3. **If returning after a debate summary**:
   - Thank them for the engaging iterative debate
   - Ask: "Would you like to explore another topic? I'm ready for the next iterative debate!"
   - When they provide a new topic, treat it as case 2

**TOPIC EXTRACTION EXAMPLES:**
- Input: "renewable energy" → Output ends with: "renewable energy"
- Input: "Should we use nuclear power?" → Output ends with: "nuclear power"  
- Input: "I want to debate climate change vs economic growth" → Output ends with: "climate change vs economic growth"
- Input: "artificial intelligence ethics" → Output ends with: "artificial intelligence ethics"
- Input: "space exploration is important" → Output ends with: "space exploration"
- Input: "the best pet" → Output ends with: "the best pet"

**OUTPUT FORMAT EXAMPLE:**
"Excellent! Let's conduct an iterative debate on nuclear power!
I'm now transferring this topic to our debate workflow team.  "

**KEY REQUIREMENTS:**
- Be flexible - users may provide topics in many different ways
- Always extract and confirm the topic before transferring
- Always make the topic clear in your response when transferring
- Transfer to AIDebateWorkflow as soon as you have a clear topic
- Don't require users to say hello first - if they give a topic directly, go with it!

Be conversational and emphasize the iterative, back-and-forth nature of the debate system.""",
    
    description="Greets users, introduces the iterative debate process, transfers to workflow, and handles follow-ups.",
    
    # The topic provided by the user becomes available as {debate_topic}
    output_key="debate_topic",
    
    # Sub_agents: The greeter can transfer control to the full workflow
    sub_agents=[debate_workflow]
    
    # ADK Pattern Note: When this agent transfers to AIDebateWorkflow,
    # the workflow agents will have access to {debate_topic} from this agent's output
)

# =============================================================================
# SUMMARY OF ADK PATTERNS DEMONSTRATED
# =============================================================================
# 1. LlmAgent: Individual AI agents with specific roles and instructions
# 2. SequentialAgent: Run agents in order (pipeline pattern)
# 3. ParallelAgent: Run agents simultaneously (efficiency pattern)
# 4. LoopAgent: Run agents repeatedly (iteration pattern)
# 5. FunctionTool: Custom Python functions as agent capabilities
# 6. Agent Transfer: Hand off control between agents
# 7. Escalation: Early termination of loops/processes
# 8. Template Variables: Share data between agents using {variable_name}
# 9. Output Keys: Define how agent outputs become available to others
# 10. Tool Context: Special capabilities for agent control and coordination
# =============================================================================