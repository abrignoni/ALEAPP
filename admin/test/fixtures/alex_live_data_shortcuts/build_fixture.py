#!/usr/bin/env python3
"""Builds a synthetic ALEX-style dumpsys file for the Dumpsys - Shortcuts artifacts.

Every value in the output is authored here. Nothing came off a device.

Format sources, read 2026-09-04:
  wrapper header/footer  frameworks/native/cmds/dumpsys/dumpsys.cpp
                         writeDumpHeader() / writeDumpFooter()
  ShortcutInfo body      frameworks/base/core/java/android/content/pm/ShortcutInfo.java
                         toDumpString() -> toStringInner(secure=false, includeInternalData=true)
  package framing        frameworks/base/services/core/java/com/android/server/pm/
                         ShortcutPackage.java dump()

The Discord payload inside intents= is shaped to match the regexes in
alex_live_data.shortcut_data(), since no ALEX extraction was available to read
the real shape from.
"""
import zipfile, os, datetime

RULE = "-" * 79
DEVICE_TS = 1756900000          # the unix stamp in the file name
DUMP_END = "2026-09-03 14:26:41"

def ms(dt_str):
    d = datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S").replace(
        tzinfo=datetime.timezone.utc)
    return int(d.timestamp() * 1000)

def shortcut(sid, flags, readable, pkg, activity, short_label, long_label,
             categories, persons, rank, timestamp, intents, extras,
             indent="      "):
    """One ShortcutInfo block in AOSP toStringInner(indent) order."""
    L = []
    L.append(f"{indent}ShortcutInfo {{id={sid}, flags=0x{flags:x} [{readable}]")
    L.append(f"{indent}packageName={pkg}")
    L.append(f"{indent}activity={activity}")
    L.append(f"{indent}shortLabel={short_label}, resId=0[null]")
    L.append(f"{indent}longLabel={long_label}, resId=0[null]")
    L.append(f"{indent}disabledMessage=null, resId=0[null]")
    L.append(f"{indent}disabledReason=[not disabled]")
    L.append(f"{indent}categories={categories}")
    L.append(f"{indent}persons={persons}")
    L.append(f"{indent}icon=null")
    L.append(f"{indent}rank={rank}, timestamp={timestamp}")
    L.append(f"{indent}intents={intents}")
    L.append(f"{indent}extras={extras}")
    L.append(f"{indent}iconRes=0[null], bitmapPath=null, iconUri=null}}")
    return "\n".join(L)

# ---------------------------------------------------------------- Discord rows
def discord_intent(channel, message, guild, username, uid, content=None,
                   body=None, iso_ts=None, scheduled=None):
    """Intent + persistable extras carrying a Discord conversation shortcut."""
    parts = [f"channel_id, {channel},", f"message_id, {message},",
             f"guild_id, {guild},"]
    if content is not None:
        parts.append(f"message_content, {content}, user_username, {username},")
    else:
        parts.append(f"body, {body}, icon, null,")
        parts.append(f"user_username, {username},")
    parts.append(f"user_id, {uid},")
    if iso_ts:
        parts.append(f'raw, {{"id":"{message}","timestamp":"{iso_ts}","pinned":false}},')
    if scheduled:
        parts.append(f"scheduled_at, {scheduled}, receiving_user_id, {uid},")
    payload = " ".join(parts)
    return ("[Intent { act=android.intent.action.VIEW "
            "cmp=com.discord/com.discord.chat.ChatActivity (has extras) }"
            f"/PersistableBundle[{{{payload}}}]]")

SHORTCUTS_DISCORD = [
    # 1. full message: message_content + an ISO timestamp in the raw blob
    shortcut(
        "known-dm-alpha", 0x811, "ImPinKey", "com.discord",
        "ComponentInfo{com.discord/com.discord.chat.ChatActivity}",
        "known_user_alpha", "known_user_alpha",
        "[]", "[Person{name=known_user_alpha, key=known-person-alpha}]",
        0, ms("2026-09-03 13:58:12"),
        discord_intent("100000000000000001", "200000000000000001",
                       "300000000000000001", "known_user_alpha",
                       "400000000000000001",
                       content="SYNTHETIC KNOWN MESSAGE ONE",
                       iso_ts="2026-09-03T13:58:12.401"),
        "PersistableBundle[{shortcut_type=dm}]"),
    # 2. body fallback (no message_content) + scheduled_at fallback (no raw ts)
    shortcut(
        "known-dm-bravo", 0x811, "ImPinKey", "com.discord",
        "ComponentInfo{com.discord/com.discord.chat.ChatActivity}",
        "known_user_bravo", "known_user_bravo",
        "[]", "[Person{name=known_user_bravo, key=known-person-bravo}]",
        1, ms("2026-09-03 12:40:05"),
        discord_intent("100000000000000002", "200000000000000002",
                       "300000000000000002", "known_user_bravo",
                       "400000000000000002",
                       body="SYNTHETIC KNOWN MESSAGE TWO",
                       scheduled="2026-09-03 12:40:05"),
        "PersistableBundle[{shortcut_type=dm}]"),
    # 3. group channel, message_content present, no user fields at all
    shortcut(
        "known-guild-charlie", 0x811, "ImPinKey", "com.discord",
        "ComponentInfo{com.discord/com.discord.chat.ChatActivity}",
        "#known-channel", "known-guild / #known-channel",
        "[]", "[]",
        2, ms("2026-09-02 21:15:33"),
        discord_intent("100000000000000003", "200000000000000003",
                       "300000000000000003", "known_user_charlie",
                       "400000000000000003",
                       content="SYNTHETIC KNOWN MESSAGE THREE",
                       iso_ts="2026-09-02T21:15:33.998"),
        "PersistableBundle[{shortcut_type=guild}]"),
    # 4. intents=null  <- the crash reported on this PR; must be skipped cleanly
    shortcut(
        "known-dm-delta", 0x811, "ImPinKey", "com.discord",
        "ComponentInfo{com.discord/com.discord.chat.ChatActivity}",
        "known_user_delta", "known_user_delta",
        "null", "null",
        3, ms("2026-09-01 08:02:44"),
        "null",
        "null"),
]

SHORTCUTS_OTHER = [
    shortcut(
        "known-camera-selfie", 0x1, "Man", "com.android.camera2",
        "ComponentInfo{com.android.camera2/com.android.camera.CameraLauncher}",
        "Selfie", "Take a selfie", "[]", "null",
        0, ms("2026-08-30 09:11:02"),
        "[Intent { act=android.media.action.IMAGE_CAPTURE "
        "cmp=com.android.camera2/com.android.camera.CameraLauncher }"
        "/PersistableBundle[{}]]",
        "null"),
    shortcut(
        "known-dialer-echo", 0x821, "ImPinKey", "com.android.dialer",
        "ComponentInfo{com.android.dialer/.main.impl.MainActivity}",
        "known_contact_echo", "Call known_contact_echo",
        "[]", "[Person{name=known_contact_echo, key=known-person-echo}]",
        0, ms("2026-08-29 17:44:19"),
        "[Intent { act=android.intent.action.CALL "
        "dat=tel:xxxxxxxxxxx cmp=com.android.dialer/.main.impl.MainActivity }"
        "/PersistableBundle[{}]]",
        "null"),
]

def package_block(pkg, uid, calls, last_reset_ms, shortcuts):
    out = [""]
    out.append(f"  Package: {pkg}  UID: {uid}")
    out.append(f"    Calls: {calls}")
    out.append("    Last known FG: 0")
    out.append(f"    Last reset: [{last_reset_ms}] "
               f"{datetime.datetime.fromtimestamp(last_reset_ms/1000, tz=datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}")
    out.append(f"    PackageInfo: version=1, lastUpdateTime={last_reset_ms}, shadow=false")
    out.append("")
    out.append("    Shortcuts:")
    out.extend(shortcuts)
    out.append("    Total bitmap size: 0 (0 B)")
    return "\n".join(out)

def shortcut_service_body():
    out = []
    out.append("Shortcut Manager State:")
    out.append("  Time: " + DUMP_END)
    out.append("  Raw last reset: [0] ")
    out.append("  Locale change sequence number: 3")
    out.append("")
    out.append("  Configuration:")
    out.append("    resetInterval: 86400000")
    out.append("    maxShortcutsPerActivity: 15")
    out.append("")
    out.append("  User: 0  Known locales: [en_US]  Last app scan: "
               f"[{DEVICE_TS*1000}]")
    out.append(package_block("com.discord", 10245, 6,
                             ms("2026-09-03 00:00:00"), SHORTCUTS_DISCORD))
    out.append(package_block("com.android.camera2", 10102, 1,
                             ms("2026-08-30 00:00:00"), [SHORTCUTS_OTHER[0]]))
    out.append(package_block("com.android.dialer", 10088, 2,
                             ms("2026-08-29 00:00:00"), [SHORTCUTS_OTHER[1]]))
    return "\n".join(out)

def service(name, body, duration="0.061"):
    return (f"{RULE}\nDUMP OF SERVICE {name}:\n{body}\n"
            f"--------- {duration}s was the duration of dumpsys {name}, "
            f"ending at: {DUMP_END}\n")

BANNER = (
    "SYNTHETIC KNOWN DATA. Authored 2026-09-04 for ALEAPP PR #1217.\n"
    "No part of this file came off a real device. Every id, name, label and\n"
    "message string below is invented. Structure follows AOSP dumpsys.cpp and\n"
    "ShortcutInfo.toDumpString().\n"
)

def build():
    # 1. populated file: has a shortcut section
    full = ""
    full += service("package", "Activity Resolver Table:\n  (elided)")
    full += service("shortcut", shortcut_service_body(), "0.184")
    full += service("battery", "Current Battery Service state:\n  AC powered: false")
    with open(f"dumpsys_{DEVICE_TS}.txt", "w", newline="\n") as f:
        f.write("# " + BANNER.replace("\n", "\n# ").rstrip("# ") + "\n")
        f.write(full)

    # 2. no-shortcut file: same shape, shortcut service absent
    none = ""
    none += service("package", "Activity Resolver Table:\n  (elided)")
    none += service("battery", "Current Battery Service state:\n  AC powered: false")
    os.makedirs("no_shortcut_repro", exist_ok=True)
    with open(f"no_shortcut_repro/dumpsys_{DEVICE_TS + 1}.txt", "w", newline="\n") as f:
        f.write("# " + BANNER.replace("\n", "\n# ").rstrip("# ") + "\n")
        f.write(none)

    # 3. the extraction zip make_test_data.py consumes
    with zipfile.ZipFile("alex_shortcut_synthetic_extraction.zip", "w",
                         zipfile.ZIP_DEFLATED) as z:
        z.write(f"dumpsys_{DEVICE_TS}.txt",
                f"ALEX_PRFS_synthetic/extra/dumpsys_{DEVICE_TS}.txt")
    # 4. the same extraction plus unrelated members. A single-file input cannot
    #    show what make_test_data.py does with a `paths` written as a bare
    #    string, because the one member it over-collects is the right one.
    with zipfile.ZipFile("with_decoys.zip", "w", zipfile.ZIP_DEFLATED) as z:
        z.write(f"dumpsys_{DEVICE_TS}.txt",
                f"ALEX_PRFS_synthetic/extra/dumpsys_{DEVICE_TS}.txt")
        for name in ("ALEX_PRFS_synthetic/extra/logcat.txt",
                     "ALEX_PRFS_synthetic/extra/app_ops.json",
                     "ALEX_PRFS_synthetic/data/data/com.example.decoy/decoy.db",
                     "ALEX_PRFS_synthetic/system/build.prop"):
            z.writestr(name, "synthetic decoy, not read by any artifact\n")

    print("wrote dumpsys_%d.txt" % DEVICE_TS)
    print("wrote no_shortcut_repro/dumpsys_%d.txt" % (DEVICE_TS + 1))
    print("wrote alex_shortcut_synthetic_extraction.zip")
    print("wrote with_decoys.zip")

if __name__ == "__main__":
    build()
