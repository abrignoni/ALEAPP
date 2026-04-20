"""Runtime compatibility helpers for the scripts package.

ALEAPP historically used the unmaintained ``blackboxprotobuf`` package. The
maintained ``bbpb`` package still exposes the same ``blackboxprotobuf`` import
path, but its type inference is not byte-for-byte compatible with the old
package. In particular, bbpb decodes valid UTF-8 length-delimited fields as
``str`` values, while the existing artifact parsers expect ``bytes`` and often
call ``.decode(...)`` themselves.

This module is imported before artifact modules are loaded, so it is a safe
place to patch bbpb's ``decode_message`` return values back to the legacy shape
without editing every parser individually.
"""

import os


os.environ.setdefault("PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION", "python")


def _coerce_blackboxprotobuf_value(value):
    """Convert decoded message values back to the legacy parser contract."""
    if isinstance(value, str):
        return value.encode("utf-8")
    if isinstance(value, list):
        return [_coerce_blackboxprotobuf_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_coerce_blackboxprotobuf_value(item) for item in value)
    if isinstance(value, dict):
        return {
            key: _coerce_blackboxprotobuf_value(item)
            for key, item in value.items()
        }
    return value


def _coerce_blackboxprotobuf_typedef(typedef):
    """Normalize bbpb-generated typedefs to the old blackboxprotobuf shape."""
    if isinstance(typedef, list):
        return [_coerce_blackboxprotobuf_typedef(item) for item in typedef]
    if not isinstance(typedef, dict):
        return typedef

    coerced = {}
    for key, value in typedef.items():
        # These bbpb bookkeeping keys are useful for re-encoding, but the old
        # package did not expose them and ALEAPP parsers do not consume them.
        if key in {"field_order", "seen_repeated"}:
            continue
        if key == "type" and value == "string":
            coerced[key] = "bytes"
        else:
            coerced[key] = _coerce_blackboxprotobuf_typedef(value)

    # Older blackboxprotobuf typedefs included empty names for inferred fields.
    # Keeping that shape avoids surprising any parser or test that inspects the
    # generated typedef metadata.
    if ("type" in coerced or "message_typedef" in coerced) and "name" not in coerced:
        coerced["name"] = ""

    return coerced


def _patch_blackboxprotobuf_decode_message():
    import blackboxprotobuf

    # Importing scripts can happen more than once during test discovery and
    # plugin loading. Avoid wrapping decode_message repeatedly.
    if getattr(blackboxprotobuf.decode_message, "aleapp_byte_compat", False):
        return

    original_decode_message = blackboxprotobuf.decode_message

    def decode_message(*args, **kwargs):
        # bbpb 1.4.x infers UTF-8 fields as str; existing parsers expect bytes.
        value, typedef = original_decode_message(*args, **kwargs)
        return (
            _coerce_blackboxprotobuf_value(value),
            _coerce_blackboxprotobuf_typedef(typedef),
        )

    decode_message.aleapp_byte_compat = True
    decode_message.__wrapped__ = original_decode_message
    blackboxprotobuf.decode_message = decode_message


_patch_blackboxprotobuf_decode_message()
