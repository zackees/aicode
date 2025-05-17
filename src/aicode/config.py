from dataclasses import asdict, dataclass, field, fields
from typing import Dict, Optional, Union

from aicode.aider_update_result import AiderUpdateResult


@dataclass
class Config:
    openai_key: Optional[str] = None
    anthropic_key: Optional[str] = None
    gemini_key: Optional[str] = None
    aider_update_info: Dict[str, Union[str, bool, None]] = field(default_factory=dict)

    @property
    def aider_update_result(self) -> AiderUpdateResult | None:
        if self.aider_update_info:
            return AiderUpdateResult.from_json(self.aider_update_info)
        return None

    @staticmethod
    def from_dict(data: dict) -> "Config":
        # Only extract keys that match the dataclass fields
        valid_keys = {f.name for f in fields(Config)}
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        return Config(**filtered_data)

    @staticmethod
    def load() -> "Config":
        from aicode.openaicfg import load_from_storage

        data: dict = load_from_storage()
        return Config.from_dict(data)

    def to_dict(self) -> dict:
        return asdict(self)

    def save(self) -> None:
        from aicode.openaicfg import save_config

        save_config(self.to_dict())
