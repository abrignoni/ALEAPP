"""Runtime compatibility helpers for the scripts package."""

import os


os.environ.setdefault("PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION", "python")


def _coerce_blackboxprotobuf_value(value):
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
    if isinstance(typedef, list):
        return [_coerce_blackboxprotobuf_typedef(item) for item in typedef]
    if not isinstance(typedef, dict):
        return typedef

    coerced = {}
    for key, value in typedef.items():
        if key in {"field_order", "seen_repeated"}:
            continue
        if key == "type" and value == "string":
            coerced[key] = "bytes"
        else:
            coerced[key] = _coerce_blackboxprotobuf_typedef(value)

    if ("type" in coerced or "message_typedef" in coerced) and "name" not in coerced:
        coerced["name"] = ""

    return coerced


def _patch_blackboxprotobuf_decode_message():
    import blackboxprotobuf

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
