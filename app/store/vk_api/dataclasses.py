from dataclasses import dataclass
from typing import Optional


@dataclass
class UpdateObject:
    id: int
    user_id: int
    peer_id: int
    text: str
    payload: Optional[str]
    mess_id: Optional[str]


@dataclass
class Update:
    type: str
    object: UpdateObject


@dataclass
class Message:
    user_id: int
    peer_id: int
    text: str
    id: str
