from pydantic import BaseModel


class TweetRequest(BaseModel):
    text: str
