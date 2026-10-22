"""
Pydantic schemas for Address data validation and serialization.
"""

from pydantic import BaseModel, Field


class AddressBase(BaseModel):
    """Shared fields for reading and writing Address data."""
    name: str = Field(..., max_length=100, description="Name associated with the address location")
    street: str = Field(..., max_length=200, description="Street name and housing number")
    city: str = Field(..., max_length=100, description="City name")
    country: str = Field(..., max_length=100, description="Country name")
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude coordinate between -90 and 90")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude coordinate between -180 and 180")


class AddressCreate(AddressBase):
    """Schema for validating data when creating a new address."""
    # Inherits all fields from AddressBase as required fields
    pass


class AddressUpdate(BaseModel):
    """Schema for validating data when performing partial updates (PATCH)."""
    # All fields are optional here to allow partial updates
    name: str | None = Field(None, max_length=100)
    street: str | None = Field(None, max_length=200)
    city: str | None = Field(None, max_length=100)
    country: str | None = Field(None, max_length=100)
    latitude: float | None = Field(None, ge=-90.0, le=90.0)
    longitude: float | None = Field(None, ge=-180.0, le=180.0)


class AddressResponse(AddressBase):
    """Schema for structuring data sent back to the API client."""
    id: int

    model_config = {
        # Crucial for Pydantic v2 to seamlessly convert SQLAlchemy models into JSON responses
        "from_attributes": True
    }
