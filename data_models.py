from pydantic import BaseModel
from typing import List


class RequestedPiece(BaseModel):
    length_mm: int
    count: int
    # AI must always fill a string, even if it is "Untitled"
    label: str


class MaterialOrder(BaseModel):
    # AI must always fill a string, even if it is "Unknown"
    material_type: str

    # AI must always fill a list (e.g. [6000])
    stock_lengths_mm: List[int]

    # Kerf width is NOT HERE. It is a saw parameter, not part of the text order.

    pieces: List[RequestedPiece]