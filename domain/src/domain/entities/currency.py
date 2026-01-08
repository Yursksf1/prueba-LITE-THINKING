from enum import Enum


class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    COP = "COP"

    @classmethod
    def from_code(cls, code: str) -> "Currency":
        normalized = (code or "").strip().upper()
        try:
            return cls(normalized)
        except ValueError as exc:  # pragma: no cover - defensive
            raise ValueError(f"Unsupported currency code: {normalized}") from exc
