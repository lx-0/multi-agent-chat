import chainlit as cl
from pydantic_ai import RunContext

from src.models.hotel_models import HotelDeps


async def get_user_input(ctx: RunContext[HotelDeps], query: str):
    res = await cl.AskUserMessage(content=query, timeout=30).send()
    if res:
        return res
    else:
        return "No response from user"
