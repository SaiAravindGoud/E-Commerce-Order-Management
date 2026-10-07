from pydantic import BaseModel, ConfigDict, Field


class AddressCreate(BaseModel):
    full_name: str = Field(
        min_length=2,
        max_length=100,
    )

    phone: str = Field(
        pattern=r"^\d{10}$",
    )

    address_line: str = Field(
        min_length=5,
        max_length=255,
    )

    city: str = Field(
        min_length=2,
        max_length=100,
    )

    state: str = Field(
        min_length=2,
        max_length=100,
    )

    pincode: str = Field(
        pattern=r"^\d{6}$",
    )

    is_default: bool = False


class AddressUpdate(BaseModel):
    full_name: str = Field(
        min_length=2,
        max_length=100,
    )

    phone: str = Field(
        pattern=r"^\d{10}$",
    )

    address_line: str = Field(
        min_length=5,
        max_length=255,
    )

    city: str = Field(
        min_length=2,
        max_length=100,
    )

    state: str = Field(
        min_length=2,
        max_length=100,
    )

    pincode: str = Field(
        pattern=r"^\d{6}$",
    )

    is_default: bool = False


class AddressResponse(BaseModel):
    id: int
    customer_id: int
    full_name: str
    phone: str
    address_line: str
    city: str
    state: str
    pincode: str
    is_default: bool

    model_config = ConfigDict(from_attributes=True)