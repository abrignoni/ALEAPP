"""HTML email bodies reach the report and LAVA as readable text, not as tag source."""
import base64
import json
import pathlib
import quopri
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts import artifact_report  # pylint: disable=wrong-import-position
from scripts.artifacts import K9Mail, yahooMail  # pylint: disable=wrong-import-position
from scripts.artifacts.gmailEmails import body_text_and_links  # pylint: disable=wrong-import-position

PAGE = ('<html><head><title>Hidden title</title><style>p{color:red}</style></head><body>'
        '<p>Hello&nbsp;<b>wor</b>ld caf&eacute; &amp; co.</p><script>var x=1</script>'
        '<div>Second line<br>Third <a href="https://example.test/x">link</a></div>'
        '<table><tr><td>Cell A</td><td>Cell B</td></tr><tr><td>Cell C</td></tr></table>'
        '<!-- a comment --></body></html>')
PAGE_TEXT = 'Hidden title\nHello world café & co.\nSecond line\nThird link [1]\nCell A Cell B\nCell C'


class FakeContext:
    def __init__(self, paths):
        self.paths = [str(path) for path in paths]

    def get_files_found(self):
        return self.paths

    @staticmethod
    def get_relative_path(path):
        return str(path)


class MultilineCellTest(unittest.TestCase):
    def test_every_line_ending_shows_one_break(self):
        self.assertEqual(artifact_report.cell_html('a\r\nb\rc\nd', 'Body', [], ['Body']), 'a<br>b<br>c<br>d')

    def test_the_page_shows_breaks_and_escapes_markup(self):
        cell = artifact_report.cell_html('<b>one</b>\ntwo', 'Body', [], ['Body'])
        self.assertEqual(cell, '&lt;b&gt;one&lt;/b&gt;<br>two')

    def test_other_columns_keep_the_default_escape(self):
        self.assertEqual(artifact_report.cell_html('a\nb', 'Other', [], ['Body']), 'a\nb')


class BodyTextTest(unittest.TestCase):
    def test_a_page_reads_as_lines_of_text(self):
        text, links = body_text_and_links(PAGE)
        self.assertEqual(text, PAGE_TEXT)
        self.assertEqual(links, '[1] https://example.test/x')

    def test_pre_keeps_its_lines(self):
        self.assertEqual(body_text_and_links('<pre>one\n  two</pre>after')[0], 'one\ntwo\nafter')

    def test_mixed_br_forms_break_in_place(self):
        self.assertEqual(body_text_and_links('a<br>b<br/>c<br />d')[0], 'a\nb\nc\nd')

    def test_an_unclosed_style_shows_the_text_after_it(self):
        self.assertIn('Kept', body_text_and_links('<p>a</p><style>Kept')[0])

    def test_a_style_named_in_a_later_comment_is_still_removed(self):
        self.assertEqual(body_text_and_links('<style>p{}</style><p>a</p><!-- <style -->')[0], 'a')

    def test_no_closing_tag_is_added_to_the_text(self):
        self.assertEqual(body_text_and_links('<p>a</p><script>var s="<style>";')[0], 'a\nvar s="<style>";')

    def test_a_tag_name_in_an_attribute_does_not_keep_style_text(self):
        self.assertEqual(body_text_and_links('<style>p{}</style><a title="<style>" href="u">x</a>')[0], 'x [1]')

    def test_explicit_blank_lines_are_kept_once(self):
        self.assertEqual(body_text_and_links('one<br><br>two')[0], 'one\n\ntwo')
        self.assertEqual(body_text_and_links('<pre>one\n\ntwo</pre>')[0], 'one\n\ntwo')
        self.assertEqual(body_text_and_links('one<br><br><br><br>two<br><br>')[0], 'one\n\ntwo')

    def test_block_edges_make_no_blank_line(self):
        self.assertEqual(body_text_and_links('<div><p>one</p></div><div><p>two</p></div>')[0], 'one\ntwo')

    def test_a_broken_character_reference_before_an_open_style_does_not_raise(self):
        self.assertIn('Hello', body_text_and_links('<p>Hello</p>&#<style>Kept')[0])

    def test_markup_the_parser_refuses_does_not_raise(self):
        self.assertIn('Hello', body_text_and_links('<p>Hello</p><![bogus]>')[0])

    def test_pre_keeps_a_line_end_before_an_inline_tag(self):
        self.assertEqual(body_text_and_links('<pre>one\n<b>two</b></pre>')[0], 'one\ntwo')

    def test_escaped_markup_stays_as_the_words_it_spells(self):
        self.assertEqual(body_text_and_links('<p>&lt;b&gt;not a tag&lt;/b&gt;</p>')[0], '<b>not a tag</b>')

    def test_an_unclosed_head_keeps_the_body(self):
        text, links = body_text_and_links('<head><title>T</title><body><p>Kept <a href="u">x</a></p>')
        self.assertEqual((text, links), ('T\nKept x [1]', '[1] u'))

    def test_an_unclosed_style_keeps_its_text(self):
        self.assertIn('Kept', body_text_and_links('<style>p{}</style><p>a</p><style>Kept')[0])

    def test_empty_body(self):
        self.assertEqual(body_text_and_links(''), ('', ''))


class K9MailTest(unittest.TestCase):
    def rows(self, mime_type, encoding, data, part_header):
        with tempfile.TemporaryDirectory() as folder:
            path = pathlib.Path(folder) / 'account.db'
            database = sqlite3.connect(path)
            database.executescript('''
                CREATE TABLE folders(id INTEGER PRIMARY KEY, name TEXT);
                CREATE TABLE messages(id INTEGER PRIMARY KEY, deleted INTEGER, folder_id INTEGER,
                    subject TEXT, date INTEGER, sender_list TEXT, to_list TEXT, cc_list TEXT,
                    bcc_list TEXT, reply_to_list TEXT, attachment_count INTEGER,
                    internal_date INTEGER, preview TEXT, read INTEGER, flagged INTEGER,
                    answered INTEGER, forwarded INTEGER, message_part_id INTEGER);
                CREATE TABLE message_parts(id INTEGER PRIMARY KEY, type INTEGER, root INTEGER,
                    parent INTEGER, seq INTEGER, mime_type TEXT, header TEXT, encoding TEXT,
                    charset TEXT, data_location INTEGER, data BLOB);
                INSERT INTO folders VALUES (1, 'INBOX');
                INSERT INTO messages VALUES (1, 0, 1, 'Subject', 1000, 'a', 'b', '', '', '', 0,
                    2000, 'preview', 1, 0, 0, 0, 1);
                INSERT INTO message_parts VALUES (1, 0, 1, -1, 0, 'multipart/mixed', 'Root: 1', NULL,
                    NULL, 3, NULL);
            ''')
            database.execute('INSERT INTO message_parts VALUES (2, 0, 1, 1, 1, ?, ?, ?, NULL, 1, ?)',
                             (mime_type, part_header, encoding, data))
            database.commit()
            database.close()
            with patch.object(K9Mail, 'logfunc'):
                headers, rows, _ = K9Mail.get_k9mail_messages.__wrapped__(FakeContext([path]))
        return [dict(zip([h if isinstance(h, str) else h[0] for h in headers], row)) for row in rows]

    def test_base64_html_is_readable(self):
        row = self.rows('text/html', 'base64', base64.b64encode(PAGE.encode()),
                        'Content-Type: text/html; charset=utf-8\r\n')[0]
        self.assertEqual(row['Content'], PAGE_TEXT)
        self.assertEqual(row['Content Links'], '[1] https://example.test/x')

    def test_quoted_printable_html_uses_the_part_charset(self):
        data = quopri.encodestring('<p>café = ok</p>'.encode('latin-1'))
        row = self.rows('TEXT/HTML', 'quoted-printable', data,
                        'Content-Type: text/html; charset="iso-8859-1"\r\n')[0]
        self.assertEqual(row['Content'], 'café = ok')

    def test_an_unknown_charset_falls_back_to_utf8(self):
        row = self.rows('text/html', '8bit', '<p>café</p>'.encode(),
                        'Content-Type: text/html; charset=not-a-charset\r\n')[0]
        self.assertEqual(row['Content'], 'café')

    def test_a_charset_that_is_not_a_text_encoding_falls_back_to_utf8(self):
        row = self.rows('text/html', '8bit', '<p>café</p>'.encode(),
                        'Content-Type: text/html; charset=base64\r\n')[0]
        self.assertEqual(row['Content'], 'café')

    def test_quoted_printable_plain_text_is_decoded_with_its_charset(self):
        data = quopri.encodestring('café = ok\nnext'.encode('latin-1'))
        row = self.rows('text/plain', 'quoted-printable', data,
                        'Content-Type: text/plain; charset="iso-8859-1"\r\n')[0]
        self.assertEqual(row['Content'], 'café = ok\nnext')
        self.assertEqual(row['Content Links'], '')

    def test_base64_plain_text_uses_its_charset(self):
        row = self.rows('text/plain', 'base64', base64.b64encode('café'.encode('latin-1')),
                        'Content-Type: text/plain; charset=iso-8859-1\r\n')[0]
        self.assertEqual(row['Content'], 'café')

    def test_a_stored_number_is_reported_as_itself(self):
        self.assertEqual(self.rows('text/plain', '8bit', 5, '')[0]['Content'], '5')

    def test_stored_text_is_not_decoded_again(self):
        row = self.rows('text/plain', '8bit', 'café', 'Content-Type: text/plain; charset=iso-8859-1\r\n')[0]
        self.assertEqual(row['Content'], 'café')

    def test_plain_text_that_looks_like_html_is_left_alone(self):
        row = self.rows('text/plain', '8bit', b'<b>literal</b>\n  spaced', '')[0]
        self.assertEqual(row['Content'], '<b>literal</b>\n  spaced')
        self.assertEqual(row['Content Links'], '')


class YahooMailTest(unittest.TestCase):
    def test_cached_html_is_readable_and_rows_sort_on_message_id(self):
        with tempfile.TemporaryDirectory() as folder:
            path = pathlib.Path(folder) / 'com.yahoo.mobile.client.android.mail' / 'databases'
            path.mkdir(parents=True)
            path = path / 'flux_database.db'
            database = sqlite3.connect(path)
            for table in ('MessagesData', 'MessagesRecipients', 'MessagesFlags', 'MessagesFolderId',
                          'MessagesRefV2', 'MessagesSubjectSnippet', 'MessagesAttachments',
                          'MessagesBody', 'Folders'):
                database.execute(f'CREATE TABLE "{table}"(mailboxYid TEXT, key TEXT, value TEXT, timestamp INTEGER)')
            for key in ('m1', 'm2'):
                database.execute('INSERT INTO MessagesData VALUES (?, ?, ?, 1)',
                                 ('box', key, json.dumps({'date': 1000})))
            database.execute('INSERT INTO MessagesBody VALUES (?, ?, ?, 1)',
                             ('box', 'm2', json.dumps({'htmlBody': PAGE})))
            database.commit()
            database.close()
            with patch.object(yahooMail, 'logfunc'):
                headers, rows, _ = yahooMail.yahoo_mail_messages.__wrapped__(FakeContext([path]))
        names = [h if isinstance(h, str) else h[0] for h in headers]
        rows = [dict(zip(names, row)) for row in rows]
        self.assertEqual([row['Message ID'] for row in rows], ['m2', 'm1'])
        self.assertEqual(rows[0]['Message Body (as text)'], PAGE_TEXT)
        self.assertEqual(rows[0]['Message Body Links'], '[1] https://example.test/x')
        self.assertEqual(rows[1]['Message Body (as text)'], '')


if __name__ == '__main__':
    unittest.main()
