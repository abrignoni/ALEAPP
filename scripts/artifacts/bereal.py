__artifacts_v2__ = {
    "bereal_device_user": {
        "name": "BeReal Android - Authenticated User",
        "description": "Reports an authenticated BeReal user only when explicit current-user evidence is present.",
        "author": "@Gear-I",
        "creation_date": "2026-07-19",
        "last_update_date": "2026-07-19",
        "requirements": "none",
        "category": "BeReal - Social Media",
        "notes": "High/Medium confidence requires a current-user endpoint/context or explicit isMe/current-user flag. Low confidence is reported only when a persisted shared_prefs account identifier matches a cached profile with no corroborating endpoint or flag. Generic cached profiles are excluded.",
        "paths": (
            "*/data/data/com.bereal.ft/cache/network/*",
            "*/data/user/0/com.bereal.ft/cache/network/*",
            "*/data/data/com.bereal.ft/shared_prefs/*.xml",
            "*/data/user/0/com.bereal.ft/shared_prefs/*.xml",
            "*/data/data/com.bereal.ft/files/*",
            "*/data/user/0/com.bereal.ft/files/*",
        ),
        "output_types": "standard",
        "artifact_icon": "user",
    },
    "bereal_friends": {
        "name": "BeReal Android - Accepted Friends",
        "description": "Reports only profiles supported by explicit accepted-friend evidence.",
        "author": "@Gear-I",
        "creation_date": "2026-07-19",
        "last_update_date": "2026-07-19",
        "requirements": "none",
        "category": "BeReal - Social Media",
        "notes": "Accepted friends are confirmed to come from the /friends-v1 endpoint. Pending requests (/friend-requests/received, /friend-requests/sent) and suggestions (/friends-of-friends) are confirmed as distinct endpoints and are excluded.",
        "paths": (
            "*/data/data/com.bereal.ft/cache/network/*",
            "*/data/user/0/com.bereal.ft/cache/network/*",
            "*/data/data/com.bereal.ft/files/*",
            "*/data/user/0/com.bereal.ft/files/*",
        ),
        "output_types": "standard",
        "artifact_icon": "users",
    },
    "bereal_posts": {
        "name": "BeReal Android - Posts",
        "description": "Reports recoverable BeReal posts and correlated front/rear/video media.",
        "author": "@Gear-I",
        "creation_date": "2026-07-19",
        "last_update_date": "2026-07-19",
        "requirements": "none",
        "category": "BeReal - Social Media",
        "notes": "Field names (id, primaryContent/secondaryContent/btsContent, myPosts/friendsPosts, comments, realMojis) confirmed against the BeReal Android client's own serialization DTOs (reverse-engineered from base.apk). Authorship is derived structurally from myPosts/friendsPosts or the posts[] wrapper's sibling user, not guessed from context.",
        "paths": (
            "*/data/data/com.bereal.ft/cache/network/*",
            "*/data/user/0/com.bereal.ft/cache/network/*",
            "*/data/data/com.bereal.ft/cache/bereal_*video_cache/*",
            "*/data/user/0/com.bereal.ft/cache/bereal_*video_cache/*",
            "*/data/data/com.bereal.ft/cache/friend_timeline_cache/*",
            "*/data/user/0/com.bereal.ft/cache/friend_timeline_cache/*",
            "*/data/data/com.bereal.ft/files/*",
            "*/data/user/0/com.bereal.ft/files/*",
        ),
        "output_types": "standard",
        "artifact_icon": "camera",
    },
    "bereal_profile_pictures": {
        "name": "BeReal Android - Correlated Profile Pictures",
        "description": "Renders cached profile pictures only when their metadata URL maps to a recovered user profile.",
        "author": "@Gear-I",
        "creation_date": "2026-07-19",
        "last_update_date": "2026-07-19",
        "requirements": "none",
        "category": "BeReal - Social Media",
        "notes": "Unassociated cache images are not reported. DiskLruCache .0 metadata is paired with .1 content.",
        "paths": (
            "*/data/data/com.bereal.ft/cache/profile_picture_friends_cache/*",
            "*/data/user/0/com.bereal.ft/cache/profile_picture_friends_cache/*",
            "*/data/data/com.bereal.ft/cache/network/*",
            "*/data/user/0/com.bereal.ft/cache/network/*",
        ),
        "output_types": "standard",
        "artifact_icon": "photo",
    },
    "bereal_comments": {
        "name": "BeReal Android - Comments",
        "description": "Reports comment records that can be linked to a post.",
        "author": "@Gear-I",
        "creation_date": "2026-07-19",
        "last_update_date": "2026-07-19",
        "requirements": "none",
        "category": "BeReal - Social Media",
        "notes": "Comments are extracted from a post's own embedded \"comments\" array (confirmed schema) or a standalone {postId, comments:[...]} endpoint response, not from generic keyword matching.",
        "paths": (
            "*/data/data/com.bereal.ft/cache/network/*",
            "*/data/user/0/com.bereal.ft/cache/network/*",
        ),
        "output_types": "standard",
        "artifact_icon": "message-square",
    },
    "bereal_realmojis": {
        "name": "BeReal Android - RealMojis",
        "description": "Reports RealMoji/reaction records linked to a post.",
        "author": "@Gear-I",
        "creation_date": "2026-07-19",
        "last_update_date": "2026-07-19",
        "requirements": "none",
        "category": "BeReal - Social Media",
        "notes": "RealMojis are extracted from a post's own embedded \"realMojis\" array (confirmed schema), distinguishing Instant vs standard RealMojis.",
        "paths": (
            "*/data/data/com.bereal.ft/cache/network/*",
            "*/data/user/0/com.bereal.ft/cache/network/*",
            "*/data/data/com.bereal.ft/cache/profile_picture_friends_cache/*",
            "*/data/user/0/com.bereal.ft/cache/profile_picture_friends_cache/*",
        ),
        "output_types": "standard",
        "artifact_icon": "thumbs-up",
    },
}

import gzip
import json
import os
import re
import zlib
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree

from scripts.ilapfuncs import artifact_processor, check_in_media, logfunc

URL_RE = re.compile(r"https?://[^\s\"'<>]+", re.I)
SENSITIVE_RE = re.compile(r"(?i)(token|authorization|cookie|password|secret|bearer)")
IMAGE_TYPES = {
    b"\xff\xd8\xff": "JPEG",
    b"\x89PNG\r\n\x1a\n": "PNG",
    b"GIF87a": "GIF",
    b"GIF89a": "GIF",
}


def _norm(path):
    return str(path).replace("\\", "/")


def _is_file(path):
    try:
        return os.path.isfile(path)
    except (OSError, TypeError):
        return False


def _read_bytes(path, limit=50_000_000):
    if not _is_file(path):
        return b""
    try:
        with open(path, "rb") as handle:
            return handle.read(limit + 1)[:limit]
    except OSError as ex:
        logfunc(f"BeReal: unable to read {path}: {ex}")
        return b""


def _read_text(path):
    raw = _read_bytes(path)
    for encoding in ("utf-8", "utf-8-sig", "utf-16", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return ""


def _decode_body(raw):
    candidates = [raw]
    for decoder in (gzip.decompress, zlib.decompress):
        try:
            candidates.append(decoder(raw))
        except (OSError, zlib.error, EOFError):
            pass
    try:
        candidates.append(zlib.decompress(raw, -zlib.MAX_WBITS))
    except zlib.error:
        pass
    for candidate in candidates:
        for encoding in ("utf-8", "utf-8-sig"):
            try:
                return candidate.decode(encoding)
            except UnicodeDecodeError:
                continue
    return ""


def _json(text):
    try:
        return json.loads(text) if text and text.strip() else None
    except (ValueError, json.JSONDecodeError):
        return None


def _walk(value, path=""):
    if isinstance(value, dict):
        yield path, value
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else str(key)
            yield from _walk(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_path = f"{path}[{index}]" if path else f"[{index}]"
            yield from _walk(child, child_path)


def _first(obj, *keys):
    if not isinstance(obj, dict):
        return None
    for key in keys:
        value = obj.get(key)
        if value not in (None, "", [], {}):
            return value
    return None


def _nested(obj, *paths):
    for dotted in paths:
        current = obj
        for part in dotted.split("."):
            if not isinstance(current, dict) or part not in current:
                current = None
                break
            current = current[part]
        if current not in (None, "", [], {}):
            return current
    return None


def _timestamp(value):
    if value in (None, ""):
        return ""
    if isinstance(value, str):
        text = value.strip()
        try:
            value = float(text)
        except ValueError:
            try:
                parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
                return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
            except ValueError:
                return text
    if isinstance(value, (int, float)):
        number = float(value)
        if abs(number) > 100_000_000_000:
            number /= 1000
        if abs(number) < 100_000_000:
            return str(value)
        try:
            return datetime.fromtimestamp(number, tz=timezone.utc)
        except (OSError, OverflowError, ValueError):
            return str(value)
    return str(value)


def _disk_cache_parts(files_found):
    pairs = {}
    for path in files_found:
        if not _is_file(path):
            continue
        match = re.match(r"^(.+)\.(0|1)$", Path(path).name)
        if match:
            key, part = match.groups()
            pairs.setdefault((str(Path(path).parent), key), {})[part] = path
    return pairs


def _parse_metadata(path):
    text = _read_text(path)
    result = {"url": "", "method": "", "status": ""}
    for line in text.splitlines():
        stripped = line.strip().rstrip("\r")
        if not result["url"] and stripped.lower().startswith(("http://", "https://")):
            result["url"] = stripped
        elif stripped.upper() in {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD"}:
            result["method"] = stripped.upper()
        elif stripped.startswith("HTTP/"):
            result["status"] = stripped
    if not result["url"]:
        urls = URL_RE.findall(text)
        if urls:
            result["url"] = urls[0]
    return result


def _json_sources(files_found):
    consumed = set()
    for _, parts in _disk_cache_parts(files_found).items():
        body = parts.get("1")
        if not body:
            continue
        parsed = _json(_decode_body(_read_bytes(body)))
        if parsed is None:
            continue
        meta = _parse_metadata(parts.get("0")) if parts.get("0") else {"url": "", "method": "", "status": ""}
        sources = [path for path in (parts.get("0"), body) if path]
        consumed.update(sources)
        yield parsed, meta, sources
    for path in files_found:
        if path in consumed or not _is_file(path):
            continue
        if not _norm(path).lower().endswith((".json", ".txt")):
            continue
        parsed = _json(_read_text(path))
        if parsed is not None:
            yield parsed, {"url": "", "method": "", "status": ""}, [path]


def _user(obj):
    if not isinstance(obj, dict):
        return {}
    for key in ("user", "author", "owner", "creator", "profile", "friend", "sender"):
        if isinstance(obj.get(key), dict):
            return obj[key]
    # Only treat the object itself as a user record when it carries a field that is
    # distinctively user-shaped. Without this check, any dict with a bare "id" (a post,
    # a moment stub, etc.) gets misread as a user, because "id" alone also satisfies the
    # user-id lookup below. Confirmed against a real /friends-v1 capture where post and
    # moment objects were otherwise leaking into the friends list this way.
    user_markers = {"username", "userName", "userId", "user_id", "profilePicture",
                     "profile_picture", "avatar", "avatarUrl", "handle"}
    if set(obj) & user_markers:
        return obj
    return {}


def _user_fields(obj):
    user = _user(obj)
    uid = _first(user, "userId", "user_id", "uid", "id") or ""
    username = _first(user, "username", "userName", "handle") or ""
    fullname = _first(user, "fullname", "fullName", "displayName", "name") or ""
    picture = _first(user, "profilePicture", "profile_picture", "profilePictureUrl", "avatar", "avatarUrl") or ""
    if isinstance(picture, dict):
        picture = _first(picture, "url", "src", "uri") or ""
    return uid, username, fullname, picture


def _preference_identifiers(files_found):
    values = []
    for path in files_found:
        normalized = _norm(path).lower()
        if not (_is_file(path) and "/shared_prefs/" in normalized and normalized.endswith(".xml")):
            continue
        try:
            root = ElementTree.fromstring(_read_text(path))
        except ElementTree.ParseError:
            continue
        for child in root:
            key = child.attrib.get("name", "")
            value = child.attrib.get("value", child.text or "")
            if not SENSITIVE_RE.search(key) and re.search(r"(?i)(current.*user|user.*id|account.*id|username)", key):
                values.append((key, str(value), path))
    return values


def _image_type(path):
    raw = _read_bytes(path, 32)
    for magic, label in IMAGE_TYPES.items():
        if raw.startswith(magic):
            return label
    if len(raw) >= 12 and raw[:4] == b"RIFF" and raw[8:12] == b"WEBP":
        return "WebP"
    if len(raw) >= 12 and raw[4:8] == b"ftyp":
        return "Video"
    return ""


def _media_index(files_found):
    by_url, entries = {}, []
    for _, parts in _disk_cache_parts(files_found).items():
        body = parts.get("1")
        if not body:
            continue
        media_type = _image_type(body)
        if not media_type:
            continue
        meta = _parse_metadata(parts.get("0")) if parts.get("0") else {"url": ""}
        url = meta.get("url", "")
        entry = {"url": url, "media": body, "metadata": parts.get("0"), "type": media_type}
        entries.append(entry)
        if url:
            by_url[url] = body
    return by_url, entries


def _media_ref(path, label):
    if not path or not _is_file(path):
        return ""
    try:
        return check_in_media(path, name=label) or ""
    except OSError as ex:
        logfunc(f"BeReal: unable to check in media {path}: {ex}")
        return ""


def _source_path(paths):
    unique = []
    for path in paths:
        if path and _is_file(path) and path not in unique:
            unique.append(path)
    return "\n".join(unique)


def _dedupe(rows):
    output, seen = [], set()
    for row in rows:
        key = tuple(str(value) for value in row)
        if key not in seen:
            seen.add(key)
            output.append(row)
    return output


def _current_user_evidence(path, obj, meta, preference_ids):
    context = f"{path} {meta.get('url', '')}".lower()
    explicit_flag = _first(obj, "isCurrentUser", "isMe", "me") is True
    endpoint = any(marker in context for marker in ("/me", "/users/me", "currentuser", "current_user", "myprofile", "my_profile"))
    uid, username, _, _ = _user_fields(obj)
    preference_match = any(value and value in {str(uid), str(username)} for _, value, _ in preference_ids)
    if explicit_flag and endpoint:
        return "Explicit current-user flag and current-user endpoint/context", "High"
    if endpoint and preference_match:
        return "Current-user endpoint/context corroborated by persisted account identifier", "High"
    if explicit_flag and preference_match:
        return "Explicit current-user flag corroborated by persisted account identifier", "High"
    if endpoint:
        return "Current-user endpoint/context only", "Medium"
    if explicit_flag:
        return "Explicit current-user flag only", "Medium"
    if preference_match:
        return "Persisted account identifier (shared_prefs) matches cached profile only; no current-user endpoint or flag observed", "Low"
    return "", ""


def _accepted_friend_evidence(path, obj, meta):
    context = f"{path} {meta.get('url', '')}".lower()
    # Confirmed from the BeReal client (com.bereal.ft) API surface: accepted friends are
    # served from /friends-v1 (and /friends-v1/read); pending requests and suggestions are
    # served from distinct endpoints (/friend-requests/received, /friend-requests/sent,
    # /friends-of-friends) and must never be reported as accepted friends.
    if any(word in context for word in (
        "friend-requests", "friends-of-friends", "suggest", "recommend", "request",
        "invitation", "search", "follower", "blocked",
    )):
        return ""
    status_value = _first(obj, "status", "relationship", "friendshipStatus", "state")
    if isinstance(status_value, dict):
        status_value = _first(status_value, "status", "type", "state")
    status = str(status_value or "").lower()
    if status in {"accepted", "friend", "friends", "connected"}:
        return f"Relationship status: {status}"
    if _first(obj, "isFriend", "areFriends", "is_friend") is True:
        return "Explicit accepted-friend flag"
    return ""


# Confirmed against the BeReal Android client (com.bereal.ft, reverse-engineered from
# base.apk's kotlinx.serialization DTOs). The canonical post/moment object keys its
# identifier as plain "id" (not "postId"/"momentId"), its media as "primaryContent" /
# "secondaryContent" / "btsContent" (behind-the-scenes video), and embeds "comments" and
# "realMojis" directly as nested arrays rather than referencing the post by ID from a
# separate record. Two structural wrappers reliably establish authorship without any
# heuristic guessing:
#   - {"myPosts": [...], "friendsPosts": [...]}  -> myPosts entries are the device user's
#     own posts; friendsPosts entries belong to friends.
#   - {"user": {...}, "posts": [...], "momentId": ..., "region": ...} -> every post in
#     "posts" was authored by the sibling "user" object (the friends-feed shape).
# Older/alternate DTO variants (Li7/c, Le7/r1) use flatter field names
# (primaryUrl/secondaryUrl, isMyPost, isFriend); these are kept as fallbacks.


def _looks_like_post(obj):
    if not isinstance(obj, dict):
        return False
    keys = {str(key) for key in obj}
    has_id = bool(keys & {"id", "postId", "post_id", "momentId", "moment_id"})
    has_media = bool(keys & {
        "primaryContent", "secondaryContent", "btsContent", "primaryImage", "secondaryImage",
        "primaryUrl", "secondaryUrl", "frontCamera", "backCamera", "primary", "secondary", "btsMedia",
    })
    has_time = bool(keys & {"takenAt", "taken_at", "takenAtMs", "captureDate", "postedAt", "posted_at"})
    return has_id and (has_media or has_time)


def _post_fields(obj, author_hint=None, ownership=""):
    post_id = _first(obj, "id", "postId", "post_id", "momentId", "moment_id") or ""
    caption = _first(obj, "caption", "text") or ""
    captured = _timestamp(_first(obj, "takenAt", "takenAtMs", "taken_at", "captureDate", "createdAt", "created_at"))
    posted = _timestamp(_first(obj, "postedAt", "posted_at", "publishedAt", "updatedAt"))
    front = (
        _nested(obj, "primaryContent.url", "primaryContent.uri", "primaryImage.url", "primaryImage.uri",
                "frontCamera.url", "frontCamera.mediaUrl", "primary.url", "primary.mediaUrl")
        or _first(obj, "primaryUrl", "frontCameraUrl", "frontUrl") or ""
    )
    back = (
        _nested(obj, "secondaryContent.url", "secondaryContent.uri", "secondaryImage.url", "secondaryImage.uri",
                "backCamera.url", "backCamera.mediaUrl", "secondary.url", "secondary.mediaUrl")
        or _first(obj, "secondaryUrl", "backCameraUrl", "backUrl") or ""
    )
    # btsContent ("behind the scenes") is BeReal's short video clip captured alongside the
    # photo pair; it is the actual source of the video shown for a post.
    video = (
        _nested(obj, "btsContent.url", "btsContent.uri", "btsMedia.url", "btsMedia.uri", "video.url", "video.mediaUrl")
        or _first(obj, "videoUrl", "videoURL") or ""
    )
    if ownership == "device_user":
        author, author_basis = "Device User", "Nested in myPosts"
    elif isinstance(author_hint, dict) and (author_hint.get("id") or author_hint.get("userId") or author_hint.get("username")):
        uid, username, fullname, _ = _user_fields(author_hint)
        author, author_basis = (username or fullname or uid), "Sibling user of posts[] wrapper"
    else:
        direct_username = _first(obj, "userName", "username")
        if direct_username:
            author, author_basis = direct_username, "Username field embedded directly on post object"
        elif _first(obj, "isMyPost") is True:
            author, author_basis = "Device User", "Explicit isMyPost flag"
        elif ownership == "friend":
            author, author_basis = "", "Friend post (specific identity not present in this record)"
        else:
            author, author_basis = "", ""
    return post_id, caption, captured, posted, author, author_basis, front, back, video


def _iter_posts(files_found):
    """Yields (post_obj, author_hint, ownership, meta, sources) for every recoverable post,
    preferring structural extraction (myPosts/friendsPosts, {user, posts} wrappers) over
    generic pattern matching so authorship is derived from schema, not guesswork."""
    for parsed, meta, sources in _json_sources(files_found):
        captured_ids = set()
        # "myPosts"/"userPosts" hold the device user's own moment; confirmed from a live
        # /api/feeds/friends-v1 capture that the own-post wrapper is a single object keyed
        # "userPosts" (not a list, and not "myPosts" -- that key name only appears in one
        # alternate DTO). Both spellings, and both dict/list shapes, are handled.
        for _, obj in _walk(parsed):
            if not isinstance(obj, dict):
                continue
            for own_key in ("myPosts", "userPosts"):
                own_wrapper = obj.get(own_key)
                own_wrappers = own_wrapper if isinstance(own_wrapper, list) else ([own_wrapper] if isinstance(own_wrapper, dict) else [])
                for wrapper in own_wrappers:
                    if not isinstance(wrapper, dict):
                        continue
                    # Either a bare post, or a {user, posts:[...]} wrapper around own posts.
                    candidate_posts = wrapper.get("posts") if isinstance(wrapper.get("posts"), list) else [wrapper]
                    for post in candidate_posts:
                        if isinstance(post, dict) and _looks_like_post(post):
                            captured_ids.add(id(post))
                            yield post, None, "device_user", meta, sources
        for _, obj in _walk(parsed):
            if not isinstance(obj, dict):
                continue
            friends_posts = obj.get("friendsPosts")
            if isinstance(friends_posts, list):
                for entry in friends_posts:
                    if not isinstance(entry, dict):
                        continue
                    # friendsPosts may be a flat list of post objects, or a list of
                    # {user, posts:[...]} wrappers (confirmed shape from a live capture).
                    if isinstance(entry.get("posts"), list) and isinstance(entry.get("user"), dict):
                        wrapper_user = entry["user"]
                        for post in entry["posts"]:
                            if isinstance(post, dict) and _looks_like_post(post):
                                captured_ids.add(id(post))
                                yield post, wrapper_user, "friend", meta, sources
                    elif _looks_like_post(entry):
                        captured_ids.add(id(entry))
                        yield entry, None, "friend", meta, sources
            posts_list = obj.get("posts")
            if isinstance(posts_list, list) and posts_list and isinstance(obj.get("user"), dict) and id(obj) not in captured_ids:
                wrapper_user = obj["user"]
                for post in posts_list:
                    if isinstance(post, dict) and _looks_like_post(post) and id(post) not in captured_ids:
                        captured_ids.add(id(post))
                        yield post, wrapper_user, "friend", meta, sources
        for path, obj in _walk(parsed):
            if not isinstance(obj, dict) or id(obj) in captured_ids:
                continue
            if isinstance(obj.get("posts"), list):
                continue  # this is a wrapper object, not a post itself
            if re.search(r"\.(comments|realMojis)\[", path):
                continue  # embedded comment/reaction objects, not posts
            if not _looks_like_post(obj):
                continue
            keys = {str(key) for key in obj}
            has_media = bool(keys & {
                "primaryContent", "secondaryContent", "btsContent", "primaryImage", "secondaryImage",
                "primaryUrl", "secondaryUrl", "frontCamera", "backCamera", "primary", "secondary", "btsMedia",
            })
            if not has_media:
                continue  # a bare id + timestamp is too weak a signal (comments/realMojis share it)
            context = f"{path} {meta.get('url', '')}".lower()
            schema_hit = bool(keys & {"retakeCounter", "isLate", "primaryContent", "primaryImage", "btsContent"})
            if any(term in context for term in ("post", "moment", "timeline", "feed")) or schema_hit:
                yield obj, None, "", meta, sources


# Correlates a device user's own post to its locally recorded BTS clip in
# */files/bereal_my_user_temp_video/*. That video is captured locally and never round-trips
# through the network cache, so a by_url lookup on the remote btsMedia URL will never find
# it. Filenames embed a capture-time epoch-millis timestamp (BtsVideo<ms>.mp4 /
# compressed_BtsVideo<ms>.mp4 / BtsVideo<ms>_trimmed.mp4); the closest one to the post's
# takenAt, within a tolerance window, is used. Confirmed against a real extraction:
# BtsVideo1722006708445.mp4's embedded timestamp landed within 3 seconds of its post's
# takenAt.
_BTS_FILENAME_RE = re.compile(r"BtsVideo(\d{10,13})", re.I)


def _own_bts_video_index(files_found):
    entries = []
    for path in files_found:
        normalized = _norm(path).lower()
        if "bereal_my_user_temp_video" not in normalized or not _is_file(path):
            continue
        match = _BTS_FILENAME_RE.search(Path(path).name)
        if match:
            entries.append((int(match.group(1)), path))
    return entries


def _closest_own_bts_video(bts_index, captured_at, tolerance_ms=120_000):
    if not bts_index or not isinstance(captured_at, datetime):
        return ""
    target_ms = captured_at.timestamp() * 1000
    best_path, best_delta = "", None
    for ts, path in bts_index:
        delta = abs(ts - target_ms)
        if delta <= tolerance_ms and (best_delta is None or delta < best_delta):
            best_path, best_delta = path, delta
    return best_path


def _comment_fields(obj):
    comment_id = _first(obj, "id", "commentId", "comment_id") or ""
    text = _first(obj, "content", "text", "body", "comment")
    created = _timestamp(_first(obj, "postedAt", "createdAt", "creationDate", "created_at", "date"))
    return comment_id, text, created


def _realmoji_fields(obj):
    realmoji_id = _first(obj, "id") or ""
    reaction = _first(obj, "emoji", "type", "reactionType", "realmoji") or ""
    media_url = _first(obj, "media", "mediaUrl", "mediaURL", "url", "picture") or ""
    if isinstance(media_url, dict):
        media_url = _first(media_url, "url", "uri", "src") or ""
    created = _timestamp(_first(obj, "postedAt", "createdAt", "created_at", "date"))
    is_instant = _first(obj, "isInstant") is True
    return realmoji_id, reaction, media_url, created, is_instant


@artifact_processor
def bereal_device_user(context):
    files_found = context.get_files_found()
    preferences = _preference_identifiers(files_found)
    by_url, _ = _media_index(files_found)
    rows, used, candidates = [], [], []
    for parsed, meta, sources in _json_sources(files_found):
        for path, obj in _walk(parsed):
            if not isinstance(obj, dict):
                continue
            uid, username, fullname, picture = _user_fields(obj)
            if not (uid or username):
                continue
            basis, confidence = _current_user_evidence(path, obj, meta, preferences)
            if not basis:
                continue
            local_picture = by_url.get(picture, "")
            rank = {"High": 3, "Medium": 2, "Low": 1}.get(confidence, 0)
            candidates.append((rank, uid, username, fullname, picture, local_picture, basis, confidence, meta.get("url", ""), sources))
    if candidates:
        candidates.sort(key=lambda row: row[0], reverse=True)
        best = candidates[0]
        _, uid, username, fullname, picture, local_picture, basis, confidence, endpoint, sources = best
        media = _media_ref(local_picture, f"BeReal authenticated user {username or uid}")
        rows.append((uid, username, fullname, picture, media, endpoint, basis, confidence))
        used.extend(sources)
        used.append(local_picture)
    headers = ("User ID", "Username", "Full Name", "Profile Picture URL", ("Profile Picture", "media"), "Source Endpoint", "Identification Evidence", "Confidence")
    return headers, rows, _source_path(used)


@artifact_processor
def bereal_friends(context):
    files_found = context.get_files_found()
    by_url, _ = _media_index(files_found)
    rows, used = [], []
    for parsed, meta, sources in _json_sources(files_found):
        for path, obj in _walk(parsed):
            if not isinstance(obj, dict):
                continue
            evidence = _accepted_friend_evidence(path, obj, meta)
            if not evidence:
                continue
            uid, username, fullname, picture = _user_fields(obj)
            if not (uid or username):
                continue
            local = by_url.get(picture, "")
            media = _media_ref(local, f"BeReal friend {username or uid}")
            rows.append((uid, username, fullname, evidence, picture, media, meta.get("url", "")))
            used.extend(sources)
            used.append(local)
    headers = ("Friend ID", "Username", "Full Name", "Relationship Evidence", "Profile Picture URL", ("Profile Picture", "media"), "Source Endpoint")
    return headers, _dedupe(rows), _source_path(used)


@artifact_processor
def bereal_posts(context):
    files_found = context.get_files_found()
    by_url, _ = _media_index(files_found)
    bts_index = _own_bts_video_index(files_found)
    rows, used = [], []
    for obj, author_hint, ownership, meta, sources in _iter_posts(files_found):
        post_id, caption, captured, posted, author, author_basis, front_url, back_url, video_url = _post_fields(
            obj, author_hint, ownership
        )
        front_local, back_local, video_local = by_url.get(front_url, ""), by_url.get(back_url, ""), by_url.get(video_url, "")
        video_note = ""
        if ownership == "device_user" and not video_local:
            local_bts = _closest_own_bts_video(bts_index, captured)
            if local_bts:
                video_local = local_bts
                video_note = " (recovered locally, not the CDN copy)"
        rows.append((captured, posted, post_id, author, author_basis, caption,
                     front_url, _media_ref(front_local, f"BeReal post {post_id} front"),
                     back_url, _media_ref(back_local, f"BeReal post {post_id} rear"),
                     video_url, _media_ref(video_local, f"BeReal post {post_id} video (behind-the-scenes){video_note}"),
                     meta.get("url", "")))
        used.extend(sources)
        used.extend((front_local, back_local, video_local))
    headers = (("Captured", "datetime"), ("Posted/Updated", "datetime"), "Post ID", "Author", "Authorship Basis", "Caption",
               "Front Camera URL", ("Front Camera Media", "media"),
               "Rear Camera URL", ("Rear Camera Media", "media"),
               "Video (BTS) URL", ("Video", "media"), "Source Endpoint")
    return headers, _dedupe(rows), _source_path(used)


@artifact_processor
def bereal_profile_pictures(context):
    files_found = context.get_files_found()
    _, entries = _media_index(files_found)
    profiles = {}
    for parsed, meta, _ in _json_sources(files_found):
        # Confirmed against a live capture: BeReal's friend-search (/api/search/profile)
        # and contact-recommendation (/api/recommendations/contacts) endpoints cache full
        # profile pictures for every candidate match, not just people the user actually
        # interacted with (e.g. searching "This" pulled six unrelated strangers). Those
        # aren't a validated user action, so they're excluded here the same way they're
        # excluded from the friends artifact.
        endpoint = (meta.get("url", "") or "").lower()
        if any(term in endpoint for term in ("search", "recommend", "suggest", "friends-of-friends")):
            continue
        for _, obj in _walk(parsed):
            uid, username, fullname, picture = _user_fields(obj)
            if picture and (uid or username):
                profiles[picture] = (uid, username, fullname)
    rows, used = [], []
    for entry in entries:
        url = entry["url"]
        if not url or url not in profiles:
            continue
        normalized = _norm(entry["media"]).lower()
        if "profile_picture_friends_cache" not in normalized and not any(term in url.lower() for term in ("profile", "avatar")):
            continue
        uid, username, fullname = profiles[url]
        media = _media_ref(entry["media"], f"BeReal profile picture {username or uid}")
        rows.append((uid, username, fullname, url, entry["type"], media))
        used.extend((entry["metadata"], entry["media"]))
    headers = ("User ID", "Username", "Full Name", "Metadata URL", "Detected Type", ("Profile Picture", "media"))
    return headers, _dedupe(rows), _source_path(used)


def _iter_comment_groups(files_found):
    """Yields (post_id, comment_obj, meta, sources) from standalone {postId, comments:[...]}
    endpoint responses (e.g. /comments), separate from comments embedded on a post object."""
    for parsed, meta, sources in _json_sources(files_found):
        for _, obj in _walk(parsed):
            if not isinstance(obj, dict) or not isinstance(obj.get("comments"), list):
                continue
            if _looks_like_post(obj):
                continue  # embedded case is handled by walking posts directly
            post_id = _first(obj, "postId", "post_id", "id") or ""
            if not post_id:
                continue
            for comment in obj["comments"]:
                if isinstance(comment, dict):
                    yield post_id, comment, meta, sources


@artifact_processor
def bereal_comments(context):
    files_found = context.get_files_found()
    by_url, _ = _media_index(files_found)
    rows, used = [], []
    # Comments embedded directly on a recovered post (BeReal's normal shape: the post
    # object's own "comments" array).
    for obj, _, _, meta, sources in _iter_posts(files_found):
        post_id = _first(obj, "id", "postId", "post_id", "momentId", "moment_id") or ""
        comments = obj.get("comments")
        if not isinstance(comments, list):
            continue
        for comment in comments:
            if not isinstance(comment, dict):
                continue
            comment_id, text, created = _comment_fields(comment)
            if not isinstance(text, str) or not text.strip():
                continue
            uid, username, _, picture = _user_fields(comment)
            local = by_url.get(picture, "")
            media = _media_ref(local, f"BeReal commenter {username or uid}")
            rows.append((created, comment_id, post_id, username or uid, text, picture, media, meta.get("url", "")))
            used.extend(sources)
            used.append(local)
    # Comments returned by a standalone endpoint response ({postId, comments: [...]}).
    for post_id, comment, meta, sources in _iter_comment_groups(files_found):
        comment_id, text, created = _comment_fields(comment)
        if not isinstance(text, str) or not text.strip():
            continue
        uid, username, _, picture = _user_fields(comment)
        local = by_url.get(picture, "")
        media = _media_ref(local, f"BeReal commenter {username or uid}")
        rows.append((created, comment_id, post_id, username or uid, text, picture, media, meta.get("url", "")))
        used.extend(sources)
        used.append(local)
    headers = (("Created", "datetime"), "Comment ID", "Post ID", "Author", "Comment",
               "Author Profile Picture URL", ("Author Profile Picture", "media"), "Source Endpoint")
    return headers, _dedupe(rows), _source_path(used)


@artifact_processor
def bereal_realmojis(context):
    files_found = context.get_files_found()
    by_url, _ = _media_index(files_found)
    rows, used = [], []
    # RealMojis are embedded directly on the post object's own "realMojis" array.
    for obj, _, _, meta, sources in _iter_posts(files_found):
        post_id = _first(obj, "id", "postId", "post_id", "momentId", "moment_id") or ""
        reactions = obj.get("realMojis")
        if not isinstance(reactions, list):
            continue
        for reaction_obj in reactions:
            if not isinstance(reaction_obj, dict):
                continue
            _, reaction, media_url, created, is_instant = _realmoji_fields(reaction_obj)
            if not (reaction or media_url):
                continue
            uid, username, _, author_picture = _user_fields(reaction_obj)
            local = by_url.get(media_url, "")
            media = _media_ref(local, f"BeReal RealMoji {reaction or post_id}")
            author_local = by_url.get(author_picture, "")
            author_media = _media_ref(author_local, f"BeReal reactor {username or uid}")
            rows.append((created, post_id, username or uid, reaction, "Instant" if is_instant else "Standard",
                         media_url, media, author_picture, author_media, meta.get("url", "")))
            used.extend(sources)
            used.extend((local, author_local))
    headers = (("Created", "datetime"), "Post ID", "Author", "Reaction", "RealMoji Type",
               "Reaction Media URL", ("RealMoji Media", "media"),
               "Author Profile Picture URL", ("Author Profile Picture", "media"), "Source Endpoint")
    return headers, _dedupe(rows), _source_path(used)
