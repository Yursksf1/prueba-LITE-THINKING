from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from typing import Any

from .currency import Currency
from ..exceptions.errors import InvalidPriceError


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: Currency

    def __post_init__(self) -> None:
        amount = self._normalize_amount(self.amount)
        if amount <= Decimal("0"):
            raise InvalidPriceError("Amount must be greater than zero")
        object.__setattr__(self, "amount", amount)

    @staticmethod
    def _normalize_amount(value: Any) -> Decimal:
        try:
            decimal_value = Decimal(value)
        except (InvalidOperation, TypeError) as exc:
            raise InvalidPriceError("Invalid price amount") from exc
        return decimal_value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def add(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise InvalidPriceError("Cannot add amounts with different currencies")
        return Money(amount=self.amount + other.amount, currency=self.currency)
