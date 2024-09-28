from pydantic import BaseModel


class ErrorResponseSchema(BaseModel):
    detail: dict[str, str]