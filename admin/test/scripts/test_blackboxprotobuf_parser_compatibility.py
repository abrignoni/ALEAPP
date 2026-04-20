import ast
import unittest
from pathlib import Path

import scripts  # pylint: disable=unused-import
import blackboxprotobuf


REPO_ROOT = Path(__file__).resolve().parents[3]
ARTIFACTS_DIR = REPO_ROOT / "scripts" / "artifacts"

BBPB_IMPORTING_ARTIFACTS = (
    "scripts/artifacts/FCMQueuedMessagesDump.py",
    "scripts/artifacts/airtagAndroid.py",
    "scripts/artifacts/appSemloc.py",
    "scripts/artifacts/battery_usage_v9.py",
    "scripts/artifacts/bumble.py",
    "scripts/artifacts/callTranscription.py",
    "scripts/artifacts/chatgpt.py",
    "scripts/artifacts/gboard.py",
    "scripts/artifacts/gmailEmails.py",
    "scripts/artifacts/googleCalendar.py",
    "scripts/artifacts/googleCallScreen.py",
    "scripts/artifacts/googleChat.py",
    "scripts/artifacts/googleInitiatedNav.py",
    "scripts/artifacts/googleLastTrip.py",
    "scripts/artifacts/googleMapsGmm.py",
    "scripts/artifacts/googleMapsSearches.py",
    "scripts/artifacts/googleNowPlaying.py",
    "scripts/artifacts/googleQuickSearchbox.py",
    "scripts/artifacts/googleQuickSearchboxRecent.py",
    "scripts/artifacts/googleTasks.py",
    "scripts/artifacts/googleVoice.py",
    "scripts/artifacts/sharedProto.py",
    "scripts/artifacts/usageapps.py",
)

BBPB_DECODING_ARTIFACTS = (
    "scripts/artifacts/FCMQueuedMessagesDump.py",
    "scripts/artifacts/airtagAndroid.py",
    "scripts/artifacts/appSemloc.py",
    "scripts/artifacts/battery_usage_v9.py",
    "scripts/artifacts/bumble.py",
    "scripts/artifacts/callTranscription.py",
    "scripts/artifacts/chatgpt.py",
    "scripts/artifacts/gboard.py",
    "scripts/artifacts/gmailEmails.py",
    "scripts/artifacts/googleCallScreen.py",
    "scripts/artifacts/googleChat.py",
    "scripts/artifacts/googleInitiatedNav.py",
    "scripts/artifacts/googleLastTrip.py",
    "scripts/artifacts/googleMapsGmm.py",
    "scripts/artifacts/googleMapsSearches.py",
    "scripts/artifacts/googleNowPlaying.py",
    "scripts/artifacts/googleQuickSearchbox.py",
    "scripts/artifacts/googleQuickSearchboxRecent.py",
    "scripts/artifacts/googleTasks.py",
    "scripts/artifacts/googleVoice.py",
    "scripts/artifacts/sharedProto.py",
    "scripts/artifacts/usageapps.py",
)


def _varint(value):
    output = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        if value:
            output.append(byte | 0x80)
        else:
            output.append(byte)
            return bytes(output)


def _key(field_number, wire_type):
    return _varint((field_number << 3) | wire_type)


def _field_varint(field_number, value):
    return _key(field_number, 0) + _varint(value)


def _field_bytes(field_number, value):
    return _key(field_number, 2) + _varint(len(value)) + value


def _field_fixed32(field_number, value):
    return _key(field_number, 5) + value.to_bytes(4, "little")


def _read_module(path):
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _imports_blackboxprotobuf(path):
    tree = _read_module(path)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "blackboxprotobuf":
                    return True
        elif isinstance(node, ast.ImportFrom) and node.module == "blackboxprotobuf":
            return True
    return False


def _calls_blackboxprotobuf_decode_message(path):
    tree = _read_module(path)
    module_aliases = set()
    decode_aliases = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "blackboxprotobuf":
                    module_aliases.add(alias.asname or alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module == "blackboxprotobuf":
            for alias in node.names:
                if alias.name == "decode_message":
                    decode_aliases.add(alias.asname or alias.name)

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        func = node.func
        if isinstance(func, ast.Attribute) and func.attr == "decode_message":
            if isinstance(func.value, ast.Name) and func.value.id in module_aliases:
                return True
        elif isinstance(func, ast.Name) and func.id in decode_aliases:
            return True

    return False


class TestBlackboxProtobufParserCompatibility(unittest.TestCase):
    def test_parser_inventory_matches_blackboxprotobuf_imports(self):
        current = tuple(
            sorted(
                path.relative_to(REPO_ROOT).as_posix()
                for path in ARTIFACTS_DIR.glob("*.py")
                if _imports_blackboxprotobuf(path)
            )
        )

        self.assertEqual(current, BBPB_IMPORTING_ARTIFACTS)

    def test_decode_inventory_matches_blackboxprotobuf_call_sites(self):
        current = tuple(
            sorted(
                path.relative_to(REPO_ROOT).as_posix()
                for path in ARTIFACTS_DIR.glob("*.py")
                if _calls_blackboxprotobuf_decode_message(path)
            )
        )

        self.assertEqual(current, BBPB_DECODING_ARTIFACTS)

    def test_implicit_nested_decode_keeps_parser_byte_contract(self):
        payload = (
            _field_bytes(
                1,
                _field_bytes(10, b"sender@example.com")
                + _field_bytes(12, _field_bytes(1, b"hello from chat")),
            )
            + _field_varint(13, 3)
        )

        values, types = blackboxprotobuf.decode_message(payload)

        self.assertEqual(values["1"]["10"], b"sender@example.com")
        self.assertEqual(values["1"]["12"]["1"], b"hello from chat")
        self.assertEqual(values["13"], 3)
        self.assertEqual(types["1"]["message_typedef"]["10"]["type"], "bytes")
        self.assertEqual(
            types["1"]["message_typedef"]["12"]["message_typedef"]["1"]["type"],
            "bytes",
        )

    def test_none_and_none_string_typedef_call_patterns_keep_bytes(self):
        payload = (
            _field_bytes(
                2,
                _field_bytes(2, b"task title") + _field_bytes(3, b"task details"),
            )
            + _field_bytes(
                6,
                _field_bytes(2, b"address") + _field_bytes(6, b"https://maps.example"),
            )
        )

        for typedef in (None, "None"):
            with self.subTest(typedef=typedef):
                values, types = blackboxprotobuf.decode_message(payload, typedef)

                self.assertEqual(values["2"]["2"], b"task title")
                self.assertEqual(values["2"]["3"], b"task details")
                self.assertEqual(values["6"]["2"], b"address")
                self.assertEqual(values["6"]["6"], b"https://maps.example")
                self.assertEqual(types["2"]["message_typedef"]["2"]["type"], "bytes")
                self.assertEqual(types["6"]["message_typedef"]["6"]["type"], "bytes")

    def test_generated_typedef_can_be_reused_for_followup_decodes(self):
        _, generated_types = blackboxprotobuf.decode_message(
            _field_bytes(1, b"cached value")
        )

        values, reused_types = blackboxprotobuf.decode_message(
            _field_bytes(1, b"fresh value"), generated_types
        )

        self.assertEqual(values["1"], b"fresh value")
        self.assertEqual(reused_types["1"]["type"], "bytes")

    def test_explicit_typedef_inputs_remain_supported(self):
        typedef = {
            "6": {
                "type": "message",
                "message_typedef": {
                    "1": {"type": "int", "name": ""},
                    "2": {"type": "bytes", "name": ""},
                    "4": {"type": "fixed32", "name": ""},
                },
                "name": "",
            }
        }
        payload = _field_bytes(
            6,
            _field_varint(1, 7)
            + _field_bytes(2, b"typed text")
            + _field_fixed32(4, 12345),
        )

        values, actual_types = blackboxprotobuf.decode_message(payload, typedef)

        self.assertEqual(values["6"]["1"], 7)
        self.assertEqual(values["6"]["2"], b"typed text")
        self.assertEqual(values["6"]["4"], 12345)
        self.assertEqual(actual_types["6"]["message_typedef"]["2"]["type"], "bytes")


if __name__ == "__main__":
    unittest.main()
