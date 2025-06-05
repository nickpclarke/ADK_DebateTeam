# =============================================================================
# DEBATE_TEAM PACKAGE - INITIALIZATION MODULE
# =============================================================================
# This is the __init__.py file for the debate_team package. In Python, any
# directory containing an __init__.py file is treated as a "package" - a
# collection of related modules that can be imported together.
#
# Key concepts demonstrated:
# - Python package structure and organization
# - Module importing and namespace management
# - Making local modules available for import
# - Package initialization patterns
# =============================================================================

"""
AI Debate Team Package

This package contains the multi-agent debate system built with Google's
Agent Development Kit (ADK). It provides sophisticated AI agents that can:

- Assign debate roles for any topic
- Research supporting evidence using Google Search  
- Conduct iterative back-and-forth debate rounds
- Summarize debates with balanced analysis

Main Components:
    agent.py: Contains all the ADK agent definitions and workflow logic

Usage:
    from debate_team.agent import root_agent
    # Now you can use root_agent in your deployment scripts
"""

# --- MODULE IMPORTS ---
# Import the agent module to make it available when someone imports this package
# The dot (.) means "import from the current package directory"
from . import agent

# This import statement does several important things:
#
# 1. **Makes the module available**: When someone writes "from debate_team import agent",
#    Python knows where to find the agent module
#
# 2. **Enables sub-imports**: Allows "from debate_team.agent import root_agent" 
#    to work properly in other files like deploy.py
#
# 3. **Package namespace**: Creates a clean namespace where agent.py becomes
#    accessible as "debate_team.agent" from outside the package
#
# 4. **Lazy loading**: The agent module isn't actually loaded until someone
#    tries to use it, which improves startup performance

# =============================================================================
# PYTHON PACKAGE CONCEPTS FOR BEGINNERS
# =============================================================================
#
# What is a Package?
# ------------------
# A package is a way to organize related Python modules (files) together.
# Think of it like a folder that contains related Python files, but with
# special powers that let you import from it.
#
# Package Structure:
# ------------------
# debate_team/                 <- This is the package directory
#   ├── __init__.py           <- This file (makes it a package)
#   ├── agent.py              <- Module containing our ADK agents
#   └── (other modules...)     <- Could add more modules here
#
# Without __init__.py:
# --------------------
# If this file didn't exist, "debate_team" would just be a regular folder
# and you couldn't write "from debate_team.agent import root_agent"
#
# Import Patterns Enabled:
# ------------------------
# Because of this __init__.py file, these imports work:
#   
#   1. import debate_team                    # Imports the whole package
#   2. import debate_team.agent              # Imports the agent module
#   3. from debate_team import agent         # Imports agent into local namespace
#   4. from debate_team.agent import root_agent  # Imports specific object
#
# Real-World Analogy:
# -------------------
# Think of a package like a library building:
# - The building is the package directory (debate_team/)
# - __init__.py is like the front desk that helps people find things
# - Each module (agent.py) is like a section of books on a specific topic
# - Imports are like asking the front desk "Where can I find the debate agents?"
#
# =============================================================================

# --- FUTURE PACKAGE EXPANSION ---
# As your project grows, you might add more modules to this package:
#
# debate_team/
#   ├── __init__.py          <- This file
#   ├── agent.py             <- Main agent definitions  
#   ├── tools.py             <- Custom tools for agents
#   ├── config.py            <- Configuration management
#   ├── utils.py             <- Helper functions
#   └── tests/               <- Test modules
#       ├── __init__.py
#       ├── test_agents.py
#       └── test_tools.py
#
# Then you could update this file to import everything:
#   from . import agent
#   from . import tools  
#   from . import config
#   from . import utils
#
# This would allow users to access everything with:
#   from debate_team import agent, tools, config, utils

# --- PACKAGE METADATA (OPTIONAL) ---
# You can also define package-level information here:

__version__ = "1.0.0"
__author__ = "Nicky Clarke"
__description__ = "Multi-agent debate system using Google ADK"

# These variables become available when someone imports the package:
#   import debate_team
#   print(debate_team.__version__)  # Prints: 1.0.0

# =============================================================================
# WHY THIS MATTERS FOR ADK DEVELOPMENT
# =============================================================================
#
# Clean Deployment:
# -----------------
# In deploy.py, we can cleanly import with:
#   from debate_team.agent import root_agent
# 
# This works because:
# 1. This __init__.py makes "debate_team" a valid package
# 2. The "from . import agent" makes agent.py accessible
# 3. Python can then find root_agent inside the agent module
#
# Professional Organization:
# --------------------------
# Having proper package structure makes your ADK project:
# - Easier to understand for other developers
# - Ready for distribution (could upload to PyPI)
# - Scalable as you add more agents and tools
# - Compatible with modern Python tooling (poetry, pip, etc.)
#
# =============================================================================