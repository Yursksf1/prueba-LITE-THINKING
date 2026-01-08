from dataclasses import dataclass
from typing import Dict, Iterable, Tuple

from ..exceptions.errors import InvalidProductError, InvalidPriceError
from .money import Money


def _normalize_text(value: str, field_name: str) -> str:
    if value is None:
        raise InvalidProductError(f"{field_name} is required")
    normalized = value.strip()
    if not normalized:
        raise InvalidProductError(f"{field_name} is required")
    return normalized


def _normalize_features(features: Iterable[str]) -> Tuple[str, ...]:
    normalized = tuple(_normalize_text(item, "Feature") for item in features)
    return normalized


@dataclass(frozen=True)
class Product:
    code: str
    name: str
    features: Tuple[str, ...]
    prices: Dict[str, Money]
    company_nit: str

    def __post_init__(self) -> None:
        normalized_code = _normalize_text(self.code, "Code")
        normalized_name = _normalize_text(self.name, "Name")
        normalized_features = _normalize_features(self.features or ())

        if not self.prices:
            raise InvalidPriceError("At least one price is required")

        normalized_prices: Dict[str, Money] = {}
        for currency_code, price in self.prices.items():
            if not isinstance(price, Money):
                raise InvalidPriceError("Price must be a Money object")
            code_key = currency_code.strip().upper()
            if code_key in normalized_prices:
                raise InvalidPriceError("Duplicated price for currency is not allowed")
            normalized_prices[code_key] = price

        object.__setattr__(self, "code", normalized_code)
        object.__setattr__(self, "name", normalized_name)
        object.__setattr__(self, "features", normalized_features)
        object.__setattr__(self, "prices", normalized_prices)

        normalized_company = _normalize_text(self.company_nit, "Company NIT")
        object.__setattr__(self, "company_nit", normalized_company)

    def price_for(self, currency_code: str) -> Money:
        key = (currency_code or "").strip().upper()
        try:
            return self.prices[key]
        except KeyError as exc:
            raise InvalidPriceError(f"Price is not defined for {key}") from exc
