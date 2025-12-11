__artifacts_v2__ = {
    "Bumble": {
        "name": "Bumble",
        "description": "Parses Bumble chats, matches and user details",
        "author": "@KevinPagano3",
        "version": "0.0.1",
        "date": "2022-11-07",
        "requirements": "none",
        "category": "Bumble",
        "paths": ('*/com.bumble.app/databases/ChatComDatabase*','*/com.bumble.app/files/c2V0dGluZ3M='),
        "function": "get_bumble"
    }
}

import sqlite3
import os
import shutil
import textwrap
import blackboxprotobuf

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone

def get_bumble(files_found, report_folder, seeker, wrap_text):
    
    source_file_settings = ''
    source_file_chat_db = ''
    settings_file = ''
    chat_db = ''
    user_name = ''
    user_email = ''
    user_phone = ''
    user_id = ''
    user_age = ''
    user_birthdate = ''
    city = ''
    country = ''
    user_occupation = ''
    user_education = ''
    user_aboutme = ''   
    data_list = []
    
    for file_found in files_found:
    
        file_found = str(file_found)
        file_name = os.path.basename(file_found)
        if file_name == 'ChatComDatabase': # skip -journal and other files
            chat_db = file_found
            source_file_chat_db = file_found.replace(seeker.data_folder, '')
            continue

        elif file_name.endswith('='):
            settings_file = file_found
            source_file_settings = file_found.replace(seeker.data_folder, '')
            continue
    
    if settings_file != '':
        with open(settings_file, 'rb') as f:

            pb = f.read()
            message = blackboxprotobuf.decode_message(pb)
            types = {'0': {'name': '', 'type': 'int'},
          '1': {'name': '', 'type': 'int'},
          '2': {'message_typedef': {'1': {'message_typedef': {'1': {'message_typedef': {'1': {'name': '',
                                                                                              'type': 'int'},
                                                                                        '2': {'message_typedef': {'1': {'name': '',
                                                                                                                        'type': 'bytes'}},
                                                                                              'name': '',
                                                                                              'type': 'message'}},
                                                                    'name': '',
                                                                    'type': 'message'},
                                                              '2': {'alt_typedefs': {'1': {'1': {'name': '',
                                                                                                 'type': 'int'},
                                                                                           '2': {'message_typedef': {'1': {'name': 'user_id',
                                                                                                                           'type': 'str'},
                                                                                                                     '10': {'message_typedef': {},
                                                                                                                            'name': '',
                                                                                                                            'type': 'message'},
                                                                                                                     '100': {'message_typedef': {'1': {'name': '',
                                                                                                                                                       'type': 'bytes'},
                                                                                                                                                 '2': {'message_typedef': {'1': {'name': '',
                                                                                                                                                                                 'type': 'int'},
                                                                                                                                                                           '10': {'name': '',
                                                                                                                                                                                  'type': 'int'},
                                                                                                                                                                           '12': {'name': '',
                                                                                                                                                                                  'type': 'bytes'},
                                                                                                                                                                           '13': {'name': '',
                                                                                                                                                                                  'type': 'bytes'},
                                                                                                                                                                           '16': {'message_typedef': {'3': {'name': '',
                                                                                                                                                                                                            'type': 'bytes'},
                                                                                                                                                                                                      '4': {'name': '',
                                                                                                                                                                                                            'type': 'int'}},
                                                                                                                                                                                  'name': '',
                                                                                                                                                                                  'type': 'message'},
                                                                                                                                                                           '2': {'name': '',
                                                                                                                                                                                 'type': 'bytes'},
                                                                                                                                                                           '20': {'name': '',
                                                                                                                                                                                  'type': 'int'},
                                                                                                                                                                           '21': {'message_typedef': {'12': {'name': '',
                                                                                                                                                                                                             'type': 'int'},
                                                                                                                                                                                                      '13': {'name': '',
                                                                                                                                                                                                             'type': 'int'},
                                                                                                                                                                                                      '2': {'name': '',
                                                                                                                                                                                                            'type': 'bytes'},
                                                                                                                                                                                                      '24': {'message_typedef': {'1': {'name': '',
                                                                                                                                                                                                                                       'type': 'bytes'},
                                                                                                                                                                                                                                 '2': {'name': '',
                                                                                                                                                                                                                                       'type': 'int'},
                                                                                                                                                                                                                                 '5': {'name': '',
                                                                                                                                                                                                                                       'type': 'int'}},
                                                                                                                                                                                                             'name': '',
                                                                                                                                                                                                             'type': 'message'},
                                                                                                                                                                                                      '31': {'message_typedef': {'1': {'name': '',
                                                                                                                                                                                                                                       'type': 'int'},
                                                                                                                                                                                                                                 '2': {'name': '',
                                                                                                                                                                                                                                       'type': 'bytes'}},
                                                                                                                                                                                                             'name': '',
                                                                                                                                                                                                             'type': 'message'},
                                                                                                                                                                                                      '5': {'name': '',
                                                                                                                                                                                                            'type': 'bytes'}},
                                                                                                                                                                                  'name': '',
                                                                                                                                                                                  'type': 'message'},
                                                                                                                                                                           '27': {'name': '',
                                                                                                                                                                                  'type': 'int'},
                                                                                                                                                                           '3': {'name': '',
                                                                                                                                                                                 'type': 'bytes'},
                                                                                                                                                                           '4': {'name': 'phone_number',
                                                                                                                                                                                 'type': 'str'},
                                                                                                                                                                           '5': {'name': '',
                                                                                                                                                                                 'type': 'int'},
                                                                                                                                                                           '6': {'name': '',
                                                                                                                                                                                 'type': 'int'},
                                                                                                                                                                           '7': {'message_typedef': {'1': {'name': '',
                                                                                                                                                                                                           'type': 'bytes'},
                                                                                                                                                                                                     '2': {'message_typedef': {'9': {'name': '',
                                                                                                                                                                                                                                     'type': 'fixed64'}},
                                                                                                                                                                                                           'name': '',
                                                                                                                                                                                                           'type': 'message'},
                                                                                                                                                                                                     '3': {'name': '',
                                                                                                                                                                                                           'type': 'bytes'},
                                                                                                                                                                                                     '4': {'name': '',
                                                                                                                                                                                                           'type': 'int'},
                                                                                                                                                                                                     '5': {'message_typedef': {'1': {'name': '',
                                                                                                                                                                                                                                     'type': 'int'},
                                                                                                                                                                                                                               '2': {'name': '',
                                                                                                                                                                                                                                     'type': 'bytes'},
                                                                                                                                                                                                                               '3': {'name': '',
                                                                                                                                                                                                                                     'type': 'bytes'}},
                                                                                                                                                                                                           'name': '',
                                                                                                                                                                                                           'type': 'message'},
                                                                                                                                                                                                     '6': {'name': '',
                                                                                                                                                                                                           'type': 'bytes'}},
                                                                                                                                                                                 'name': '',
                                                                                                                                                                                 'type': 'message'},
                                                                                                                                                                           '8': {'name': '',
                                                                                                                                                                                 'type': 'int'}},
                                                                                                                                                       'name': '',
                                                                                                                                                       'type': 'message'},
                                                                                                                                                 '4': {'name': '',
                                                                                                                                                       'type': 'int'}},
                                                                                                                             'name': '',
                                                                                                                             'type': 'message'},
                                                                                                                     '11': {'name': 'user_email',
                                                                                                                            'type': 'str'},
                                                                                                                     '1110': {'message_typedef': {'1': {'name': '',
                                                                                                                                                        'type': 'int'},
                                                                                                                                                  '3': {'name': '',
                                                                                                                                                        'type': 'bytes'}},
                                                                                                                              'name': '',
                                                                                                                              'type': 'message'},
                                                                                                                     '1160': {'message_typedef': {},
                                                                                                                              'name': '',
                                                                                                                              'type': 'message'},
                                                                                                                     '1161': {'message_typedef': {},
                                                                                                                              'name': '',
                                                                                                                              'type': 'message'},
                                                                                                                     '1162': {'message_typedef': {},
                                                                                                                              'name': '',
                                                                                                                              'type': 'message'},
                                                                                                                     '1163': {'name': '',
                                                                                                                              'type': 'bytes'},
                                                                                                                     '1410': {'name': '',
                                                                                                                              'type': 'int'},
                                                                                                                     '1424': {'message_typedef': {'1': {'name': '',
                                                                                                                                                        'type': 'int'},
                                                                                                                                                  '2': {'name': '',
                                                                                                                                                        'type': 'bytes'}},
                                                                                                                              'name': '',
                                                                                                                              'type': 'message'},
                                                                                                                     '1442': {'name': '',
                                                                                                                              'type': 'int'},
                                                                                                                     '200': {'name': 'user_name',
                                                                                                                             'type': 'str'},
                                                                                                                     '210': {'name': 'user_age',
                                                                                                                             'type': 'int'},
                                                                                                                     '220': {'name': 'user_birthdate',
                                                                                                                             'type': 'str'},
                                                                                                                     '230': {'name': '',
                                                                                                                             'type': 'int'},
                                                                                                                     '291': {'name': '',
                                                                                                                             'type': 'int'},
                                                                                                                     '3': {'name': '',
                                                                                                                           'type': 'int'},
                                                                                                                     '310': {'name': '',
                                                                                                                             'type': 'int'},
                                                                                                                     '340': {'message_typedef': {'1': {'name': '',
                                                                                                                                                       'type': 'bytes'},
                                                                                                                                                 '2': {'name': '',
                                                                                                                                                       'type': 'bytes'},
                                                                                                                                                 '26': {'name': '',
                                                                                                                                                        'type': 'int'},
                                                                                                                                                 '27': {'name': '',
                                                                                                                                                        'type': 'int'},
                                                                                                                                                 '3': {'name': '',
                                                                                                                                                       'type': 'bytes'},
                                                                                                                                                 '4': {'message_typedef': {'1': {'name': '',
                                                                                                                                                                                 'type': 'int'},
                                                                                                                                                                           '2': {'name': '',
                                                                                                                                                                                 'type': 'int'}},
                                                                                                                                                       'name': '',
                                                                                                                                                       'type': 'message'},
                                                                                                                                                 '5': {'message_typedef': {'1': {'name': '',
                                                                                                                                                                                 'type': 'int'},
                                                                                                                                                                           '2': {'name': '',
                                                                                                                                                                                 'type': 'int'}},
                                                                                                                                                       'name': '',
                                                                                                                                                       'type': 'message'},
                                                                                                                                                 '6': {'message_typedef': {'1': {'name': '',
                                                                                                                                                                                 'type': 'int'},
                                                                                                                                                                           '2': {'name': '',
                                                                                                                                                                                 'type': 'int'}},
                                                                                                                                                       'name': '',
                                                                                                                                                       'type': 'message'}},
                                                                                                                             'name': '',
                                                                                                                             'type': 'message'},
                                                                                                                     '341': {'name': '',
                                                                                                                             'type': 'bytes'},
                                                                                                                     '370': {'message_typedef': {'1': {'name': '',
                                                                                                                                                       'type': 'bytes'},
                                                                                                                                                 '10': {'name': '',
                                                                                                                                                        'type': 'int'},
                                                                                                                                                 '11': {'name': '',
                                                                                                                                                        'type': 'int'},
                                                                                                                                                 '13': {'name': '',
                                                                                                                                                        'type': 'int'},
                                                                                                                                                 '14': {'name': '',
                                                                                                                                                        'type': 'bytes'},
                                                                                                                                                 '15': {'name': '',
                                                                                                                                                        'type': 'int'},
                                                                                                                                                 '18': {'message_typedef': {'1': {'name': '',
                                                                                                                                                                                  'type': 'bytes'},
                                                                                                                                                                            '17': {'name': '',
                                                                                                                                                                                   'type': 'int'},
                                                                                                                                                                            '2': {'name': '',
                                                                                                                                                                                  'type': 'bytes'},
                                                                                                                                                                            '26': {'name': '',
                                                                                                                                                                                   'type': 'int'},
                                                                                                                                                                            '27': {'name': '',
                                                                                                                                                                                   'type': 'int'},
                                                                                                                                                                            '3': {'name': '',
                                                                                                                                                                                  'type': 'bytes'},
                                                                                                                                                                            '4': {'message_typedef': {'1': {'name': '',
                                                                                                                                                                                                            'type': 'int'},
                                                                                                                                                                                                      '2': {'name': '',
                                                                                                                                                                                                            'type': 'int'}},
                                                                                                                                                                                  'name': '',
                                                                                                                                                                                  'type': 'message'},
                                                                                                                                                                            '5': {'message_typedef': {'1': {'name': '',
                                                                                                                                                                                                            'type': 'int'},
                                                                                                                                                                                                      '2': {'name': '',
                                                                                                                                                                                                            'type': 'int'}},
                                                                                                                                                                                  'name': '',
                                                                                                                                                                                  'type': 'message'},
                                                                                                                                                                            '6': {'message_typedef': {'1': {'name': '',
                                                                                                                                                                                                            'type': 'int'},
                                                                                                                                                                                                      '2': {'name': '',
                                                                                                                                                                                                            'type': 'int'}},
                                                                                                                                                                                  'name': '',
                                                                                                                                                                                  'type': 'message'},
                                                                                                                                                                            '8': {'name': '',
                                                                                                                                                                                  'type': 'int'}},
                                                                                                                                                        'name': '',
                                                                                                                                                        'type': 'message'},
                                                                                                                                                 '19': {'name': '',
                                                                                                                                                        'type': 'int'},
                                                                                                                                                 '20': {'name': '',
                                                                                                                                                        'type': 'int'},
                                                                                                                                                 '21': {'name': '',
                                                                                                                                                        'type': 'bytes'},
                                                                                                                                                 '22': {'message_typedef': {'12': {'name': '',
                                                                                                                                                                                   'type': 'int'},
                                                                                                                                                                            '13': {'name': '',
                                                                                                                                                                                   'type': 'int'},
                                                                                                                                                                            '2': {'name': '',
                                                                                                                                                                                  'type': 'bytes'},
                                                                                                                                                                            '24': {'message_typedef': {'1': {'name': '',
                                                                                                                                                                                                             'type': 'bytes'},
                                                                                                                                                                                                       '2': {'name': '',
                                                                                                                                                                                                             'type': 'int'},
                                                                                                                                                                                                       '5': {'name': '',
                                                                                                                                                                                                             'type': 'int'},
                                                                                                                                                                                                       '9': {'name': '',
                                                                                                                                                                                                             'type': 'int'}},
                                                                                                                                                                                   'name': '',
                                                                                                                                                                                   'type': 'message'},
                                                                                                                                                                            '32': {'name': '',
                                                                                                                                                                                   'type': 'int'},
                                                                                                                                                                            '48': {'name': '',
                                                                                                                                                                                   'type': 'int'}},
                                                                                                                                                        'name': '',
                                                                                                                                                        'type': 'message'},
                                                                                                                                                 '23': {'name': '',
                                                                                                                                                        'type': 'int'},
                                                                                                                                                 '25': {'name': '',
                                                                                                                                                        'type': 'int'},
                                                                                                                                                 '3': {'name': '',
                                                                                                                                                       'type': 'bytes'},
                                                                                                                                                 '4': {'name': '',
                                                                                                                                                       'type': 'bytes'},
                                                                                                                                                 '8': {'name': '',
                                                                                                                                                       'type': 'int'},
                                                                                                                                                 '9': {'name': '',
                                                                                                                                                       'type': 'int'}},
                                                                                                                             'name': '',
                                                                                                                             'type': 'message'},
                                                                                                                     '380': {'message_typedef': {'1': {'name': '',
                                                                                                                                                       'type': 'int'},
                                                                                                                                                 '3': {'message_typedef': {'1': {'name': '',
                                                                                                                                                                                 'type': 'bytes'},
                                                                                                                                                                           '12': {'name': '',
                                                                                                                                                                                  'type': 'bytes'},
                                                                                                                                                                           '2': {'name': '',
                                                                                                                                                                                 'type': 'bytes'},
                                                                                                                                                                           '3': {'name': '',
                                                                                                                                                                                 'type': 'bytes'},
                                                                                                                                                                           '4': {'name': '',
                                                                                                                                                                                 'type': 'int'},
                                                                                                                                                                           '5': {'message_typedef': {'1': {'name': '',
                                                                                                                                                                                                           'type': 'int'},
                                                                                                                                                                                                     '3': {'name': '',
                                                                                                                                                                                                           'type': 'bytes'}},
                                                                                                                                                                                 'name': '',
                                                                                                                                                                                 'type': 'message'},
                                                                                                                                                                           '6': {'name': '',
                                                                                                                                                                                 'type': 'bytes'}},
                                                                                                                                                       'name': '',
                                                                                                                                                       'type': 'message'},
                                                                                                                                                 '5': {'name': '',
                                                                                                                                                       'type': 'bytes'}},
                                                                                                                             'name': '',
                                                                                                                             'type': 'message'},
                                                                                                                     '4': {'name': '',
                                                                                                                           'type': 'int'},
                                                                                                                     '41': {'name': '',
                                                                                                                            'type': 'int'},
                                                                                                                     '420': {'message_typedef': {'1': {'name': '',
                                                                                                                                                       'type': 'int'},
                                                                                                                                                 '10': {'name': '',
                                                                                                                                                        'type': 'bytes'},
                                                                                                                                                 '2': {'name': '',
                                                                                                                                                       'type': 'bytes'},
                                                                                                                                                 '3': {'name': '',
                                                                                                                                                       'type': 'int'}},
                                                                                                                             'name': '',
                                                                                                                             'type': 'message'},
                                                                                                                     '421': {'message_typedef': {'1': {'name': '',
                                                                                                                                                       'type': 'int'},
                                                                                                                                                 '10': {'name': '',
                                                                                                                                                        'type': 'bytes'},
                                                                                                                                                 '2': {'name': '',
                                                                                                                                                       'type': 'bytes'},
                                                                                                                                                 '3': {'name': '',
                                                                                                                                                       'type': 'int'}},
                                                                                                                             'name': '',
                                                                                                                             'type': 'message'},
                                                                                                                     '490': {'alt_typedefs': {'1': {'1': {'name': '',
                                                                                                                                                          'type': 'bytes'},
                                                                                                                                                    '15': {'name': '',
                                                                                                                                                           'type': 'int'},
                                                                                                                                                    '2': {'name': '',
                                                                                                                                                          'type': 'int'},
                                                                                                                                                    '3': {'name': '',
                                                                                                                                                          'type': 'bytes'},
                                                                                                                                                    '4': {'name': '',
                                                                                                                                                          'type': 'bytes'},
                                                                                                                                                    '5': {'name': '',
                                                                                                                                                          'type': 'int'},
                                                                                                                                                    '9': {'name': '',
                                                                                                                                                          'type': 'int'}}},
                                                                                                                             'message_typedef': {'1': {'name': '',
                                                                                                                                                       'type': 'bytes'},
                                                                                                                                                 '15': {'name': '',
                                                                                                                                                        'type': 'int'},
                                                                                                                                                 '2': {'name': '',
                                                                                                                                                       'type': 'int'},
                                                                                                                                                 '3': {'name': '',
                                                                                                                                                       'type': 'bytes'},
                                                                                                                                                 '4': {'message_typedef': {},
                                                                                                                                                       'name': '',
                                                                                                                                                       'type': 'message'},
                                                                                                                                                 '5': {'name': '',
                                                                                                                                                       'type': 'int'},
                                                                                                                                                 '9': {'name': '',
                                                                                                                                                       'type': 'int'}},
                                                                                                                             'name': '',
                                                                                                                             'type': 'message'},
                                                                                                                     '493': {'message_typedef': {},
                                                                                                                             'name': '',
                                                                                                                             'type': 'message'},
                                                                                                                     '50': {'name': '',
                                                                                                                            'type': 'int'},
                                                                                                                     '530': {'name': '',
                                                                                                                             'type': 'bytes'},
                                                                                                                     '890': {'name': '',
                                                                                                                             'type': 'int'},
                                                                                                                     '91': {'message_typedef': {'1': {'name': '',
                                                                                                                                                      'type': 'int'},
                                                                                                                                                '2': {'name': 'country_full',
                                                                                                                                                      'type': 'str'},
                                                                                                                                                '3': {'name': '',
                                                                                                                                                      'type': 'bytes'},
                                                                                                                                                '4': {'name': '',
                                                                                                                                                      'type': 'bytes'},
                                                                                                                                                '5': {'name': '',
                                                                                                                                                      'type': 'bytes'},
                                                                                                                                                '6': {'name': '',
                                                                                                                                                      'type': 'int'},
                                                                                                                                                '7': {'name': '',
                                                                                                                                                      'type': 'int'}},
                                                                                                                            'name': '',
                                                                                                                            'type': 'message'},
                                                                                                                     '93': {'message_typedef': {'1': {'name': '',
                                                                                                                                                      'type': 'int'},
                                                                                                                                                '2': {'name': 'city_full',
                                                                                                                                                      'type': 'str'}},
                                                                                                                            'name': '',
                                                                                                                            'type': 'message'},
                                                                                                                     '930': {'name': '',
                                                                                                                             'type': 'int'}},
                                                                                                 'name': '',
                                                                                                 'type': 'message'}}},
                                                                    'message_typedef': {'1': {'name': '',
                                                                                              'type': 'int'},
                                                                                        '2': {'alt_typedefs': {'1': {'1': {'name': '',
                                                                                                                           'type': 'int'}}},
                                                                                              'message_typedef': {'1': {'message_typedef': {'1': {'message_typedef': {'1': {'name': '',
                                                                                                                                                                            'type': 'int'},
                                                                                                                                                                      '2': {'message_typedef': {'1': {'name': '',
                                                                                                                                                                                                      'type': 'int'}},
                                                                                                                                                                            'name': '',
                                                                                                                                                                            'type': 'message'}},
                                                                                                                                                  'name': '',
                                                                                                                                                  'type': 'message'},
                                                                                                                                            '2': {'message_typedef': {'1': {'name': '',
                                                                                                                                                                            'type': 'int'},
                                                                                                                                                                      '2': {'message_typedef': {'1': {'name': '',
                                                                                                                                                                                                      'type': 'int'},
                                                                                                                                                                                                '14': {'name': '',
                                                                                                                                                                                                       'type': 'int'},
                                                                                                                                                                                                '18': {'message_typedef': {'1': {'name': '',
                                                                                                                                                                                                                                 'type': 'int'},
                                                                                                                                                                                                                           '2': {'name': '',
                                                                                                                                                                                                                                 'type': 'int'},
                                                                                                                                                                                                                           '3': {'name': '',
                                                                                                                                                                                                                                 'type': 'int'},
                                                                                                                                                                                                                           '4': {'name': '',
                                                                                                                                                                                                                                 'type': 'int'},
                                                                                                                                                                                                                           '5': {'name': '',
                                                                                                                                                                                                                                 'type': 'int'},
                                                                                                                                                                                                                           '6': {'name': '',
                                                                                                                                                                                                                                 'type': 'int'}},
                                                                                                                                                                                                       'name': '',
                                                                                                                                                                                                       'type': 'message'},
                                                                                                                                                                                                '2': {'name': '',
                                                                                                                                                                                                      'type': 'int'},
                                                                                                                                                                                                '20': {'name': '',
                                                                                                                                                                                                       'type': 'int'},
                                                                                                                                                                                                '21': {'message_typedef': {'1': {'name': '',
                                                                                                                                                                                                                                 'type': 'int'},
                                                                                                                                                                                                                           '2': {'name': '',
                                                                                                                                                                                                                                 'type': 'int'},
                                                                                                                                                                                                                           '3': {'name': '',
                                                                                                                                                                                                                                 'type': 'int'},
                                                                                                                                                                                                                           '4': {'name': '',
                                                                                                                                                                                                                                 'type': 'int'}},
                                                                                                                                                                                                       'name': '',
                                                                                                                                                                                                       'type': 'message'},
                                                                                                                                                                                                '26': {'name': '',
                                                                                                                                                                                                       'type': 'bytes'},
                                                                                                                                                                                                '27': {'message_typedef': {'1': {'name': '',
                                                                                                                                                                                                                                 'type': 'bytes'},
                                                                                                                                                                                                                           '2': {'message_typedef': {'9': {'name': '',
                                                                                                                                                                                                                                                           'type': 'fixed64'}},
                                                                                                                                                                                                                                 'name': '',
                                                                                                                                                                                                                                 'type': 'message'},
                                                                                                                                                                                                                           '3': {'name': '',
                                                                                                                                                                                                                                 'type': 'bytes'},
                                                                                                                                                                                                                           '4': {'name': '',
                                                                                                                                                                                                                                 'type': 'int'},
                                                                                                                                                                                                                           '5': {'message_typedef': {'1': {'name': '',
                                                                                                                                                                                                                                                           'type': 'int'},
                                                                                                                                                                                                                                                     '2': {'name': '',
                                                                                                                                                                                                                                                           'type': 'bytes'},
                                                                                                                                                                                                                                                     '3': {'name': '',
                                                                                                                                                                                                                                                           'type': 'bytes'}},
                                                                                                                                                                                                                                 'name': '',
                                                                                                                                                                                                                                 'type': 'message'}},
                                                                                                                                                                                                       'name': '',
                                                                                                                                                                                                       'type': 'message'},
                                                                                                                                                                                                '3': {'name': '',
                                                                                                                                                                                                      'type': 'int'},
                                                                                                                                                                                                '4': {'name': '',
                                                                                                                                                                                                      'type': 'bytes'},
                                                                                                                                                                                                '7': {'name': '',
                                                                                                                                                                                                      'type': 'int'}},
                                                                                                                                                                            'name': '',
                                                                                                                                                                            'type': 'message'}},
                                                                                                                                                  'name': '',
                                                                                                                                                  'type': 'message'}},
                                                                                                                        'name': '',
                                                                                                                        'type': 'message'}},
                                                                                              'name': '',
                                                                                              'type': 'message'}},
                                                                    'name': '',
                                                                    'type': 'message'}},
                                          'name': '',
                                          'type': 'message'}},
                'name': '',
                'type': 'message'},
          '482': {'name': '', 'type': 'fixed64'}}
            
            values, types = blackboxprotobuf.decode_message(pb, types)
            
            user_name = values['2']['1'][2]['2-1']['2']['user_name']
            user_email = values['2']['1'][2]['2-1']['2']['user_email']
            user_phone = values['2']['1'][2]['2-1']['2']['100']['2'][0]['phone_number']
            user_id = values['2']['1'][2]['2-1']['2']['user_id']
            user_age = values['2']['1'][2]['2-1']['2']['user_age']
            user_birthdate = values['2']['1'][2]['2-1']['2']['user_birthdate']
            city = values['2']['1'][2]['2-1']['2']['93']['city_full']
            country = values['2']['1'][2]['2-1']['2']['91']['country_full']
            user_occupation = values['2']['1'][2]['2-1']['2']['490'][0]['4']
            user_education = values['2']['1'][2]['2-1']['2']['490'][1]['4']
            user_aboutme = values['2']['1'][2]['2-1']['2']['490'][3]['4']
            
            data_list.append((user_name,user_email,user_phone,user_id,user_age,user_birthdate,city,country,user_occupation,user_education,user_aboutme))

        if len(data_list) > 0:
            report = ArtifactHtmlReport('Bumble - User Settings')
            report.start_artifact_report(report_folder, 'Bumble - User Settings')
            report.add_script()
            data_headers = ('User Name','Email','Phone','ID','Age','Birthdate','City','Country','Occupation','Education','About') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
            
            report.write_artifact_data_table(data_headers, data_list, source_file_settings)
            report.end_artifact_report()
            
            tsvname = f'Bumble - User Settings'
            tsv(report_folder, data_headers, data_list, tsvname)
            
        else:
            logfunc('No Bumble - User Settings data available')
    
    db = open_sqlite_db_readonly(chat_db)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    datetime(message.created_timestamp/1000,'unixepoch') as 'Created Timestamp',
    datetime(message.modified_timestamp/1000,'unixepoch') as 'Modified Timestamp',
    message.sender_id,
    message.recipient_id,
    json_extract(message.payload, '$.text'),
    json_extract(message.payload, '$.url'),
    message.payload_type,
    case message.is_incoming
        when 0 then 'Outgoing'
        when 1 then 'Incoming'
    end as 'Message Direction',
    message.conversation_id as 'Conversation ID',
    message.id as 'Message ID',
    conversation_info.user_name
    from message
    left join conversation_info on conversation_info.user_id = message.conversation_id
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Bumble - Chat Messages')
        report.start_artifact_report(report_folder, 'Bumble - Chat Messages')
        report.add_script()
        data_headers = ('Created Timestamp','Modified Timestamp','Sender ID','Sender Name','Recipient ID','Recipient Name','Message Text','Message URL','Message Type','Message Direction','Conversation ID','Message ID') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            time_create = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[0]),'UTC')
            time_mod = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[1]),'UTC')
            if row[7] == 'Outgoing':
                data_list.append((time_create,time_mod,row[2],str(user_name + ' (local user)'),row[3],row[10],row[4],row[5],row[6],row[7],row[8],row[9]))
            else:
                data_list.append((time_create,time_mod,row[2],row[10],row[3],str(user_name + ' (local user)'),row[4],row[5],row[6],row[7],row[8],row[9]))

        report.write_artifact_data_table(data_headers, data_list, source_file_chat_db)
        report.end_artifact_report()
        
        tsvname = f'Bumble - Chat Messages'
        tsv(report_folder, data_headers, data_list, tsvname)
        
    else:
        logfunc('No Bumble - Chat Messages data available')
        
    cursor.execute('''
    SELECT 
    user_name,
    age,
    gender,
    case game_mode
        when 0 then 'Bumble Date'
        when 1 then 'Bumble Friends'
        when 5 then 'Bumble Bizz'
    end,
    user_image_url,
    user_id,
    encrypted_user_id
    FROM conversation_info 
    ORDER BY user_id
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Bumble - Matches')
        report.start_artifact_report(report_folder, 'Bumble - Matches')
        report.add_script()
        data_headers = ('User Name','Age','Gender','Mode','Profile Image URL','User ID','Encrypted User ID') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6]))

        report.write_artifact_data_table(data_headers, data_list, source_file_chat_db)
        report.end_artifact_report()
        
        tsvname = f'Bumble - Matches'
        tsv(report_folder, data_headers, data_list, tsvname)
        
    else:
        logfunc('No Bumble - Matches data available')    
    
    db.close()

