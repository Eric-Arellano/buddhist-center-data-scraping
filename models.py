from dataclasses import dataclass


@dataclass(frozen=True)
class Address:
    addr1: str
    addr2: str | None
    city: str
    state: str
    zip: str


@dataclass(frozen=True)
class Center:
    name: str
    address: Address
    website: str | None
    emails: tuple[str, ...]
    phone_numbers: tuple[str, ...]
    traditions: tuple[str, ...]
    affiliation: str | None
