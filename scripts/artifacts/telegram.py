__artifacts_v2__ = {
    "telegram_cache4_messages": {
        "name": "Messages",
        "description": "Extracts forensically relevant Telegram message records from cache4.db",
        "author": "@WriteBlocked - Hiller Hoover",
        "version": "0.1",
        "date": "2026-04-13",
        "requirements": "none",
        "category": "Telegram",
        "artifact_icon": "message-circle",
        "notes": "",
        "paths": (
            '*/org.telegram.messenger/files/cache4.db*',
            '*/org.telegram.messenger/files/account*/cache4.db*',
        ),
        "function": "get_telegram_cache4_messages"
    },
    "telegram_user_preferences": {
        "name": "User Prefs",
        "description": "Extracts Telegram account and user preference data from userconfig XML files",
        "author": "@WriteBlocked - Hiller Hoover",
        "version": "0.1",
        "date": "2026-04-10",
        "requirements": "none",
        "category": "Telegram",
        "artifact_icon": "settings",
        "notes": "",
        "paths": (
            '*/org.telegram.messenger/shared_prefs/userconfing.xml',
            '*/org.telegram.messenger/shared_prefs/userconfig*.xml',
        ),
        "function": "get_telegram_user_preferences"
    }
}

"""
Version history:

4/6/2026: Cloned aLEAPP, set up pycharm for editing. started creating functions.
4/7/2026: added userconfing.xml parsing.  
4/9/2026: added helper functions for TLObject parsing.
4/13/2026: Improved SQLite query logic
4/14/2026: deduplicated some functionality and created new helper functions.
Between 4/15/2026-6/8/2026: added support for new constructor

TODO:
Add more compatible versions of Telegram. I believe this version works for the most recent of Telegram, and can work on versions installed back to 2024.
Integrate with LAVA conversational view.
remove standalone test, set up ALEAPP profile

NOTE:
this parser only supports one user, the active one. 
Also, I did not have a full set of test data to parse artifacts like drafts. 
in the event i didnt understand the relevance of an artifact I didn't include it. 
I can add more upon request if necessary. 
"""

from datetime import datetime, timezone, timedelta
import argparse
import sqlite3
import base64
import xml.etree.ElementTree as ET
import io
import struct
import os
import re
import html

try:
    from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly, does_column_exist_in_db, media_to_html, icons
    from scripts.artifact_report import ArtifactHtmlReport
    from scripts.filetype import types
    import scripts.ilapfuncs
    _ALEAPP_AVAILABLE = True
except ImportError:
    _ALEAPP_AVAILABLE = False

    def logfunc(message):
        print(message)

    def tsv(*args, **kwargs):
        return None

    def timeline(*args, **kwargs):
        return None

    def media_to_html(file_name, media_files, report_folder):
        return html.escape(file_name or "")

# Telegram build support is intentionally conservative for now.
# The parser will still attempt untested builds, but ALEAPP output will warn
# when the current dump was not validated against one of these build numbers.
SUPPORTED_TELEGRAM_APP_UPDATE_BUILDS = {
    42832: "Validated against the sample Android 14 Telegram cache4.db used during development.",
}

# TLReader and the helper functions later in this file are not duplicates:
# - TLReader is a stateful reader for cache4.db BLOBs and keeps its own offset.
# - The helper region contains small stateless helpers used for XML/base64 blobs
#   and for older experiments that are still useful elsewhere in this file.

class TLReader:
    """
    Minimal stdlib-only TL (Type Language) binary stream reader for decoding
    Telegram cache4.db message blobs.

    TL is Telegram's binary serialization format. All integers are little-endian.
    Strings are length-prefixed with 4-byte alignment padding.

    This implementation covers the constructors needed to decode messages_v2 blobs
    from Telegram for Android's local SQLite cache (cache4.db), targeting the
    constructor layout introduced around Telegram API layer 158+ (message#76bec211).

    Reference: https://core.telegram.org/mtproto/TL

    The class is intentionally stateful: every read advances self._off.
    That makes it easier to walk a Telegram message blob in the exact field
    order it was serialized on disk.
    """

    # -- Peer constructor IDs --
    _PEER_USER_32    = 0x9db1bc6d  # peerUser    user_id:int
    _PEER_CHAT_32    = 0xbad0e5bb  # peerChat    chat_id:int
    _PEER_CHANNEL_32 = 0xbddde532  # peerChannel channel_id:int
    _PEER_USER_64    = 0x59511722  # peerUser    user_id:long
    _PEER_CHAT_64    = 0x36c6019a  # peerChat    chat_id:long
    _PEER_CHANNEL_64 = 0x20d51b14  # peerChannel channel_id:long

    # -- Vector constructor --
    _VECTOR = 0x1cb5c415

    def __init__(self, data):
        self._buf = bytes(data)
        self._off = 0

    @property
    def offset(self):
        return self._off

    def remaining(self):
        return len(self._buf) - self._off

    # ---- Primitive read methods ----

    def read_u32(self):
        """Read a 32-bit unsigned little-endian integer."""
        if self._off + 4 > len(self._buf):
            raise EOFError(f"read_u32 past end at offset {self._off}")
        v = struct.unpack_from("<I", self._buf, self._off)[0]
        self._off += 4
        return v

    def read_i32(self):
        """Read a 32-bit signed little-endian integer."""
        if self._off + 4 > len(self._buf):
            raise EOFError(f"read_i32 past end at offset {self._off}")
        v = struct.unpack_from("<i", self._buf, self._off)[0]
        self._off += 4
        return v

    def read_i64(self):
        """Read a 64-bit signed little-endian integer."""
        if self._off + 8 > len(self._buf):
            raise EOFError(f"read_i64 past end at offset {self._off}")
        v = struct.unpack_from("<q", self._buf, self._off)[0]
        self._off += 8
        return v

    def read_u64(self):
        """Read a 64-bit unsigned little-endian integer."""
        if self._off + 8 > len(self._buf):
            raise EOFError(f"read_u64 past end at offset {self._off}")
        v = struct.unpack_from("<Q", self._buf, self._off)[0]
        self._off += 8
        return v

    def read_double(self):
        """Read a 64-bit IEEE 754 double."""
        if self._off + 8 > len(self._buf):
            raise EOFError(f"read_double past end at offset {self._off}")
        v = struct.unpack_from("<d", self._buf, self._off)[0]
        self._off += 8
        return v

    def peek_u32(self):
        """Peek at the next uint32 without advancing the offset."""
        if self._off + 4 > len(self._buf):
            raise EOFError(f"peek_u32 past end at offset {self._off}")
        return struct.unpack_from("<I", self._buf, self._off)[0]

    def read_bytes_raw(self):
        """
        Read a TL-encoded byte string.

        Encoding rules:
          - If first byte < 254: that byte is the length; data follows;
            then zero-padding to bring (1+length) to a 4-byte boundary.
          - If first byte == 254: next 3 bytes (LE) are the length; data follows;
            then zero-padding to bring (4+length) to a 4-byte boundary.
        """
        if self._off >= len(self._buf):
            raise EOFError(f"read_bytes_raw past end at offset {self._off}")
        first = self._buf[self._off]
        self._off += 1

        if first < 254:
            length = first
            header_size = 1
        elif first == 254:
            if self._off + 3 > len(self._buf):
                raise EOFError("read_bytes_raw: truncated long-form header")
            length = (self._buf[self._off] |
                      (self._buf[self._off + 1] << 8) |
                      (self._buf[self._off + 2] << 16))
            self._off += 3
            header_size = 4
        else:
            raise ValueError(f"read_bytes_raw: invalid length byte 0xff at offset {self._off - 1}")

        if self._off + length > len(self._buf):
            raise EOFError(
                f"read_bytes_raw: body truncated (need {length}, "
                f"have {len(self._buf) - self._off}) at offset {self._off}"
            )

        value = self._buf[self._off : self._off + length]
        self._off += length
        # pad to next 4-byte boundary
        pad = (4 - ((header_size + length) % 4)) % 4
        self._off += pad
        return value

    def read_str(self):
        """Read a TL-encoded UTF-8 string."""
        return self.read_bytes_raw().decode("utf-8", errors="replace")

    # ---- Sub-object skip helpers ----
    _PEER_CHANNEL_64_ALT = 0xa2a5371e
    def skip_peer(self):
        """
        Skip a Peer object (constructor + one int32).
        peerUser#9db1bc6d user_id:int
        peerChat#bad0e5bb chat_id:int
        peerChannel#bddde532 channel_id:int
        """

        cid = self.read_u32()
        if cid in (self._PEER_USER_32, self._PEER_CHAT_32, self._PEER_CHANNEL_32):
            self.read_i32()
        elif cid in (self._PEER_USER_64, self._PEER_CHAT_64, self._PEER_CHANNEL_64, self._PEER_CHANNEL_64_ALT):
            self.read_i64()
        else:
            raise ValueError(f"skip_peer: unknown constructor 0x{cid:08x} at offset {self._off - 4}")

    def read_peer(self):
        """Read a Peer object and return (type_str, id_int)."""
        cid = self.read_u32()
        if cid == self._PEER_USER_32:
            return ("user", self.read_i32())
        elif cid == self._PEER_CHAT_32:
            return ("chat", self.read_i32())
        elif cid == self._PEER_CHANNEL_32:
            return ("channel", self.read_i32())
        elif cid == self._PEER_USER_64:
            return ("user", self.read_i64())
        elif cid == self._PEER_CHAT_64:
            return ("chat", self.read_i64())
        elif cid == self._PEER_CHANNEL_64:
            return ("channel", self.read_i64())
        elif cid == self._PEER_CHANNEL_64_ALT:
            return ("channel", self.read_i64())
        else:
            raise ValueError(f"read_peer: unknown constructor 0x{cid:08x} at offset {self._off - 4}")

    def skip_vector(self, element_fn):
        """
        Skip a boxed TL vector (constructor 0x1cb5c415 + count + N elements).
        element_fn is called once per element with no arguments; it should
        advance self._off past the element.
        """
        cid = self.read_u32()
        if cid != self._VECTOR:
            raise ValueError(
                f"skip_vector: expected 0x1cb5c415, got 0x{cid:08x} at offset {self._off - 4}"
            )
        count = self.read_i32()
        if count < 0 or count > 100_000:
            raise ValueError(f"skip_vector: implausible count {count}")
        for _ in range(count):
            element_fn()

    def skip_geopoint(self):
        """
        Skip a GeoPoint object.
        geoPointEmpty#1117dd5f
        geoPoint#b2a2f663 flags:# lon:double lat:double access_hash:long accuracy_radius:flags.0?int
        """
        cid = self.read_u32()
        if cid == 0x1117dd5f:
            pass
        elif cid == 0xb2a2f663:
            flags = self.read_u32()
            self.read_double()  # lon
            self.read_double()  # lat
            self.read_u64()     # access_hash
            if flags & (1 << 0):
                self.read_i32()  # accuracy_radius
        else:
            raise ValueError(f"skip_geopoint: unknown constructor 0x{cid:08x}")

    def skip_photo_size(self):
        """
        Skip a PhotoSize variant.
        photoSizeEmpty#0e17e23c type:string
        photoSize#75c78e60 type:string w:int h:int size:int
        photoCachedSize#021e1ad6 type:string w:int h:int bytes:bytes
        photoStrippedSize#e0b0bc2e type:string bytes:bytes
        photoSizeProgressive#fa3efb95 type:string w:int h:int sizes:Vector<int>
        photoPathSize#d8214d41 type:string bytes:bytes
        """
        cid = self.read_u32()
        if cid == 0x0e17e23c:
            self.read_str()
        elif cid == 0x75c78e60:
            self.read_str()
            self.read_i32()
            self.read_i32()
            self.read_i32()
        elif cid == 0x021e1ad6:
            self.read_str()
            self.read_i32()
            self.read_i32()
            self.read_bytes_raw()
        elif cid == 0xe0b0bc2e:
            self.read_str()
            self.read_bytes_raw()
        elif cid == 0xfa3efb95:
            self.read_str()
            self.read_i32()
            self.read_i32()

            # Newer blobs may store this as boxed Vector<int>.
            # Older/local blobs may store only count + ints.
            if self.remaining() >= 4 and self.peek_u32() == self._VECTOR:
                self.read_u32()
                count = self.read_i32()
            else:
                count = self.read_i32()

            if count < 0 or count > 100_000:
                raise ValueError(f"skip_photo_size: implausible progressive size count {count}")

            self._off += 4 * count
        elif cid == 0xd8214d41:
            self.read_str()
            self.read_bytes_raw()
        else:
            raise ValueError(f"skip_photo_size: unknown constructor 0x{cid:08x}")

    def skip_video_size(self):
        """
        Skip a VideoSize variant.
        videoSize#de33b094 flags:# type:string w:int h:int size:int video_start_ts:flags.0?double
        videoSizeEmojiMarkup#f85c413c emoji_id:long background_colors:%Vector<int>
        videoSizeStickerMarkup#0da082fe emoji_stickerset:InputStickerSet sticker_id:long background_colors:%Vector<int>
        """
        cid = self.read_u32()
        if cid == 0xde33b094:
            flags = self.read_u32()
            self.read_str(); self.read_i32(); self.read_i32(); self.read_i32()
            if flags & (1 << 0):
                self.read_double()
        elif cid == 0xf85c413c:
            self.read_u64()
            count = self.read_i32()
            self._off += 4 * count
        elif cid == 0x0da082fe:
            self._skip_input_sticker_set()
            self.read_u64()
            count = self.read_i32()
            self._off += 4 * count
        else:
            raise ValueError(f"skip_video_size: unknown constructor 0x{cid:08x}")

    def _skip_input_sticker_set(self):
        """
        Skip an InputStickerSet variant (internal helper used by skip_video_size).
        inputStickerSetEmpty#ffb62b95
        inputStickerSetID#9de7a269 id:long access_hash:long
        inputStickerSetShortName#861cc8a0 short_name:string
        inputStickerSetDice#e67f520e emoticon:string
        inputStickerSetAnimatedEmoji#028703c8
        inputStickerSetAnimatedEmojiAnimations#0cde3739
        inputStickerSetPremiumGifts#c88b3b02
        inputStickerSetEmojiGenericAnimations#04c4d4ce
        inputStickerSetEmojiDefaultTopicIcons#44c1f8d9
        inputStickerSetEmojiDefaultStatuses#49748553
        inputStickerSetEmojiChannelDefaultStatuses#37c66648
        """
        _no_fields = {0xffb62b95, 0x028703c8, 0x0cde3739, 0xc88b3b02,
                      0x04c4d4ce, 0x44c1f8d9, 0x49748553, 0x37c66648}
        cid = self.read_u32()
        if cid in _no_fields:
            pass
        elif cid == 0x9de7a269:
            self.read_u64(); self.read_u64()
        elif cid == 0x861cc8a0:
            self.read_str()
        elif cid == 0xe67f520e:
            self.read_str()
        else:
            raise ValueError(f"_skip_input_sticker_set: unknown constructor 0x{cid:08x}")

    def skip_photo(self):
        """
        Skip a Photo object.
        photoEmpty#2331b22d id:long
        photo#fb197a65 flags:# id:long access_hash:long file_reference:bytes date:int
          sizes:Vector<PhotoSize> video_sizes:flags.0?Vector<VideoSize> dc_id:int
        """
        cid = self.read_u32()
        if cid == 0x2331b22d:
            self.read_u64()
        elif cid == 0xfb197a65:
            flags = self.read_u32()
            self.read_u64(); self.read_u64(); self.read_bytes_raw(); self.read_i32()
            self.skip_vector(self.skip_photo_size)
            if flags & (1 << 0):
                self.skip_vector(self.skip_video_size)
            self.read_i32()
        else:
            raise ValueError(f"skip_photo: unknown constructor 0x{cid:08x}")

    def skip_document_attribute(self):
        """
        Skip a DocumentAttribute variant.
        documentAttributeImageSize#6c37c15c w:int h:int
        documentAttributeAnimated#11b58939
        documentAttributeHasStickers#9801d2f7
        documentAttributeSticker#6319d612 flags:# alt:string stickerset:InputStickerSet mask_coords:flags.0?MaskCoords
        documentAttributeVideo#d38ff940 flags:# duration:double w:int h:int preload_prefix_size:flags.2?int video_start_ts:flags.4?double
        documentAttributeAudio#9852f9c6 flags:# duration:int title:flags.0?string performer:flags.1?string waveform:flags.2?bytes
        documentAttributeFilename#15590068 file_name:string
        documentAttributeCustomEmoji#fd149899 flags:# alt:string stickerset:InputStickerSet
        """
        cid = self.read_u32()
        if cid == 0x6c37c15c:
            self.read_i32(); self.read_i32()
        elif cid in (0x11b58939, 0x9801d2f7):
            pass
        elif cid == 0x6319d612:
            flags = self.read_u32()
            self.read_str()
            self._skip_input_sticker_set()
            if flags & (1 << 0):
                # MaskCoords: n:int x:double y:double zoom:double
                self.read_i32(); self.read_double(); self.read_double(); self.read_double()
        elif cid == 0xd38ff940:
            flags = self.read_u32()
            self.read_double(); self.read_i32(); self.read_i32()
            if flags & (1 << 2):
                self.read_i32()
            if flags & (1 << 4):
                self.read_double()
        elif cid == 0x9852f9c6:
            flags = self.read_u32()
            self.read_i32()
            if flags & (1 << 0): self.read_str()
            if flags & (1 << 1): self.read_str()
            if flags & (1 << 2): self.read_bytes_raw()
        elif cid == 0x15590068:
            self.read_str()
        elif cid == 0xfd149899:
            self.read_u32()
            self.read_str()
            self._skip_input_sticker_set()
        else:
            raise ValueError(f"skip_document_attribute: unknown constructor 0x{cid:08x}")

    def skip_document(self):
        """
        Skip a Document object.
        documentEmpty#36f8c871 id:long
        document#8fd4c4d8 flags:# id:long access_hash:long file_reference:bytes date:int
          mime_type:string size:long thumbs:flags.0?Vector<PhotoSize>
          video_thumbs:flags.1?Vector<VideoSize> dc_id:int
          attributes:Vector<DocumentAttribute>
        """
        cid = self.read_u32()
        if cid == 0x36f8c871:
            self.read_u64()
        elif cid == 0x8fd4c4d8:
            flags = self.read_u32()
            self.read_u64(); self.read_u64(); self.read_bytes_raw(); self.read_i32()
            self.read_str(); self.read_i64()
            if flags & (1 << 0): self.skip_vector(self.skip_photo_size)
            if flags & (1 << 1): self.skip_vector(self.skip_video_size)
            self.read_i32()
            self.skip_vector(self.skip_document_attribute)
        else:
            raise ValueError(f"skip_document: unknown constructor 0x{cid:08x}")

    def read_photo_summary(self):
        """
        Read just enough of a Photo object to identify it in reports.

        This is used for the ALEAPP media report, where we want a media type and
        stable Telegram object ID without decoding every thumbnail in detail.
        """
        cid = self.read_u32()
        if cid == 0x2331b22d:
            photo_id = self.read_u64()
            return {"media_kind": "photo", "media_id": str(photo_id), "media_mime_type": ""}
        elif cid == 0xfb197a65:
            flags = self.read_u32()
            photo_id = self.read_u64()
            self.read_u64()
            self.read_bytes_raw()
            self.read_i32()
            self.skip_vector(self.skip_photo_size)
            if flags & (1 << 0):
                self.skip_vector(self.skip_video_size)
            self.read_i32()
            return {"media_kind": "photo", "media_id": str(photo_id), "media_mime_type": ""}
        else:
            raise ValueError(f"read_photo_summary: unknown constructor 0x{cid:08x}")

    def read_document_summary(self):
        """
        Read just enough of a Document object to identify the Telegram document
        ID and MIME type for ALEAPP output.
        """
        cid = self.read_u32()
        if cid == 0x36f8c871:
            document_id = self.read_u64()
            return {"media_kind": "document", "media_id": str(document_id), "media_mime_type": ""}
        elif cid == 0x8fd4c4d8:
            flags = self.read_u32()
            document_id = self.read_u64()
            self.read_u64()
            self.read_bytes_raw()
            self.read_i32()
            mime_type = self.read_str()
            self.read_i64()
            if flags & (1 << 0):
                self.skip_vector(self.skip_photo_size)
            if flags & (1 << 1):
                self.skip_vector(self.skip_video_size)
            self.read_i32()
            self.skip_vector(self.skip_document_attribute)
            return {"media_kind": "document", "media_id": str(document_id), "media_mime_type": mime_type}
        else:
            raise ValueError(f"read_document_summary: unknown constructor 0x{cid:08x}")

    def read_message_media_summary(self):
        """
        Read the top-level MessageMedia field and return a compact summary for
        ALEAPP reports.

        This does not try to map Telegram media objects to local cache files.
        It only extracts the media type and, where available, the Telegram
        object ID/MIME metadata that can safely be shown next to the message row.
        """
        cid = self.read_u32()
        if cid == 0x3ded6320:
            return {"media_kind": "empty", "media_id": "", "media_mime_type": ""}
        elif cid == 0x9f84f49e:
            return {"media_kind": "unsupported", "media_id": "", "media_mime_type": ""}
        elif cid == 0x695150d7:
            flags = self.read_u32()
            summary = {"media_kind": "photo", "media_id": "", "media_mime_type": ""}
            if flags & (1 << 0):
                summary = self.read_photo_summary()
            if flags & (1 << 2):
                self.read_i32()
            return summary
        elif cid == 0x4cf4d72d:
            flags = self.read_u32()
            summary = {"media_kind": "document", "media_id": "", "media_mime_type": ""}
            if flags & (1 << 1):
                summary = self.read_document_summary()
            if flags & (1 << 7):
                self.skip_vector(self.skip_document)
            if flags & (1 << 2):
                self.read_i32()
            return summary
        elif cid == 0x56e0d474:
            self.skip_geopoint()
            return {"media_kind": "geo", "media_id": "", "media_mime_type": ""}
        elif cid == 0x70322949:
            self.read_str(); self.read_str(); self.read_str(); self.read_str(); self.read_i64()
            return {"media_kind": "contact", "media_id": "", "media_mime_type": ""}
        elif cid == 0xa32dd600:
            self.read_u32()
            self._skip_webpage()
            return {"media_kind": "webpage", "media_id": "", "media_mime_type": ""}
        elif cid == 0x2ec0533f:
            self.skip_geopoint()
            self.read_str(); self.read_str(); self.read_str(); self.read_str(); self.read_str()
            return {"media_kind": "venue", "media_id": "", "media_mime_type": ""}
        elif cid == 0xfdb19008:
            gcid = self.read_u32()
            if gcid != 0xbdf9653b:
                raise ValueError(f"read_message_media_summary(game): unknown Game 0x{gcid:08x}")
            gflags = self.read_u32()
            game_id = self.read_u64()
            self.read_u64()
            self.read_str(); self.read_str(); self.read_str()
            self.skip_photo()
            if gflags & (1 << 0):
                self.skip_document()
            return {"media_kind": "game", "media_id": str(game_id), "media_mime_type": ""}
        elif cid == 0xb940c666:
            flags = self.read_u32()
            self.skip_geopoint()
            if flags & (1 << 0):
                self.read_i32()
            self.read_i32()
            if flags & (1 << 1):
                self.read_i32()
            return {"media_kind": "geo_live", "media_id": "", "media_mime_type": ""}
        elif cid == 0x3f7ee58b:
            self.read_str()
            self.read_i32()
            return {"media_kind": "dice", "media_id": "", "media_mime_type": ""}
        elif cid == 0x68cb6283:
            flags = self.read_u32()
            peer_type, peer_id = self.read_peer()
            story_id = self.read_i32()
            if flags & (1 << 1):
                raise NotImplementedError("read_message_media_summary: storyItem inside messageMediaStory not implemented")
            return {"media_kind": "story", "media_id": f"{peer_type}:{peer_id}:{story_id}", "media_mime_type": ""}
        else:
            raise ValueError(f"read_message_media_summary: unknown constructor 0x{cid:08x}")

    def skip_message_entity(self):
        """
        Skip a MessageEntity variant.
        Basic entities (offset:int length:int only): Unknown, Mention, Hashtag, BotCommand,
        Url, Email, Bold, Italic, Code, Phone, Cashtag, Underline, Strike, Spoiler, BankCard.
        Extended entities add extra fields after offset+length.
        messageEntityPre#73924be0       offset length language:string
        messageEntityTextUrl#76a6d327   offset length url:string
        messageEntityMentionName#dc7b1140 offset length user_id:long
        messageEntityCustomEmoji#c8cf05f8 offset length document_id:long
        messageEntityBlockquote#f1ccaaac flags:# offset length  (flags come first!)
        """
        _basic = {
            0xbb92ba95, 0xfa04579d, 0x6f635b0d, 0x6cef8ac7, 0x6ed02538,
            0x64e475c2, 0xbd610bc9, 0x826f8b60, 0x28a20571, 0x9b69e34b,
            0x4c4e743f, 0x9c4e7e8b, 0xbf0693d4, 0x32ca960f, 0x761e6af4,
        }
        cid = self.read_u32()
        if cid in _basic:
            self.read_i32(); self.read_i32()
        elif cid == 0x73924be0:
            self.read_i32(); self.read_i32(); self.read_str()
        elif cid == 0x76a6d327:
            self.read_i32(); self.read_i32(); self.read_str()
        elif cid == 0xdc7b1140:
            self.read_i32(); self.read_i32(); self.read_i64()
        elif cid == 0xc8cf05f8:
            self.read_i32(); self.read_i32(); self.read_u64()
        elif cid == 0xf1ccaaac:
            # messageEntityBlockquote: flags first, then offset, then length
            self.read_u32(); self.read_i32(); self.read_i32()
        else:
            raise ValueError(f"skip_message_entity: unknown constructor 0x{cid:08x}")

    def skip_reaction(self):
        """
        Skip a Reaction object.
        reactionEmpty#79f5d419
        reactionPaid#aa123dc4
        reactionEmoji#1b2286be emoticon:string
        reactionCustomEmoji#8935fc73 document_id:long
        """
        cid = self.read_u32()
        if cid in (0x79f5d419, 0xaa123dc4):
            pass
        elif cid == 0x1b2286be:
            self.read_str()
        elif cid == 0x8935fc73:
            self.read_u64()
        else:
            raise ValueError(f"skip_reaction: unknown constructor 0x{cid:08x}")

    def skip_reaction_count(self):
        """
        Skip a ReactionCount object.
        reactionCount#a6d984db flags:# chosen_order:flags.0?int reaction:Reaction count:int
        """
        cid = self.read_u32()
        if cid != 0xa6d984db:
            raise ValueError(f"skip_reaction_count: unknown constructor 0x{cid:08x}")
        flags = self.read_u32()
        if flags & (1 << 0):
            self.read_i32()
        self.skip_reaction()
        self.read_i32()

    def skip_message_peer_reaction(self):
        """
        Skip a MessagePeerReaction object.
        messagePeerReaction#8a20b329 flags:# peer_id:Peer date:int reaction:Reaction
        """
        cid = self.read_u32()
        if cid != 0x8a20b329:
            raise ValueError(f"skip_message_peer_reaction: unknown constructor 0x{cid:08x}")
        self.read_u32()   # flags (big:0, unread:1, my:2)
        self.skip_peer()
        self.read_i32()   # date
        self.skip_reaction()

    def skip_message_reactor(self):
        """
        Skip a MessageReactor object.
        messageReactor#b156fe9c flags:# peer_id:flags.3?Peer count:int
        """
        cid = self.read_u32()
        if cid != 0xb156fe9c:
            raise ValueError(f"skip_message_reactor: unknown constructor 0x{cid:08x}")
        flags = self.read_u32()
        if flags & (1 << 3):
            self.skip_peer()
        self.read_i32()

    def skip_text_with_entities(self):
        """
        Skip a TextWithEntities object.
        textWithEntities#8d5b74a8 text:string entities:Vector<MessageEntity>
        """
        cid = self.read_u32()
        if cid != 0x8d5b74a8:
            raise ValueError(f"skip_text_with_entities: unknown constructor 0x{cid:08x}")
        self.read_str()
        self.skip_vector(self.skip_message_entity)

    def skip_message_fwd_header(self):
        """
        Skip a MessageFwdHeader object.
        messageFwdHeader#4e4df4bb flags:#
          from_id:flags.0?Peer  from_name:flags.5?string  date:int
          channel_post:flags.2?int  post_author:flags.3?string
          saved_from_peer:flags.4?Peer  saved_from_msg_id:flags.4?int
          saved_from_id:flags.8?Peer  saved_from_name:flags.9?string
          saved_date:flags.10?int  psa_type:flags.6?string
        """
        cid = self.read_u32()
        if cid != 0x4e4df4bb:
            raise ValueError(f"skip_message_fwd_header: unknown constructor 0x{cid:08x}")
        flags = self.read_u32()
        if flags & (1 << 0):  self.skip_peer()
        if flags & (1 << 5):  self.read_str()
        self.read_i32()                          # date (always)
        if flags & (1 << 2):  self.read_i32()
        if flags & (1 << 3):  self.read_str()
        if flags & (1 << 4):  self.skip_peer(); self.read_i32()
        if flags & (1 << 8):  self.skip_peer()
        if flags & (1 << 9):  self.read_str()
        if flags & (1 << 10): self.read_i32()
        if flags & (1 << 6):  self.read_str()

    def _skip_webpage(self):
        """
        Skip a WebPage object (internal helper).
        webPageEmpty#eb1477e8 flags:# id:long url:flags.0?string
        webPagePending#c586da1c flags:# id:long url:flags.0?string date:int
        webPageNotModified#7311ca11 flags:# cached_page_views:flags.0?int
        webPage#e89c45b2 — complex full webpage (raises NotImplementedError)
        """
        cid = self.read_u32()
        if cid == 0xeb1477e8:
            flags = self.read_u32(); self.read_u64()
            if flags & (1 << 0): self.read_str()
        elif cid == 0xc586da1c:
            flags = self.read_u32(); self.read_u64()
            if flags & (1 << 0): self.read_str()
            self.read_i32()
        elif cid == 0x7311ca11:
            flags = self.read_u32()
            if flags & (1 << 0): self.read_i32()
        elif cid == 0xe89c45b2:
            raise NotImplementedError("_skip_webpage: full webPage#e89c45b2 not implemented")
        else:
            raise ValueError(f"_skip_webpage: unknown constructor 0x{cid:08x}")

    def skip_message_media(self):
        """
        Skip a MessageMedia object.
        Handles common variants found in Telegram for Android cache blobs.
        Raises NotImplementedError for rare/complex variants (Poll, Invoice, Giveaway, etc.)
        so the caller can record the failure and continue gracefully.
        """
        cid = self.read_u32()
        if cid == 0x3ded6320:
            # messageMediaEmpty — no fields
            pass
        elif cid == 0x9f84f49e:
            # messageMediaUnsupported — no fields
            pass
        elif cid == 0x695150d7:
            # messageMediaPhoto flags:# spoiler:flags.3?true photo:flags.0?Photo ttl_seconds:flags.2?int
            flags = self.read_u32()
            if flags & (1 << 0): self.skip_photo()
            if flags & (1 << 2): self.read_i32()
        elif cid == 0x56e0d474:
            # messageMediaGeo geo:GeoPoint
            self.skip_geopoint()
        elif cid == 0x70322949:
            # messageMediaContact phone_number first_name last_name vcard user_id:long
            self.read_str(); self.read_str(); self.read_str(); self.read_str(); self.read_i64()
        elif cid == 0x4cf4d72d:
            # messageMediaDocument flags:# document:flags.1?Document alt_documents:flags.7?Vector<Document> ttl_seconds:flags.2?int
            flags = self.read_u32()
            if flags & (1 << 1): self.skip_document()
            if flags & (1 << 7): self.skip_vector(self.skip_document)
            if flags & (1 << 2): self.read_i32()
        elif cid == 0xa32dd600:
            # messageMediaWebPage flags:# webpage:WebPage
            self.read_u32()
            self._skip_webpage()
        elif cid == 0x2ec0533f:
            # messageMediaVenue geo title address provider venue_id venue_type
            self.skip_geopoint()
            self.read_str(); self.read_str(); self.read_str(); self.read_str(); self.read_str()
        elif cid == 0xfdb19008:
            # messageMediaGame game:Game
            # game#bdf9653b flags:# id:long access_hash:long short_name title description photo document:flags.0?Document
            gcid = self.read_u32()
            if gcid != 0xbdf9653b:
                raise ValueError(f"skip_message_media(game): unknown Game 0x{gcid:08x}")
            gflags = self.read_u32()
            self.read_u64(); self.read_u64()
            self.read_str(); self.read_str(); self.read_str()
            self.skip_photo()
            if gflags & (1 << 0): self.skip_document()
        elif cid == 0xb940c666:
            # messageMediaGeoLive flags:# geo heading:flags.0?int period proximity_notification_radius:flags.1?int
            flags = self.read_u32()
            self.skip_geopoint()
            if flags & (1 << 0): self.read_i32()
            self.read_i32()
            if flags & (1 << 1): self.read_i32()
        elif cid == 0x3f7ee58b:
            # messageMediaDice emoticon:string value:int
            self.read_str(); self.read_i32()
        elif cid == 0x68cb6283:
            # messageMediaStory flags:# peer:Peer id:int story:flags.1?StoryItem
            flags = self.read_u32()
            self.skip_peer(); self.read_i32()
            if flags & (1 << 1):
                # storyItem is complex; raise to record the failure
                raise NotImplementedError("skip_message_media: storyItem inside messageMediaStory not implemented")
        elif cid in (0x4bd6e798, 0xf6a548d3, 0xdaad85b0, 0xc6991068, 0xa8852491):
            # messageMediaPoll / messageMediaInvoice / messageMediaGiveaway /
            # messageMediaGiveawayResults / messageMediaPaidMedia — rare and complex
            raise NotImplementedError(f"skip_message_media: complex variant 0x{cid:08x} not implemented")
        else:
            raise ValueError(f"skip_message_media: unknown constructor 0x{cid:08x}")

    def skip_message_reply_header(self):
        """
        Skip a MessageReplyHeader or MessageReplyStoryHeader object.
        messageReplyHeader#afbc09db flags:#
        messageReplyHeader#6917560b flags:#
        messageReplyStoryHeader#16f1c8b4 peer:Peer story_id:int
        """
        cid = self.read_u32()
        if cid in (0xafbc09db, 0x6917560b):
            flags = self.read_u32()
            if flags & (1 << 4):
                self.read_i32()
            if flags & (1 << 0):
                self.skip_peer()
            if flags & (1 << 5):
                self.skip_message_fwd_header()
            if flags & (1 << 8):
                self.skip_message_media()
            if flags & (1 << 1):
                self.read_i32()
            if flags & (1 << 6):
                self.read_str()
            if flags & (1 << 7):
                self.skip_vector(self.skip_message_entity)
            if flags & (1 << 10):
                self.read_i32()
        elif cid == 0x16f1c8b4:
            self.skip_peer()
            self.read_i32()
        else:
            raise ValueError(f"skip_message_reply_header: unknown constructor 0x{cid:08x}")

    def skip_message_replies(self):
        """
        Skip a MessageReplies object.
        messageReplies#83d60fc2 flags:#
          replies:int  replies_pts:int
          recent_repliers:flags.1?Vector<Peer>  channel_id:flags.0?long
          max_id:flags.2?int  read_max_id:flags.2?int
        """
        cid = self.read_u32()
        if cid != 0x83d60fc2:
            raise ValueError(f"skip_message_replies: unknown constructor 0x{cid:08x}")
        flags = self.read_u32()
        self.read_i32(); self.read_i32()
        if flags & (1 << 1): self.skip_vector(self.skip_peer)
        if flags & (1 << 0): self.read_i64()
        if flags & (1 << 2): self.read_i32(); self.read_i32()

    def skip_message_reactions(self):
        """
        Skip a MessageReactions object.
        messageReactions#4f2b9479 flags:#
          results:Vector<ReactionCount>
          recent_reactions:flags.1?Vector<MessagePeerReaction>
          top_reactors:flags.4?Vector<MessageReactor>
        """
        cid = self.read_u32()
        if cid != 0x4f2b9479:
            raise ValueError(f"skip_message_reactions: unknown constructor 0x{cid:08x}")
        flags = self.read_u32()
        self.skip_vector(self.skip_reaction_count)
        if flags & (1 << 1): self.skip_vector(self.skip_message_peer_reaction)
        if flags & (1 << 4): self.skip_vector(self.skip_message_reactor)

    def skip_restriction_reason(self):
        """
        Skip a RestrictionReason object.
        restrictionReason#d072acb4 platform:string reason:string text:string
        """
        cid = self.read_u32()
        if cid != 0xd072acb4:
            raise ValueError(f"skip_restriction_reason: unknown constructor 0x{cid:08x}")
        self.read_str(); self.read_str(); self.read_str()

    def skip_fact_check(self):
        """
        Skip a FactCheck object.
        factCheck#b5be5b08 flags:# country:string text:flags.1?TextWithEntities hash:long
        """
        cid = self.read_u32()
        if cid != 0xb5be5b08:
            raise ValueError(f"skip_fact_check: unknown constructor 0x{cid:08x}")
        flags = self.read_u32()
        self.read_str()
        if flags & (1 << 1): self.skip_text_with_entities()
        self.read_i64()

    def decode_message(self, constructor):
        """
        Decode standard Telegram message TL objects.

        Supported constructors:
          message#76bec211 - older/current-ish Android cache message layout with flags only
          message#9815cec8 - newer layout with flags and flags2

        The main compatibility difference is:
          0x76bec211: flags, id, ...
          0x9815cec8: flags, flags2, id, ...

        This method decodes the fields needed for ALEAPP output:
        message id, from peer, peer id, date, text, and compact media summary.
        """

        flags = self.read_u32()
        flags2 = 0

        if constructor == 0x9815cec8:
            flags2 = self.read_u32()
        elif constructor != 0x76bec211:
            raise ValueError(f"decode_message: unsupported constructor 0x{constructor:08x}")

        msg_id = self.read_i32()

        from_peer = None
        if flags & (1 << 8):
            from_peer = self.read_peer()

        # message#9815cec8 adds this before peer_id.
        if constructor == 0x9815cec8 and flags & (1 << 29):
            self.read_i32()  # from_boosts_applied

        peer_id = self.read_peer()

        # message#9815cec8 adds saved_peer_id before fwd_from.
        if constructor == 0x9815cec8 and flags & (1 << 28):
            self.read_peer()

        if flags & (1 << 2):
            self.skip_message_fwd_header()

        if flags & (1 << 11):
            if constructor == 0x9815cec8:
                self.read_i64()  # via_bot_id:long
            else:
                self.read_i32()  # via_bot_id:int

        # message#9815cec8 adds via_business_bot_id:flags2.0?long.
        if constructor == 0x9815cec8 and flags2 & (1 << 0):
            self.read_i64()

        if flags & (1 << 3):
            self.skip_message_reply_header()

        date = self.read_i32()
        message = self.read_str()

        media_summary = {
            "media_kind": "",
            "media_id": "",
            "media_mime_type": "",
            "media_parse_note": "",
        }

        if flags & (1 << 9):
            try:
                media_summary = self.read_message_media_summary()
                media_summary.setdefault("media_parse_note", "")
            except Exception as e:
                media_summary = {
                    "media_kind": "unparsed_media",
                    "media_id": "",
                    "media_mime_type": "",
                    "media_parse_note": f"media summary skipped: {e!r}",
                }

        return {
            "msg_id": msg_id,
            "from_peer": from_peer,
            "peer_id": peer_id,
            "date": date,
            "message": message,
            "flags": flags,
            "flags2": flags2,
            "media_kind": media_summary["media_kind"],
            "media_id": media_summary["media_id"],
            "media_mime_type": media_summary["media_mime_type"],
            "media_parse_note": media_summary["media_parse_note"],
        }


def parse_cache4db(cache4db_path, is_channel=None):
    """
    Parse Telegram's cache4.db messages_v2 table into plain Python rows for
    ALEAPP reporting.

    This function is intentionally database-focused: it handles table lookups,
    name resolution, and row shaping, while TLReader handles the BLOB decoding.
    """
    results = []

    def table_exists(conn, name):
        """Return True when the target SQLite table exists."""
        cur = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
            (name,)
        )
        return cur.fetchone() is not None

    def table_columns(conn, name):
        """Return the set of column names for a SQLite table."""
        try:
            cur = conn.execute(f"PRAGMA table_info({name})")
            return {row[1] for row in cur.fetchall()}
        except Exception:
            return set()

    def preferred_column(columns, *candidates):
        """Pick the first candidate column name that actually exists."""
        for candidate in candidates:
            if candidate in columns:
                return candidate
        return None

    def parse_message_blob(blob):
        """Decode the main Telegram message blob stored in messages_v2.data."""
        parsed = {
            "constructor": None,
            "text": "",
            "strings": [],
            "parse_note": "",
            "media_kind": "",
            "media_id": "",
            "media_mime_type": "",
            "media_parse_note": "",
        }

        if not blob or len(blob) < 4:
            parsed["parse_note"] = "empty or too short"
            return parsed

        try:
            reader = TLReader(blob)
            constructor = reader.read_u32()
            parsed["constructor"] = hex(constructor)

            match constructor:
                case 0x76bec211 | 0x9815cec8:
                    # Standard Telegram message constructors.
                    # 0x76bec211 uses one flags field.
                    # 0x9815cec8 adds flags2 immediately after flags.
                    try:
                        fields = reader.decode_message(constructor)
                        parsed["text"] = fields["message"]
                        parsed["media_kind"] = fields.get("media_kind", "")
                        parsed["media_id"] = fields.get("media_id", "")
                        parsed["media_mime_type"] = fields.get("media_mime_type", "")
                        parsed["media_parse_note"] = fields.get("media_parse_note", "")
                        parsed["parse_note"] = f"decoded message#{constructor:08x} (id={fields['msg_id']})"
                        if parsed["media_parse_note"]:
                            parsed["parse_note"] += f"; {parsed['media_parse_note']}"
                    except Exception as e:
                        parsed["parse_note"] = f"0x{constructor:08x} decode failed at offset {reader.offset}: {e!r}"

                case 0x2b085862 | 0xeabcdd4d:
                    # Treat these as service/non-standard message records.
                    # Do not force message text from printable runs.
                    parsed["service_type"] = "message_service_or_non_text"
                    parsed["parse_note"] = f"service/non-text constructor 0x{constructor:08x}"

                    try:
                        flags = reader.read_u32()
                    except Exception:
                        pass

                case _:
                    parsed["parse_note"] = "unsupported constructor"

            return parsed

        except Exception as e:
            parsed["parse_note"] = f"blob parse failed: {e!r}"
            return parsed

    def build_name_map(conn, table_name):
        """Create a simple ID -> display name lookup for Telegram users/chats tables."""
        columns = table_columns(conn, table_name)
        if not columns:
            return {}

        id_col = preferred_column(columns, "uid", "id")
        name_col = preferred_column(columns, "name", "title", "first_name", "username")
        if not id_col or not name_col:
            return {}

        out = {}
        try:
            cur = conn.execute(f"SELECT {id_col}, {name_col} FROM {table_name}")
            for row in cur:
                display_name, username = split_telegram_name(row[1] or "")
                out[row[0]] = display_name or username or ""
        except Exception:
            pass
        return out

    def resolve_peer(uid, user_map, chat_map, is_channel=0):
        """Resolve a Telegram uid to the best display name/type we currently know."""
        if uid in user_map:
            return user_map[uid], "user"
        if uid in chat_map:
            return chat_map[uid], "channel" if is_channel else "chat"
        if isinstance(uid, int) and uid < 0:
            return "", "channel" if is_channel else "chat_or_group"
        return "", "user_or_unknown"

    def clean_extracted_message(text):
        """
        Remove common junk prefixes and obvious non-message values from
        extracted Telegram message text.
        """
        if not text:
            return ""

        text = text.strip().replace("\x00", "")

        # Strip common 2-character junk prefixes seen in cache4.db output
        if len(text) >= 3 and text[0] == "e" and not text[1].isalnum():
            text = text[2:].lstrip()
        elif len(text) >= 3 and text[0] == "e" and text[1].isalnum() and text[2].isalpha():
            text = text[1:].lstrip()

        return text.strip()

    conn = sqlite3.connect(cache4db_path)
    conn.row_factory = sqlite3.Row

    try:
        if not table_exists(conn, "messages_v2"):
            return results

        user_map = build_name_map(conn, "users")
        chat_map = build_name_map(conn, "chats")
        message_columns = table_columns(conn, "messages_v2")

        wanted_columns = (
            "mid",
            "uid",
            "read_state",
            "send_state",
            "date",
            "data",
            "ttl",
            "media",
            "replydata",
            "imp",
            "mention",
            "forwards",
            "replies_data",
            "thread_reply_id",
            "is_channel",
            "reply_to_message_id",
            "custom_params",
            "group_id",
            "reply_to_story_id",
            "out"
        )

        selected_columns = [col for col in wanted_columns if col in message_columns]

        if not {"mid", "uid", "date", "data"}.issubset(selected_columns):
            return results

        query = f"SELECT {', '.join(selected_columns)} FROM messages_v2 ORDER BY date"
        cur = conn.execute(query)

        for row in cur:
            blob_info = parse_message_blob(row["data"])
            uid = row["uid"]
            is_channel = row["is_channel"] if "is_channel" in row.keys() else 0
            peer_name, peer_type = resolve_peer(uid, user_map, chat_map, is_channel)

            results.append({
                "mid": row["mid"],
                "uid": uid,
                "peer_name": peer_name,
                "peer_type": peer_type,
                "date_iso": unix_to_iso(row["date"]),
                "read_state": row["read_state"] if "read_state" in row.keys() else "",
                "send_state": row["send_state"] if "send_state" in row.keys() else "",
                "out": row["out"] if "out" in row.keys() else "",
                "ttl": row["ttl"] if "ttl" in row.keys() else "",
                "media": row["media"] if "media" in row.keys() else "",
                "imp": row["imp"] if "imp" in row.keys() else "",
                "mention": row["mention"] if "mention" in row.keys() else "",
                "forwards": row["forwards"] if "forwards" in row.keys() else "",
                "thread_reply_id": row["thread_reply_id"] if "thread_reply_id" in row.keys() else "",
                "is_channel": row["is_channel"] if "is_channel" in row.keys() else "",
                "reply_to_message_id": row["reply_to_message_id"] if "reply_to_message_id" in row.keys() else "",
                "group_id": row["group_id"] if "group_id" in row.keys() else "",
                "reply_to_story_id": row["reply_to_story_id"] if "reply_to_story_id" in row.keys() else "",
                "constructor": blob_info["constructor"],
                "message_text": blob_info["text"] or "",
                "message_media_kind": blob_info["media_kind"],
                "message_media_id": blob_info["media_id"],
                "message_media_mime_type": blob_info["media_mime_type"],
                "parse_note": blob_info["parse_note"],
                "visible_strings": " | ".join(blob_info["strings"]),
                                "has_media": 1 if (
                    blob_info.get("media_kind")
                    or ("media" in row.keys() and row["media"] not in ("", None, -1))
                ) else 0,
                "has_replydata": 1 if ("replydata" in row.keys() and row["replydata"]) else 0,
                "has_replies_data": 1 if ("replies_data" in row.keys() and row["replies_data"]) else 0,
                "has_custom_params": 1 if ("custom_params" in row.keys() and row["custom_params"]) else 0,
            })

    finally:
        conn.close()

    return results


def parse_shared_prefs_map(xml_path):
    """
    Read a Telegram shared_prefs XML file into a Python dict with simple type
    conversion for the primitive Android preference types.
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()
    values = {}

    for child in root:
        name = child.attrib.get("name")
        if not name:
            continue

        tag = child.tag.lower()
        value = child.attrib.get("value")
        text = (child.text or "").strip()

        if tag == "boolean":
            values[name] = str(value).lower() == "true"
        elif tag in ("int", "long"):
            try:
                values[name] = int(value)
            except (TypeError, ValueError):
                values[name] = value
        elif tag == "float":
            try:
                values[name] = float(value)
            except (TypeError, ValueError):
                values[name] = value
        elif tag == "string":
            values[name] = text
        elif tag == "set":
            values[name] = [item.text or "" for item in child.findall("string")]
        else:
            values[name] = value if value is not None else text

    return values


def split_telegram_name(raw_name):
    """
    Telegram stores many names in the local DB as:
        display_name;;;username
    so the trailing semicolons in old output were the raw field separator.
    """
    raw_name = (raw_name or "").strip()
    if ";;;" in raw_name:
        display_name, username = raw_name.split(";;;", 1)
        return display_name.strip(), username.strip()
    return raw_name, ""


def parse_telegram_user_blob(raw):
    """
    Parse a Telegram user TL object from either shared prefs or users.data.

    Supported user constructors:
    - user#215c4438
    - user#020b1422

    Both layouts have flags, flags2, user_id, and optional
    access_hash/name/username/phone fields near the beginning.
    """
    user_info = {
        "constructor": None,
        "user_id": "",
        "first_name": "",
        "last_name": "",
        "username": "",
        "phone": "",
        "display_name": "",
    }

    if not raw:
        return user_info

    f = io.BytesIO(raw)
    constructor = read_int32(f)
    user_info["constructor"] = constructor

    if constructor not in (0x215C4438, 0x020B1422):
        return user_info

    flags = read_int32(f)
    flags2 = read_int32(f)  # read to keep alignment with modern user constructors
    user_info["user_id"] = read_int64(f)

    # Fields must be read in the exact order Telegram writes them.
    # Refer to: https://core.telegram.org/constructor/user
    if flag_set(flags, 0):  # access_hash
        _ = read_int64(f)
    if flag_set(flags, 1):
        user_info["first_name"] = read_tl_string_from_file(f)
    if flag_set(flags, 2):
        user_info["last_name"] = read_tl_string_from_file(f)
    if flag_set(flags, 3):
        user_info["username"] = read_tl_string_from_file(f)
    if flag_set(flags, 4):
        user_info["phone"] = read_tl_string_from_file(f)

    user_info["display_name"] = " ".join(
        part for part in (user_info["first_name"], user_info["last_name"]) if part
    ).strip() or user_info["username"] or str(user_info["user_id"])

    return user_info


def find_telegram_userconfig_files(files_found, seeker=None):
    """Find Telegram userconfig XML files from direct artifact hits or extra seeker searches."""
    matches = []
    seen = set()

    for file_found in files_found:
        file_found = str(file_found)
        name = os.path.basename(file_found).lower()
        if "org.telegram.messenger" in file_found and (name == "userconfing.xml" or name.startswith("userconfig")):
            if file_found not in seen:
                seen.add(file_found)
                matches.append(file_found)

    if seeker:
        for pattern in (
            '*/org.telegram.messenger/shared_prefs/userconfing.xml',
            '*/org.telegram.messenger/shared_prefs/userconfig*.xml',
        ):
            for match in seeker.search(pattern):
                match = str(match)
                if match not in seen:
                    seen.add(match)
                    matches.append(match)

    def sort_key(path):
        name = os.path.basename(path).lower()
        if name == "userconfing.xml":
            return (0, name, path)
        return (1, name, path)

    return sorted(matches, key=sort_key)


def find_telegram_media_cache_files(seeker=None):
    """
    Locate Telegram media cache files from both app-private cache and the shared
    Android media cache area.
    """
    if not seeker:
        return []

    media_extensions = {
        ".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic", ".heif",
        ".mp4", ".mov", ".webm", ".mkv",
        ".mp3", ".m4a", ".aac", ".ogg", ".opus", ".wav",
        ".tgs",
    }

    matches = []
    seen = set()
    for pattern in (
        '*/org.telegram.messenger/cache/*',
        '*/Android/data/org.telegram.messenger/cache/*',
    ):
        for match in seeker.search(pattern):
            match = str(match)
            if not os.path.isfile(match):
                continue
            if os.path.basename(match).lower() in {"cache4.db", "cache4.db-shm", "cache4.db-wal", ".nomedia"}:
                continue
            if os.path.splitext(match)[1].lower() not in media_extensions:
                continue
            if match not in seen:
                seen.add(match)
                matches.append(match)
    return sorted(matches)


def classify_telegram_build(app_update_build):
    """Classify the current Telegram build as supported, untested, or unknown."""
    match app_update_build:
        case None:
            return ("unknown", "Telegram appUpdateBuild was not found in the dump.")
        case build if build in SUPPORTED_TELEGRAM_APP_UPDATE_BUILDS:
            return ("supported", SUPPORTED_TELEGRAM_APP_UPDATE_BUILDS[build])
        case _:
            return (
                "untested",
                "This build was not validated during development. The parser will still run, but review the output carefully.",
            )


def get_telegram_build_info(files_found, seeker=None):
    """
    Get Telegram build metadata from userconfig XML.

    appUpdateBuild is not the Play Store version name, but it is Telegram's own
    build identifier stored in the app's shared preferences and is stable enough
    to gate parser support.
    """
    fallback = None
    for config_path in find_telegram_userconfig_files(files_found, seeker):
        prefs = parse_shared_prefs_map(config_path)
        app_update_build = prefs.get("appUpdateBuild")
        if app_update_build not in (None, ""):
            support_status, support_note = classify_telegram_build(app_update_build)
            return {
                "app_update_build": app_update_build,
                "support_status": support_status,
                "support_note": support_note,
                "source_path": config_path,
            }

        if fallback is None:
            support_status, support_note = classify_telegram_build(app_update_build)
            fallback = {
                "app_update_build": app_update_build,
                "support_status": support_status,
                "support_note": support_note,
                "source_path": config_path,
            }

    if fallback is not None:
        return fallback

    support_status, support_note = classify_telegram_build(None)
    return {
        "app_update_build": None,
        "support_status": support_status,
        "support_note": support_note,
        "source_path": "",
    }


def format_fs_timestamp(ts):
    """Convert a filesystem timestamp to ISO-8601 UTC for media file reporting."""
    if not ts:
        return ""
    try:
        return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
    except Exception:
        return ""


def format_message_direction(out_value):
    """Convert Telegram's outgoing flag into a simple direction label."""
    return "Sent" if out_value else "Received"


def classify_message_report(row):
    """Split message rows into direct, group, and channel report buckets."""
    if row.get("is_channel") or row.get("peer_type") == "channel":
        return "channel"
    if row.get("peer_type") in ("chat", "chat_or_group"):
        return "group"
    return "direct"


def build_message_report_rows(rows, report_kind):
    """
    Build simplified ALEAPP rows for one Telegram message bucket.

    The user requested a small set of columns for message views, so these rows
    only include date, peer, direction, text, and whether media was present.
    """
    data_list = []
    for row in rows:
        if classify_message_report(row) != report_kind:
            continue
        if not row.get("message_text") and not row.get("has_media"):
            continue
        data_list.append((
            row.get("date_iso", ""),
            row.get("peer_name", ""),
            format_message_direction(row.get("out")),
            row.get("message_text", ""),
            "Yes" if row.get("has_media") else "No",
        ))
    return data_list


def build_telegram_media_cache_rows(media_files, report_folder, seeker):
    """
    Build a file-system oriented view of Telegram media cache items.

    This report is intentionally separate from the message-media table because
    Telegram cache file names are not always deterministically mappable back to a
    single message row without more media-specific TL decoding work.
    """
    rows = []
    for media_path in media_files:
        file_info = seeker.file_infos.get(media_path) if seeker else None
        preview = media_to_html(os.path.basename(media_path), media_files, report_folder)
        rows.append((
            os.path.basename(media_path),
            os.path.splitext(media_path)[1].lower(),
            os.path.getsize(media_path),
            format_fs_timestamp(file_info.creation_date if file_info else os.path.getctime(media_path)),
            format_fs_timestamp(file_info.modification_date if file_info else os.path.getmtime(media_path)),
            preview,
        ))
    return rows


def summarize_source_locations(*labels):
    """Return a short report source string instead of a long file-by-file path list."""
    return " | ".join(label for label in labels if label)


def find_matching_media_file(media_files, token):
    """Find the first media file whose basename contains the supplied token."""
    token = str(token or "").strip()
    if not token:
        return ""
    for media_path in media_files:
        if token in os.path.basename(media_path):
            return media_path
    return ""


def build_avatar_preview(media_files, photo_id, report_folder):
    """Render an avatar preview for a Telegram photo ID when a cache file exists."""
    match = find_matching_media_file(media_files, photo_id)
    if not match:
        return ""
    return media_to_html(os.path.basename(match), media_files, report_folder)


def parse_telegram_contacts(cache4db_path, media_files, report_folder):
    """
    Parse Telegram contacts and best-effort imported phonebook rows.

    Telegram keeps:
    - actual Telegram contacts in contacts/users/dialog_photos
    - imported phonebook style records in user_contacts_v7/user_phones_v7
    """
    contacts_out = []
    contacts_by_name = {}

    conn = sqlite3.connect(cache4db_path)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.execute("""
            SELECT c.uid, c.mutual, u.name, u.data,
                   (SELECT id FROM dialog_photos dp WHERE dp.uid = c.uid ORDER BY num ASC LIMIT 1) AS photo_id
            FROM contacts c
            LEFT JOIN users u ON u.uid = c.uid
            ORDER BY u.name
        """)
        for row in cur:
            raw_name = row["name"] or ""
            display_name, fallback_username = split_telegram_name(raw_name)
            user_info = parse_telegram_user_blob(row["data"]) if row["data"] else {}
            contact = {
                "name": display_name or user_info.get("display_name", "") or fallback_username or str(row["uid"]),
                "phone": user_info.get("phone", ""),
                "telegram_uid": row["uid"],
                "username": user_info.get("username", "") or fallback_username,
                "mutual": "Yes" if row["mutual"] else "No",
                "avatar": build_avatar_preview(media_files, row["photo_id"], report_folder) if row["photo_id"] else "",
            }
            contacts_out.append(contact)
            contacts_by_name[contact["name"].strip().lower()] = contact

        cur = conn.execute("""
            SELECT uc.uid AS imported_uid, uc.fname, uc.sname, uc.imported, up.phone
            FROM user_contacts_v7 uc
            LEFT JOIN user_phones_v7 up ON up.key = uc.key
            ORDER BY uc.fname, uc.sname
        """)
        for row in cur:
            name = " ".join(part for part in (row["fname"], row["sname"]) if part).strip()
            normalized_name = name.lower()
            existing = contacts_by_name.get(normalized_name)
            if existing:
                if not existing["phone"] and row["phone"]:
                    existing["phone"] = row["phone"]
                continue

            contacts_out.append({
                "name": name or f"Imported Contact {row['imported_uid']}",
                "phone": row["phone"] or "",
                "telegram_uid": "",
                "username": "",
                "mutual": "",
                "avatar": "",
            })
    finally:
        conn.close()

    return [
        (
            contact["name"],
            contact["phone"],
            contact["telegram_uid"],
            contact["username"],
            contact["mutual"],
            contact["avatar"],
        )
        for contact in contacts_out
    ]


def infer_telegram_voip_log_paths(cache4db_path):
    """Infer Telegram voip log paths from the cache4.db location for standalone use."""
    app_root = os.path.dirname(os.path.dirname(cache4db_path))
    log_dir = os.path.join(app_root, "cache", "voip_logs")
    if not os.path.isdir(log_dir):
        return []
    return sorted(
        os.path.join(log_dir, name)
        for name in os.listdir(log_dir)
        if name.endswith(".log") and name != "voip_persistent_state.json" and not name.endswith("_stats.log")
    )


def parse_voip_log_span(log_path):
    """
    Calculate start/end timestamps and duration from a Telegram voip log.

    The timestamps inside the log are local-time strings without timezone, so we
    only use their difference. The file mtime is used as the UTC end time.
    """
    first_local = None
    last_local = None
    pattern = re.compile(r'^(\d{4})-(\d+)-(\d+) (\d+):(\d+):(\d+):(\d+)')

    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            match = pattern.match(line)
            if not match:
                continue
            local_dt = datetime(
                int(match.group(1)),
                int(match.group(2)),
                int(match.group(3)),
                int(match.group(4)),
                int(match.group(5)),
                int(match.group(6)),
                int(match.group(7)) * 1000,
            )
            if first_local is None:
                first_local = local_dt
            last_local = local_dt

    end_utc = datetime.fromtimestamp(os.path.getmtime(log_path), tz=timezone.utc)
    if first_local and last_local:
        duration_seconds = max(0, int((last_local - first_local).total_seconds()))
        start_utc = end_utc - timedelta(seconds=duration_seconds)
    else:
        duration_seconds = 0
        start_utc = end_utc

    start_label = first_local.isoformat(sep=" ") if first_local else start_utc.isoformat()
    end_label = last_local.isoformat(sep=" ") if last_local else end_utc.isoformat()
    return start_label, end_label, duration_seconds, first_local, last_local


def parse_telegram_calls(cache4db_path, rows, voip_log_paths):
    """Build a Telegram calls table from voip logs plus nearby service messages."""
    calls = []
    for log_path in voip_log_paths:
        start_iso, end_iso, duration_seconds, first_local, last_local = parse_voip_log_span(log_path)
        if last_local:
            end_ts = int(last_local.timestamp())
        else:
            end_ts = int(os.path.getmtime(log_path))

        def row_ts(row):
            raw_date = row.get("raw_date")
            if raw_date not in (None, ""):
                try:
                    return int(raw_date)
                except Exception:
                    pass
            if row.get("date_iso"):
                try:
                    return int(datetime.fromisoformat(row["date_iso"]).timestamp())
                except Exception:
                    return 0
            return 0

        nearby = [
            row for row in rows
            if row.get("constructor") == "0x2b085862" and abs(row_ts(row) - end_ts) <= 300
        ]
        nearest = min(nearby, key=lambda row: abs(row_ts(row) - end_ts)) if nearby else None
        peer_name = nearest.get("peer_name", "") if nearest else ""
        peer_id = nearest.get("uid", "") if nearest else ""
        direction = format_message_direction(nearest.get("out")) if nearest else ""

        call_type = "Voice"
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            sample = f.read(2000).lower()
            if "camera" in sample or "video" in sample:
                call_type = "Video"

        call_id = os.path.splitext(os.path.basename(log_path))[0]
        calls.append((
            start_iso,
            end_iso,
            duration_seconds,
            direction,
            peer_name,
            peer_id,
            call_id,
            call_type,
        ))
    return calls


def write_simple_table_report(
    report_folder,
    report_name,
    data_headers,
    data_list,
    source_text,
    html_escape=True,
    description="",
    category="Telegram",
    artifact_icon="file-text",
):
    """Small helper for writing ALEAPP HTML + TSV + timeline with a concise source string."""
    icons.setdefault(category, {}).update({report_name: artifact_icon})

    report = ArtifactHtmlReport(report_name)
    report.start_artifact_report(report_folder, report_name, description)
    report.add_script()
    report.write_artifact_data_table(data_headers, data_list, source_text, html_escape=html_escape)
    report.end_artifact_report()
    tsv(report_folder, data_headers, data_list, report_name)


def get_telegram_cache4_messages(files_found, report_folder, seeker, wrap_text):
    """
    ALEAPP entry point for Telegram cache4.db message extraction.

    This function now orchestrates four related outputs:
    1. Direct messages
    2. Group messages
    3. Channel messages
    4. Telegram media cache inventory
    """
    cache_files = []
    for file_found in files_found:
        file_found = str(file_found)
        if os.path.basename(file_found) == "cache4.db":
            cache_files.append(file_found)

    if not cache_files:
        logfunc("No Telegram cache4.db files found")
        return

    build_info = get_telegram_build_info(files_found, seeker)
    if build_info["support_status"] != "supported":
        logfunc(f"Telegram parser warning: {build_info['support_note']}")

    rows = []
    for cache_file in cache_files:
        parsed_rows = parse_cache4db(cache_file)
        for row in parsed_rows:
            row["source_db"] = cache_file
            rows.append(row)

    if not rows:
        logfunc("No Telegram cache4 messages found")
        return

    data_headers = (
        "Date (UTC)",
        "Peer Name",
        "Direction",
        "Text",
        "Has Media",
    )

    report_specs = (
        ("direct", "Messages"),
        ("group", "Group Messages"),
        ("channel", "Channel Messages"),
    )
    message_source = summarize_source_locations(
        "Telegram message databases: */org.telegram.messenger/files/cache4.db",
        "Additional account databases: */org.telegram.messenger/files/account*/cache4.db",
    )
    for report_kind, report_name in report_specs:
        data_list = build_message_report_rows(rows, report_kind)
        write_simple_table_report(
            report_folder,
            report_name,
            data_headers,
            data_list,
            message_source,
            html_escape=True,
            artifact_icon={
                "Messages": "message-circle",
                "Group Messages": "users",
                "Channel Messages": "radio",
            }.get(report_name, "message-circle"),
        )
        timeline(report_folder, report_name, data_list, data_headers)
        logfunc(f"{report_name}: {len(data_list)} records")

    media_files = find_telegram_media_cache_files(seeker)
    media_cache_rows = build_telegram_media_cache_rows(media_files, report_folder, seeker)
    cache_headers = (
        "File Name",
        "Extension",
        "Size (bytes)",
        "Created (UTC)",
        "Modified (UTC)",
        "Preview",
    )
    media_source = summarize_source_locations(
        "Telegram app-private cache: */org.telegram.messenger/cache/*",
        "Telegram shared media cache: */Android/data/org.telegram.messenger/cache/*",
    )
    write_simple_table_report(
        report_folder,
        "Media",
        cache_headers,
        media_cache_rows,
        media_source,
        html_escape=False,
        description="Telegram media cache files found on disk.",
        artifact_icon="image",
    )
    logfunc(f"Media: {len(media_cache_rows)} records")

    voip_log_paths = []
    for cache_file in cache_files:
        for log_path in infer_telegram_voip_log_paths(cache_file):
            if log_path not in voip_log_paths:
                voip_log_paths.append(log_path)
    call_headers = (
        "Start",
        "End",
        "Duration (seconds)",
        "Direction",
        "Caller",
        "Peer ID",
        "Call ID",
        "Call Type",
    )
    call_rows = parse_telegram_calls(cache_files[0], rows, voip_log_paths)
    call_source = summarize_source_locations(
        "Telegram VoIP logs: */org.telegram.messenger/cache/voip_logs/*.log",
    )
    write_simple_table_report(
        report_folder,
        "Calls",
        call_headers,
        call_rows,
        call_source,
        html_escape=True,
        artifact_icon="phone-call",
    )
    logfunc(f"Calls: {len(call_rows)} records")

    contacts_headers = (
        "Name",
        "Phone Number",
        "Telegram UID",
        "Username",
        "Mutual Contact",
        "Avatar",
    )
    contacts_rows = parse_telegram_contacts(cache_files[0], media_files, report_folder)
    contacts_source = summarize_source_locations(
        "Telegram contacts DB: */org.telegram.messenger/files/cache4.db",
        "Telegram avatar cache: */org.telegram.messenger/cache/*",
    )
    write_simple_table_report(
        report_folder,
        "Contacts",
        contacts_headers,
        contacts_rows,
        contacts_source,
        html_escape=False,
        artifact_icon="user",
    )
    logfunc(f"Contacts: {len(contacts_rows)} records")


def parse_userconfig_xml(files_found, report_folder=1, seeker=1, wrap_text=1):
    # temporarily giving default arguments, will remove before production
    """
    Parse a single Telegram userconfig XML file and return rows for a simple
    preferences table.

    This function focuses on user/account state that is useful in ALEAPP output.
    The wrapper entry point below handles file discovery and report writing.
    """

    #report = ArtifactHtmlReport("Telegram - User Preferences")
    #report.start_artifact_report(report_folder, "Telegram - User Preferences")
    results = parse_shared_prefs_map(files_found)

    targets = {
        "appLocked",
        "passcodeType",
        "hasSecureData",
        "user",
        "lastContactsSyncTime",
        "last_call_time",
        "last_call_phone_number",
        "selectedAccount",
        "autoLockIn",
        "loginTime",
        "sharingMyLocationUntil",
        "badPasscodeTries",
        "appUpdateBuild",
        "contactsSavedCount",
        # Optional extras worth reporting if present:
        "syncContacts",
        "suggestContacts",
        "showCallsTab",
        "useFingerprint",
        "passcodeRetryInMs",
        "lastPauseTime",
    }
    results = {key: results[key] for key in targets if key in results}

    # Creating dictionary for user info.
    user_info = parse_telegram_user_blob(base64.b64decode(results["user"])) if results.get("user") else {
        "user_id": "",
        "first_name": "",
        "last_name": "",
        "username": "",
        "phone": "",
        "display_name": "",
    }

    if user_info.get("constructor") not in (None, 0x215C4438, 0x020B1422):
        print(f"Unsupported Telegram user constructor: 0x{user_info['constructor']:08x}")
        # Future work on this plugin should focus on adding support for more constructors for compatibility.
        # I think it was last changed in 2024.
        # Per https://github.com/danog/schemas/blob/master/TL_telegram_v172.tl

    passcode_type_raw = results.get("passcodeType")
    if passcode_type_raw == 0:
        passcode_type_display = "PIN"
    elif passcode_type_raw == 1:
        passcode_type_display = "Password"
    elif passcode_type_raw in ("0", "1"):
        passcode_type_display = "PIN" if str(passcode_type_raw) == "0" else "Password"
    elif passcode_type_raw is None:
        passcode_type_display = ""
    else:
        passcode_type_display = f"Unknown ({passcode_type_raw})"

    app_locked_display = "Enabled" if results.get("appLocked") is True else "Disabled" if results.get(
        "appLocked") is False else ""
    has_secure_data_display = "Present" if results.get("hasSecureData") is True else "Not Present" if results.get(
        "hasSecureData") is False else ""

    auto_lock_value = results.get("autoLockIn")
    if isinstance(auto_lock_value, int):
        if auto_lock_value == 0:
            auto_lock_display = "Disabled / immediate value 0"
        elif auto_lock_value < 60:
            auto_lock_display = f"{auto_lock_value} seconds"
        elif auto_lock_value % 3600 == 0:
            auto_lock_display = f"{auto_lock_value // 3600} hour(s)"
        elif auto_lock_value % 60 == 0:
            auto_lock_display = f"{auto_lock_value // 60} minute(s)"
        else:
            auto_lock_display = f"{auto_lock_value} seconds"
    else:
        auto_lock_display = str(auto_lock_value or "")

    # Build rows for ALEAPP.
    data_list = []

    # Account identity from serialized user blob
    data_list.append(("Telegram User ID", user_info["user_id"], "Current Telegram account identifier"))
    data_list.append(("First Name", user_info["first_name"], "Current Telegram account first name"))
    data_list.append(("Last Name", user_info["last_name"], "Current Telegram account last name"))
    data_list.append(("Username", user_info["username"], "Current Telegram account username"))
    data_list.append(("Phone Number", user_info["phone"], "Current Telegram account phone number"))

    # Config values from userconfing.xml
    data_list.append(("App Lock", app_locked_display, "Whether Telegram app lock was enabled"))
    data_list.append(("Passcode Type", passcode_type_display, "App lock mode used by Telegram"))
    data_list.append(("Has Secure Data", has_secure_data_display, "Whether Telegram stored secure data state"))
    data_list.append(("Selected Account", results.get("selectedAccount", ""), "Active Telegram account slot on device"))
    data_list.append(("Auto Lock Interval", auto_lock_display, "Configured Telegram app auto-lock interval"))
    data_list.append(
        ("Bad Passcode Tries", results.get("badPasscodeTries", ""), "Recorded failed Telegram passcode attempts"))
    data_list.append(
        ("Login Time (UTC)", unix_to_iso(results.get("loginTime")), "Stored Telegram login/account timestamp"))
    data_list.append(("Last Contacts Sync Time (UTC)", unix_to_iso(results.get("lastContactsSyncTime")),
                      "Last Telegram contacts synchronization time"))
    data_list.append(("Sharing My Location Until (UTC)", unix_to_iso(results.get("sharingMyLocationUntil")),
                      "Live location sharing end time if non-zero"))
    data_list.append(
        ("Contacts Saved Count", results.get("contactsSavedCount", ""), "Saved/imported contacts count metadata"))
    data_list.append(("App Update Build", results.get("appUpdateBuild", ""), "Telegram app update build metadata"))
    data_list.append(
        ("Last Call Time (UTC)", unix_ms_to_iso(results.get("last_call_time")), "Call-related timestamp if present"))

    # Optional extras if present
    if "syncContacts" in results:
        data_list.append(("Sync Contacts", results.get("syncContacts"), "Whether contact synchronization was enabled"))
    if "suggestContacts" in results:
        data_list.append(
            ("Suggest Contacts", results.get("suggestContacts"), "Whether Telegram contact suggestions were enabled"))
    if "showCallsTab" in results:
        data_list.append(("Show Calls Tab", results.get("showCallsTab"), "Whether the calls tab was enabled"))
    if "useFingerprint" in results:
        data_list.append(("Use Fingerprint", results.get("useFingerprint"),
                          "Whether fingerprint unlock was enabled for Telegram app lock"))
    if "passcodeRetryInMs" in results:
        data_list.append(
            ("Passcode Retry Delay (ms)", results.get("passcodeRetryInMs"), "Current Telegram lockout/backoff delay"))
    if "lastPauseTime" in results:
        data_list.append(
            ("Last Pause Time", results.get("lastPauseTime"), "Last pause time used by Telegram for lock timing"))

    return data_list


def get_telegram_user_preferences(files_found, report_folder, seeker, wrap_text):
    """ALEAPP entry point for Telegram user preferences and account metadata."""
    config_files = find_telegram_userconfig_files(files_found, seeker)
    if not config_files:
        logfunc("No Telegram userconfig XML files found")
        return

    primary_config = config_files[0]
    data_headers = ("Setting", "Value", "Meaning")
    data_list = []

    for setting, value, meaning in parse_userconfig_xml(primary_config):
        if value in ("", None):
            continue
        data_list.append((setting, value, meaning))

    if not data_list:
        logfunc("No Telegram user preference data found")
        return

    icons.setdefault("Telegram", {}).update({"User Prefs": "settings"})
    report = ArtifactHtmlReport("User Prefs")
    report.start_artifact_report(report_folder, "User Prefs")
    report.add_script()
    prefs_source = summarize_source_locations(
        "Telegram shared preferences: */org.telegram.messenger/shared_prefs/userconfing.xml",
        "Fallback config files: */org.telegram.messenger/shared_prefs/userconfig*.xml",
    )
    report.write_artifact_data_table(data_headers, data_list, prefs_source, html_escape=True)
    report.end_artifact_report()

    tsv(report_folder, data_headers, data_list, "User Prefs")
    logfunc(f"User Prefs: {len(data_list)} records")


def parse_media():
    """
    Placeholder kept for future media-specific TL decoding work.

    The current ALEAPP media output is built from:
    - message rows that have a media field
    - Telegram media cache files discovered on disk
    """
    pass

# region Helper Functions

# The helper region below is intentionally split across two styles:
# 1. offset-based helpers for raw bytes buffers (used by cache4.db parsing)
# 2. file-stream helpers for BytesIO/base64 decoded XML content
# The TLReader class above is the stateful version of the first style.

def read_tl_bytes(buf, off):
    """Read a TL-encoded bytes field from a bytes buffer using an explicit offset."""
    if off >= len(buf):
        raise ValueError("read_tl_bytes past end")

    first = buf[off]
    off += 1

    if first < 254:
        length = first
        if off + length > len(buf):
            raise ValueError("short tl bytes")
        value = buf[off:off + length]
        off += length
        consumed = 1 + length
    else:
        if off + 3 > len(buf):
            raise ValueError("short tl long bytes header")
        length = buf[off] | (buf[off + 1] << 8) | (buf[off + 2] << 16)
        off += 3
        if off + length > len(buf):
            raise ValueError("short tl long bytes body")
        value = buf[off:off + length]
        off += length
        consumed = 4 + length

    pad = (4 - (consumed % 4)) % 4
    off += pad
    return value, off

def read_tl_string(buf, off):
    """Read a TL-encoded UTF-8 string from a bytes buffer using an explicit offset."""
    raw, off = read_tl_bytes(buf, off)
    return raw.decode("utf-8", errors="replace"), off


def read_tl_bytes_from_file(f):
    """Read a TL-encoded bytes field from a file-like stream."""
    first_raw = f.read(1)
    if len(first_raw) != 1:
        raise EOFError("Could not read TL bytes length")

    first = first_raw[0]
    if first < 254:
        length = first
        value = read_bytes(f, length)
        consumed = 1 + length
    else:
        header = read_bytes(f, 3)
        length = header[0] | (header[1] << 8) | (header[2] << 16)
        value = read_bytes(f, length)
        consumed = 4 + length

    pad = (4 - (consumed % 4)) % 4
    if pad:
        read_bytes(f, pad)
    return value


def read_tl_string_from_file(f):
    """Read a TL-encoded UTF-8 string from a file-like stream."""
    return read_tl_bytes_from_file(f).decode("utf-8", errors="replace")

def printable_runs(blob, min_length=4):
    """
    Extract readable text runs from a byte blob.

    This keeps ASCII printable bytes and also allows a few common text bytes
    that appear in UTF-8 encoded punctuation often seen in messages.
    """
    runs = []
    current = bytearray()

    for b in blob:
        if (
            32 <= b <= 126               # normal ASCII printable
            or b in (9, 10, 13)          # tab/newline/carriage return
        ):
            current.append(b)
        else:
            if len(current) >= min_length:
                runs.append(current.decode("utf-8", errors="ignore"))
            current = bytearray()

    if len(current) >= min_length:
        runs.append(current.decode("utf-8", errors="ignore"))

    return runs

def read_u32(buf, off):
    """Read a uint32 from a bytes buffer using an explicit offset."""
    if off + 4 > len(buf):
        raise ValueError("read_u32 past end")
    return struct.unpack_from("<I", buf, off)[0], off + 4

def read_int32(f):
    """
    Read a 32-bit little-endian integer from the current stream position.

    Telegram TL serialization uses little-endian integers for constructor IDs,
    flags fields, message IDs, dates, and many other values.
    """
    data = f.read(4)
    if len(data) != 4:
        raise EOFError("Could not read int32")
    return struct.unpack("<I", data)[0]

def read_int64(f):
    """
    Read a 64-bit little-endian integer from the current stream position.

    Telegram uses 64-bit integers for some IDs and access hashes.
    """
    data = f.read(8)
    if len(data) != 8:
        raise EOFError("Could not read int64")
    return struct.unpack("<q", data)[0]

def flag_set(value, bit):
    """
    Check whether a specific bit is set in a Telegram flags integer.

    Telegram uses bit flags to indicate whether optional fields exist.
    Example:
    - if bit 1 is set, first_name exists
    - if bit 4 is set, phone exists

    Telegram also relies heavily on flags for cache4.db messages.
    """
    return (value & (1 << bit)) != 0

def unix_to_iso(ts):
    if not ts:
        return None
    try:
        return datetime.fromtimestamp(int(ts), tz=timezone.utc).isoformat()
    except Exception:
        return str(ts)

def unix_ms_to_iso(ts):
    if not ts:
        return None
    try:
        return datetime.fromtimestamp(int(ts) / 1000, tz=timezone.utc).isoformat()
    except Exception:
        return None

def read_bytes(f, n):
    data = f.read(n)
    if len(data) != n:
        raise EOFError(f"Could not read {n} bytes")
    return data

def read_int32_signed(f):
    data = f.read(4)
    if len(data) != 4:
        raise EOFError("Could not read int32")
    return struct.unpack("<i", data)[0]

def read_int64_unsigned(f):
    data = f.read(8)
    if len(data) != 8:
        raise EOFError("Could not read int64")
    return struct.unpack("<Q", data)[0]

# endregion

if __name__ == '__main__':
    from collections import Counter

    def inventory_message_constructors(db_path):
        counts = Counter()

        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        cur.execute("SELECT data FROM messages_v2 WHERE data IS NOT NULL")
        for (blob,) in cur.fetchall():
            if blob and len(blob) >= 4:
                constructor = struct.unpack("<I", blob[:4])[0]
                counts[f"0x{constructor:08x}"] += 1

        conn.close()
        return counts

    def debug_cache4_rows(cache4db_path, limit=20, only_with_text=False):
        # shouldn't be needed anymore. only used to debug logic issues, but I'm keeping it in just in case.
        rows = parse_cache4db(cache4db_path)
        shown = 0

        for row in rows:
            if shown >= limit:
                break
            if only_with_text and not row.get("message_text"):
                continue
            shown += 1

            print("=" * 80)
            print(f"ROW {shown}")
            print(f"date:        {row.get('date_iso')}")
            print(f"mid:         {row.get('mid')}")
            print(f"uid:         {row.get('uid')}")
            print(f"peer_name:   {row.get('peer_name')}")
            print(f"peer_type:   {row.get('peer_type')}")
            print(f"out:         {row.get('out', '')}")
            print(f"ttl:         {row.get('ttl', '')}")
            print(f"has_media:   {row.get('has_media', '')}")
            print(f"is_channel:  {row.get('is_channel', '')}")
            print(f"constructor: {row.get('constructor')}")
            print(f"parse_note:  {row.get('parse_note')}")
            print(f"text:        {repr(row.get('message_text', ''))}")
            print(f"strings:     {row.get('visible_strings', '')[:300]}")

    def prompt_for_path(prompt_text):
        while True:
            value = input(prompt_text).strip().strip('"')
            if value:
                return value

    def render_standalone_html(output_path, sections):
        page = [
            "<!doctype html>",
            "<html><head><meta charset='utf-8'><title>Telegram Sample Output</title>",
            "<style>body{font-family:Segoe UI,Arial,sans-serif;margin:24px;}table{border-collapse:collapse;width:100%;margin:12px 0 24px;}th,td{border:1px solid #ccc;padding:6px 8px;vertical-align:top;}th{background:#f2f2f2;}h1,h2{margin-bottom:8px;}code{background:#f4f4f4;padding:2px 4px;}</style>",
            "</head><body>",
            "<h1>Telegram Sample Output</h1>",
        ]
        for title, headers, rows in sections:
            page.append(f"<h2>{html.escape(title)}</h2>")
            page.append("<table><thead><tr>")
            for header in headers:
                page.append(f"<th>{html.escape(str(header))}</th>")
            page.append("</tr></thead><tbody>")
            for row in rows:
                page.append("<tr>")
                for cell in row:
                    page.append(f"<td>{cell if title in ('Media', 'Contacts') else html.escape(str(cell or ''))}</td>")
                page.append("</tr>")
            if not rows:
                page.append(f"<tr><td colspan='{len(headers)}'>No rows</td></tr>")
            page.append("</tbody></table>")
        page.append("</body></html>")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("".join(page))

    def run_test():
        """
        Standalone test runner — validates TL decoding without launching ALEAPP.
        Run with:
            python scripts\\artifacts\\Telegram.py --cache4db "D:\\path\\to\\cache4.db" --userconfig "D:\\path\\to\\userconfing.xml" --output "D:\\path\\to\\telegram_sample.html"
        """
        parser = argparse.ArgumentParser(description="Standalone Telegram parser test for ALEAPP development.")
        parser.add_argument("--cache4db", help="Path to Telegram cache4.db")
        parser.add_argument("--userconfig", help="Path to Telegram userconfing.xml")
        parser.add_argument("--output", help="Path to write a small sample HTML report")
        parser.add_argument("--limit", type=int, default=10, help="Number of sample message rows to include in the HTML output")
        args = parser.parse_args()

        cache4db_path = args.cache4db or prompt_for_path("cache4.db path: ")
        userconfig_path = args.userconfig or prompt_for_path("userconfing.xml path: ")
        output_path = args.output or prompt_for_path("Output HTML path: ")

        print("\n" + "=" * 80)
        print("Telegram.py — standalone test")
        print("=" * 80)
        print(f"cache4.db:      {cache4db_path}")
        print(f"userconfing.xml:{userconfig_path}")
        print(f"output html:    {output_path}")

        if not os.path.exists(cache4db_path):
            raise FileNotFoundError(f"cache4.db not found: {cache4db_path}")
        if not os.path.exists(userconfig_path):
            raise FileNotFoundError(f"userconfing.xml not found: {userconfig_path}")

        print("\n[Constructor inventory]")
        counts = inventory_message_constructors(cache4db_path)
        for cid, n in counts.most_common():
            print(f"  {cid}  x{n}")

        rows = parse_cache4db(cache4db_path)
        total = len(rows)
        with_text = sum(1 for r in rows if r.get("message_text"))
        service = sum(1 for r in rows if r.get("constructor") == "0x2b085862")
        failed = [r for r in rows if "decode failed" in (r.get("parse_note") or "")]

        print("\n[Parse stats]")
        print(f"  Total rows:          {total}")
        print(f"  Messages with text:  {with_text}")
        print(f"  Service messages:    {service}")
        print(f"  Decode failures:     {len(failed)}")

        print(f"\n[Sample rows with text] (up to {args.limit})")
        debug_cache4_rows(cache4db_path, limit=args.limit, only_with_text=True)

        if failed:
            print("\n[Decode failures] (first 5)")
            for r in failed[:5]:
                print(f"  mid={r.get('mid')}  ctor={r.get('constructor')}  note={r.get('parse_note')}")

        prefs_rows = parse_userconfig_xml(userconfig_path)
        media_files = []
        inferred_media_dir = os.path.join(os.path.dirname(os.path.dirname(cache4db_path)), "cache")
        if os.path.isdir(inferred_media_dir):
            for name in os.listdir(inferred_media_dir):
                full_path = os.path.join(inferred_media_dir, name)
                if os.path.isfile(full_path):
                    media_files.append(full_path)

        sample_sections = [
            ("User Prefs", ("Setting", "Value", "Meaning"), prefs_rows),
            ("Messages", ("Date (UTC)", "Peer Name", "Direction", "Text", "Has Media"), build_message_report_rows(rows, "direct")[:args.limit]),
            ("Group Messages", ("Date (UTC)", "Peer Name", "Direction", "Text", "Has Media"), build_message_report_rows(rows, "group")[:args.limit]),
            ("Channel Messages", ("Date (UTC)", "Peer Name", "Direction", "Text", "Has Media"), build_message_report_rows(rows, "channel")[:args.limit]),
            ("Calls", ("Start", "End", "Duration (seconds)", "Direction", "Caller", "Peer ID", "Call ID", "Call Type"), parse_telegram_calls(cache4db_path, rows, infer_telegram_voip_log_paths(cache4db_path))),
            ("Contacts", ("Name", "Phone Number", "Telegram UID", "Username", "Mutual Contact", "Avatar"), parse_telegram_contacts(cache4db_path, media_files, os.path.dirname(output_path))[:args.limit]),
            ("Media", ("File Name", "Extension", "Size (bytes)", "Created (UTC)", "Modified (UTC)", "Preview"), build_telegram_media_cache_rows(media_files, os.path.dirname(output_path), None)[:args.limit]),
        ]
        render_standalone_html(output_path, sample_sections)
        print(f"\n[+] Wrote sample HTML: {output_path}")
        print("\n" + "=" * 80)

    run_test()
