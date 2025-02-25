from dataclasses import dataclass

from aicode.args import Args

CHAT_GPT = "openai/gpt-4o"


@dataclass
class Model:
    name: str
    description: str
    model_str: str


MODELS = {
    "chatgpt": Model("gpt-4o", "The GPT-4o model.", CHAT_GPT),
    "claude": Model(
        "claude", "The Claude model.", "anthropic/claude-3-7-sonnet-20250219"
    ),
    "deepseek": Model(
        "deepseek",
        "The deepseek model.",
        "deepseek",
    ),
}

CLAUD3_MODELS = {"claude"}

MODEL_CHOICES = list(MODELS.keys())


def get_model(args: Args, anthropic_key: str | None, openai_key: str | None) -> str:

    if args.claude:
        assert "claude" in MODELS
        return "claude"
    elif args.chatgpt:
        return CHAT_GPT
    elif args.model is not None:
        return args.model
    elif anthropic_key is not None:
        return "claude"
    elif openai_key is not None:
        return CHAT_GPT
    return "claude"
