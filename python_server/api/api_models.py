from pydantic import BaseModel


class PromptInput(BaseModel):
    user_message: str

class ImageInput(BaseModel):
    image: str