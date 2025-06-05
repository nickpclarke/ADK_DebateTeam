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
# AI DEBATE TEAM - DEPLOYMENT TESTING SCRIPT
# =============================================================================
# This script tests your deployed ADK agents by creating an interactive chat
# session with the remote agent running on Google Cloud Platform.
#
# Key concepts demonstrated:
# - Connecting to deployed Agent Engines
# - Creating and managing user sessions
# - Streaming real-time responses from cloud agents
# - Interactive command-line chat interface
# - Session lifecycle management (create/delete)
# - Event parsing from agent responses
# =============================================================================

"""
Test deployment of AI Debate Team to Agent Engine.

This module provides an interactive command-line interface to test deployed
ADK agents. It creates a chat session where you can send messages to your
cloud-deployed agent and receive streaming responses.
"""

# --- IMPORTS ---
import os
# os: Built-in Python module for operating system interface
# Used here for environment variable access

import vertexai
# vertexai: Google Cloud's AI platform SDK
# Required to connect to deployed Agent Engines

from absl import app, flags
# absl: Google's Python library for building command-line applications
# app: Framework for creating command-line applications
# flags: System for defining and parsing command-line flags/arguments

from dotenv import load_dotenv
# dotenv: Third-party library for loading environment variables from .env files
# Essential for loading cloud configuration without hardcoding sensitive data

from vertexai import agent_engines
# agent_engines: Vertex AI service for connecting to deployed ADK agents
# This allows us to interact with agents running in Google Cloud

# --- COMMAND-LINE FLAGS SETUP ---
# absl.flags provides a robust system for command-line argument parsing
FLAGS = flags.FLAGS

# Define string flags for cloud configuration
flags.DEFINE_string("project_id", None, "GCP project ID.")
# Example: --project_id=my-gcp-project

flags.DEFINE_string("location", None, "GCP location.")
# Example: --location=us-central1

flags.DEFINE_string("bucket", None, "GCP bucket.")
# Example: --bucket=my-storage-bucket

flags.DEFINE_string(
    "resource_id",
    None,
    "ReasoningEngine resource ID (returned after deploying the agent)",
)
# This is the ID you got when running deploy.py --create
# Example: --resource_id=projects/my-project/locations/us-central1/reasoningEngines/1234567890

flags.DEFINE_string("user_id", None, "User ID (can be any string).")
# This identifies the user session - can be any string like "test-user" or "nicky"
# Example: --user_id=nicky

# Mark these flags as required - the script won't run without them
flags.mark_flag_as_required("resource_id")
flags.mark_flag_as_required("user_id")


def main(argv: list[str]) -> None:  # pylint: disable=unused-argument
    """
    Main entry point for the deployment testing script.
    
    This function coordinates the entire testing process:
    1. Load environment variables from .env file
    2. Parse command-line flags or use environment defaults
    3. Validate required configuration
    4. Initialize Vertex AI connection
    5. Connect to the deployed agent
    6. Create an interactive chat session
    7. Stream responses in real-time
    8. Clean up the session when done
    
    Args:
        argv (list[str]): Command-line arguments (handled by absl framework)
        
    Required Flags:
        --resource_id: The ID of your deployed agent
        --user_id: Any string to identify this user session
        
    Environment Variables Required:
        GOOGLE_CLOUD_PROJECT: Your GCP project ID
        GOOGLE_CLOUD_LOCATION: GCP region (e.g., 'us-central1')
        GOOGLE_CLOUD_STORAGE_BUCKET: GCS bucket for staging files
    """

    # Load environment variables from .env file
    # This reads key-value pairs from a file named ".env" in your project root
    load_dotenv()

    # Get configuration values with priority: command-line flags > environment variables
    # This pattern allows flexibility: use flags for one-time overrides, env vars for defaults
    project_id = (
        FLAGS.project_id
        if FLAGS.project_id
        else os.getenv("GOOGLE_CLOUD_PROJECT")
    )
    location = (
        FLAGS.location if FLAGS.location else os.getenv("GOOGLE_CLOUD_LOCATION")
    )
    bucket = (
        FLAGS.bucket
        if FLAGS.bucket
        else os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")
    )

    # Note: There's some redundant code here (this overwrites the above variables)
    # This is a common pattern in scripts that evolved over time
    # The environment variables take precedence in this case
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION")
    bucket = os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")

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
        location=location,                     # Which region the agent is deployed in
        staging_bucket=f"gs://{bucket}",       # Where to store temporary files
    )

    # Connect to the deployed agent using its resource ID
    # This creates a client object for interacting with the remote agent
    agent = agent_engines.get(FLAGS.resource_id)
    print(f"Found agent with resource ID: {FLAGS.resource_id}")
    
    # Create a user session for this conversation
    # Sessions help the agent maintain context across multiple messages
    # Each user can have their own session to keep conversations separate
    session = agent.create_session(user_id=FLAGS.user_id)
    print(f"Created session for user ID: {FLAGS.user_id}")
    
    # Start the interactive chat loop
    print("Type 'quit' to exit.")
    
    # Main interaction loop - continues until user types 'quit'
    while True:
        # Get user input from command line
        user_input = input("Input: ")
        
        # Check for exit condition
        if user_input == "quit":
            break

        # Send message to agent and stream the response
        # stream_query() returns real-time events as the agent processes the request
        for event in agent.stream_query(
            user_id=FLAGS.user_id,       # Which user is sending this message
            session_id=session["id"],    # Which session this message belongs to
            message=user_input          # The actual message content
        ):
            # Parse the streaming event to extract the agent's response
            # Events come in a nested structure that we need to unpack
            
            # Check if this event contains actual content (not just metadata)
            if "content" in event:
                # Check if the content has parts (agent responses are structured in parts)
                if "parts" in event["content"]:
                    parts = event["content"]["parts"]
                    
                    # Process each part of the response
                    for part in parts:
                        # Check if this part contains text (vs. other types like images)
                        if "text" in part:
                            text_part = part["text"]
                            # Print the agent's response in real-time
                            print(f"Response: {text_part}")

    # Clean up: Delete the session when the conversation is over
    # This is good practice to avoid accumulating unused sessions
    agent.delete_session(user_id=FLAGS.user_id, session_id=session["id"])
    print(f"Deleted session for user ID: {FLAGS.user_id}")


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
# Test your deployed agent:
#   python deployment/test_deployment.py --resource_id="projects/my-project/locations/us-central1/reasoningEngines/123" --user_id="nicky"
# 
# Example conversation flow:
#   Input: hello
#   Response: Hello! I'm the AI Debate Team. What topic would you like us to debate?
#   Input: renewable energy
#   Response: Excellent! Let's conduct an iterative debate on: renewable energy
#   [Agent proceeds with role assignment, research, and debate rounds]
#   Input: quit
#   [Session ends and cleanup occurs]
# 
# Troubleshooting:
#   - If "resource_id not found": Make sure you deployed an agent first with deploy.py --create
#   - If "permission denied": Check your GCP authentication and project access
#   - If "location mismatch": Ensure your .env GOOGLE_CLOUD_LOCATION matches deployment
# 
# =============================================================================
