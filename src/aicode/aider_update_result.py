from dataclasses import dataclass
from typing import Optional, Union


@dataclass
class AiderUpdateResult:
    has_update: bool
    latest_version: str
    current_version: str
    error: Optional[str] = None

    def get_update_msg(self) -> str:
        msg = "\n#######################################\n"
        msg += f"# UPDATE AVAILABLE: {self.current_version} -> {self.latest_version}.\n"
        msg += "# run `aicode --upgrade` to upgrade\n"
        msg += "#######################################\n"
        return msg

    def to_json_data(self) -> dict[str, Union[str, bool, None]]:
        return {
            "has_update": self.has_update,
            "latest_version": self.latest_version,
            "current_version": self.current_version,
            "error": str(self.error) if self.error is not None else None,
        }

    @classmethod
    def from_json(cls, json_data: dict[str, Union[str, bool]]) -> "AiderUpdateResult":
        return AiderUpdateResult(
            has_update=bool(json_data["has_update"]),
            latest_version=str(json_data["latest_version"]),
            current_version=str(json_data["current_version"]),
            error=str(json_data["error"]) if json_data["error"] is not None else None,
        )
