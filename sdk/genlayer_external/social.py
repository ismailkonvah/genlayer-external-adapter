from .core import relay_call


def get_social_buzz(topic: str, platform: str = "reddit") -> int:
    response = relay_call("social", {"topic": topic, "platform": platform})
    return response["buzz_score"]
