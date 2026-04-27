from pydantic import BaseModel as PydanticBaseModel, ConfigDict


class BaseInputSchema(PydanticBaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")
