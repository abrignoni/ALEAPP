import datetime
import os
import re
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import abxread, artifact_processor, check_in_media, checkabx, logfunc

__artifacts_v2__ = {
    "wallpapers": {
        "name": "Wallpapers",
        "description": "The wp and kwp wallpaper entries (home screen and lock screen in AOSP) recorded in "
                       "each Android user's wallpaper_info.xml, with the wallpaper image files of that user "
                       "folder, their modified times, the wallpaper ID, component, bind source and backup flag.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-23",
        "requirements": "none",
        "category": "Device Information",
        "notes": "One row per wp or kwp element of each wallpaper_info.xml under system/users/<n>; Android User is n. In AOSP (android-15.0.0_r1) WallpaperDataParser writes the system (home) wallpaper as wp and the lock screen wallpaper as kwp, the second only when a separate lock wallpaper exists (written at https://github.com/aosp-mirror/platform_frameworks_base/blob/4e43ad12e1b211f15152e9c5b16b0fe88e6b93f3/services/core/java/com/android/server/wallpaper/WallpaperDataParser.java#L436-L442; read back at L178-L183). With no kwp entry AOSP loads wp for both screens (L248), so a Home (wp) row with no Lock (kwp) row for the same user covers both screens there. The meaning of wp and kwp on Samsung builds was not sourced. It writes with Xml.resolveSerializer (L433), which emits binary XML when its ENABLE_BINARY_DEFAULT flag is set (https://github.com/aosp-mirror/platform_frameworks_base/blob/4e43ad12e1b211f15152e9c5b16b0fe88e6b93f3/core/java/android/util/Xml.java#L74-L79). Both forms are read: 22 binary and 5 text files on the tested images. The image files are named in WallpaperUtils.java (https://github.com/aosp-mirror/platform_frameworks_base/blob/4e43ad12e1b211f15152e9c5b16b0fe88e6b93f3/services/core/java/com/android/server/wallpaper/WallpaperUtils.java#L27-L30): wallpaper_orig and wallpaper for wp, wallpaper_lock_orig and wallpaper_lock for kwp. Original Image is the first of each pair and Cropped Image the second, both from the same user folder, shown as media. For a kwp row with neither file, the same names under wallpaper_lock_images/ are used: that folder is not named in the three AOSP files cited here and was found on all 10 Samsung images tested and no other. On s20fe_a13 and cookbook_a11 it held the lock images, byte-identical to the home images; on 6 others it held one file named wallpaper_first, which is not read, and on 2 it was empty. Image Files lists the files used. Cropped Image Modified (UTC) and Original Image Modified (UTC) are the UTC modified times the tool read from the input for those files. They are file times, not times stored in the XML. For a folder input they are the times of the copies on the examiner's disk. When the tool reads no UTC time for a file, its UTC column is blank and Cropped Image Modified (no zone, as stored) or Original Image Modified (no zone, as stored) shows the date and time the input holds, with no zone conversion. A recorded time of 0 is treated as no time. A file's two columns are blank when the input holds neither. That is the case for a FAT directory entry, an exFAT directory entry (its stored UTC offset is not applied or shown here) and a zip entry from which no UTC modification time is read, for example one with only its DOS date and time, or with an extra field whose modification time is missing, 0 or unreadable. Which zone such a reading is in is not established. A zip entry's DOS date and time is shown as decoded, with no validity check, so an unset one reads 1980-00-00 00:00:00. Cropped Image Modified (no zone, as stored) and Original Image Modified (no zone, as stored) had no value on any row of the registered images in sample_data on a run of 2026-11-23. The reading was exercised on constructed FAT32, exFAT and DOS-only zip inputs under two examiner time zones. The UTC columns were blank, the no-zone columns showed the value decoded separately from the input for each file, and they did not change with the zone. Cropped Image Modified (UTC) and Original Image Modified (UTC) were identical on 12 of the 13 rows that had images and one second apart on the other. Wallpaper ID is id as stored; AOSP assigns it from a counter the source describes as incremented every time anything sets a wallpaper (https://github.com/aosp-mirror/platform_frameworks_base/blob/4e43ad12e1b211f15152e9c5b16b0fe88e6b93f3/services/core/java/com/android/server/wallpaper/WallpaperUtils.java#L43-L46 and L56-L60). Component is component as stored, written in android-15.0.0_r1 only when a component is set and is not the platform's image wallpaper (WallpaperDataParser.java#L565-L569), so in that source a blank Component is an image wallpaper or no component. Other versions and vendors were not sourced. On hc_pixel8pro_a16 and hc_pixel8pro_a17 the wp element held a child element named description with its own component and id, which is not read. Bind Source is bindSource as stored, written in android-15.0.0_r1 (WallpaperDataParser.java#L527) from the BindSource names in WallpaperData.java (https://github.com/aosp-mirror/platform_frameworks_base/blob/4e43ad12e1b211f15152e9c5b16b0fe88e6b93f3/services/core/java/com/android/server/wallpaper/WallpaperData.java#L142-L157); on the tested images it was present only on Android 14 to 17. Name is name as stored. Backup is backup as stored, written in android-15.0.0_r1 only when true (WallpaperDataParser.java#L571-L573). Known data emu_a15_wallpaper_known_20261116 (Android 15 emulator, three synthetic images set in the Google wallpaper app: home, lock, then a second home): 2 rows; the two image files of each row had the same pixels as the image set last for that screen, their modified times, whole seconds, were 0.5 s and 1.1 s before the tap times recorded on the host, the first home image matched none of the four wallpaper image files, and the ids were 4 (lock) and 5 (home). On the tested images: 39 rows on 23 images (20 device images and 3 emulator images; some are the same device at two OS versions). 13 rows on 9 images had both image files; the other 26 rows had neither file in their user folder. Name held an empty string on all 39 rows. Component held a value on 1 row (a second user on pixel3_a11). Bind Source had no value on 26 rows; the values seen were UNKNOWN (9), SET_STATIC (3) and PACKAGE_UPDATE_FINISHED (1). Not read: on the Samsung images, wallpaper_colors_info/ (home_phone.xml, lock_phone.xml, lock_sub.xml), wallpaper_backup_info.xml, wallpaper_status and wallpaper_first; wallpaper_thumbs/ (1 image); wallpaper_info.xml.fallback (1 image, identical to wallpaper_info.xml there); the description child element (2 images); and every attribute other than id, component, bindSource, name and backup, which on the Samsung images included lastCallingPackage, uri, type, history and the video attributes.",
        "paths": ('*/system/users/*/wallpaper*',),
        "output_types": "standard",
        "artifact_icon": "image",
        "sample_data": {
            "emu_a15_wallpaper_known_20261116": "Android 15 | 2 rows (known data; home and lock images)",
            "cookbook_a11": "Android 11 | 2 rows (images; lock under wallpaper_lock_images)",
            "hickman_a13": "Android 13 | 1 row (images)",
            "kevin_pocox7_a15": "Android 15 | 2 rows (lock images)",
            "pixel3_a11": "Android 11 | 2 rows (user 0 images; user 10 has a Component)",
            "pixel3_a12": "Android 12 | 1 row (images)",
            "russell_a14": "Android 14 | 2 rows (images, users 0 and 10)",
            "russell_pixel6a_a13": "Android 13 | 2 rows (user 10 images)",
            "s20fe_a13": "Android 13 | 2 rows (images; lock under wallpaper_lock_images)",
            "samsunga53_a14": "Android 14 | 2 rows (no image files read)",
            "pixel7a_a14": "Android 14 | 1 row (no image files)",
            "galaxys10_a10": "Android 10 | 2 rows (no image files)",
        },
    }
}

# WallpaperUtils.java: original and cropped image files per screen
_FILES = {'wp': ('wallpaper', 'wallpaper_orig'), 'kwp': ('wallpaper_lock', 'wallpaper_lock_orig')}
_SCREENS = {'wp': 'Home (wp)', 'kwp': 'Lock (kwp)'}
_USER_DIR = re.compile(r'/system/users/(\d+)/')
_VENDOR_LOCK_DIR = 'wallpaper_lock_images/'


def _root(path):
    '''The entries of wallpaper_info.xml: Android binary XML or text, one or two root elements.'''
    if checkabx(path):
        try:
            return list(abxread(path, True).getroot())
        except Exception as ex:  # pylint: disable=broad-except
            logfunc(f'Wallpapers: could not read {path} as binary XML: {ex}')
            return None
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as handle:
            text = handle.read()
        text = re.sub(r'<\?xml[^>]*\?>', '', text)
        return list(ET.fromstring(f'<root>{text}</root>'))
    except (OSError, ET.ParseError) as ex:
        logfunc(f'Wallpapers: could not read {path}: {ex}')
        return None


def _sec_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(seconds=value // 1)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _usable(value):
    """Whether a recorded time is a nonzero, finite number."""
    return isinstance(value, (int, float)) and value != 0 and value == value and abs(value) != float('inf')


def _file_times(seeker, path):
    """(UTC seconds, reading with no zone) the input records for a staged file.

    The staged copy's own time is not used: for a FAT, exFAT or DOS-only zip reading it is
    that reading placed in the examiner's time zone.
    """
    infos = getattr(seeker, 'file_infos', None) or {}
    windows = str(path).replace('/', '\\')
    bare = windows.removeprefix('\\\\?\\')
    info = next((infos[name] for name in (str(path), windows, bare, '\\\\?\\' + bare)
                 if name in infos), None)
    times = getattr(info, 'times', None)
    modified = getattr(times, 'modified', None)
    if _usable(modified):
        return modified, ''
    # a reading with no zone comes before the older field, which is never read as its UTC time
    reading = getattr(times, 'modified_no_zone', None)
    if reading:
        return None, reading
    modified = getattr(info, 'modification_date', None)
    if _usable(modified):
        return modified, ''
    return None, ''


def _modified(seeker, path):
    """(UTC modification time or None, reading with no zone or '') for a staged file."""
    if not path:
        return None, ''
    recorded, no_zone = _file_times(seeker, path)
    return _sec_to_utc(recorded) or None, no_zone


@artifact_processor
def wallpapers(context):
    files_found = context.get_files_found()
    try:
        seeker = context.get_seeker()
    except ValueError:
        seeker = None
    folders = {}
    for path in sorted(files_found):
        norm = path.replace(os.sep, '/')
        match = _USER_DIR.search(norm)
        if not match or not os.path.isfile(path):
            continue
        folder = norm[:match.end()]
        folders.setdefault(folder, {'user': int(match.group(1)), 'files': {}})
        folders[folder]['files'][norm[match.end():]] = path

    data_list = []
    sources = []
    for folder in sorted(folders):
        user = folders[folder]['user']
        files = folders[folder]['files']
        info_path = files.get('wallpaper_info.xml')
        if not info_path:
            continue
        entries = _root(info_path)
        sources.append(info_path)
        if entries is None:
            continue
        for entry in entries:
            if entry.tag not in _FILES:
                continue
            crop_name, orig_name = _FILES[entry.tag]
            if entry.tag == 'kwp' and crop_name not in files and orig_name not in files:
                # a folder some Samsung images keep their lock screen images in
                crop_name, orig_name = (_VENDOR_LOCK_DIR + crop_name, _VENDOR_LOCK_DIR + orig_name)
            crop_path, orig_path = files.get(crop_name), files.get(orig_name)
            crop_ref = check_in_media(crop_path, os.path.basename(crop_name)) if crop_path else None
            orig_ref = check_in_media(orig_path, os.path.basename(orig_name)) if orig_path else None
            for path in (crop_path, orig_path):
                if path:
                    sources.append(path)
            crop_modified, crop_no_zone = _modified(seeker, crop_path)
            orig_modified, orig_no_zone = _modified(seeker, orig_path)
            data_list.append((
                crop_modified,
                orig_modified,
                crop_no_zone,
                orig_no_zone,
                user,
                _SCREENS[entry.tag],
                crop_ref,
                orig_ref,
                entry.get('id', ''),
                entry.get('component', ''),
                entry.get('bindSource', ''),
                entry.get('name', ''),
                entry.get('backup', ''),
                ', '.join(n for n, p in ((crop_name, crop_path), (orig_name, orig_path)) if p),
            ))

    data_headers = (('Cropped Image Modified (UTC)', 'datetime'), ('Original Image Modified (UTC)', 'datetime'),
                    'Cropped Image Modified (no zone, as stored)', 'Original Image Modified (no zone, as stored)',
                    'Android User', 'Screen', ('Cropped Image', 'media'), ('Original Image', 'media'),
                    'Wallpaper ID', 'Component', 'Bind Source', 'Name', 'Backup', 'Image Files')
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))
