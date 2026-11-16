import datetime
import os
import re
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import abxread, artifact_processor, check_in_media, checkabx, logfunc

__artifacts_v2__ = {
    "wallpapers": {
        "name": "Wallpapers",
        "description": "The home screen and lock screen wallpapers recorded in each Android user's "
                       "wallpaper_info.xml, with the wallpaper image files of that user folder, their "
                       "modified times, the wallpaper ID, live wallpaper component, bind source and "
                       "backup flag.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Device Information",
        "notes": "One row per wp or kwp element of each wallpaper_info.xml under system/users/<n>; Android User is n. In AOSP (android-15.0.0_r1) WallpaperDataParser writes the system (home) wallpaper as wp and the lock screen wallpaper as kwp, the second only when a separate lock wallpaper exists (https://github.com/aosp-mirror/platform_frameworks_base/blob/4e43ad12e1b211f15152e9c5b16b0fe88e6b93f3/services/core/java/com/android/server/wallpaper/WallpaperDataParser.java#L436-L442), with Xml.resolveSerializer, which can write Android binary XML; both binary and text files are read. The image files are named in WallpaperUtils.java (https://github.com/aosp-mirror/platform_frameworks_base/blob/4e43ad12e1b211f15152e9c5b16b0fe88e6b93f3/services/core/java/com/android/server/wallpaper/WallpaperUtils.java#L27-L31): wallpaper_orig and wallpaper for wp, wallpaper_lock_orig and wallpaper_lock for kwp. Original Image is the first of each pair and Cropped Image the second, both from the same user folder, shown as media. For a kwp row with neither file, the same names under wallpaper_lock_images/ are used: that folder is not in the AOSP source and was found on 10 Samsung images; on s20fe_a13 and cookbook_a11 it held the lock images, byte-identical to the home images, and elsewhere a file named wallpaper_first, which is not read. Image Files lists the files used. Cropped Image Modified (UTC) and Original Image Modified (UTC) are the modified times the extraction recorded for those files, file system times, not times stored in the XML. Cropped Image Modified (UTC) and Original Image Modified (UTC) were identical on 14 of the 15 rows that had images on the tested images and one second apart on the other. Wallpaper ID is id as stored; the source describes it as incremented every time anything sets a wallpaper (https://github.com/aosp-mirror/platform_frameworks_base/blob/4e43ad12e1b211f15152e9c5b16b0fe88e6b93f3/services/core/java/com/android/server/wallpaper/WallpaperUtils.java#L43). Component is component as stored, written only for a wallpaper that is not the platform's image wallpaper (WallpaperDataParser.java#L564-L569), so a blank Component is an image wallpaper or a file that lacks the attribute. Bind Source is bindSource as stored, written by newer versions (WallpaperDataParser.java#L527) from the BindSource names in WallpaperData.java (https://github.com/aosp-mirror/platform_frameworks_base/blob/4e43ad12e1b211f15152e9c5b16b0fe88e6b93f3/services/core/java/com/android/server/wallpaper/WallpaperData.java#L142-L157). Name is name as stored. Backup is backup as stored, written only when true (WallpaperDataParser.java#L571-L573). Known data emu_a15_wallpaper_known_20261116 (Android 15 emulator, three synthetic images set in the Google wallpaper app: home, lock, then a second home): 2 rows; both images had the same pixels as the images set last for each screen, their modified times were within about a second of the taps in the mint record, the first home image was not in the folder, and the ids were 4 (lock) and 5 (home). On the tested images: 39 rows on 23 images (20 devices and 3 emulator keys). 13 rows on 9 images had both image files; the other 26 rows had neither file in their user folder. Name held an empty string on all 39 rows. Component held a value on 1 row (a second user on pixel3_a11). Bind Source had no value on 26 rows; the values seen were UNKNOWN (9), SET_STATIC (3) and PACKAGE_UPDATE_FINISHED (1). Not read: Samsung's home_phone.xml, lock_phone.xml, lock_sub.xml, wallpaper_backup_info.xml, wallpaper_status and wallpaper_first, and the crop, dim and color attributes.",
        "paths": ('*/system/users/*/wallpaper*',),
        "output_types": "standard",
        "artifact_icon": "image",
        "sample_data": {
            "emu_a15_wallpaper_known_20261116": "Android 15 | 2 rows (known data; home and lock images)",
            "cookbook_a11": "Android 11 | 2 rows (images; lock under wallpaper_lock_images)",
            "hickman_a13": "Android 13 | 1 row (images)",
            "kevin_pocox7_a15": "Android 15 | 2 rows (lock images)",
            "pixel3_a11": "Android 11 | 2 rows (images; user 10 live wallpaper)",
            "pixel3_a12": "Android 12 | 1 row (images)",
            "russell_a14": "Android 14 | 2 rows (images, users 0 and 10)",
            "russell_pixel6a_a13": "Android 13 | 2 rows (user 10 images)",
            "s20fe_a13": "Android 13 | 2 rows (images; lock under wallpaper_lock_images)",
            "samsunga53_a14": "Android 14 | 2 rows (no image files)",
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


def _modified(seeker, path):
    info = seeker.file_infos.get(path) if seeker else None
    if not info or not info.modification_date:
        return None
    try:
        return datetime.datetime.fromtimestamp(int(info.modification_date), datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return None


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
            data_list.append((
                _modified(seeker, crop_path) if crop_path else None,
                _modified(seeker, orig_path) if orig_path else None,
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
                    'Android User', 'Screen', ('Cropped Image', 'media'), ('Original Image', 'media'),
                    'Wallpaper ID', 'Component', 'Bind Source', 'Name', 'Backup', 'Image Files')
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))
