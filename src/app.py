import chainlit as cl
from pydantic_ai.usage import Usage, UsageLimits, UsageLimitExceeded
from typing import Any, cast, Union
from engineio.payload import Payload
from pydantic import ValidationError
from pydantic_ai.messages import ModelMessage

# Configure engineio to handle larger payloads
Payload.max_decode_packets = 1000

from src.agents.supervisor_agent import supervisor_agent, reset_processed_requests
from src.agents.room_service_agent import room_service_agent
from src.models.hotel_models import HotelDeps, HotelRequest, TaskResponse, Failed, SAMPLE_HOTEL_DATA

# Initialize usage limits - reduce limits to prevent too many API calls
usage_limits = UsageLimits(
    request_limit=10,  # Allow for supervisor + 2 specialized agent calls
    total_tokens_limit=12000,  # Keep reasonable token limit
)

# Store conversation history
message_history: list[ModelMessage] = []

@cl.on_chat_start
async def start():
    """Initialize the chat session."""
    # Reset the processed requests and message history at the start of each conversation
    reset_processed_requests()
    message_history.clear()

    await cl.Message(
        content="""
# 🏨 Hotel Service Coordinator

I'm your virtual concierge, ready to assist you 24/7 with:

- **🛎️ Concierge Services**
  Local recommendations, reservations, and arrangements

- **🔧 Maintenance & Housekeeping**
  Room supplies, maintenance, and cleaning services

- **🍽️ Room Service**
  Meals, beverages, and special dietary requests

💡 For the best service, please send separate messages for different requests.
For example: first ask for towels, then for dinner recommendations.

How may I assist you today?
        """,
        author="Concierge"
    ).send()

def format_usage(usage: Usage) -> str:
    """Format usage statistics."""
    return f"""
## 📊 Session Statistics
- **Total Tokens**: {usage.total_tokens}
- **Prompt Tokens**: {usage.request_tokens}
- **Completion Tokens**: {usage.response_tokens}
- **API Calls**: {usage.requests}
    """

@cl.on_message
async def main(message: cl.Message):
    """Handle incoming guest requests."""
    try:
        # Create a root step for the entire request
        async with cl.Step(name="Request Processing", type="run") as root_step:
            root_step.input = message.content

            # Mock guest info - in a real system this would come from authentication
            deps = HotelDeps(
                room_number="101",
                guest_name="John Doe",
                hotel_location=SAMPLE_HOTEL_DATA["location"]
            )

            formatted_response = ""  # Initialize response variable
            user_message = ""  # Initialize user message
            try:
                # Run the supervisor agent with streaming and message history
                async with supervisor_agent.run_stream(
                    message.content,
                    deps=deps,
                    usage_limits=usage_limits,
                    message_history=message_history,  # Pass the conversation history
                ) as result:
                    try:
                        # Stream the structured response
                        async for message_data, is_last in result.stream_structured(debounce_by=1.0):
                            try:
                                # Validate the response
                                response = await result.validate_structured_result(
                                    message_data,
                                    allow_partial=not is_last,
                                )

                                if isinstance(response, dict):
                                    # Format the response based on type
                                    if "reason" in response:
                                        if "Usage limit reached" in response["reason"]:
                                            formatted_response = f"""
## ⏸️ Request Paused
Some parts of your request were processed, but we need to pause to stay within limits.
Please try any remaining requests as separate messages.

**Reason**: {response["reason"]}

## 💡 Tip
For multiple requests like towels and restaurant recommendations,
try sending them as separate messages for better handling.
"""
                                            user_message = (
                                                "I need to pause briefly to stay within limits. "
                                                "I've processed part of your request, but please send any "
                                                "remaining requests as separate messages."
                                            )
                                        else:
                                            formatted_response = f"""
## ❌ Request Failed
**Reason**: {response["reason"]}
"""
                                            user_message = f"I apologize, but I couldn't process your request: {response['reason']}"
                                    else:
                                        status = response.get('status', 'Processing')
                                        message = response.get('message', 'Working on your request...')
                                        eta = response.get('eta', 'Calculating...')

                                        formatted_response = f"""
## ✅ Request Status
**Status**: {status}
**Details**: {message}
**Timeline**: {eta}
"""
                                        # Create a more natural response for the user
                                        user_message = message
                                        if eta and eta != "immediate":
                                            user_message += f"\n\nExpected time: {eta}"

                                    if is_last:
                                        # Add usage statistics to step output only
                                        usage_stats = result.usage()
                                        formatted_response += "\n" + format_usage(usage_stats)
                                        # Update message history with the completed interaction
                                        message_history.extend(result.all_messages())

                                    # Update step output but don't send message yet
                                    root_step.output = formatted_response

                            except ValidationError:
                                # Skip invalid partial responses
                                continue

                    except Exception as stream_error:
                        if isinstance(stream_error, UsageLimitExceeded):
                            formatted_response = f"""
## ⏸️ Request Paused
We need to pause processing to stay within usage limits.
Please try breaking down your request into smaller parts.

**Reason**: {str(stream_error)}

## 💡 Tip
For multiple requests, try sending them as separate messages
for better handling (e.g. first ask for towels, then for recommendations).
"""
                            user_message = (
                                "I need to pause to stay within limits. "
                                "Please break down your request into smaller parts - "
                                "first ask about the towels, then about restaurant recommendations."
                            )
                        else:
                            formatted_response = f"⚠️ Stream processing error: {str(stream_error)}"
                            user_message = "I encountered an error while processing your request. Please try again."

                        root_step.output = formatted_response

            except Exception as agent_error:
                if isinstance(agent_error, UsageLimitExceeded):
                    formatted_response = f"""
## ⏸️ Request Paused
We need to pause processing to stay within usage limits.
Please try your request again as smaller parts.

**Reason**: {str(agent_error)}
"""
                    user_message = (
                        "I need to pause to stay within limits. "
                        "Please send your requests separately - "
                        "first ask about one thing, then about the other."
                    )
                else:
                    formatted_response = f"🚨 Agent error: {str(agent_error)}"
                    user_message = "I encountered an error processing your request. Please try again."

                root_step.output = formatted_response

            # Send the final response as a regular message only once at the end
            if user_message:
                await cl.Message(content=user_message).send()

    except Exception as e:
        formatted_response = ""
        if isinstance(e, UsageLimitExceeded):
            formatted_response = f"""
## ⏸️ Request Paused
We need to pause processing to stay within usage limits.
Please try breaking down your request into smaller parts.

**Reason**: {str(e)}

## 💡 Tip
For multiple requests, try sending them separately:
1. First ask for towels
2. Then ask for restaurant recommendations
"""
            user_message = (
                "I need to pause briefly. Please break down your request into parts:\n"
                "1. First ask about the towels\n"
                "2. Then ask about restaurant recommendations"
            )
        else:
            formatted_response = f"""
❌ System Error:
**Type**: {type(e).__name__}
**Details**: {str(e)}

Please try again or contact the front desk for assistance.
"""
            user_message = "I encountered a system error. Please try again or contact the front desk for assistance."

        if root_step:
            root_step.output = formatted_response
        await cl.Message(content=user_message).send()
