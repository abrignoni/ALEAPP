__artifacts_v2__ = {
    "get_etc_hosts": {
        "name": "Etc_hosts",
        "description": "Reports stored hosts aliases and malformed-line evidence, excluding two exact default address/hostname pairs.",
        "author": "@ydkhatri; @AlexisBrignoni, Codex",
        "creation_date": "2020-10-09",
        "last_update_date": "2026-10-06",
        "requirements": "none",
        "category": "Etc Hosts",
        "notes": "One row per hostname token occurrence in the first selected input, in physical "
                 "line and token order. Exact 127.0.0.1/localhost and ::1/ip6-localhost pairs "
                 "are suppressed; other aliases on those lines remain. Blank and comment-only "
                 "lines are skipped; the first # begins a comment. One-token noncomment lines "
                 "retain the stored token with blank hostname and explicit status. Raw Line "
                 "removes only the physical line ending; invalid UTF-8 uses replacement display, "
                 "while Raw Line Bytes Hex preserves all original bytes including BOM/endings. "
                 "An initial UTF-8 BOM is ignored only for tokenization. Physical lines are not "
                 "joined and backslash tokens are not interpreted as continuations. No IP validity, "
                 "connection, ownership, user modification or malicious meaning is inferred. "
                 "Only the first matched input is read; other sources remain outside this artifact.",
        "paths": ('*/system/etc/hosts',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "file",
        "sample_data": {
            "galaxys10_a10": "Android 10 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 0 rows",
            "pixel7a_a14": "Android 14 | 0 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "sharon_a14": "Android 14 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | 0 rows",
        },
    }
}


from scripts.ilapfuncs import artifact_processor, logfunc


@artifact_processor
def get_etc_hosts(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = str(files_found[0])

    with open(source_path, 'rb') as hosts_file:
        for line_number, raw in enumerate(hosts_file, 1):
            try:
                text = raw.decode('utf-8')
                replacement = False
            except UnicodeDecodeError:
                text = raw.decode('utf-8', errors='replace')
                replacement = True
            display = text.removesuffix('\n').removesuffix('\r')
            lexical = raw[3:] if line_number == 1 and raw.startswith(b'\xef\xbb\xbf') else raw
            tokens = lexical.split(b'#', 1)[0].split()
            if not tokens:
                continue
            address = tokens[0].decode('utf-8', errors='replace')
            status = 'Stored alias'
            if len(tokens) == 1:
                logfunc(f'Hosts line has no hostname: {context.get_relative_path(source_path)}:{line_number}')
                data_list.append((address, '', line_number, None, 'Missing hostname', display, raw.hex()))
                continue
            if replacement:
                status = 'Stored alias; replacement UTF-8 display'
            for ordinal, token in enumerate(tokens[1:], 1):
                hostname = token.decode('utf-8', errors='replace')
                if (address, hostname) in [('127.0.0.1', 'localhost'), ('::1', 'ip6-localhost')]:
                    continue
                data_list.append((address, hostname, line_number, ordinal, status, display, raw.hex()))

    data_headers = ('IP Address', 'Hostname', 'Line Number', 'Hostname Ordinal',
                    'Parse Status', 'Raw Line', 'Raw Line Bytes Hex')
    return data_headers, data_list, source_path
