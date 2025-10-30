# Strands Agent with Elastic Observability on Amazon Bedrock AgentCore Runtime

## Overview
This Agentic AI application demonstrates deploying a Strands agent to Amazon Bedrock AgentCore Runtime with Elastic observability integration. The implementation uses Amazon Bedrock Claude models and sends telemetry data to Elastic through OpenTelemetry (OTEL) using [EDOT](https://www.elastic.co/docs/reference/opentelemetry)

## Key Components
- **Strands Agents**: Python framework for building LLM-powered agents with built-in telemetry support
- **Amazon Bedrock AgentCore Runtime**: Managed runtime service for hosting and scaling agents on AWS
- **Elastic**: Observability platform for monitoring and debugging LLM applications
- **OpenTelemetry**: Industry-standard protocol for collecting and exporting telemetry data

## Architecture
The agent is containerized and deployed to Amazon Bedrock AgentCore Runtime, which provides HTTP endpoints for invocation. Telemetry data flows from the Strands agent through OTEL exporters to Elastic for monitoring and debugging. The implementation uses a lazy initialization pattern to ensure proper configuration order.

## Prerequisites
- Python 3.10+
- AWS CLI Configured
- AWS credentials configured with Bedrock and AgentCore permissions
- Elastic account with credentials to login in. Please check [Elastic website](https://cloud.elastic.co) for details
- Docker installed locally
- Access to Amazon Bedrock Claude models in us-west-2

## Installation

First, invoke a python virtual environment. Activate it and install the python dependencies, as shown below:
```
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

## Agent Implementation

The agent file (`strands_claude.py`) implements multiple agents in a Swarm pattern.
-  a travel agent with web search capabilities.
-  a weather agent 

Key features:
- Lazy initialization pattern ensures telemetry is configured after environment variables

## Configure AgentCore Runtime deployment
Next we will use AgentCore CLI to configure the AgentCore Runtime deployment with an entrypoint, the execution role we just created and a requirements file. We will also configure the AgentCore CLI auto create the Amazon ECR repository on launch.

During the configure step, your docker file will be generated based on your application code. Please note that when using the AgentCore CLI to configure your agent, it configures AgentCore Observability by default.111

<div style="text-align:left">
        <img src=".\images\configure.png" width="60%"/>
</div>

```
agentcore configure -n "strands_multiagent_elastic_observability" -e "strands_claude.py" -rf "requirements.txt" -r "us-west-2"
```
This will create a dockerfile in a folder like `.bedrock_agentcore/strands_multiagent_elastic_observability`


## Deploy to AgentCore Runtime
Now that we've got a docker file, let's launch the agent to the AgentCore Runtime. This will create the Amazon ECR repository and the AgentCore Runtime. 

<div style="text-align:left">
        <img src=".\images\launch.png" width="80%"/>
</div>

```
agentcore launch --env BEDROCK_MODEL_ID="us.anthropic.claude-3-5-sonnet-20240620-v1:0" --env OTEL_EXPORTER_OTLP_ENDPOINT="https://<REPLACE_WITH_ELASTIC_ENDPOINT>.elastic.cloud:443" --env OTEL_EXPORTER_OTLP_HEADERS="REPLACE_ EXAMPLE > Authorization=ApiKey UlNiMUo1b0JQUk1JXXXXXXXUdWRDZoOVdrSi1Ha0Jidw==" --env OTEL_RESOURCE_ATTRIBUTES="service.name='strands_multiagent_elastic_observability',service.version='0.1',deployment.environment='production'"  --env DISABLE_ADOT_OBSERVABILITY=true
```

## Invoking AgentCore Runtime
Finally, we can invoke our AgentCore Runtime with a payload

<div style="text-align:left">
        <img src=".\images\invoke.png" width="80%"/>
</div>

```
agentcore invoke '{"prompt": "I am planning a weekend trip to Orlando, Florida. What are the best times to visit and what are the must-visit places and local food I should try?"}'
```

Invoke Agent again with a few more different queries:

```
agentcore invoke '{"prompt": "How is the weather in Amsterdam, Netharlands. What are the must-see places in Amsterdam?"}'

 ```
 ```
agentcore invoke '{"prompt": "Going to London next Summer. I have only 4 hours to go on a sightseeing in London. What are the must see places? I am interested in arts and history"}'
 ```

 ## Elastic Observability

 If Elastic endpoints are correctly configured, now you should see the logs, traces and metrics making it to Elastic endpoints over OTEL. 