__artifacts_v2__ = {
    "job_scheduler_jobs": {
        "name": "Job Scheduler Persisted Jobs",
        "description": "Jobs scheduled with JobScheduler and marked persisted, which the platform keeps "
                       "across reboots, with the recorded last successful and failed run times, the "
                       "scheduled run window and the extras attached to the job.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-28",
        "last_update_date": "2026-11-28",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": (
            "Reads the JobScheduler store in system/job: jobs.xml, one file for all jobs, and "
            "jobs_<uid>.xml, one file per UID, which JobStore writes from Android 14 when its "
            "split-file setting is on (JOB_FILE_SPLIT_PREFIX, "
            "https://android.googlesource.com/platform/frameworks/base/+/6e47c7075b91983ae501114425ea25e6df7690c8/apex/jobscheduler/service/java/com/android/server/job/JobStore.java#101 "
            "and #734-738). In the tested images jobs.xml held the jobs on the 7 Android 10 to 13 "
            "images and the per-UID files on the 3 Android 14 and 16 images. One row per job "
            "element. Only jobs marked as persisted are written (JobStore.java at android13-release, "
            "https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/apex/jobscheduler/service/java/com/android/server/job/JobStore.java#466), "
            "so a job not marked persisted is not here, and the file holds the jobs scheduled when "
            "it was last written, not every job that ever ran.\nThe fields and their meanings are "
            "AOSP JobStore's (addAttributesToJobTag, writeConstraintsToXml, "
            "writeExecutionCriteriaToXml and writeBundleToXml, JobStore.java#537-668 at "
            "android13-release, and the same methods at android14-release, which add Namespace and "
            "Cumulative Execution Time). The attribute and element names the writer emits were read "
            "at the android10 to android16 release branch heads on 2026-11-28. On all 10 tested "
            "images, Samsung ones included, every attribute and child element was one the AOSP "
            "writer writes. On samsungs20_a13 the file was text XML in a layout the AOSP writer does "
            "not produce, as were that image's other system XML files; how the extraction came to "
            "hold it in that form was not established, and it is read as given.\nLast Successful Run "
            "is lastSuccessfulRunTime, the wall clock time JobSchedulerService at android13-release "
            "records when it reschedules a periodic job after a run (getRescheduleJobForPeriodic, "
            "https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/apex/jobscheduler/service/java/com/android/server/job/JobSchedulerService.java#1934 "
            "and #1949). It was set only on periodic jobs: 1,306 of the 2,047 tested rows, none of "
            "them one-off. Last Failed Run is lastFailedRunTime, the wall clock time recorded when a "
            "job is rescheduled after a failure (getRescheduleJobForFailureLocked, "
            "https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/apex/jobscheduler/service/java/com/android/server/job/JobSchedulerService.java#1843), "
            "set on 134 rows. Both are Unix milliseconds rendered in UTC, and the platform writes 0 "
            "when the time was never recorded, shown as blank. JobSchedulerService was read at "
            "android13-release only.\nEarliest Run and Deadline are the delay and deadline "
            "attributes. At write time JobStore converts the job's elapsed-time window to wall clock "
            "with the clock it had then, or writes the wall clock times it read at boot if it has "
            "not yet been able to convert them "
            "(https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/apex/jobscheduler/service/java/com/android/server/job/JobStore.java#639-652). "
            "They are blank when the job has no delay or no deadline.\nSource Package is "
            "sourcePackageName, which JobStatus describes as the app in which the job is hosted "
            "(https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/apex/jobscheduler/service/java/com/android/server/job/controllers/JobStatus.java#193-196), "
            "or the package of the job service when the file names none; no tested job lacked it. "
            "Job Service Package and Job Service Class name the service that runs the job; for "
            "account sync jobs that is android and com.android.server.content.SyncJobService, and "
            "only on those 375 rows did Source Package differ from Job Service Package. Source Tag "
            "was set only on those sync jobs, 375 of 375 rows. SyncManager passes "
            "SyncOperation.wakeLockName as the tag "
            "(https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/services/core/java/com/android/server/content/SyncManager.java#1691-1692). "
            "At android13-release and android14-release that is provider/account type/account name "
            "(https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/services/core/java/com/android/server/content/SyncOperation.java#586-593), "
            "and the 327 tags on the 9 Android 10 to 14 images have three parts, so they name the "
            "sync authority and the account. At android15-release it is provider/account type only "
            "(https://android.googlesource.com/platform/frameworks/base/+/cc8bb19595c661f5cf42f330457000e643c67d1b/services/core/java/com/android/server/content/SyncOperation.java#586-592), "
            "and the 48 tags on the Android 16 image have two parts, with no account name. Source "
            "User is sourceUserId, the Android user, as stored; it held one value on 6 of the 10 "
            "images. UID and Job ID are as stored.\nSchedule is Periodic or One-off from the element "
            "the job carries; Period (ms) and Flex (ms) are the periodic job's interval and flex "
            "window. Constraints lists the constraint attributes present: network when a network "
            "requirement is written, then idle, charging, battery-not-low, storage-not-low and the "
            "Android 14 prefer- forms; no tested job had a prefer- attribute. The network capability "
            "and transport numbers are not decoded or shown.\nCumulative Execution Time (ms) is "
            "cumulativeExecutionTime, written from Android 14, the time the job has run, reset for "
            "periodic jobs after a successful run (JobStatus.java, "
            "https://android.googlesource.com/platform/frameworks/base/+/6e47c7075b91983ae501114425ea25e6df7690c8/apex/jobscheduler/service/java/com/android/server/job/controllers/JobStatus.java#408-412). "
            "It was blank on the Android 13 and earlier images and 0 on 510 of the 517 later rows. "
            "Namespace is written from Android 14 when the job has one.\nExtras is the "
            "PersistableBundle attached to the job, one name = value line per entry in the element "
            "forms XmlUtils.writeValueXml writes, a nested bundle's names joined with a dot and an "
            "array's items in brackets "
            "(https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/core/java/com/android/internal/util/XmlUtils.java#830). "
            "The names and values are set by whoever scheduled the job and their meaning is not "
            "established here. A bundle nested more than 10 levels deep is shown as (nested bundle "
            "not read); none was. Android 14 work items (job-work-item) are read from the item's "
            "extras element and added to Extras with a work item number; this path is unexercised, "
            "as none of the tested images had one.\nNot shown: bias, priority, flags, internalFlags, "
            "the back-off policy and initial back-off, the network capability and transport numbers, "
            "the estimated and minimum network byte counts, the work item delivery count, and the "
            "Android 15 debug and trace tags.\nA Source File column is added when jobs files are read "
            "from more than one job folder; a test tree with two copies of one image's folder and a "
            "third image's file gave each copy its own rows under its path."),
        "paths": ('*/system/job/jobs.xml', '*/system/job/jobs_*.xml'),
        "output_types": "standard",
        "artifact_icon": "clock",
        "multiline_columns": ["Extras"],
        "sample_data": {
            "cookbook_a11": "Android 11 | 259 rows",
            "galaxys10_a10": "Android 10 | 164 rows",
            "pixel3_a11": "Android 11 | 269 rows",
            "pixel3_a12": "Android 12 | 168 rows",
            "pixel7a_a14": "Android 14 | 209 rows, 38 per-UID files read (5 with no jobs)",
            "russell_pixel6a_a13": "Android 13 | 359 rows",
            "s20fe_a13": "Android 13 | 126 rows",
            "samsung_a166u_a16_known_20261116": "Android 16 | 137 rows, 29 per-UID files read (3 with no jobs)",
            "samsunga53_a14": "Android 14 | 171 rows, 34 per-UID files read (6 with no jobs)",
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
        item_extras = item.find('extras')
        for line in (_bundle_lines(item_extras) if item_extras is not None else []):
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
