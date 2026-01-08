class DomainError(Exception):
    """Base class for domain-specific errors."""


class InvalidCompanyError(DomainError):
    pass


class InvalidProductError(DomainError):
    pass


class InvalidPriceError(DomainError):
    pass


class InvalidInventoryError(DomainError):
    pass
