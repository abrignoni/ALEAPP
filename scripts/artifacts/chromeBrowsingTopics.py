__artifacts_v2__ = {
    "chromeBrowsingTopics": {
        "name": "Browsing Topics API Usage",
        "description": "Rows of the browsing_topics_api_usages table from the BrowsingTopicsSiteData "
                       "database of Chromium based browsers on Android: the last usage time, the "
                       "context domain named by the database's own lookup table, and the main frame "
                       "host recovered by recomputing its stored hash over host names found in the "
                       "same profile's History and Cookies databases.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Chromium",
        "notes": "Reads the browsing_topics_api_usages table of each BrowsingTopicsSiteData database in "
                 "an app_chrome/Default profile folder; one row per table row. Chromium source is cited "
                 "at tag 130.0.6723.0 (commit ed44bc873f9ef776a2ef1ccb90252a6de5666cd6). The writer "
                 "inserts or replaces one row per context domain and main frame host pair (primary key at "
                 "https://chromium.googlesource.com/chromium/src/+/ed44bc873f9ef776a2ef1ccb90252a6de5666cd6/content/browser/browsing_topics/browsing_topics_site_data_storage.cc#312) and binds "
                 "the time with BindTime "
                 "(https://chromium.googlesource.com/chromium/src/+/ed44bc873f9ef776a2ef1ccb90252a6de5666cd6/content/browser/browsing_topics/browsing_topics_site_data_storage.cc#186); Last "
                 "Usage Time is last_usage_time read as microseconds since 1601-01-01 UTC, the same "
                 "reading Omnibox Shortcuts uses for its Last Access Time column, which Chromium also "
                 "binds with BindTime, and across the tested images the "
                 "values decode to dates from 2024 to 2026. Context Domain is the context_domain the "
                 "database's own browsing_topics_api_hashed_to_unhashed_domain table gives for the row's "
                 "hashed_context_domain; that hash is keyed with a per-profile secret "
                 "(https://chromium.googlesource.com/chromium/src/+/ed44bc873f9ef776a2ef1ccb90252a6de5666cd6/components/browsing_topics/util.cc#119), so this artifact does not recompute it; "
                 "Chromium keeps that key in the profile's BrowsingTopicsState file, which this "
                 "artifact does not read. Where the "
                 "lookup table has no entry the stored hash is shown in Context Domain Hash (as stored). "
                 "Every tested row had an entry, so Context Domain Hash (as stored) was empty on every "
                 "tested row. The main frame host is stored only as the first eight bytes of SHA-256 over "
                 "the prefix TopicsV1_MainFrameHostStorage| and the host, read as a 64-bit integer, with "
                 "no secret (https://chromium.googlesource.com/chromium/src/+/ed44bc873f9ef776a2ef1ccb90252a6de5666cd6/components/browsing_topics/util.cc#125). Main Frame Host is a host name "
                 "whose recomputed hash equals the stored value: host names are taken from the url "
                 "column of the same profile's History database and then from the host_key column of "
                 "its Cookies database with any leading dot removed, and Host Matched In names the database that supplied the name. "
                 "The match names the host the Topics record was written for; the History or Cookies "
                 "row it came from is not itself evidence of that visit. Where neither database holds a "
                 "matching host, Main Frame Host is blank and the stored value remains in Main Frame Host "
                 "Hash (as stored). On the tested images 228 of the 248 rows resolved, 140 through "
                 "History and 88 through Cookies; the 20 that did not are all on kevin_pocox7_a15. "
                 "Every tested row came from com.android.chrome under Android user 0, so Browser Package "
                 "and Android User each held one value on every tested image. A constructed tree with "
                 "one profile's three databases under data/data and data/user/0, another's under "
                 "data/user/10, and a BrowsingTopicsSiteData copy in a Profile 1 folder returned the "
                 "first profile's rows once and the second's separately, each resolved only against "
                 "its own History and Cookies with the same counts as its own image, and nothing from "
                 "Profile 1. Not read: profiles other than Default, the History and Cookies of another "
                 "profile or user, and other databases that hold host names.",
        "paths": ('*/app_chrome/Default/BrowsingTopicsSiteData*', '*/app_chrome/Default/History*',
                  '*/app_chrome/Default/Cookies*'),
        "output_types": "standard",
        "artifact_icon": "globe",
        "sample_data": {
            "adams_ss135dl_a13": "Android 13 | 7 rows",
            "anne_a15": "Android 15 | 44 rows",
            "cookbook_a11": "Android 11 | 9 rows",
            "falken_a326u_a13": "Android 13 | 5 rows",
            "hc_pixel8pro_a16": "Android 16 | 1 row",
            "hc_pixel8pro_a17": "Android 17 | 1 row",
            "kevin_pocox7_a15": "Android 15 | 158 rows",
            "pixel7a_a14": "Android 14 | 0 rows (browsing_topics_api_usages empty)",
            "russell_a14": "Android 14 | 13 rows",
            "s20fe_a13": "Android 13 | 2 rows",
            "samsunga53_a14": "Android 14 | 5 rows",
            "sharon_a14": "Android 14 | 3 rows",
        },
    }
}

import hashlib
import os
import re
import sqlite3
import urllib.parse

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly
from scripts.artifacts.storagePathViews import canonical_path, user_files
from scripts.artifacts.chrome import _webkit_to_utc

# Chromium components/browsing_topics/util.cc at tag 130.0.6723.0: the main frame host is
# stored as the first eight bytes of SHA-256 over this prefix and the host, read as int64.
_MAIN_FRAME_PREFIX = 'TopicsV1_MainFrameHostStorage|'


def _host_hash(host):
    digest = hashlib.sha256((_MAIN_FRAME_PREFIX + host).encode('utf-8')).digest()
    return int.from_bytes(digest[:8], 'little', signed=True)


def _sibling(context, path, name):
    """The file called name in the same profile folder as path, matched on the storage view
    independent key so a sibling kept under another spelling of the folder is still found."""
    folder = os.path.dirname(str(context.get_relative_path(path))).replace('\\', '/')
    wanted = canonical_path(f'{folder}/{name}')[0]
    for found in context.get_files_found():
        if canonical_path(str(context.get_relative_path(str(found))).replace('\\', '/'))[0] == wanted:
            return str(found)
    return ''


def _hosts(path, sql, is_url):
    hosts = set()
    if not path:
        return hosts
    db = open_sqlite_db_readonly(path)
    if db is None:
        return hosts
    try:
        for (value,) in db.execute(sql):
            if not value or not isinstance(value, str):
                continue
            if is_url:
                try:
                    value = urllib.parse.urlsplit(value).hostname
                except ValueError:
                    value = None
            else:
                value = value.lstrip('.')
            if value:
                hosts.add(value)
    except sqlite3.Error as ex:
        logfunc(f'Browsing Topics API Usage: could not read hosts from {path}: {ex}')
    finally:
        db.close()
    return hosts


def _package(context, path):
    segments = re.split(r'[\\/]', str(context.get_relative_path(path)))
    if 'app_chrome' in segments:
        index = segments.index('app_chrome')
        if index > 0:
            return segments[index - 1]
    return ''


@artifact_processor
def chromeBrowsingTopics(context):
    data_list = []
    sources = []
    for path, user in user_files(context, 'BrowsingTopicsSiteData'):
        db = open_sqlite_db_readonly(path)
        if db is None:
            continue
        try:
            rows = db.execute('''
                SELECT u.last_usage_time, d.context_domain, u.hashed_context_domain,
                       u.hashed_main_frame_host
                FROM browsing_topics_api_usages u
                LEFT JOIN browsing_topics_api_hashed_to_unhashed_domain d
                       ON d.hashed_context_domain = u.hashed_context_domain
                ORDER BY u.last_usage_time, u.hashed_context_domain''').fetchall()
        except sqlite3.Error as ex:
            logfunc(f'Browsing Topics API Usage: could not read {context.get_relative_path(path)}: {ex}')
            continue
        finally:
            db.close()
        sources.append(path)
        lookups = []
        history = _sibling(context, path, 'History')
        if history:
            sources.append(history)
            lookups.append(('History', {_host_hash(h): h for h in
                                        _hosts(history, 'SELECT url FROM urls', True)}))
        cookies = _sibling(context, path, 'Cookies')
        if cookies:
            sources.append(cookies)
            lookups.append(('Cookies', {_host_hash(h): h for h in
                                        _hosts(cookies, 'SELECT host_key FROM cookies', False)}))
        package = _package(context, path)
        for last_usage, context_domain, hashed_domain, hashed_host in rows:
            host, matched_in = '', ''
            for label, table in lookups:
                if hashed_host in table:
                    host, matched_in = table[hashed_host], label
                    break
            data_list.append((_webkit_to_utc(last_usage),
                              context_domain if context_domain else '',
                              host, matched_in, hashed_host,
                              '' if context_domain else hashed_domain,
                              package, user))

    data_headers = (('Last Usage Time', 'datetime'), 'Context Domain', 'Main Frame Host',
                    'Host Matched In', 'Main Frame Host Hash (as stored)',
                    'Context Domain Hash (as stored)', 'Browser Package', 'Android User')
    return data_headers, data_list, '\n'.join(sources)
