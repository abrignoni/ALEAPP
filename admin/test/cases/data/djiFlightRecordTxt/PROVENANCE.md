# DJI TXT fixture provenance

Case 1 is synthetic binary test data authored for this module. It contains version
6 and version 12 records with known coordinates, units, timestamps and gimbal
angles. It does not claim to be a mobile extraction or the DF020 corpus.

Case 2 contains the original public example from
[pydjirecord](https://github.com/rembish/pydjirecord/blob/cabbce1bb8c24bb00bd861af80aac7601c03e5f6/examples/DJIFlightRecord_2024-09-01_%5B14-55-49%5D.txt),
commit `cabbce1bb8c24bb00bd861af80aac7601c03e5f6`, unchanged. It is a version 14
encrypted log. Android-style archive paths were chosen for the test and do not
establish the acquisition device's OS or original filesystem paths.
The original TXT bytes are packaged twice because ALEAPP uses one fixture per
artifact. No API key or keychain is included.

Case 3 comes from VTO/NIST DF020's
`2018_June/mobile_android_logical/Android_Logical.zip`. The publisher archive MD5 was
verified as `6bc5cdc147e813f8744c04814a89e18a`. The two `dji.go.v4` logs are version 11
from June 19, 2018. The `dji.pilot` log is version 9 from October 10, 2017;
it is retained as an older log, not claimed as a June salted flight.

The Summary case 3 zip holds the three original logs, unchanged, with their original
archive paths and member times. SHA256:

- `DJIFlightRecord_2018-06-19_[14-50-34].txt`: `0a9f1816d52a98f840f6e67c08a14473ae5a0a2e75e9484d5de66368c4fd4c4a`
- `DJIFlightRecord_2018-06-19_[18-48-38].txt`: `ab5bbc58a921d81c323a76c3a9d955fde58d503536facf43306e7e6bbb208c8d`
- `DJIFlightRecord_2017-10-10_[10-02-22].txt`: `f134bef34e6877ae5a030297f56ae6e12fe946b468c5143ef9976c08170295f8`

The Records case 3 zip holds shortened copies of two of them, so the recorded baseline
stays small (the full Records baseline was about 42 MB). Each copy keeps the original
100-byte prefix, the first N complete records, and the original Details block, with the
prefix's Details offset rewritten to the new position. Nothing inside a kept record is
changed. Archive paths and member times are the originals.

- `DJIFlightRecord_2018-06-19_[18-48-38].txt`: first 60 records, plus the 4 bytes that
  sat between the last complete record and the Details block in the original, so the
  stopped-parse warning is still exercised. SHA256 of the copy:
  `d48094f0a54c5e5b9a0338f408f367391896bb92fc12e3b9792d06657ee2794c`.
- `DJIFlightRecord_2017-10-10_[10-02-22].txt`: first 170 records. SHA256 of the copy:
  `e5e9d6c0b5b10631696eeba60e4ab95aa09446db3f4a429a91e1d886f53e67b5`.

Together the two copies contain every record type the Records artifact decodes into
fields, App Tip and App Warning messages, and types it counts without reporting. App
Serious Warning (type 24) does not occur in DF020. The dataset's MIT notice is preserved in
`DF020_DATASET_LICENSE.txt` beside the fixture zips.

The case 2 public example is distributed with this license:

MIT License

Copyright (c) 2025 pydjirecord contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
