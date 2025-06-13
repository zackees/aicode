from dataclasses import dataclass

from aicode.args import Args

# Represents the best model so far.
CHAT_GPT = "openai/o3"

SONNET = "anthropic/claude-sonnet-4-20250514"
OPUS = "anthropic/claude-opus-4-20250514"


@dataclass
class Model:
    name: str
    description: str
    model_str: str


MODELS = {
    "chatgpt": Model("gpt-4o", "The GPT-o3 model.", CHAT_GPT),
    "o3": Model("o3", "The O3 model.", "openai/o3"),
    "claude": Model(
        "claude", "The Claude model.", "anthropic/claude-sonnet-4-20250514"
    ),
    "sonnet": Model(
        "sonnet", "The Claude Sonnet model, best performance for price.", SONNET
    ),
    "opus": Model(
        "opus", "The Claude Opus model, best performance but high cost.", OPUS
    ),
    "deepseek": Model(
        "deepseek",
        "The deepseek model.",
        "deepseek",
    ),
    "gemini": Model(
        "gemini",
        "The Google Gemini model.",
        "gemini/gemini-2.5-pro-preview-05-0",
    ),
}

CLAUD3_MODELS = {MODELS["claude"].model_str}

MODEL_CHOICES = list(MODELS.keys())


def get_model(
    args: Args,
    anthropic_key: str | None,
    openai_key: str | None,
    gemini_key: str | None,
) -> str:

    deep = not args.no_architect
    if deep:
        if args.model is not None and args.model in MODELS:
            return MODELS[args.model].model_str
        if openai_key is not None:
            return "openai/gpt-4o"

    if args.claude:
        assert "claude" in MODELS
        return MODELS["claude"].model_str
    elif args.chatgpt:
        return CHAT_GPT
    elif args.model is not None:
        return MODELS[args.model].model_str if args.model in MODELS else args.model
    elif anthropic_key is not None:
        return MODELS["claude"].model_str
    elif openai_key is not None:
        return CHAT_GPT
    elif gemini_key is not None:
        return MODELS["gemini"].model_str
    return MODELS["claude"].model_str
