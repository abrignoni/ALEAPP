__artifacts_v2__ = {
    "DroneFlightDATFiles": {
        "name": "DroneFlightDATFiles",
        "description": "Extracts cool data from database files",
        "author": "@username",  # Replace with the actual author's username or name
        "version": "0.1",  # Version number
        "date": "2022-10-25",  # Date of the latest version
        "requirements": "none",
        "category": "A2",
        "notes": "",
        "paths": ("**/*.DAT"),
        "function": "DroneFlightDATFiles"
    }
}

import glob
import  struct
import zlib,struct,os
import traceback
from datetime import datetime
import csv
from scripts.artifact_report import ArtifactHtmlReport
import scripts.ilapfuncs

acconfig = {5: ("M100", 8.5E7),      6:("P3I1", 600.0),          9:("P4", 4500000.0),
           14: ("M600", 4500000.0), 16:("MavicPro", 4500000.0), 17:("I2", 4500000.0),
           18: ("P4P", 4500000.0),  20:("S900", 4500000.0),     21:("SPARK", 4500000.0),
           23: ("M600", 4500000.0), 24:("MavicAir", 3850000.0), 25:("M200", 4500000.0),
           27: ("P4A", 4500000.0), 28: ("Matrice", 4500000.0), 36:("P4PV2", 4500000.0),
           39:("Tello", 4500000.0), 40:("P4RTK", 4500000.0), 41:("Mavic2", 3847700.0),
           51:("MavicEnterprise", 3847700), 53:("MavicMini", 8014713.88506), 58:("MavicAir2", 3830000.0),
           85:("MavicAir2", 3830000.0), 63:("MavicMini2", 8014713.88506) }
        
crc_table = [0x0000,0x1189,0x2312,0x329B,0x4624,0x57AD,0x6536,0x74BF,0x8C48,0x9DC1,0xAF5A,0xBED3,0xCA6C,0xDBE5,0xE97E,0xF8F7,
                0x1081,0x0108,0x3393,0x221A,0x56A5,0x472C,0x75B7,0x643E,0x9CC9,0x8D40,0xBFDB,0xAE52,0xDAED,0xCB64,0xF9FF,0xE876,
                0x2102,0x308B,0x0210,0x1399,0x6726,0x76AF,0x4434,0x55BD,0xAD4A,0xBCC3,0x8E58,0x9FD1,0xEB6E,0xFAE7,0xC87C,0xD9F5,
                0x3183,0x200A,0x1291,0x0318,0x77A7,0x662E,0x54B5,0x453C,0xBDCB,0xAC42,0x9ED9,0x8F50,0xFBEF,0xEA66,0xD8FD,0xC974,
                0x4204,0x538D,0x6116,0x709F,0x0420,0x15A9,0x2732,0x36BB,0xCE4C,0xDFC5,0xED5E,0xFCD7,0x8868,0x99E1,0xAB7A,0xBAF3,
                0x5285,0x430C,0x7197,0x601E,0x14A1,0x0528,0x37B3,0x263A,0xDECD,0xCF44,0xFDDF,0xEC56,0x98E9,0x8960,0xBBFB,0xAA72,
                0x6306,0x728F,0x4014,0x519D,0x2522,0x34AB,0x0630,0x17B9,0xEF4E,0xFEC7,0xCC5C,0xDDD5,0xA96A,0xB8E3,0x8A78,0x9BF1,
                0x7387,0x620E,0x5095,0x411C,0x35A3,0x242A,0x16B1,0x0738,0xFFCF,0xEE46,0xDCDD,0xCD54,0xB9EB,0xA862,0x9AF9,0x8B70,
                0x8408,0x9581,0xA71A,0xB693,0xC22C,0xD3A5,0xE13E,0xF0B7,0x0840,0x19C9,0x2B52,0x3ADB,0x4E64,0x5FED,0x6D76,0x7CFF,
                0x9489,0x8500,0xB79B,0xA612,0xD2AD,0xC324,0xF1BF,0xE036,0x18C1,0x0948,0x3BD3,0x2A5A,0x5EE5,0x4F6C,0x7DF7,0x6C7E,
                0xA50A,0xB483,0x8618,0x9791,0xE32E,0xF2A7,0xC03C,0xD1B5,0x2942,0x38CB,0x0A50,0x1BD9,0x6F66,0x7EEF,0x4C74,0x5DFD,
                0xB58B,0xA402,0x9699,0x8710,0xF3AF,0xE226,0xD0BD,0xC134,0x39C3,0x284A,0x1AD1,0x0B58,0x7FE7,0x6E6E,0x5CF5,0x4D7C,
                0xC60C,0xD785,0xE51E,0xF497,0x8028,0x91A1,0xA33A,0xB2B3,0x4A44,0x5BCD,0x6956,0x78DF,0x0C60,0x1DE9,0x2F72,0x3EFB,
                0xD68D,0xC704,0xF59F,0xE416,0x90A9,0x8120,0xB3BB,0xA232,0x5AC5,0x4B4C,0x79D7,0x685E,0x1CE1,0x0D68,0x3FF3,0x2E7A,
                0xE70E,0xF687,0xC41C,0xD595,0xA12A,0xB0A3,0x8238,0x93B1,0x6B46,0x7ACF,0x4854,0x59DD,0x2D62,0x3CEB,0x0E70,0x1FF9,
                0xF78F,0xE606,0xD49D,0xC514,0xB1AB,0xA022,0x92B9,0x8330,0x7BC7,0x6A4E,0x58D5,0x495C,0x3DE3,0x2C6A,0x1EF1,0x0F78]
def check_sum(data):
    v = 13970
    for i in data:
        v = (v >> 8) ^ crc_table[(i ^ v) & 0xFF]
    return v

class DatRecord:
    def __init__(self):
        self.start = 0
        self.len=0
        self.type = 0
        self.tickt_no = 0
        self.actual_ticket_no =0
        self.payload = b""
        #self.status = Record_Status_OK
    def __len__(self):
        return self.len
    def __repr__(self):
        return f"start:{self.start} len:{self.len} type:{self.type} ticket_no:{self.ticket_no} status:{self.status}"

class DATFile:
    def __init__(self, data):
        self.data = data
        if self.data[16:21] == b"BUILD":
            if self.data[242:252] == b"DJI_LOG_V3":
                self.record_start_pos = 256
            else:
                self.record_start_pos = 128
    def find_next55(self, start):
        try:
            return self.data.index(0x55, start)
        except:
            return -1

    def parse_records(self):
        record_count = 0
        record_list = []
        cur_pos = self.record_start_pos
        while True:
            if cur_pos >= len(self.data):
                break
            try:
                if self.data[cur_pos] != 0x55:
                    cur_pos += 1
                    raise Exception(f"Corrupted data at pos:{cur_pos-1}")
                record_len = self.data[cur_pos+1]
                if record_len < 10 or cur_pos+record_len>len(self.data):
                    cur_pos += 2
                    raise Exception(f"Corrupted record length at pos:{cur_pos-1}")
                crc = check_sum(self.data[cur_pos:cur_pos+record_len-2])
                if crc&0xFF != self.data[cur_pos+record_len-2] or crc>>8 != self.data[cur_pos+record_len-1]:
                    cur_pos += record_len
                    raise Exception(f"crc error at pos:{cur_pos-2}")
                record = DatRecord()
                record.start = cur_pos
                record.len =  record_len
                record.ticket_no = struct.unpack("<I", self.data[cur_pos+6:cur_pos+10])[0]
                record.type = (self.data[cur_pos+5]<<8) + self.data[cur_pos+4]
                record_list.append(record)
                cur_pos = cur_pos + record_len
                record_count += 1
            except Exception as e:
                cur_pos = self.find_next55(cur_pos)
                if cur_pos == -1:
                    break
        return record_list
        
    def parse_gps_records(self):
        gps_records = []
        def get_payload(record):
            payload = self.data[record.start+10:record.start+record.len-2]
            payload = bytes(map(lambda x:x^(record.ticket_no%256),payload)) # Potongan kode implementasi XOR pada parser
            return payload
        for v in [x for x in self.parse_records() if x.type ==2096 ]:
            date,time,longtitude,latitude = struct.unpack("<IIii", get_payload(v)[:16])
            year,month,day = int(date/10000),int(date/100)%100,date%100
            hour,minute,second = int(time/10000),int(time/100)%100,time%100
            gps_records.append([datetime(year,month,day,hour,minute,second), longtitude/(10**7),  latitude/(10**7)])
        return gps_records

def extract_dat(path):
    out = {}
    f = open(path, "rb")
    src_data = f.read()
    baseName = os.path.basename(path)
    if not baseName.startswith("DJI_"):
        fsize = os.path.getsize(path)
        out[baseName] = src_data[:fsize]
    else:   # 无人机内部的文件
        HEADER_SIZE = 283
        data = zlib.decompress(src_data)
        index = 0
        while True:
            try:
                file_size = struct.unpack("<I", data[index+1:index+5])[0]
                file_name = data[index+7:index+HEADER_SIZE]
                index += HEADER_SIZE
                file_name = file_name[:file_name.index(b"\x00")].decode("utf-8")
                out[file_name] = data[index:index+file_size]
                index += file_size
            except:
                if len(data)!=index:
                    print("toal size:",len(data))
                    print("processed size:", index)
                    traceback.print_exc()
                break
    return out

def DroneFlightDATFiles(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''

    for file_found in files_found:
        source_path = str(file_found)
        if not source_path.lower().endswith(".dat"):
            continue
        try:
            for key, value in extract_dat(source_path).items():
                # Filter file blob yang memuat data penerbangan
                if key.endswith(".DAT") and value[16:21] == b"BUILD":
                    for record in DATFile(value).parse_gps_records():
                        record_time = record[0]
                        longitude = record[1]
                        latitude = record[2]
                        data_list.append((record_time, longitude, latitude))
        except Exception as e:
            continue    
    data_headers = ("Timestamp", "Longitude", "Latitude")
     # HTML output:
    report = ArtifactHtmlReport("Cool stuff")
    report_name = "DroneFlight- DAT Files"
    report.start_artifact_report(report_folder, report_name)
    report.add_script()
    report.write_artifact_data_table(data_headers, data_list, files_found[0])  # assuming only the first file was processed
    report.end_artifact_report()

    # TSV output:
    scripts.ilapfuncs.tsv(report_folder, data_headers, data_list, report_name, files_found[0])  # assuming first file only

    # Timeline:
    scripts.ilapfuncs.timeline(report_folder, report_name, data_list, data_headers)