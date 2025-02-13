from datetime import date
from pydantic_ai import Agent, RunContext
from typing import Union, List, Dict
import chainlit as cl

from src.models.hotel_models import HotelRequest, TaskResponse, Failed, HotelDeps
from src.agents.room_service_agent import room_service_agent
from src.agents.concierge_agent import concierge_agent
from src.agents.maintenance_agent import maintenance_agent
from src.agents.tools.user_input import get_user_input
# Keep track of processed requests to avoid duplicates
processed_requests: Dict[str, bool] = {}

def reset_processed_requests():
    """Reset the processed requests dictionary."""
    processed_requests.clear()

# Define the supervisor agent with a warmer, more personable prompt
supervisor_agent = Agent(
    'openai:gpt-4o',
    deps_type=HotelDeps,
    result_type=Union[TaskResponse, Failed],
    system_prompt=(
        'You are Sofia, the warm and attentive Hotel Concierge Manager with 15 years of luxury hospitality experience. '
        'Your goal is to make every guest feel special and well-cared for.\n\n'

        'When handling multiple requests in a single message:\n'
        '1. Identify each distinct request\n'
        '2. Process them separately using appropriate specialized agents\n'
        '3. Combine the responses into a single coherent message\n'
        '4. If some requests succeed and others fail, include both in your response\n\n'

        'Request Categories:\n'
        '1. "room_service": Food and beverage orders\n'
        '2. "concierge": Local recommendations, arrangements, information requests, website checks\n'
        '3. "maintenance": Room supplies and services\n\n'

        'For each request:\n'
        '1. Identify the request type\n'
        '2. Create a detailed HotelRequest\n'
        '3. Delegate to appropriate agent\n'
        '4. Handle the response appropriately\n\n'

        'Important Notes:\n'
        '- Website checks and information requests should be handled by the concierge agent\n'
        '- When guests ask about specific venues or websites, treat it as a concierge request\n'
        '- For any local information or online checks, delegate to the concierge agent\n\n'

        'Always format your final response as a TaskResponse with:\n'
        '- status: "completed" if ANY request succeeded, "failed" if ALL failed\n'
        '- message: Combined response addressing all requests\n'
        '- eta: Longest estimated time from successful requests\n\n'

        'If all requests fail, return a Failed response with clear reasons for each failure.'
    ),
)

@supervisor_agent.system_prompt
def add_hotel_location(ctx: RunContext[HotelDeps]) -> str:
    return f'The hotel is located in {ctx.deps.hotel_location.full_address}.\n\n'

@supervisor_agent.system_prompt
def add_the_date() -> str:
    return f'The date is {date.today()}.'

@supervisor_agent.tool
async def get_user_input(ctx: RunContext[HotelDeps], query: str):
    return await get_user_input(query)

@supervisor_agent.tool
async def delegate_task(
    ctx: RunContext[HotelDeps],
    request: HotelRequest
) -> Union[TaskResponse, Failed]:
    """Delegate a task to the appropriate specialized agent"""
    try:
        # Create a unique key for this request
        request_key = f"{request['request_type']}:{request['description']}"

        # Check if we've already processed this request
        if request_key in processed_requests:
            return Failed(reason=f"I've already processed this request. Would you like to make any modifications or try something else?")

        # Mark this request as processed
        processed_requests[request_key] = True

        # Select the appropriate agent based on request type
        request_type = request['request_type'].lower()
        if request_type == "room_service":
            agent = room_service_agent
            emoji = "🍽️"
            service = "Room Service"
        elif request_type == "concierge" or "website" in request['description'].lower() or "check" in request['description'].lower():
            agent = concierge_agent
            emoji = "🛎️"
            service = "Concierge"
        elif request_type == "maintenance":
            agent = maintenance_agent
            emoji = "🔧"
            service = "Maintenance"
        else:
            # Default to concierge for information and general requests
            agent = concierge_agent
            emoji = "🛎️"
            service = "Concierge"

        # Create a step for this delegation
        async with cl.Step(name=f"{service} Agent", type="agent") as step:
            step.input = request['description']

            try:
                # Execute the request with the specialized agent
                response = await agent.run(
                    request['description'],
                    deps=ctx.deps,
                    usage=ctx.usage,  # Share usage context
                )

                # Extract the actual response data
                response_data = response.data

                # Handle the response
                if isinstance(response_data, dict):
                    if "reason" in response_data:
                        # This request failed, but don't fail the entire interaction
                        step.output = f"{emoji} {response_data.get('reason', 'There was an issue with your request')}"
                        return Failed(reason=response_data['reason'])
                    else:
                        # Create a more natural response
                        message = response_data.get('message', '')
                        eta = response_data.get('eta', '')
                        status = response_data.get('status', 'completed')

                        step.output = f"{emoji} {message}"
                        return TaskResponse(
                            status=status,
                            message=message,
                            eta=eta
                        )
                else:
                    step.output = f"{emoji} Request processed successfully"
                    return TaskResponse(
                        status="completed",
                        message="Your request has been processed",
                        eta="immediate"
                    )

            except Exception as e:
                step.output = f"{emoji} Unable to process request: {str(e)}"
                return Failed(reason=f"Error processing {service.lower()} request: {str(e)}")

    except Exception as e:
        return Failed(reason=f"Unexpected error while delegating task: {str(e)}")