from pydantic import BaseModel


class PromptInput(BaseModel):
    use_pinecone: bool = False
    user_message: str
    image: str
