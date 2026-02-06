from dataclasses import dataclass


@dataclass
class User:
    id: int
    name: str
    api_key: str
