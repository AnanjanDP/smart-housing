import time

import jwt
import pytest
from starlette.websockets import WebSocketDisconnect

from app.api import ws_chat
from app.core.config import settings

KEY = "k" * 40
USER_A = "11111111-1111-4111-8111-111111111111"
USER_B = "22222222-2222-4222-8222-222222222222"
USER_C = "33333333-3333-4333-8333-333333333333"
LISTING = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
DM_AB = f"dm.{USER_A}.{USER_B}"
DM_AC = f"dm.{USER_A}.{USER_C}"
LISTING_ROOM = f"listing.{LISTING}.{USER_A}"  # tenant A talking to the listing's owner (user B)


@pytest.fixture(autouse=True)
def chat_settings(monkeypatch):
    monkeypatch.setattr(settings, "JWT_SIGNING_KEY", KEY)
    monkeypatch.setattr(ws_chat, "lookup_listing_owner", lambda listing_id: USER_B if listing_id == LISTING else None)
    ws_chat.manager.rooms.clear()
    yield
    ws_chat.manager.rooms.clear()


def token_for(user_id, **overrides):
    claims = {"user_id": user_id, "token_type": "access", "exp": int(time.time()) + 600}
    claims.update(overrides)
    return jwt.encode({k: v for k, v in claims.items() if v is not None}, KEY, algorithm="HS256")


def open_room(client, room, **kwargs):
    return client.websocket_connect(f"/api/v1/search/ws/chat/{room}", **kwargs)


def join(socket, token):
    socket.send_json({"type": "auth", "token": token})
    return socket.receive_json()


def assert_closed(socket, code):
    with pytest.raises(WebSocketDisconnect) as closed:
        socket.receive_json()
    assert closed.value.code == code


# ---------------------------------------------------------------- authentication
def test_a_valid_token_joins_its_own_room(client):
    with open_room(client, DM_AB) as socket:
        hello = join(socket, token_for(USER_A))
    assert hello["type"] == "connection_established"
    assert hello["user_id"] == USER_A


def test_no_token_means_no_access(client):
    with open_room(client, DM_AB) as socket:
        socket.send_json({"type": "chat", "text": "let me in"})
        assert_closed(socket, 4401)


def test_the_connection_is_dropped_if_nothing_is_sent_in_time(client, monkeypatch):
    monkeypatch.setattr(ws_chat, "AUTH_TIMEOUT_SECONDS", 0.2)
    with open_room(client, DM_AB) as socket:
        assert_closed(socket, 4401)


@pytest.mark.parametrize("bad", ["", "abc", "a.b.c", None, 123])
def test_malformed_tokens_are_rejected(client, bad):
    with open_room(client, DM_AB) as socket:
        socket.send_json({"type": "auth", "token": bad})
        assert_closed(socket, 4401)


def test_non_json_first_frame_is_rejected(client):
    with open_room(client, DM_AB) as socket:
        socket.send_text("hello")
        assert_closed(socket, 4401)


def test_a_token_signed_with_another_key_is_rejected(client):
    forged = jwt.encode({"user_id": USER_A, "token_type": "access", "exp": int(time.time()) + 600},
                        "x" * 40, algorithm="HS256")
    with open_room(client, DM_AB) as socket:
        socket.send_json({"type": "auth", "token": forged})
        assert_closed(socket, 4401)


def test_an_expired_token_is_rejected(client):
    with open_room(client, DM_AB) as socket:
        socket.send_json({"type": "auth", "token": token_for(USER_A, exp=int(time.time()) - 5)})
        assert_closed(socket, 4401)


def test_a_refresh_token_cannot_be_used_for_chat(client):
    with open_room(client, DM_AB) as socket:
        socket.send_json({"type": "auth", "token": token_for(USER_A, token_type="refresh")})
        assert_closed(socket, 4401)


def test_a_token_without_a_user_is_rejected(client):
    with open_room(client, DM_AB) as socket:
        socket.send_json({"type": "auth", "token": token_for(None)})
        assert_closed(socket, 4401)


def test_nothing_is_accepted_when_the_signing_key_is_not_configured(client, monkeypatch):
    monkeypatch.setattr(settings, "JWT_SIGNING_KEY", "")
    with open_room(client, DM_AB) as socket:
        socket.send_json({"type": "auth", "token": token_for(USER_A)})
        assert_closed(socket, 4401)


# ---------------------------------------------------------------- room privacy
def test_a_third_person_cannot_join_a_private_conversation(client):
    with open_room(client, DM_AB) as socket:
        socket.send_json({"type": "auth", "token": token_for(USER_C)})
        assert_closed(socket, 4403)


@pytest.mark.parametrize("room", [
    "landlord-general", "landlord-prop-123", "roommate-1", "dm.not-a-uuid.also-not", "x" * 300,
    f"dm.{USER_B}.{USER_A}",          # ids out of order: only the sorted form is a valid room
    f"dm.{USER_A}.{USER_A}",          # a conversation with yourself
    f"listing.{LISTING}",             # missing the tenant
])
def test_invalid_room_ids_are_refused(client, room):
    with open_room(client, room) as socket:
        socket.send_json({"type": "auth", "token": token_for(USER_A)})
        assert_closed(socket, 4403)


def test_the_tenant_and_the_owner_can_share_a_listing_room(client):
    with open_room(client, LISTING_ROOM) as tenant, open_room(client, LISTING_ROOM) as owner:
        assert join(tenant, token_for(USER_A))["type"] == "connection_established"
        assert join(owner, token_for(USER_B))["type"] == "connection_established"
        tenant.send_json({"id": 1, "text": "Is it available?", "sender_name": "Alex"})
        assert tenant.receive_json()["text"] == "Is it available?"
        assert owner.receive_json()["text"] == "Is it available?"


def test_other_tenants_cannot_read_someone_elses_conversation_with_the_owner(client):
    with open_room(client, LISTING_ROOM) as socket:
        socket.send_json({"type": "auth", "token": token_for(USER_C)})
        assert_closed(socket, 4403)


def test_a_room_for_a_listing_that_does_not_exist_is_closed_to_non_tenants(client):
    unknown = f"listing.bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb.{USER_A}"
    with open_room(client, unknown) as socket:
        socket.send_json({"type": "auth", "token": token_for(USER_B)})
        assert_closed(socket, 4403)


def test_a_failing_ownership_lookup_denies_access(client, monkeypatch):
    def broken(listing_id):
        raise RuntimeError("database down")

    monkeypatch.setattr(ws_chat, "lookup_listing_owner", broken)
    with open_room(client, LISTING_ROOM) as socket:
        socket.send_json({"type": "auth", "token": token_for(USER_B)})
        assert_closed(socket, 1011)


def test_messages_stay_inside_their_room(client):
    with open_room(client, DM_AB) as a_in_ab, open_room(client, DM_AC) as c_in_ac:
        join(a_in_ab, token_for(USER_A))
        join(c_in_ac, token_for(USER_C))
        a_in_ab.send_json({"text": "private to B"})
        assert a_in_ab.receive_json()["text"] == "private to B"
        c_in_ac.send_json({"text": "private to A"})
        assert c_in_ac.receive_json()["text"] == "private to A"  # first frame C sees is its own


# ---------------------------------------------------------------- message handling
def test_the_sender_comes_from_the_token_not_the_message(client):
    with open_room(client, DM_AB) as socket:
        join(socket, token_for(USER_A))
        socket.send_json({"text": "hi", "sender_id": USER_B, "sender": "admin", "sender_name": "\x00Bob\x07\n"})
        message = socket.receive_json()
    assert message["sender_id"] == USER_A
    assert message["sender_name"] == "Bob"
    assert message["type"] == "chat_message"
    assert "T" in message["timestamp"]  # server-assigned ISO timestamp


def test_the_clients_message_id_is_echoed_so_it_can_deduplicate(client):
    with open_room(client, DM_AB) as socket:
        join(socket, token_for(USER_A))
        socket.send_json({"id": 1731000000000, "text": "hi"})
        message = socket.receive_json()
    assert message["client_id"] == 1731000000000
    assert message["id"] != message["client_id"]


def test_oversized_client_ids_are_dropped(client):
    with open_room(client, DM_AB) as socket:
        join(socket, token_for(USER_A))
        socket.send_json({"id": "x" * 500, "text": "hi"})
        assert socket.receive_json()["client_id"] is None


def test_empty_and_non_text_messages_are_ignored(client):
    with open_room(client, DM_AB) as socket:
        join(socket, token_for(USER_A))
        for junk in ({"text": ""}, {"text": "   "}, {"text": 42}, {"text": ["x"]}, {}, [1, 2], "plain text"):
            socket.send_json(junk)
        socket.send_json({"text": "real"})
        assert socket.receive_json()["text"] == "real"


def test_long_text_is_truncated(client):
    with open_room(client, DM_AB) as socket:
        join(socket, token_for(USER_A))
        socket.send_json({"text": "a" * (ws_chat.MAX_TEXT_CHARS + 500)})
        assert len(socket.receive_json()["text"]) == ws_chat.MAX_TEXT_CHARS


def test_an_oversized_frame_closes_the_connection(client):
    with open_room(client, DM_AB) as socket:
        join(socket, token_for(USER_A))
        socket.send_text("x" * (ws_chat.MAX_FRAME_CHARS + 1))
        assert_closed(socket, 1009)


def test_flooding_is_rate_limited(client, monkeypatch):
    monkeypatch.setattr(ws_chat, "RATE_LIMIT_MESSAGES", 3)
    with open_room(client, DM_AB) as socket:
        join(socket, token_for(USER_A))
        for n in range(5):
            socket.send_json({"text": f"m{n}"})
        frames = [socket.receive_json() for _ in range(5)]
    assert [f["type"] for f in frames] == ["chat_message"] * 3 + ["error"] * 2
    assert frames[3]["code"] == "rate_limited"


def test_a_room_has_a_connection_limit(client, monkeypatch):
    monkeypatch.setattr(ws_chat, "MAX_CONNECTIONS_PER_ROOM", 2)
    with open_room(client, DM_AB) as first, open_room(client, DM_AB) as second, open_room(client, DM_AB) as third:
        join(first, token_for(USER_A))
        join(second, token_for(USER_B))
        third.send_json({"type": "auth", "token": token_for(USER_A)})
        assert_closed(third, 4429)


def test_leaving_frees_the_slot(client):
    with open_room(client, DM_AB) as socket:
        join(socket, token_for(USER_A))
        assert ws_chat.manager.room_size(DM_AB) == 1
    assert ws_chat.manager.room_size(DM_AB) == 0


# ---------------------------------------------------------------- cross-site protection
def test_other_websites_cannot_open_a_chat_connection(client):
    with pytest.raises(WebSocketDisconnect):
        with open_room(client, DM_AB, headers={"origin": "https://evil.example"}):
            pass


def test_the_frontend_origin_is_allowed(client):
    with open_room(client, DM_AB, headers={"origin": "http://localhost:5173"}) as socket:
        assert join(socket, token_for(USER_A))["type"] == "connection_established"
