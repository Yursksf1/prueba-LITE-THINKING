from dataclasses import dataclass, replace

from ..exceptions.errors import InvalidCompanyError


def _normalize_text(value: str, field_name: str) -> str:
    if value is None:
        raise InvalidCompanyError(f"{field_name} is required")
    normalized = value.strip()
    if not normalized:
        raise InvalidCompanyError(f"{field_name} is required")
    return normalized


@dataclass(frozen=True)
class Company:
    nit: str
    name: str
    address: str
    phone: str

    def __post_init__(self) -> None:
        normalized_nit = _normalize_text(self.nit, "NIT")
        if len(normalized_nit) < 5:
            raise InvalidCompanyError("NIT must have at least 5 characters")
        normalized_name = _normalize_text(self.name, "Name")
        normalized_address = _normalize_text(self.address, "Address")
        normalized_phone = _normalize_text(self.phone, "Phone")
        if not normalized_phone.replace("+", "").replace(" ", "").isdigit():
            raise InvalidCompanyError("Phone must contain only digits and optional '+'.")
        object.__setattr__(self, "nit", normalized_nit)
        object.__setattr__(self, "name", normalized_name)
        object.__setattr__(self, "address", normalized_address)
        object.__setattr__(self, "phone", normalized_phone)

    def change_address(self, new_address: str) -> "Company":
        updated_address = _normalize_text(new_address, "Address")
        return replace(self, address=updated_address)
