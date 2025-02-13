from datetime import date
from pydantic_ai import Agent, RunContext
from typing import Union, List, Dict
import chainlit as cl

from src.models.hotel_models import HotelRequest, TaskResponse, Failed, HotelDeps

# Define the room service agent
room_service_agent = Agent(
    'openai:gpt-4o',
    deps_type=HotelDeps,
    result_type=Union[TaskResponse, Failed],
    system_prompt=(
        'You are the Room Service Specialist, dedicated to providing an excellent dining experience '
        'for our hotel guests. You handle food and beverage orders with attention to detail and care.\n\n'

        'You have access to a menu search tool that can find:\n'
        '- Current menu items and availability\n'
        '- Prices and preparation times\n'
        '- Dietary information and customization options\n'
        '- Special promotions and chef recommendations\n\n'

        'Service Hours:\n'
        '- Breakfast: 6:00 AM - 11:00 AM\n'
        '- All-day dining: 11:00 AM - 10:00 PM\n'
        '- Late night menu: 10:00 PM - 6:00 AM\n'
        '- Beverages: 24/7\n\n'

        'When taking orders:\n'
        '1. Search the menu for requested items\n'
        '2. Confirm availability and preparation time\n'
        '3. Note any dietary restrictions or preferences\n'
        '4. Suggest complementary items when appropriate\n'
        '5. Be courteous and attentive to special requests\n\n'

        'Always format your responses as a TaskResponse with:\n'
        '- status: "completed" for successful orders\n'
        '- message: order confirmation with details\n'
        '- eta: estimated delivery time\n\n'

        'If you encounter any issues, return a Failed response with a clear reason.'
    ),
)

@room_service_agent.system_prompt
def add_the_date() -> str:
    return f'The date is {date.today()}.'

@room_service_agent.tool
async def search_menu(ctx: RunContext[HotelDeps], query: str) -> List[Dict]:
    """Search the current menu for items matching the query"""
    # This would be replaced with actual menu database queries
    # For now returning simulated responses
    async with cl.Step(name="Search Menu Tool", type="tool") as step:
        step.input = query
        output = [
            {
                "category": "breakfast",
                "name": "American Breakfast",
                "description": "Two eggs any style, bacon or sausage, toast, breakfast potatoes",
                "price": 24.00,
                "preparation_time": "20-25 minutes",
                "available": True,
                "dietary_info": ["gluten-free option available"],
                "customization": ["egg style", "meat choice", "bread type"]
            },
            {
                "category": "main_course",
                "name": "Grilled Salmon",
                "description": "Fresh Atlantic salmon, seasonal vegetables, herb rice",
                "price": 38.00,
                "preparation_time": "25-30 minutes",
                "available": True,
                "dietary_info": ["gluten-free", "dairy-free"],
                "customization": ["cooking temperature", "sauce on side"]
            },
            {
                "category": "beverages",
                "name": "Fresh Orange Juice",
                "description": "Freshly squeezed orange juice",
                "price": 8.00,
                "preparation_time": "5-10 minutes",
                "available": True,
                "size_options": ["small", "large"]
            },
            {
                "category": "late_night",
                "name": "Cheeseburger",
                "description": "A juicy cheeseburger with all the fixings",
                "price": 12.00,
                "preparation_time": "10-15 minutes",
                "available": True,
                "dietary_info": ["gluten-free option available"],
            }
        ]
        step.output = output
        return output