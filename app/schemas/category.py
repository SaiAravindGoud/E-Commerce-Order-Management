from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    category_name: str = Field(
        min_length=2,
        max_length=100,
    )


class CategoryUpdate(BaseModel):
    category_name: str = Field(
        min_length=2,
        max_length=100,
    )


class CategoryResponse(BaseModel):
    id: int
    category_name: str

    model_config = ConfigDict(from_attributes=True)