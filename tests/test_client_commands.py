from messenger.client import parse_user_input


def test_plain_text_goes_to_current_room() -> None:
    parsed = parse_user_input("hello", "main")
    assert parsed.action == "send_room"
    assert parsed.payload == {"room": "main", "text": "hello"}


def test_join_changes_room() -> None:
    parsed = parse_user_input("/join team", "main")
    assert parsed.action == "join_room"
    assert parsed.room == "team"


def test_dm_command() -> None:
    parsed = parse_user_input("/dm Bob ping", "main")
    assert parsed.action == "send_dm"
    assert parsed.payload == {"to": "Bob", "text": "ping"}


def test_unknown_command() -> None:
    parsed = parse_user_input("/abracadabra", "main")
    assert parsed.action is None
    assert parsed.local_message is not None
