from pydantic import Field

from apps.base.schemas import BaseInputSchema


class AreaCreateSchema(BaseInputSchema):
    """Validate input for creating a custom user area."""

    name: str = Field(max_length=100)
    description: str | None = None
    icon: str | None = Field(None, max_length=50)
    image_url: str | None = None
    color: str | None = Field(None, max_length=20)
    display_order: int | None = None
