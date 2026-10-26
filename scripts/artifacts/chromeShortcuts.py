__artifacts_v2__ = {
    "chromeShortcuts": {
        "name": "Omnibox Shortcuts",
        "description": "Rows of the omni_box_shortcuts table from the Shortcuts database of Chromium "
                       "based browsers on Android (packages with an app_chrome/Default profile): the "
                       "stored input text, the URL and suggestion text stored with it, the match type "
                       "and transition, the hit count and the last access time.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Chromium",
        "notes": "Reads the omni_box_shortcuts table of each Shortcuts database in an app_chrome/Default "
                 "profile folder; one row per table row. Browser Package is the app folder that holds "
                 "app_chrome, and Android User is the user whose app data folder holds it (data/data "
                 "and userdata/data are user 0; data/user/N and data_mirror/data_ce/<volume>/N are "
                 "user N). The same database seen under data/data, data/user/0 and data_mirror is read "
                 "once. Chromium source is cited at commit 33f34ef179f55596f6c2fc8a55878b7ccf6276e4. "
                 "The writer binds each column in order, transition, type, keyword, last_access_time "
                 "and number_of_hits included "
                 "(https://chromium.googlesource.com/chromium/src/+/33f34ef179f55596f6c2fc8a55878b7ccf6276e4/components/omnibox/browser/shortcuts_database.cc#36). "
                 "Last Access Time is last_access_time, bound with BindTime and read as microseconds "
                 "since 1601-01-01 UTC, the same reading as DLEAPP's Chromium Omnibox Shortcuts; on "
                 "every tested image the values decode to years 2024 to 2026. Match Type is the type "
                 "column, an AutocompleteMatchType value, shown as stored with the name the enum gives "
                 "it; the header says these values are stored in ShortcutsDatabase and cannot be "
                 "renumbered "
                 "(https://chromium.googlesource.com/chromium/src/+/33f34ef179f55596f6c2fc8a55878b7ccf6276e4/components/omnibox/browser/autocomplete_match_type.h#16). "
                 "Transition is the transition column, a ui::PageTransition value: the name is that of "
                 "its low byte, the core value, and any higher qualifier bits are shown in hex "
                 "(https://chromium.googlesource.com/chromium/src/+/33f34ef179f55596f6c2fc8a55878b7ccf6276e4/ui/base/page_transition_types.h#40). "
                 "On the tested images only two pairs occur: 7 (SEARCH_HISTORY) with 5 (GENERATED) on "
                 "42 rows and 1 (HISTORY_URL) with 1 (TYPED) on 4 rows; no qualifier bits were set. "
                 "Match Type and Transition each held one value on every row of anne_a15 and "
                 "samsungs20_a13, which carry only the first pair. Input Text, Fill Into Edit, URL, "
                 "Contents, Description and Keyword are the text, fill_into_edit, url, contents, "
                 "description and keyword columns as stored, and Hits is number_of_hits as stored. "
                 "Keyword was blank on 4 of the 46 tested rows. Not reported: document_type, which "
                 "held 0 on every tested row, and contents_class and description_class. Tested on "
                 "Chrome (com.android.chrome), Brave "
                 "(com.brave.browser) and Edge (com.microsoft.emmx), including a Brave profile under "
                 "Android user 150; a constructed tree with the Chrome store under data/data, "
                 "data/user/0 and data/user/10 and a decoy Shortcuts file outside app_chrome returned "
                 "the first copy once, the user 10 copy separately, and nothing from the decoy. Not "
                 "read: Shortcuts files in profiles other than Default, Samsung Internet "
                 "(app_sbrowser), Opera (app_opera) and Android System WebView (app_webview) folders, "
                 "none of which held a Shortcuts database on the tested images.",
        "paths": ('*/app_chrome/Default/Shortcuts*',),
        "output_types": "standard",
        "artifact_icon": "search",
        "sample_data": {
            "adams_ss135dl_a13": "Android 13 | 1 row",
            "anne_a15": "Android 15 | 19 rows",
            "hc_pixel8pro_a17": "Android 17 | 1 row",
            "kevin_pocox7_a15": "Android 15 | 2 rows",
            "pixel7a_a14": "Android 14 | 0 rows (Chrome, Brave and Edge tables empty)",
            "russell_a14": "Android 14 | 2 rows",
            "s20fe_a13": "Android 13 | 2 rows",
            "samsunga53_a14": "Android 14 | 1 row",
            "samsungs20_a13": "Android 13 | 11 rows",
            "sharon_a14": "Android 14 | 3 rows",
            "userb2_a13": "Android 13 | 4 rows",
        },
    }
}

import os
import re
import sqlite3

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly
from scripts.artifacts.storagePathViews import user_files
from scripts.artifacts.chrome import _webkit_to_utc

# Chromium at 33f34ef179f55596f6c2fc8a55878b7ccf6276e4.
# ui/base/page_transition_types.h: the core transition is the low byte of the stored value.
_TRANSITIONS = {
    0: 'LINK', 1: 'TYPED', 2: 'AUTO_BOOKMARK', 3: 'AUTO_SUBFRAME', 4: 'MANUAL_SUBFRAME',
    5: 'GENERATED', 6: 'AUTO_TOPLEVEL', 7: 'FORM_SUBMIT', 8: 'RELOAD', 9: 'KEYWORD',
    10: 'KEYWORD_GENERATED',
}
# components/omnibox/browser/autocomplete_match_type.h
_MATCH_TYPES = {
    0: 'URL_WHAT_YOU_TYPED', 1: 'HISTORY_URL', 2: 'HISTORY_TITLE', 3: 'HISTORY_BODY',
    4: 'HISTORY_KEYWORD', 5: 'NAVSUGGEST', 6: 'SEARCH_WHAT_YOU_TYPED', 7: 'SEARCH_HISTORY',
    8: 'SEARCH_SUGGEST', 9: 'SEARCH_SUGGEST_ENTITY', 10: 'SEARCH_SUGGEST_TAIL',
    11: 'SEARCH_SUGGEST_PERSONALIZED', 12: 'SEARCH_SUGGEST_PROFILE', 13: 'SEARCH_OTHER_ENGINE',
    14: 'EXTENSION_APP_DEPRECATED', 15: 'CONTACT_DEPRECATED', 16: 'BOOKMARK_TITLE',
    17: 'NAVSUGGEST_PERSONALIZED', 18: 'CALCULATOR', 19: 'CLIPBOARD_URL', 20: 'VOICE_SUGGEST',
    21: 'PHYSICAL_WEB_DEPRECATED', 22: 'PHYSICAL_WEB_OVERFLOW_DEPRECATED',
    23: 'TAB_SEARCH_DEPRECATED', 24: 'DOCUMENT_SUGGESTION', 25: 'PEDAL', 26: 'CLIPBOARD_TEXT',
    27: 'CLIPBOARD_IMAGE', 28: 'TILE_SUGGESTION', 29: 'TILE_NAVSUGGEST', 30: 'OPEN_TAB',
    31: 'HISTORY_CLUSTER', 32: 'NULL_RESULT_MESSAGE', 33: 'STARTER_PACK',
    34: 'TILE_MOST_VISITED_SITE', 35: 'TILE_REPEATABLE_QUERY', 36: 'HISTORY_EMBEDDINGS',
    37: 'FEATURED_ENTERPRISE_SEARCH', 38: 'HISTORY_EMBEDDINGS_ANSWER', 39: 'TAB_GROUP',
    40: 'CROSS_DEVICE_TAB',
}


def _named(value, names):
    """The stored integer with the enum name the cited source gives it."""
    if not isinstance(value, int):
        return value
    name = names.get(value)
    return f'{value} ({name})' if name else str(value)


def _transition(value):
    if not isinstance(value, int):
        return value
    core = value & 0xFF
    text = _named(core, _TRANSITIONS)
    if value != core:
        text += f', qualifiers 0x{value & ~0xFF:08X}'
    return text


def _package(context, path):
    """The app package directory above app_chrome, read from the evidence relative path."""
    segments = re.split(r'[\\/]', str(context.get_relative_path(path)))
    if 'app_chrome' in segments:
        index = segments.index('app_chrome')
        if index > 0:
            return segments[index - 1]
    return ''


@artifact_processor
def chromeShortcuts(context):
    data_list = []
    sources = []
    for path, user in user_files(context, 'Shortcuts'):
        if os.path.basename(os.path.dirname(path)) != 'Default':
            continue
        db = open_sqlite_db_readonly(path)
        if db is None:
            continue
        try:
            rows = db.execute('''
                SELECT last_access_time, text, type, transition, url, fill_into_edit, contents,
                       description, keyword, number_of_hits
                FROM omni_box_shortcuts ORDER BY last_access_time, id''').fetchall()
        except sqlite3.Error as ex:
            logfunc(f'Omnibox Shortcuts: could not read {context.get_relative_path(path)}: {ex}')
            continue
        finally:
            db.close()
        sources.append(path)
        package = _package(context, path)
        for (last_access, text, match_type, transition, url, fill_into_edit, contents,
             description, keyword, hits) in rows:
            data_list.append((_webkit_to_utc(last_access), text, _named(match_type, _MATCH_TYPES),
                              _transition(transition), url, fill_into_edit, contents, description,
                              keyword, hits, package, user))

    data_headers = (('Last Access Time', 'datetime'), 'Input Text', 'Match Type', 'Transition',
                    'URL', 'Fill Into Edit', 'Contents', 'Description', 'Keyword', 'Hits',
                    'Browser Package', 'Android User')
    return data_headers, data_list, '\n'.join(sources)
