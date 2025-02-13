from pydantic_ai import Agent, RunContext
from typing import Union, List, Dict
import chainlit as cl

from src.models.hotel_models import HotelRequest, TaskResponse, Failed, HotelDeps

# Define the maintenance agent with a more personable approach
maintenance_agent = Agent(
    'openai:gpt-4o',
    deps_type=HotelDeps,
    result_type=Union[TaskResponse, Failed],
    system_prompt=(
        'You are Alex, the experienced Maintenance and Housekeeping Specialist who ensures '
        'guest comfort and room perfection. You handle all room-related requests with care and efficiency.\n\n'

        'You have access to a service lookup tool that can check:\n'
        '- Available supplies and amenities\n'
        '- Current maintenance staff and their expertise\n'
        '- Service request priorities and response times\n'
        '- Room status and scheduled services\n\n'

        'Service Categories:\n'
        '- Room Supplies: 5-10 minutes\n'
        '- Climate Control: 10-15 minutes\n'
        '- Housekeeping: 20-30 minutes\n'
        '- Basic Repairs: 30-45 minutes\n'
        '- Technical Issues: 15-30 minutes\n'
        '- Emergency Services: Immediate\n\n'

        'When handling requests:\n'
        '1. Check service availability and current status\n'
        '2. Determine request priority and response time\n'
        '3. Note any special requirements or preferences\n'
        '4. Anticipate related needs\n'
        '5. Be professional and reassuring\n\n'

        'Always format your responses as a TaskResponse with:\n'
        '- status: "completed" for successful requests\n'
        '- message: service confirmation with details\n'
        '- eta: estimated response time\n\n'

        'If you encounter any issues, return a Failed response with a clear reason.'
    ),
)

@maintenance_agent.tool
async def check_service(ctx: RunContext[HotelDeps], query: str) -> List[Dict]:
    """Look up service availability and details based on the query"""
    # This would be replaced with actual service system queries
    # For now returning simulated responses
    async with cl.Step(name="Check Service Tool", type="tool") as step:
        step.input = query
        output = []
        if any(word in query.lower() for word in ["towel", "amenity", "supply"]):
            output = [{
                "type": "supplies",
                "service": "Room Supplies",
                "items_available": True,
                "response_time": "5-10 minutes",
                "staff_assigned": True,
                "priority": "normal",
                "additional_info": "Extra amenities available upon request"
            }]
        elif any(word in query.lower() for word in ["ac", "heat", "temperature", "climate"]):
            output = [{
                "type": "climate",
                "service": "Climate Control",
                "technician_available": True,
                "response_time": "10-15 minutes",
                "priority": "high",
                "additional_info": "Temperature adjustment and system check"
            }]
        elif any(word in query.lower() for word in ["clean", "housekeeping", "tidy"]):
            output = [{
                "type": "housekeeping",
                "service": "Room Cleaning",
                "staff_available": True,
                "response_time": "20-30 minutes",
                "priority": "normal",
                "services": ["full cleaning", "turndown", "refresh"]
            }]
        elif any(word in query.lower() for word in ["repair", "fix", "broken"]):
            output = [{
                "type": "maintenance",
                "service": "Repairs",
                "technician_available": True,
                "response_time": "30-45 minutes",
                "priority": "high",
                "additional_info": "Initial assessment and basic repairs"
            }]
        else:
            output = []  # No matching services found
        step.output = output
        return output