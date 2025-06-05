# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# =============================================================================
# AI DEBATE TEAM - DEPLOYMENT SCRIPT
# =============================================================================
# This script handles deploying your local ADK agents to Google Cloud Platform
# where they can be accessed remotely by users around the world.
#
# Key concepts demonstrated:
# - Environment variable management with .env files
# - Google Cloud Vertex AI initialization
# - Agent Engine creation and management
# - Command-line flag handling with absl-py
# - Package dependency management
# - Remote agent lifecycle (create, list, delete)
# =============================================================================

"""
Deployment script for AI Debate Team

This module provides command-line tools to deploy, manage, and cleanup
ADK agents on Google Cloud Platform using Vertex AI Agent Engines.
"""

# --- IMPORTS ---
import os
# os: Built-in Python module for operating system interface
# Used here for environment variable access

import vertexai
# vertexai: Google Cloud's AI platform SDK
# Provides access to AI services like Agent Engines, models, etc.

from absl import app, flags
# absl: Google's Python library for building command-line applications
# app: Framework for creating command-line applications
# flags: System for defining and parsing command-line flags/arguments

from dotenv import load_dotenv
# dotenv: Third-party library for loading environment variables from .env files
# This is essential for keeping sensitive data (like project IDs) out of code

from debate_team.agent import root_agent
# Import our main agent from the local package
# This is the agent we defined in agent.py that will be deployed

from vertexai import agent_engines
# agent_engines: Vertex AI service for deploying and managing ADK agents
# This allows our local agents to run in Google Cloud

from vertexai.preview.reasoning_engines import AdkApp
# AdkApp: Wrapper that packages our ADK agent for cloud deployment
# This bridges local ADK agents and cloud Agent Engines

# --- COMMAND-LINE FLAGS SETUP ---
# absl.flags provides a robust system for command-line argument parsing
# FLAGS is the global object that holds all defined flags
FLAGS = flags.FLAGS

# Define string flags (command-line arguments that accept text values)
# Syntax: flags.DEFINE_string(name, default_value, help_text)
flags.DEFINE_string("project_id", None, "GCP project ID.")
# Example usage: --project_id=my-gcp-project

flags.DEFINE_string("location", None, "GCP location.")
# Example usage: --location=us-central1

flags.DEFINE_string("bucket", None, "GCP bucket.")
# Example usage: --bucket=my-storage-bucket

flags.DEFINE_string("resource_id", None, "ReasoningEngine resource ID.")
# Example usage: --resource_id=projects/.../locations/.../reasoningEngines/123
# This ID is returned when you create an agent and needed for deletion

# Define boolean flags (true/false flags)
# Syntax: flags.DEFINE_bool(name, default_value, help_text)
flags.DEFINE_bool("list", False, "List all agents.")
# Example usage: --list (sets to True)

flags.DEFINE_bool("create", False, "Creates a new agent.")
# Example usage: --create (sets to True)

flags.DEFINE_bool("delete", False, "Deletes an existing agent.")
# Example usage: --delete (sets to True)

# Ensure that create and delete cannot be used together
# This prevents conflicting operations in a single command
flags.mark_bool_flags_as_mutual_exclusive(["create", "delete"])

# --- DEPLOYMENT FUNCTIONS ---

def create() -> None:
    """
    Creates an agent engine for AI Debate Team on Google Cloud.
    
    This function takes your local ADK agent and deploys it to Vertex AI
    where it becomes accessible remotely via API calls.
    
    Steps performed:
    1. Wrap the local agent in an AdkApp container
    2. Define package requirements for the cloud environment
    3. Create the remote agent engine
    4. Return the resource ID for future management
    
    Returns:
        None: Prints the resource ID of the created agent
        
    Cloud Deployment Note:
        The agent runs in Google's managed environment, not your local machine.
        Users can interact with it through API calls from anywhere.
    """
    # AdkApp wraps our local agent for cloud deployment
    # enable_tracing=True allows you to see detailed execution logs
    adk_app = AdkApp(agent=root_agent, enable_tracing=True)
    
    # Environment variables that will be available to the deployed agent
    # Add any environment variables your agent needs in the cloud here
    env_vars = {}
    # Example: env_vars = {"API_KEY": "your-secret-key", "DEBUG": "true"}

    # Create the remote agent on Google Cloud
    remote_agent = agent_engines.create(
        adk_app,  # The wrapped ADK application
        
        # Display name shown in Google Cloud Console
        display_name=root_agent.name,
        
        # Python packages that must be installed in the cloud environment
        # These are the dependencies your agent needs to run
        requirements=[
            "google-adk>=1.1.1",                           # ADK framework
            "google-cloud-aiplatform[agent_engines]>=1.95.0",  # Vertex AI client
            "google-genai>=1.5.0,<2.0.0",                 # Google AI models
            "pydantic>=2.10.6,<3.0.0",                    # Data validation
            "absl-py>=2.2.1,<3.0.0",                      # Command-line tools
            "python-dotenv>=1.0.0",                       # Environment variables
        ],
        
        # Local packages to include (our debate_team package)
        # This uploads your local code to the cloud environment
        extra_packages=["debate_team"],
        
        # Environment variables for the cloud agent
        env_vars=env_vars,
    )
    
    # Print the resource ID - save this! You need it to manage the agent later
    print(f"Created remote agent: {remote_agent.resource_name}")


def delete(resource_id: str) -> None:
    """
    Deletes an existing agent engine from Google Cloud.
    
    This permanently removes the deployed agent and stops any running instances.
    Use this to clean up when you no longer need the agent or want to redeploy.
    
    Args:
        resource_id (str): The unique resource identifier of the agent to delete
                          (obtained when creating the agent)
    
    Returns:
        None: Prints confirmation of deletion
        
    Warning:
        This operation is irreversible! The agent and all its data will be lost.
    """
    # Get reference to the remote agent using its resource ID
    remote_agent = agent_engines.get(resource_id)
    
    # Delete the agent (force=True bypasses confirmation prompts)
    remote_agent.delete(force=True)
    
    print(f"Deleted remote agent: {resource_id}")


def list_agents() -> None:
    """
    Lists all agent engines deployed in your Google Cloud project.
    
    This helps you see what agents are currently deployed, when they were
    created/updated, and their resource IDs for management.
    
    Returns:
        None: Prints formatted list of all remote agents
        
    Useful for:
        - Checking what agents are currently deployed
        - Finding resource IDs for management operations
        - Monitoring agent creation/update times
    """
    # Get list of all agent engines in the current project
    remote_agents = agent_engines.list()
    
    # Template for formatting each agent's information
    # This creates a consistent, readable output format
    template = """
{agent.name} ("{agent.display_name}")
- Create time: {agent.create_time}
- Update time: {agent.update_time}
"""
    
    # Format each agent using the template
    # This Python pattern creates a string for each agent, then joins them
    remote_agents_string = "\n".join(
        template.format(agent=agent) for agent in remote_agents
    )
    
    print(f"All remote agents:\n{remote_agents_string}")


def main(argv: list[str]) -> None:
    """
    Main entry point for the deployment script.
    
    This function coordinates the entire deployment process:
    1. Load environment variables from .env file
    2. Parse command-line flags or use environment defaults
    3. Validate required configuration
    4. Initialize Vertex AI connection
    5. Execute the requested operation (list/create/delete)
    
    Args:
        argv (list[str]): Command-line arguments (handled by absl framework)
        
    Environment Variables Required:
        GOOGLE_CLOUD_PROJECT: Your GCP project ID
        GOOGLE_CLOUD_LOCATION: GCP region (e.g., 'us-central1')
        GOOGLE_CLOUD_STORAGE_BUCKET: GCS bucket for staging files
    """
    del argv  # Mark argv as unused (absl handles argument parsing)

    # Load environment variables from .env file
    # This reads key-value pairs from a file named ".env" in your project root
    # Example .env content:
    #   GOOGLE_CLOUD_PROJECT=my-project
    #   GOOGLE_CLOUD_LOCATION=us-central1
    #   GOOGLE_CLOUD_STORAGE_BUCKET=my-bucket
    load_dotenv()

    # Get configuration values with priority: command-line flags > environment variables
    # This pattern allows flexibility: use flags for one-time overrides, env vars for defaults
    
    project_id = (
        FLAGS.project_id           # Command-line flag value (if provided)
        if FLAGS.project_id        # Check if flag was set
        else os.getenv("GOOGLE_CLOUD_PROJECT")  # Otherwise use environment variable
    )
    
    location = (
        FLAGS.location if FLAGS.location else os.getenv("GOOGLE_CLOUD_LOCATION")
    )
    
    bucket = (
        FLAGS.bucket
        if FLAGS.bucket
        else os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")
    )

    # Display current configuration for verification
    # This helps debug configuration issues
    print(f"PROJECT: {project_id}")
    print(f"LOCATION: {location}")
    print(f"BUCKET: {bucket}")

    # Validate that all required configuration is present
    # Early validation prevents cryptic errors later in the process
    if not project_id:
        print("Missing required environment variable: GOOGLE_CLOUD_PROJECT")
        return
    elif not location:
        print("Missing required environment variable: GOOGLE_CLOUD_LOCATION")
        return
    elif not bucket:
        print(
            "Missing required environment variable: GOOGLE_CLOUD_STORAGE_BUCKET"
        )
        return

    # Initialize Vertex AI with our project configuration
    # This sets up the connection to Google Cloud services
    vertexai.init(
        project=project_id,                    # Which GCP project to use
        location=location,                     # Which region to deploy in
        staging_bucket=f"gs://{bucket}",       # Where to store temporary files
    )

    # Execute the requested operation based on command-line flags
    # This implements a simple command dispatch pattern
    if FLAGS.list:
        # List all existing agents
        list_agents()
    elif FLAGS.create:
        # Create a new agent
        create()
    elif FLAGS.delete:
        # Delete an existing agent (requires resource_id)
        if not FLAGS.resource_id:
            print("resource_id is required for delete")
            return
        delete(FLAGS.resource_id)
    else:
        # No valid operation specified
        print("Unknown command")


# --- SCRIPT ENTRY POINT ---
# This Python idiom ensures main() only runs when the script is executed directly
# (not when imported as a module)
if __name__ == "__main__":
    # app.run() handles command-line parsing and calls our main() function
    # This is the absl-py way of running command-line applications
    app.run(main)

# =============================================================================
# USAGE EXAMPLES (run these commands in PowerShell):
# =============================================================================
# 
# List all deployed agents:
#   python deployment/deploy.py --list
# 
# Create a new agent:
#   python deployment/deploy.py --create
# 
# Delete an agent:
#   python deployment/deploy.py --delete --resource_id="projects/.../reasoningEngines/123"
# 
# Override environment variables:
#   python deployment/deploy.py --create --project_id=my-project --location=us-west1
# 
# =============================================================================
