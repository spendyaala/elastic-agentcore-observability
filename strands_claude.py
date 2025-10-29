import os
import logging
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent, tool
from strands.multiagent import Swarm
from strands.models import BedrockModel
from strands.telemetry import StrandsTelemetry
from ddgs import DDGS

logging.basicConfig(level=logging.ERROR, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("AGENT_RUNTIME_LOG_LEVEL", "INFO").upper())


@tool
def web_search(query: str) -> str:
    """
    Search the web for information using DuckDuckGo.

    Args:
        query: The search query

    Returns:
        A string containing the search results
    """
    try:
        ddgs = DDGS()
        results = ddgs.text(query, max_results=5)

        formatted_results = []
        for i, result in enumerate(results, 1):
            formatted_results.append(
                f"{i}. {result.get('title', 'No title')}\n"
                f"   {result.get('body', 'No summary')}\n"
                f"   Source: {result.get('href', 'No URL')}\n"
            )

        return "\n".join(formatted_results) if formatted_results else "No results found."

    except Exception as e:
        return f"Error searching the web: {str(e)}"

# Function to initialize Bedrock model
def get_bedrock_model():
    region = os.getenv("AWS_DEFAULT_REGION", "us-west-2")
    model_id = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-3-5-sonnet-20240620-v1:0")

    bedrock_model = BedrockModel(
        model_id=model_id,
        region_name=region,
        temperature=0.0,
        max_tokens=1024
    )
    return bedrock_model

# Initialize the Bedrock model
bedrock_model = get_bedrock_model()

# Define the agent's system prompt
system_prompt_travel = """You are an experienced travel agent specializing in personalized travel recommendations 
with access to real-time web information. Your role is to find dream destinations matching user preferences 
using web search for current information. You should provide comprehensive recommendations with current 
information, brief descriptions, and practical travel details."""

system_prompt_weather = """You are an experienced weather agent specialized in searching for weather patterns
in a given city, identify current weather conditions and for the next 1 month and suggest best weather days to visit a place"""


app = BedrockAgentCoreApp()

def initialize_agents():
    """Initialize the agent with proper telemetry configuration."""

    # Initialize Strands telemetry with 3P configuration
    #strands_telemetry = StrandsTelemetry()
    #strands_telemetry.setup_otlp_exporter()
    
    
    # Create and cache the agent
    travel_agent = Agent(
        name="travel_agent",
        model=bedrock_model,
        system_prompt=system_prompt_travel,
        tools=[web_search]
    )
    weather_agent = Agent(
        name="weather_agent",
        model=bedrock_model,
        system_prompt=system_prompt_weather,
        tools=[web_search]
    )

    swarm_agent = Swarm(
        [travel_agent, weather_agent],
        entry_point=weather_agent,  # Start with the weather_agent
        max_handoffs=20,
        max_iterations=20,
        execution_timeout=900.0,  # 15 minutes
        node_timeout=300.0,       # 5 minutes per agent
        repetitive_handoff_detection_window=8,  # There must be >= 3 unique agents in the last 8 handoffs
        repetitive_handoff_min_unique_agents=3
    )
    
    return swarm_agent

@app.entrypoint
def strands_agent_bedrock(payload, context=None):
    """
    Invoke the agent with a payload
    """
    user_input = payload.get("prompt")
    logger.info("[%s] User input: %s", context.session_id, user_input)
    
    # Initialize agent with proper configuration
    agent = initialize_agents()
    
    response = agent(user_input)
    #return response.message['content'][0]['text']
    return response

if __name__ == "__main__":
    app.run()