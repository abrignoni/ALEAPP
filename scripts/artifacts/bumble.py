# pylint: disable=W0613,W0718
__artifacts_v2__ = {
    "get_bumble": {
        "name": "Bumble - User Settings",
        "description": "Bumble local user details from the settings protobuf",
        "author": "@KevinPagano3", "creation_date": "2022-11-07", "last_update_date": "2022-11-07",
        "requirements": "none", "category": "Bumble",
        "paths": ('*/com.bumble.app/files/c2V0dGluZ3M=',),
        "output_types": "standard", "artifact_icon": "user",
    },
    "get_bumble_messages": {
        "name": "Bumble - Chat Messages",
        "description": "Bumble chat messages",
        "author": "@KevinPagano3", "creation_date": "2022-11-07", "last_update_date": "2026-07-03",
        "requirements": "none", "category": "Bumble",
        "paths": ('*/com.bumble.app/databases/ChatComDatabase*', '*/com.bumble.app/files/c2V0dGluZ3M='),
        "output_types": "standard", "artifact_icon": "message",
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Conversation ID",
                "textColumn": "Message Text",
                "directionColumn": "Message Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Created Timestamp",
                "senderColumn": "Sender Name"
            }
        },
    },
    "get_bumble_matches": {
        "name": "Bumble - Matches",
        "description": "Bumble matches / conversations",
        "author": "@KevinPagano3", "creation_date": "2022-11-07", "last_update_date": "2022-11-07",
        "requirements": "none", "category": "Bumble",
        "paths": ('*/com.bumble.app/databases/ChatComDatabase*',),
        "output_types": "standard", "artifact_icon": "users",
    }
}

import datetime
import sqlite3

import blackboxprotobuf

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly

_TYPES = {'0': {'name': '', 'type': 'int'},
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

_SETTINGS_CACHE = {}


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _txt(value):
    if isinstance(value, bytes):
        return value.decode('utf-8', 'replace')
    return value if value is not None else ''


def _g(data, *keys):
    for k in keys:
        try:
            data = data[k]
        except (KeyError, IndexError, TypeError):
            return ''
    return data


def _settings_file(files_found):
    return next((str(f) for f in files_found if str(f).endswith('=')), '')


def _chat_db(files_found):
    return next((str(f) for f in files_found if str(f).endswith('ChatComDatabase')), '')


def _run(source_path, sql):
    if not source_path:
        return []
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
    except sqlite3.Error:
        rows = []
    db.close()
    return rows


def _parse_settings(files_found):
    key = tuple(sorted(str(f) for f in files_found))
    if key in _SETTINGS_CACHE:
        return _SETTINGS_CACHE[key]
    info = {}
    sf = _settings_file(files_found)
    if sf:
        try:
            with open(sf, 'rb') as handle:
                values, _ = blackboxprotobuf.decode_message(handle.read(), _TYPES)
            base = _g(values, '2', '1', 2, '2-1', '2')
            if isinstance(base, dict):
                info = {
                    'user_name': _txt(base.get('user_name')),
                    'user_email': _txt(base.get('user_email')),
                    'user_phone': _txt(_g(base, '100', '2', 0, 'phone_number')),
                    'user_id': _txt(base.get('user_id')),
                    'user_age': base.get('user_age', ''),
                    'user_birthdate': _txt(base.get('user_birthdate')),
                    'city': _txt(_g(base, '93', 'city_full')),
                    'country': _txt(_g(base, '91', 'country_full')),
                    'user_occupation': _txt(_g(base, '490', 0, '4')),
                    'user_education': _txt(_g(base, '490', 1, '4')),
                    'user_aboutme': _txt(_g(base, '490', 3, '4')),
                }
        except Exception:
            info = {}
    _SETTINGS_CACHE[key] = (info, sf)
    return _SETTINGS_CACHE[key]


@artifact_processor
def get_bumble(files_found, report_folder, seeker, wrap_text):
    info, source_path = _parse_settings(files_found)
    data_list = []
    if info:
        data_list.append((info['user_name'], info['user_email'], info['user_phone'], info['user_id'],
                          info['user_age'], info['user_birthdate'], info['city'], info['country'],
                          info['user_occupation'], info['user_education'], info['user_aboutme']))
    data_headers = ('User Name', 'Email', 'Phone', 'ID', 'Age', 'Birthdate', 'City', 'Country',
                    'Occupation', 'Education', 'About')
    return data_headers, data_list, source_path


@artifact_processor
def get_bumble_messages(files_found, report_folder, seeker, wrap_text):
    info, _settings = _parse_settings(files_found)
    user_name = info.get('user_name', '') if info else ''
    local = f'{user_name} (local user)' if user_name else '(local user)'
    source_path = _chat_db(files_found)
    rows = _run(source_path, """
        SELECT message.created_timestamp, message.modified_timestamp, message.sender_id,
               message.recipient_id, json_extract(message.payload, '$.text'),
               json_extract(message.payload, '$.url'), message.payload_type,
               CASE message.is_incoming WHEN 0 THEN 'Outgoing' WHEN 1 THEN 'Incoming' END,
               message.conversation_id, message.id, conversation_info.user_name
        FROM message
        LEFT JOIN conversation_info ON conversation_info.user_id = message.conversation_id
    """)
    data_list = []
    for r in rows:
        if r[7] == 'Outgoing':
            sender_name, recipient_name = local, r[10]
        else:
            sender_name, recipient_name = r[10], local
        data_list.append((_ms_to_utc(r[0]), _ms_to_utc(r[1]), r[2], sender_name, r[3], recipient_name,
                          r[4], r[5], r[6], r[7], r[8], r[9]))
    data_headers = (('Created Timestamp', 'datetime'), ('Modified Timestamp', 'datetime'), 'Sender ID',
                    'Sender Name', 'Recipient ID', 'Recipient Name', 'Message Text', 'Message URL',
                    'Message Type', 'Message Direction', 'Conversation ID', 'Message ID')
    return data_headers, data_list, source_path


@artifact_processor
def get_bumble_matches(files_found, report_folder, seeker, wrap_text):
    source_path = _chat_db(files_found)
    rows = _run(source_path, """
        SELECT user_name, age, gender,
               CASE game_mode WHEN 0 THEN 'Bumble Date' WHEN 1 THEN 'Bumble Friends'
                    WHEN 5 THEN 'Bumble Bizz' END,
               user_image_url, user_id, encrypted_user_id
        FROM conversation_info ORDER BY user_id
    """)
    data_list = [(r[0], r[1], r[2], r[3], r[4], r[5], r[6]) for r in rows]
    data_headers = ('User Name', 'Age', 'Gender', 'Mode', 'Profile Image URL', 'User ID',
                    'Encrypted User ID')
    return data_headers, data_list, source_path
