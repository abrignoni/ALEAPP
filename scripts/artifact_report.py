import html
import os

class ArtifactHtmlReport:

    def __init__(self, artifact_name, artifact_category=''):
        self.report_file = None
        self.report_file_path = ''
        self.artifact_name = artifact_name
        self.artifact_category = artifact_category # unused

    def __del__(self):
        if self.report_file:
            self.end_artifact_report()

    def start_artifact_report(self, report_folder, artifact_file_name, extra_info=''):
        '''Creates the report HTML file and writes the artifact name as a heading'''
        self.report_file_path
        self.report_file = open(os.path.join(report_folder, f'{artifact_file_name}.html'), 'w', encoding='utf8')
        self.report_file.write('<html><body>')
        self.report_file.write(f'<h2> {self.artifact_name} report</h2>')
        if extra_info:
            self.report_file.write(f'<h2> {extra_info}</h2>')

    def add_style(self, style=''):
        '''Adds a default style or the style element supplied'''
        if style == '':
            self.report_file.write('<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>')
        else:
            self.report_file.write(style)

    def write_artifact_data_table(self, data_headers, data_list, source_path, table_class='table sticky', write_total=True, write_location=True, html_escape=True):
        '''Writes info about data, then writes the table to html file
            Input params
            ------------
            data_headers   : List of table column names
            data_list      : List of lists/tuples which contain rows of data
            source_path    : Source path of data
            write_total    : Toggles whether to write out a line of total rows written
            write_location : Toggles whether to write the location of data source
            html_escape    : If True (default), then html special characters are encoded
            table_class    : class type for the table, default is 'table sticky'
        '''
        if (not self.report_file):
            raise ValueError('Output report file is closed/unavailable!')
        num_entries = len(data_list)
        if write_total:
            self.report_file.write(f'Total number of entries: {num_entries}<br>')
        if write_location:
            self.report_file.write(f'{self.artifact_name} located at: {source_path}<br>')

        # setup table here
        self.report_file.write('<br/>')
        self.report_file.write('')
        if table_class:
            self.report_file.write(f'<table class="{table_class}">')
        else:
            self.report_file.write('<table>')
        self.report_file.write('<tr>' + ''.join( (f'<th>{x}</th>' for x in data_headers) ) + '</tr>')
        if html_escape:
            for row in data_list:
                self.report_file.write('<tr>' + ''.join( ('<td>{}</td>'.format(html.escape(x)) for x in row) ) + '</tr>')
        else:
            for row in data_list:
                self.report_file.write('<tr>' + ''.join( (f'<td>{x}</td>' for x in row) ) + '</tr>')
        self.report_file.write('</table>')

    def write_minor_header(self, heading, heading_tag=''):
        heading = html.escape(heading)
        if heading_tag:
            self.report_file.write(f'<{heading_tag}>{heading}</{heading_tag}>')
        else:
            self.report_file.write(f'<h3>{heading}</h3>')
    
    def write_raw_html(self, code):
        self.report_file.write(code)

    def end_artifact_report(self):
        self.report_file.write('</body></html>')
        self.report_file.close()
        self.report_file = None