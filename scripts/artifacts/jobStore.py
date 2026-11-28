__artifacts_v2__ = {
    "job_scheduler_jobs": {
        "name": "Job Scheduler Persisted Jobs",
        "description": "Background jobs that apps scheduled with JobScheduler and asked to keep across "
                       "reboots, with the last successful and failed run times, the scheduled run window "
                       "and the extras the app attached.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-28",
        "last_update_date": "2026-11-28",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": (
            "Reads the JobScheduler store in system/job: jobs.xml, one file for all apps, and "
            "jobs_<uid>.xml, one file per app UID, which JobStore writes from Android 14 "
            "(JOB_FILE_SPLIT_PREFIX, "
            "https://android.googlesource.com/platform/frameworks/base/+/6e47c7075b91983ae501114425ea25e6df7690c8/apex/jobscheduler/service/java/com/android/server/job/JobStore.java#101 "
            "and #738). In the tested images jobs.xml held the jobs on the 7 Android 10 to 13 images "
            "and the per-UID files on the 3 Android 14 and 16 images. One row per job element. Only "
            "jobs the app marked as persisted are written (JobStore.java at android13-release, "
            "https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/apex/jobscheduler/service/java/com/android/server/job/JobStore.java#466), "
            "so a job an app did not ask to keep across reboots is not here, and the file holds the "
            "jobs scheduled when it was last written, not every job that ever ran.\nThe fields and "
            "their meanings are AOSP JobStore's (addAttributesToJobTag, writeConstraintsToXml, "
            "writeExecutionCriteriaToXml and writeBundleToXml, JobStore.java#537-652 at "
            "android13-release, and the same methods at android14-release, which add Namespace and "
            "Cumulative Execution Time). The writer was checked at the android10, 11, 12, 13, 14, 15 "
            "and 16 release branches. On all 10 tested images, Samsung ones included, every "
            "attribute and child element was one the AOSP writer writes.\nLast Successful Run is "
            "lastSuccessfulRunTime, the wall clock time JobSchedulerService records when it "
            "reschedules a periodic job after a run finished (getRescheduleJobForPeriodic, "
            "https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/apex/jobscheduler/service/java/com/android/server/job/JobSchedulerService.java#1934 "
            "and #1949). It was set only on periodic jobs: 1,306 of the 2,047 tested rows, none of "
            "them one-off. Last Failed Run is lastFailedRunTime, the wall clock time recorded when a "
            "job is rescheduled after a failure (getRescheduleJobForFailureLocked, "
            "https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/apex/jobscheduler/service/java/com/android/server/job/JobSchedulerService.java#1843), "
            "set on 134 rows. Both are Unix milliseconds rendered in UTC, and the platform writes 0 "
            "when the time was never recorded, shown as blank.\nEarliest Run and Deadline are the "
            "delay and deadline attributes. At write time JobStore converts the job's elapsed-time "
            "window to wall clock with the clock it had then, or writes the wall clock times it read "
            "at boot if it has not yet been able to convert them "
            "(https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/apex/jobscheduler/service/java/com/android/server/job/JobStore.java#639-652). "
            "They are blank when the job has no delay or no deadline.\nSource Package is "
            "sourcePackageName, the app the job runs for, or the package of the job service when the "
            "file names none. Job Service Package and Job Service Class name the service that runs "
            "the job; for account sync jobs that is android and "
            "com.android.server.content.SyncJobService. Source Tag was set only on those sync jobs, "
            "375 of 375 rows, and SyncManager builds it as provider/account type/account name "
            "(SyncOperation.wakeLockName, "
            "https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/services/core/java/com/android/server/content/SyncOperation.java#586-593, "
            "passed as the tag at "
            "https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/services/core/java/com/android/server/content/SyncManager.java#1691), "
            "so it names the sync authority and the account. Source User is sourceUserId, the "
            "Android user, as stored; it held one value on all rows of some images. UID and Job ID "
            "are as stored.\nSchedule is Periodic or One-off from the element the job carries; Period "
            "(ms) and Flex (ms) are the periodic job's interval and flex window. Constraints lists "
            "the constraint attributes present: network when a network requirement is written, then "
            "idle, charging, battery-not-low, storage-not-low and the Android 14 prefer- forms. The "
            "network capability and transport numbers are not decoded or shown.\nCumulative Execution "
            "Time (ms) is cumulativeExecutionTime, written from Android 14, the time the job has "
            "run, reset for periodic jobs after a successful run (JobStatus.java, "
            "https://android.googlesource.com/platform/frameworks/base/+/6e47c7075b91983ae501114425ea25e6df7690c8/apex/jobscheduler/service/java/com/android/server/job/controllers/JobStatus.java#408-412). "
            "It was blank on the Android 13 and earlier images and 0 on 510 of the 517 later rows. "
            "Namespace is written from Android 14 when the app set one.\nExtras is the "
            "PersistableBundle the app attached, one name = value line per entry in the element "
            "forms XmlUtils.writeValueXml writes, a nested bundle's names joined with a dot and an "
            "array's items in brackets "
            "(https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/core/java/com/android/internal/util/XmlUtils.java#830). "
            "The names and values are the app's own and their meaning is not established here. "
            "Android 14 work items (job-work-item) are added to Extras with a work item number; none "
            "of the tested images had one.\nNot shown: bias, priority, flags, internalFlags, back-off "
            "policy, the network capability numbers, the estimated byte counts and the Android 15 "
            "debug tags, which describe how the scheduler treats a job rather than what the app "
            "did.\nCopies of one file under storage-view spellings are reported once. A Source File "
            "column is added when jobs files are read from more than one job folder; a test tree "
            "with two copies of one image's folder and a third image's file gave each copy its own "
            "rows under its path."),
        "paths": ('*/system/job/jobs.xml', '*/system/job/jobs_*.xml'),
        "output_types": "standard",
        "artifact_icon": "clock",
        "multiline_columns": ["Extras"],
        "sample_data": {
            "cookbook_a11": "Android 11 | 259 rows",
            "galaxys10_a10": "Android 10 | 164 rows",
            "pixel3_a11": "Android 11 | 269 rows",
            "pixel3_a12": "Android 12 | 168 rows",
            "pixel7a_a14": "Android 14 | 209 rows from 38 per-UID files",
            "russell_pixel6a_a13": "Android 13 | 359 rows",
            "s20fe_a13": "Android 13 | 126 rows",
            "samsung_a166u_a16_known_20261116": "Android 16 | 137 rows from 29 per-UID files",
            "samsunga53_a14": "Android 14 | 171 rows from 34 per-UID files",
            "samsungs20_a13": "Android 13 | 185 rows",
        },
    },
}

import os
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

from scripts.artifacts.storagePathViews import union_view_rows, unique_files
from scripts.ilapfuncs import abxread, artifact_processor, checkabx, logfunc

_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
# The constraint attributes JobStore.writeConstraintsToXml writes, in the order it writes them.
CONSTRAINTS = ('idle', 'charging', 'battery-not-low', 'storage-not-low',
               'prefer-battery-not-low', 'prefer-charging', 'prefer-idle')
# A PersistableBundle nests at most 10 levels (JobStore.deepCopyBundle); a deeper element is
# reported by name only.
MAX_DEPTH = 10


def _ms_to_utc(value):
    """A UTC datetime from Unix milliseconds, or '' for an absent, zero or unreadable value."""
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    if value <= 0:
        return ''
    try:
        return _EPOCH + timedelta(milliseconds=value)
    except (OverflowError, ValueError):
        return ''


def _root(path):
    """The XML root of an ABX binary or a text XML file."""
    if checkabx(path):
        return abxread(path, False).getroot()
    return ET.parse(path).getroot()


def _bundle_lines(element, prefix='', depth=0):
    """name = value lines for the children of a PersistableBundle element, as
    XmlUtils.writeValueXml writes them: a string holds its value as text, a number or boolean
    in a value attribute, an array in item children and a nested bundle as pbundle_as_map."""
    lines = []
    for child in element:
        if not isinstance(child.tag, str):
            continue
        name = prefix + (child.get('name') or '')
        if child.tag == 'pbundle_as_map':
            if depth + 1 >= MAX_DEPTH:
                lines.append(f'{name} = (nested bundle not read)')
            else:
                lines.extend(_bundle_lines(child, name + '.', depth + 1))
        elif child.tag == 'string':
            lines.append(f'{name} = {child.text or ""}')
        elif child.tag == 'null':
            lines.append(f'{name} = null')
        elif child.tag.endswith('-array'):
            items = [item.get('value', '') for item in child if item.tag == 'item']
            lines.append(f'{name} = [{", ".join(items)}]')
        else:
            lines.append(f'{name} = {child.get("value", child.text or "")}')
    return lines


def _job_row(job):
    """The report row for one job element."""
    def attr(name):
        value = job.get(name)
        return '' if value is None else value

    periodic = job.find('periodic')
    one_off = job.find('one-off')
    timing = periodic if periodic is not None else one_off
    if periodic is not None:
        schedule = 'Periodic'
    elif one_off is not None:
        schedule = 'One-off'
    else:
        schedule = ''

    constraints = []
    element = job.find('constraints')
    if element is not None:
        if element.get('net-capabilities-csv') is not None or element.get('net-capabilities') is not None:
            constraints.append('network')
        constraints.extend(name for name in CONSTRAINTS if element.get(name) == 'true')

    extras = []
    element = job.find('extras')
    if element is not None:
        extras.extend(_bundle_lines(element))
    for number, item in enumerate(job.findall('job-work-item'), 1):
        for line in _bundle_lines(item):
            extras.append(f'work item {number}: {line}')

    return (
        _ms_to_utc(attr('lastSuccessfulRunTime')),
        _ms_to_utc(attr('lastFailedRunTime')),
        _ms_to_utc(timing.get('delay') if timing is not None else None),
        _ms_to_utc(timing.get('deadline') if timing is not None else None),
        attr('sourcePackageName') or attr('package'),
        attr('sourceUserId'),
        attr('uid'),
        attr('package'),
        attr('class'),
        attr('jobid'),
        attr('namespace'),
        attr('sourceTag'),
        schedule,
        periodic.get('period', '') if periodic is not None else '',
        periodic.get('flex', '') if periodic is not None else '',
        ', '.join(constraints),
        attr('cumulativeExecutionTime'),
        '\n'.join(extras),
    )


def _file_rows(path):
    """The rows of one jobs file; a job that cannot be read is logged and skipped."""
    try:
        root = _root(path)
    except Exception as error:  # pylint: disable=broad-except
        logfunc(f'Job Scheduler: could not read {os.path.basename(path)}: {error}')
        return None
    rows = []
    for job in root.iter('job'):
        try:
            rows.append(_job_row(job))
        except Exception as error:  # pylint: disable=broad-except
            logfunc(f'Job Scheduler: a job in {os.path.basename(path)} could not be read: {error}')
    return rows


@artifact_processor
def job_scheduler_jobs(context):
    data_headers = (
        ('Last Successful Run', 'datetime'),
        ('Last Failed Run', 'datetime'),
        ('Earliest Run', 'datetime'),
        ('Deadline', 'datetime'),
        'Source Package',
        'Source User',
        'UID',
        'Job Service Package',
        'Job Service Class',
        'Job ID',
        'Namespace',
        'Source Tag',
        'Schedule',
        'Period (ms)',
        'Flex (ms)',
        'Constraints',
        'Cumulative Execution Time (ms)',
        'Extras',
    )
    file_rows = []
    sources = []
    for path in unique_files(context, keep_differing_views=True):
        path = str(path)
        if os.path.isdir(path):
            continue
        name = os.path.basename(path)
        if name != 'jobs.xml' and not (name.startswith('jobs_') and name.endswith('.xml')):
            continue
        rows = _file_rows(path)
        if rows is None:
            continue
        relative = context.get_relative_path(path)
        sources.append(relative)
        file_rows.append((path, rows, relative))
    # A Source File column only when jobs files from more than one job folder are read.
    folders = {os.path.dirname(path) for path, _rows, _relative in file_rows}
    if len(folders) > 1:
        data_headers += ('Source File',)
        file_rows = [(path, [row + (relative,) for row in rows], relative)
                     for path, rows, relative in file_rows]
    data_list = union_view_rows(context, [(path, rows) for path, rows, _relative in file_rows],
                                ignore=(len(data_headers) - 1,) if len(folders) > 1 else ())
    return data_headers, data_list, '\n'.join(sources)
