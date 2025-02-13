from typing import List, Dict
import os
from pydantic_ai import RunContext
import chainlit as cl
import aiohttp
from urllib.parse import urlencode

from src.models.hotel_models import HotelDeps

async def web_search(ctx: RunContext[HotelDeps], query: str) -> List[Dict]:
    """Search the web for local information based on the query"""
    # Create a step for the web search
    async with cl.Step(name="Web Search Tool", type="tool") as step:
        step.input = query

        # Get SerpAPI key from environment
        api_key = os.getenv('SERPAPI_API_KEY')
        if not api_key:
            step.output = "No SerpAPI key found"
            return []

        # Prepare the search query with location context
        location = ctx.deps.hotel_location
        search_query = f"{query} near {location.full_address}"

        # Prepare the search parameters
        params = {
            "engine": "google",
            "q": search_query,
            "api_key": api_key,
            "google_domain": "google.com",
            "gl": location.country,  # Location parameter
            "hl": "en",  # Language
            "num": 5,  # Number of results
            # "tbm": "lcl"  # Local results
        }

        try:
            # Make direct API request to SerpAPI
            url = f"https://serpapi.com/search?{urlencode(params)}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response_text = await response.text()
                    if response.status == 200:
                        result = await response.json()

                        # print(f'✅ Result: {result}')

                        # Use organic results if available
                        organic_results = result.get("organic_results", [])
                        if not organic_results:
                            step.output = "No organic results found"
                            return []

                        # # Extract local results if available
                        # local_results = result.get("local_results", [])
                        # if not local_results:
                        #     # Fall back to organic results if no local results
                        #     local_results = result.get("organic_results", [])

                        step.output = organic_results
                        return organic_results
                    else:
                        error_msg = f"Search failed with status {response.status}. Response: {response_text}"
                        print(f'❌ Error Response: {response_text}')
                        step.output = error_msg
                        return []

        except Exception as e:
            error_msg = f"Error performing web search: {str(e)}"
            print(f'❌ Exception: {str(e)}')
            step.output = error_msg
            return []
