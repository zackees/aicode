from dataclasses import dataclass
from typing import Any, Optional, Union


@dataclass
class Version:
    major: int
    minor: int
    patch: int

    def __init__(self, string_version: str) -> None:
        self.major, self.minor, self.patch = map(int, string_version.split("."))

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def __gt__(self, other: Any) -> bool:
        if not isinstance(other, Version):
            raise ValueError(f"Cannot compare Version with {type(other)}")
        if self.major > other.major:
            return True
        if self.major == other.major and self.minor > other.minor:
            return True
        if (
            self.major == other.major
            and self.minor == other.minor
            and self.patch > other.patch
        ):
            return True
        return False

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, Version):
            raise ValueError(f"Cannot compare Version with {type(other)}")
        if self.major < other.major:
            return True
        if self.major == other.major and self.minor < other.minor:
            return True
        if (
            self.major == other.major
            and self.minor == other.minor
            and self.patch < other.patch
        ):
            return True
        return False

    def __ge__(self, other: Any) -> bool:
        if not isinstance(other, Version):
            raise ValueError(f"Cannot compare Version with {type(other)}")
        return self > other or self == other

    def __le__(self, other: Any) -> bool:
        if not isinstance(other, Version):
            raise ValueError(f"Cannot compare Version with {type(other)}")
        return self < other or self == other

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Version):
            raise ValueError(f"Cannot compare Version with {type(other)}")
        return (
            self.major == other.major
            and self.minor == other.minor
            and self.patch == other.patch
        )


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

    def get_current_version(self) -> Version | None:
        try:
            return Version(self.current_version)
        except ValueError:
            return None

    @classmethod
    def from_json(cls, json_data: dict[str, str | bool | None]) -> "AiderUpdateResult":
        return AiderUpdateResult(
            has_update=bool(json_data["has_update"]),
            latest_version=str(json_data["latest_version"]),
            current_version=str(json_data["current_version"]),
            error=str(json_data["error"]) if json_data["error"] is not None else None,
        )
