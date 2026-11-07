import re
import uuid
from typing import Callable, Optional, Tuple

_UUID = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
_ROOM = re.compile(rf"^(dm|listing)\.({_UUID})\.({_UUID})$")


def parse_room(room_id: str) -> Optional[Tuple[str, str, str]]:
    """Split a room id into (kind, first, second), or None if it is not a valid room id.

    dm.<userA>.<userB>        a private conversation between two users (ids in sorted order)
    listing.<listing>.<tenant>  a tenant's private conversation with a listing's owner
    """
    match = _ROOM.match(room_id or "")
    if not match:
        return None
    kind, first, second = match.groups()
    for value in (first, second):
        try:
            uuid.UUID(value)
        except ValueError:
            return None
    if kind == "dm" and not first < second:
        return None
    return kind, first, second


def can_join(user_id: str, room_id: str, owner_lookup: Callable[[str], Optional[str]]) -> bool:
    """A user may join a room only if they are one of the two people it belongs to."""
    parsed = parse_room(room_id)
    if parsed is None:
        return False
    kind, first, second = parsed
    if kind == "dm":
        return user_id in (first, second)
    listing_id, tenant_id = first, second
    if user_id == tenant_id:
        return True
    owner_id = owner_lookup(listing_id)
    return owner_id is not None and user_id == owner_id
