import pytest

from messenger.protocol import ProtocolError, decode, encode


def test_encode_decode_roundtrip() -> None:
    packet = decode(encode("message", {"text": "hello"}))
    assert packet.action == "message"
    assert packet.payload == {"text": "hello"}


@pytest.mark.parametrize(
    "raw",
    [
        b"not-json\n",
        b"[]\n",
        b'{"action":"","payload":{}}\n',
        b'{"action":"message","payload":[]}\n',
    ],
)
def test_decode_errors(raw: bytes) -> None:
    with pytest.raises(ProtocolError):
        decode(raw)
