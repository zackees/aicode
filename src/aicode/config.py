from dataclasses import asdict, dataclass, field, fields
from typing import Dict, Optional, Union


@dataclass
class Config:
    openai_key: Optional[str] = None
    anthropic_key: Optional[str] = None
    aider_update_info: Dict[str, Union[str, bool, None]] = field(default_factory=dict)

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
