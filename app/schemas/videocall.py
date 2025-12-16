from pydantic import BaseModel


class TokenRequest(BaseModel):
    channel_name: str
    uid: int
    role: str = "publisher"