__artifacts_v2__ = {
    "get_puma_users": {
        "name": "PumaUsers",
        "description": "Parses the users table of the Puma Trac database.",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}, @AlexisBrignoni, Codex",
        "creation_date": "2023-03-25",
        "last_update_date": "2026-10-06",
        "requirements": "Python 3.7 or higher",
        "category": "Puma-Trac",
        "notes": "Date of Birth is read as Unix milliseconds. Workout Duration (as stored) "
                 "retains preferences_workoutDuration, including zero and NULL. Workout "
                 "Duration / 60 (unit unverified) preserves the existing division and N/A "
                 "fallback; its unit is not established. An empty profile image URL is "
                 "shown as N/A. Every distinct main database state is read. Known canonical aliases collapse only when main/WAL/journal bytes agree; conflicts remain separate. Combined inputs carry per-row evidence sources.",
        "paths": ('*com.pumapumatrac/databases/pumatrac-db*',),
        "output_types": "standard",
        "artifact_icon": "user",
        "html_columns": ['Profile Image URL'],
    }
}

import datetime
import hashlib
import sqlite3
from pathlib import Path

from scripts.artifacts.storagePathViews import canonical_path

_EPOCH_UTC = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)

from scripts.html_safe import esc
from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly


def _puma_sources(context):
    """Collapse known aliases only when main and logical sidecar bytes agree."""
    paths = []
    seen = set()
    for candidate in context.get_files_found():
        path = str(candidate)
        if Path(path).name != 'pumatrac-db':
            continue
        try:
            state = []
            for suffix in ('', '-wal', '-journal'):
                try:
                    with open(path + suffix, 'rb') as source:
                        digest = hashlib.sha256()
                        for chunk in iter(lambda source=source: source.read(1024 * 1024), b''):
                            digest.update(chunk)
                    state.append(digest.hexdigest())
                except FileNotFoundError:
                    if not suffix:
                        raise
                    state.append(None)
            identity = (canonical_path(context.get_relative_path(path))[0], tuple(state))
        except OSError as error:
            logfunc(f'Puma: skipping unreadable database {context.get_relative_path(path)}: {error}')
            continue
        if identity not in seen:
            seen.add(identity)
            paths.append(path)
    return paths


@artifact_processor
def get_puma_users(context):
    source_paths = _puma_sources(context)
    multiple_sources = len(source_paths) > 1
    reported_sources = set()
    data_list = []
    for source_path in source_paths:
        db = open_sqlite_db_readonly(source_path)
        if db is None:
            logfunc(f'Puma: unavailable database {context.get_relative_path(source_path)}; continuing other sources')
            continue
        try:
            cursor = db.cursor()
            cursor.execute('''
                Select id, email, name, sex, dateOfBirth, weight, height, country, location, interestsIds,
                       profileImageUrl, totalScore, followingCount, followersCount, goal_id,
                       preferences_workoutTimeOfDay, preferences_workoutDuration
                from users
            ''')
            all_rows = cursor.fetchall()
        except sqlite3.Error as error:
            logfunc(f'Puma: query failed for {context.get_relative_path(source_path)}: {error}; continuing other sources')
            continue
        finally:
            db.close()
        logfunc(f"Found {len(all_rows)} entries in users")

        for row in all_rows:
            reported_sources.add(source_path)
            # Added to the epoch rather than passed to fromtimestamp: a date of birth can
            # predate 1970, where that function raises gmtime() errors on some platforms.
            dob = _EPOCH_UTC + datetime.timedelta(milliseconds=int(row[4])) if row[4] else ''
            work_time = row[16] / 60 if row[16] else 'N/A'
            # The avatar URL is remote, so an <img> here would make opening the report
            # fetch it and disclose the examination to the service. Report the URL as
            # escaped text instead; the evidence is preserved, nothing is fetched.
            image = esc(row[10]) if row[10] else 'N/A'
            data_list.append((row[0], row[1], row[2], row[3], dob, row[5], row[6], row[7], row[8], row[9], image, row[11], row[12], row[13], row[14], row[15], row[16], work_time))
            if multiple_sources:
                data_list[-1] += (context.get_relative_path(source_path),)

    data_headers = (('Date of Birth', 'datetime'), 'ID', 'Email', 'Name', 'Gender', 'Weight', 'Height', 'Country', 'Location', 'Interests', 'Profile Image URL', 'Total Score', 'Following Count', 'Followers Count', 'Goal', 'Workout Time of Day', 'Workout Duration (as stored)', 'Workout Duration / 60 (unit unverified)')
    data_list = [(row[4],) + row[:4] + row[5:] for row in data_list]
    if multiple_sources:
        data_headers += ('Source File',)
    return data_headers, data_list, '\n'.join(sorted(reported_sources))
