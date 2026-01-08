from dataclasses import dataclass

from ..exceptions.errors import InvalidInventoryError


@dataclass(frozen=True)
class InventoryItem:
    company_nit: str
    product_code: str
    quantity: int = 0

    def __post_init__(self) -> None:
        if not self.company_nit or not self.company_nit.strip():
            raise InvalidInventoryError("Company NIT is required")
        if not self.product_code or not self.product_code.strip():
            raise InvalidInventoryError("Product code is required")
        if self.quantity < 0:
            raise InvalidInventoryError("Quantity cannot be negative")

    def increase(self, delta: int) -> "InventoryItem":
        if delta <= 0:
            raise InvalidInventoryError("Increment must be positive")
        return InventoryItem(
            company_nit=self.company_nit,
            product_code=self.product_code,
            quantity=self.quantity + delta,
        )

    def decrease(self, delta: int) -> "InventoryItem":
        if delta <= 0:
            raise InvalidInventoryError("Decrement must be positive")
        if delta > self.quantity:
            raise InvalidInventoryError("Insufficient stock")
        return InventoryItem(
            company_nit=self.company_nit,
            product_code=self.product_code,
            quantity=self.quantity - delta,
        )
