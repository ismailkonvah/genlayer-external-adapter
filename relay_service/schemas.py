from pydantic import BaseModel, ConfigDict, Field


class BaseRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nonce: str = Field(min_length=8, max_length=128)
    request_timestamp: int


class WeatherRequest(BaseRequest):
    city: str = Field(min_length=1, max_length=128)


class PriceRequest(BaseRequest):
    symbol: str = Field(min_length=1, max_length=32)


class SocialRequest(BaseRequest):
    platform: str = Field(min_length=1, max_length=32)
    topic: str = Field(min_length=1, max_length=128)
