"""Prove the claim checker reads notes, and reads them with the right vocabulary.

Extending the check to `notes` is only worth having if three things hold at once, and
each fails silently on its own:

* notes are actually matched, or the field is nominally covered and never read;
* the completeness words do not apply to notes, or the check fires on every artifact
  that states what it was tested against, which is the wording this project asks for;
* a denial is not treated as a claim, or the same wording is taxed and the allowlist
  grows every time somebody writes a limitation down correctly.

The expected values here are spelled out as literals rather than derived from the
patterns under test. A fixture built from the constant it verifies moves with the bug.
"""
import importlib.util
import pathlib
import sys
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
_MODULE_PATH = REPO_ROOT / 'admin' / 'scripts' / 'check_claim_language.py'

# admin/scripts is not a package, so load the module from its path.
_spec = importlib.util.spec_from_file_location('check_claim_language', _MODULE_PATH)
ccl = importlib.util.module_from_spec(_spec)
sys.modules['check_claim_language'] = ccl
_spec.loader.exec_module(ccl)


def fires(field, text):
    """True when the vocabulary for `field` reports a match in `text`, negation applied."""
    pattern = ccl.CHECKED_FIELDS[field]
    hits = list(pattern.finditer(text))
    if field == 'notes':
        hits = [hit for hit in hits if not ccl.negated(text, hit.start())]
    return bool(hits)


class FieldCoverage(unittest.TestCase):
    def test_notes_is_checked(self):
        self.assertIn('notes', ccl.CHECKED_FIELDS)

    def test_name_and_description_keep_the_full_vocabulary(self):
        self.assertIs(ccl.CHECKED_FIELDS['name'], ccl.CLAIM_PATTERN)
        self.assertIs(ccl.CHECKED_FIELDS['description'], ccl.CLAIM_PATTERN)

    def test_notes_uses_its_own_vocabulary(self):
        self.assertIs(ccl.CHECKED_FIELDS['notes'], ccl.NOTES_PATTERN)


class NotesVocabulary(unittest.TestCase):
    # Attribution and certainty mean the same thing in a note as in a description.
    CLAIMS = (
        'the term the user typed into the search box',
        'a page the user visited',
        'a term the user entered',
        'this proves the account holder sent it',
        'the column is always populated',
        'a reliable record of the conversation',
    )
    # Notes state what was tested. These must stay silent or the check punishes the
    # coverage discipline it exists alongside.
    COVERAGE = (
        'empty on all 18 copies tested',
        'NULL for every account tested',
        'the complete table list is given above',
        'present on the entire corpus',
        'columns are read by position over a select star',
        'the sidecar is not read by this artifact',
    )

    def test_claims_fire(self):
        for text in self.CLAIMS:
            with self.subTest(text=text):
                self.assertTrue(fires('notes', text))

    def test_coverage_wording_stays_silent(self):
        for text in self.COVERAGE:
            with self.subTest(text=text):
                self.assertFalse(fires('notes', text))

    def test_notes_drops_exactly_the_two_documented_classes(self):
        """The two vocabularies differ only where the module says they do.

        Anything else diverging means one of them has been edited alone, which is how
        the check for one field quietly stops matching the check for another.
        """
        removed = ('all', 'every', 'complete', 'entire', 'full list', 'read by')
        for word in removed:
            with self.subTest(word=word, vocabulary='description'):
                self.assertTrue(ccl.CLAIM_PATTERN.search(word))
            with self.subTest(word=word, vocabulary='notes'):
                self.assertFalse(ccl.NOTES_PATTERN.search(word))
        kept = ('the user typed', 'typed by', 'manually', 'proves', 'always',
                'reliable', 'visited', 'habits', 'user-created')
        for word in kept:
            with self.subTest(word=word):
                self.assertTrue(ccl.CLAIM_PATTERN.search(word))
                self.assertTrue(ccl.NOTES_PATTERN.search(word))

    def test_description_still_flags_completeness(self):
        # The narrowing applies to notes only. Regression guard on the original behaviour.
        self.assertTrue(fires('description', 'every message in the conversation'))
        self.assertTrue(fires('description', 'all sites the user visited'))


class Negation(unittest.TestCase):
    def test_denial_in_the_same_clause_is_not_a_claim(self):
        for text in (
            'this store holds suggestions the app downloaded, not terms the user searched for',
            'their presence does not establish that the user viewed them',
            'they evidence the app running rather than anything the user chose',
            'the app stores no user created images',
        ):
            with self.subTest(text=text):
                self.assertFalse(fires('notes', text))

    def test_a_negation_in_the_previous_sentence_does_not_carry(self):
        # "not" governs its own clause. A full stop ends it, so the claim after it stands.
        text = 'The table is not a cache. It records the term the user typed.'
        self.assertTrue(fires('notes', text))

    def test_a_distant_negation_does_not_carry(self):
        # Sixty characters is the window; padding past it must leave the claim visible.
        text = 'not' + ' x' * 45 + ' the term the user typed'
        self.assertTrue(fires('notes', text))

    def test_the_window_is_bounded_and_short(self):
        self.assertLessEqual(ccl.NEGATION_WINDOW, 80)


if __name__ == '__main__':
    unittest.main()
