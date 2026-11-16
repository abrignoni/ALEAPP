"""Reader for the shortcut service dump of an Android bug report text (the dumpstate file).

The reader plugs into the single pass of ``scripts/dumpstate_reader.py``: it is handed the lines
of the ``DUMP OF SERVICE shortcut`` section while the text is read, keeps one row per
``ShortcutInfo {`` entry on the report object and never touches the file itself.

The layout is the one AOSP prints (``ShortcutService.dumpInner``, ``ShortcutUser.dump``,
``ShortcutPackage.dump`` and ``ShortcutInfo.toDumpString`` at android-16.0.0_r1):

    User: 0  Known locales: ...  Last app scan: [ms] text
          Package: <package>  UID: <uid>
            Shortcuts:
              ShortcutInfo {id=<id>, flags=0x<hex> [<letters>]
                packageName=...
                activity=ComponentInfo{...}
                shortLabel=<text>, resId=<n>[<name>]
                longLabel=<text>, resId=<n>[<name>]
                disabledMessage=<text>, resId=<n>[<name>]
                disabledReason=[Not disabled]
                categories={...}
                persons=[...]
                icon=...
                rank=<n>, timestamp=<ms>
                intents=[...]
                extras=...
                iconRes=<n>[<name>], bitmapPath=..., iconUri=...}

``toDumpString`` prints each field on its own line, two spaces deeper than ``ShortcutInfo {``,
so a line that does not start a known field at that depth continues the field above it (a label
with a line break). ``SplashScreenThemeResName=`` is printed only when set and ``locusId=`` is
appended to the last line without a separator. The ``** SHORTCUT MANAGER UID STATES`` and
``** SHORTCUT MANAGER FILES`` parts the same section ends with are not read.

Nothing is decoded beyond splitting the printed fields: values are kept as printed, cut to a
bounded length, and the flag letters are named from ``ShortcutInfo.addReadableFlags``.
"""
import collections
import re

from scripts import dumpstate_reader as reader
from scripts.dumpstate_reader import SectionReader, tidy, to_int

TABLE = 'shortcuts'
TEXT_CHARS = 1000
LABEL_CHARS = 500

Shortcut = collections.namedtuple(
    'Shortcut', 'user package shortcut_id flags_hex flag_letters kinds unknown_letters activity short_label long_label '
                'disabled_message disabled_reason categories person_count persons_text rank timestamp_text '
                'intents extras line')

# The letters ShortcutInfo.addReadableFlags prints, in its order (android-16.0.0_r1). Used only to check the printed
# run; the Kind column is decoded from the hexadecimal value, because the letters do not show the cached bits.
FLAG_LETTERS = ('Sdw', 'Dis', 'Im', 'Man', 'Dyn', 'Pin', 'Ic-f', 'Pens', 'Ic-r', 'Ic-u', 'Ic-a', 'Key', 'Str', 'Rets',
                'Liv', 'Hid-L')
# ShortcutInfo.FLAG_* bits named in the Kind column, in this order (android-16.0.0_r1). The icon, string and key bits
# describe how the shortcut is stored and are left out.
KIND_BITS = (
    (1 << 5, 'manifest'), (1 << 0, 'dynamic'), (1 << 1, 'pinned'), (1 << 13, 'long lived'),
    (1 << 14, 'cached for notifications'), (1 << 30, 'cached for bubbles'), (1 << 29, 'cached for people tile'),
    (1 << 6, 'disabled'), (1 << 8, 'immutable'), (1 << 12, 'shadow'),
)

FIELDS = ('packageName', 'activity', 'shortLabel', 'longLabel', 'disabledMessage', 'disabledReason',
          'SplashScreenThemeResName', 'categories', 'persons', 'icon', 'rank', 'intents', 'extras', 'iconRes')
_FIELD = re.compile(r'(%s)=' % '|'.join(re.escape(name) for name in FIELDS))
_USER = re.compile(r'^User: (\d+)\b')
_FLAGS = re.compile(r'^([0-9a-fA-F]+) \[(.*)\]$')


def rows_of(report):
    """The shortcut rows a report holds (none when the section was not in it)."""
    return getattr(report, TABLE, [])


def split_letters(letters):
    """``(names, leftover)`` for a flag letter run such as ``DynIc-fStrLiv``, read left to right."""
    names, rest = [], letters
    while rest:
        for letter in FLAG_LETTERS:
            if rest.startswith(letter):
                names.append(letter)
                rest = rest[len(letter):]
                break
        else:
            return names, rest
    return names, ''


def kind_text(flags, letters):
    """The Kind names of a flags value, plus ``excluded from launcher`` when the printed letters carry ``Hid-L``."""
    if flags is None:
        return ''
    names = [name for bit, name in KIND_BITS if flags & bit]
    if 'Hid-L' in letters:
        names.append('excluded from launcher')
    return ', '.join(names)


def _label(text):
    """The label of ``<label>, resId=<n>[<name>]``; ``null`` (no label) becomes empty."""
    label = text.rpartition(', resId=')[0] if ', resId=' in text else text
    return '' if label == 'null' else label


def _none(text):
    return '' if text == 'null' else text


def person_count(text):
    """Number of entries in ``Arrays.toString(Person[])``: None for ``null``, 0 for ``[]``."""
    if text == 'null' or not text:
        return None
    if text == '[]':
        return 0
    count = text.count('android.app.Person@')
    return count or None


class ShortcutReader(SectionReader):
    """``dumpsys shortcut``: the ShortcutInfo entries of each user and package."""
    kind = 'service'
    name = 'shortcut'

    def __init__(self, report, section):
        SectionReader.__init__(self, report, section)
        if not hasattr(report, TABLE):
            setattr(report, TABLE, [])
        self.user = None
        self.entry = None
        self.depth = None
        self.last_field = None
        self.stopped = False

    def _flush(self):
        entry, self.entry, self.last_field = self.entry, None, None
        if entry is None:
            return
        fields = entry['fields']
        flags = _FLAGS.match(entry['flags'])
        flags_hex, letters = (flags.group(1), flags.group(2)) if flags else ('', entry['flags'])
        names, leftover = split_letters(letters)
        kinds = kind_text(int(flags_hex, 16) if flags_hex else None, names)
        rank_text, _sep, timestamp = fields.get('rank', '').partition(', timestamp=')
        activity = fields.get('activity', '')
        if activity.startswith('ComponentInfo{') and activity.endswith('}'):
            activity = activity[len('ComponentInfo{'):-1]
        persons = fields.get('persons', '')
        self.report.add(TABLE, Shortcut(
            self.user, tidy(fields.get('packageName', ''))[:LABEL_CHARS], tidy(entry['id'])[:LABEL_CHARS],
            flags_hex, tidy(letters)[:200], kinds, tidy(leftover)[:200], tidy(_none(activity))[:LABEL_CHARS],
            tidy(_label(fields.get('shortLabel', '')))[:LABEL_CHARS],
            tidy(_label(fields.get('longLabel', '')))[:LABEL_CHARS],
            tidy(_label(fields.get('disabledMessage', '')))[:LABEL_CHARS],
            tidy(fields.get('disabledReason', '')).strip('[]'),
            tidy(_none(fields.get('categories', '')))[:TEXT_CHARS],
            person_count(persons), tidy(persons)[:200], to_int(rank_text), timestamp.strip(),
            tidy(_none(fields.get('intents', '')))[:TEXT_CHARS], tidy(_none(fields.get('extras', '')))[:TEXT_CHARS],
            entry['line']))

    def feed(self, line_no, text):
        if self.stopped:
            return
        body = text.strip()
        if text.startswith('** SHORTCUT MANAGER'):
            self._flush()
            self.stopped = True
            return
        indent = len(text) - len(text.lstrip(' '))
        if body.startswith('ShortcutInfo {id='):
            self._flush()
            shortcut_id, _sep, flags = body[len('ShortcutInfo {id='):].rpartition(', flags=0x')
            self.entry = {'id': shortcut_id, 'flags': flags, 'fields': {}, 'line': line_no}
            self.depth = indent + 2
            return
        if self.entry is not None:
            found = _FIELD.match(text[self.depth:]) if indent == self.depth else None
            if found:
                self.last_field = found.group(1)
                self.entry['fields'][self.last_field] = text[self.depth + found.end():]
                if self.last_field == 'iconRes':
                    self._flush()
            elif self.last_field is not None:
                fields = self.entry['fields']
                fields[self.last_field] = fields[self.last_field] + ' ' + body
            return
        if indent == 2:
            found = _USER.match(body)
            if found:
                self.user = int(found.group(1))

    def finish(self):
        self._flush()


READERS = [ShortcutReader]
READ_BY = {('service', 'shortcut'): 'Shortcuts'}


def register():
    """Add the reader and the section index entry to the pass of ``dumpstate_reader`` (once, in any import order)."""
    for reader_class in READERS:
        if reader_class not in reader.READERS:
            reader.READERS.append(reader_class)
    for key, value in READ_BY.items():
        reader.READ_BY.setdefault(key, value)


register()
