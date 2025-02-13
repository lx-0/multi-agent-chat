from crawl4ai import AsyncWebCrawler
from pydantic_ai import RunContext
import chainlit as cl

from src.models.hotel_models import HotelDeps


async def get_website(ctx: RunContext[HotelDeps], url: str) -> str:
    """Get the website defined by url"""
    print(f'🔍 Getting website for {url}')
    async with cl.Step(name="Get Website", type="tool") as step:
        step.input = url
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(
                url=url,
            )
            print(result.markdown)
            step.output = result.markdown
        return result.markdown