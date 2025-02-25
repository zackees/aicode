from dataclasses import dataclass, field


@dataclass
class Config:
    openai_key: str | None = None
    anthropic_key: str | None = None
    aider_update_info: dict[str, str | bool | None] = field(default_factory=dict)

    @staticmethod
    def from_dict(data: dict) -> "Config":
        return Config(
            openai_key=data.get("openai_key"),
            anthropic_key=data.get("anthropic_key"),
            aider_update_info=data.get("aider_update_info", {}),
        )

    def to_dict(self) -> dict:
        return {
            "openai_key": self.openai_key,
            "anthropic_key": self.anthropic_key,
            "aider_update_info": self.aider_update_info,
        }
