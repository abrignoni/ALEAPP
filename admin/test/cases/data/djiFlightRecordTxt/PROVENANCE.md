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

Case 3 contains all three original TXT flight logs from VTO/NIST DF020's
`2018_June/mobile_android_logical/Android_Logical.zip`, with their original
archive paths and member times. The publisher archive MD5 was verified as
`6bc5cdc147e813f8744c04814a89e18a`. The two `dji.go.v4` logs are version 11
from June 19, 2018. The `dji.pilot` log is version 9 from October 10, 2017;
it is retained as an older log, not claimed as a June salted flight. Individual
SHA256 hashes and validation counts are in `admin/docs/df020_txt_validation.json`.
The dataset's MIT notice is preserved in `DF020_DATASET_LICENSE.txt` beside
the fixture zips. Each case 3 zip is below 10 MB.

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
