from typing import Literal, Union, Dict, List
from typing_extensions import TypedDict
from dataclasses import dataclass

class HotelRequest(TypedDict, total=False):
    """Guest request details"""
    request_type: str  # Type of request (room service, concierge, maintenance)
    description: str  # Detailed description of the request
    room_number: str  # Guest's room number
    priority: Literal["low", "medium", "high"]  # Priority level, defaults to medium

class TaskResponse(TypedDict, total=False):
    """Response from a specialized agent"""
    status: Literal["completed", "pending", "failed"]
    message: str  # Response message or status update
    eta: str  # Estimated time for task completion

class Failed(TypedDict, total=False):
    """When request cannot be handled"""
    reason: str  # Reason for failure


@dataclass
class Location:
    """Location information"""
    full_address: str
    name: str
    address: str
    city: str
    state: str
    country: str
    postal_code: str
    coordinates: tuple[float, float]  # latitude, longitude

@dataclass
class HotelDeps:
    """Dependencies for hotel service agents"""
    room_number: str
    guest_name: str
    hotel_location: Location

# Example hotel data (in production this would come from a real database)
SAMPLE_HOTEL_DATA = {
    "location": Location(
        name="The Funkhaus Hotel",
        full_address="Kortumstr 68, 44787 Bochum, Germany",
        address="Kortumstr 68",
        city="Bochum",
        state="NRW",
        country="de",
        postal_code="44787",
        coordinates=(51.4803947247399, 7.217586297768458)
    )
}