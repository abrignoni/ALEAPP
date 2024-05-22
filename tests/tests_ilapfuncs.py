import os
import shutil
import sqlite3

from scripts import ilapfuncs


def test_timeline():
    data_list = [('row1_value1', 'row1_value2'), ('row2_value1', 'row2_value2')]
    data_headers = ['col1', 'col2']
    ilapfuncs.timeline('test_data/test/', 'mock-activity', data_list, data_headers)

    assert os.path.exists('test_data/_Timeline/tl.db')

    conn = sqlite3.connect('test_data/_Timeline/tl.db')
    cursor = conn.cursor()
    result = cursor.execute("SELECT * from data").fetchall()
    assert result[0] == (
        'row1_value1', 'mock-activity',
        '[{"row1_value1": "col1", "row1_value2": "col2"}, '
        '{"row2_value1": "col1", "row2_value2": "col2"}]')
    assert result[1] == (
        'row2_value1', 'mock-activity',
        '[{"row1_value1": "col1", "row1_value2": "col2"}, '
        '{"row2_value1": "col1", "row2_value2": "col2"}]')

    shutil.rmtree('test_data/')
