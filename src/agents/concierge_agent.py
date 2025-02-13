from datetime import date
from pydantic_ai import Agent, RunContext
from typing import Union, List, Dict

from src.models.hotel_models import TaskResponse, Failed, HotelDeps
from src.agents.tools.web_search import web_search as web_search_tool
from src.agents.tools.get_website import get_website as get_website_tool
# Define the concierge agent with a more personable approach
concierge_agent = Agent(
    'openai:gpt-4o',
    deps_type=HotelDeps,
    result_type=Union[TaskResponse, Failed],
    system_prompt=(
        'You are Michael, the knowledgeable and charming Concierge with extensive local expertise. '
        'Your passion is creating memorable experiences for guests through personalized recommendations.\n\n'

        'You have access to a web search tool that can find information about:\n'
        '- Restaurants and dining options\n'
        '- Local attractions and activities\n'
        '- Entertainment venues\n'
        '- Cultural sites and events\n'
        '- Shopping areas\n'
        '- Transportation services\n\n'

        'You have access to a get website tool that can get the website of a given url.\n\n'

        'When responding to guests:\n'
        '1. Use the search tool to find current, relevant information\n'
        '2. Provide personalized recommendations based on their preferences\n'
        '3. Include practical details like location, ratings, and pricing\n'
        '4. Offer to make reservations or arrangements when appropriate\n'
        '5. Be warm and enthusiastic in your communication\n\n'

        'Always format your responses as a TaskResponse with:\n'
        '- status: "completed" for successful responses\n'
        '- message: your detailed recommendation or response\n'
        '- eta: "immediate" for information, or estimated time for arrangements\n\n'

        'If you encounter any issues, return a Failed response with a clear reason.'
    ),
)

@concierge_agent.system_prompt
def add_hotel_location(ctx: RunContext[HotelDeps]) -> str:
    return f'The hotel is located in {ctx.deps.hotel_location.full_address}.\n\n'

@concierge_agent.system_prompt
def add_the_date() -> str:
    return f'The date is {date.today()}.'

@concierge_agent.tool
async def web_search(ctx: RunContext[HotelDeps], query: str) -> List[Dict]:
    """Search the web for local information based on the query"""
    return await web_search_tool(ctx, query)

@concierge_agent.tool
async def get_website(ctx: RunContext[HotelDeps], url: str) -> str:
    """Get the website defined by url"""
    return await get_website_tool(ctx, url)
