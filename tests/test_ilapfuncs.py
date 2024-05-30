from unittest.mock import Mock, patch

from scripts import ilapfuncs


@patch('sqlite3')
def test_timeline(mock_sqlite3):
    mock_cursor = Mock()
    mock_connect = Mock()
    mock_connect.cursor.return_value = mock_cursor
    mock_sqlite3.connect.return_value = mock_connect

    data_list = [('row1_value1', 'row1_value2'), ('row2_value1', 'row2_value2')]
    data_headers = ['col1', 'col2']
    ilapfuncs.timeline('test_data/test', 'mock-activity', data_list, data_headers)

    mock_cursor.assert_called()