# Public Images Behind `sample_data`

Artifacts record what they produced against a named corpus:

```python
"sample_data": {
    "galaxys10_a10": "Android 10 | 61 rows",
}
```

The key names an entry in a corpus registry (`samples.json`) that lives with the test data rather
than in this repository, because most extractions are not ours to distribute. That is fine for
`admin/scripts/validate_sample_data.py`, which reads the registry directly, but it leaves anyone
reading an artifact with a bare key and no way to tell which image produced the count.

This document closes that gap for the keys that name **publicly available** images. If you want to
reproduce a recorded row count, this is where you find out what to download.

Keys naming non-public images are listed at the end so you know not to go looking.

`admin/image_manifest.json` carries the same public keys in machine-readable form, one entry per
key, and `admin/test/scripts/make_test_data.py` reads it to find your local copy. Anything added
here should be added there too, and the other way round.

## How to read the "correlated by" column

The identification is not equally strong for every row, and the difference matters if you are
relying on it.

- **MD5** means the file we hold was hashed and the digest equals the value the publisher
  distributes. That is a definitive identification.
- **Extraction metadata** means our copy is the inner image un-nested from the publisher's wrapper
  archive, so its hash cannot match the published wrapper by construction. The link comes from the
  publisher's own packaging and the documentation inside the extraction naming the event and the
  persona (`DeviceInfo.txt`, the `.ufd`, an `image_info.txt`, the folder structure).
- **Publisher datasheet** means the publisher distributes a hash for the file itself and our copy
  matches it.
- **Inferred** means none of the above. Read the note before relying on it.

The MD5 column is the publisher's own published value, not something measured here, except on the
rows marked MD5 where the two are known to agree.

## Android images

| `sample_data` key | Device and OS | Published by | Published file | MD5 (as published) | Correlated by |
| --- | --- | --- | --- | --- | --- |
| `galaxys10_a10` | Samsung Galaxy S10 SM-G973F, Android 10 | DFRWS 2021 Challenge | `3_Samsung GSM_SM-G973F_DS Galaxy S10.zip` | `A86049E46D1E19A961A3AECD97B78BD5` | **MD5** |
| `cookbook_a11` | Samsung Galaxy S21 SM-G991U, Android 11 | Cody Bounds, Digital Forensics Cookbook Datasets | `Android.7z` | `7188177ACDC73A5EDB8F6B969E9D6881` | Extraction metadata |
| `pixel3_a11` | Google Pixel 3, Android 11 | Josh Hickman, public images | `android_11.zip` | `9553729D10BC6CAE84916A506CB74D98` | Extraction metadata |
| `pixel3_a12` | Google Pixel 3, Android 12 | Josh Hickman, public images | `android_12.zip` | `B9CB5E213B765D5D649A9634E119B3AA` | Extraction metadata |
| `russell_pixel6a_a13` | Google Pixel 6a, Android 13 | Cellebrite CTF 2023 ("Russell") | `CellebriteCTF23_Russell.zip` | `DC5C077DBD2C2DF6C644473447DE092B` | Extraction metadata |
| `sharon_a13` | Samsung Galaxy S21 5G SM-G991B, Android 13 | Cellebrite CTF 2023 ("Sharon") | `CellebriteCTF23_Sharon.zip` | `C94AB827D5AF5ED22A394FD45D676DE3` | Extraction metadata |
| `userb2_a13` | Android 13, data partition only | Hexordia, Magnet Virtual Summit CTF 2025 | `UserB2.7z` | `76077DCE06C68D8EC5505173180E0A5F` | Extraction metadata |
| `russell_a14` | Google Pixel 6a, Android 14 | Cellebrite CTF 2024 ("Russell") | `CellebriteCTF24_Russell.zip` | `E182FC05A9B83FCACC9582DB92CEF6C8` | Extraction metadata |
| `sharon_a14` | Samsung Galaxy S21 SM-G991B, Android 14 | Cellebrite CTF 2024 ("Sharon") | `CellebriteCTF24_Sharon.zip` | `514BF12C5862B20937F9F808932B1368` | Extraction metadata |
| `samsunga53_a14` | Samsung A53 SM-S536DL, Android 14 | Hexordia, Magnet Virtual Summit CTF 2026 | `SamsungA53.zip` | `BEE600ECC8086325211A4AB5CBF5FF47` | Extraction metadata |
| `pixel7a_a14` | Google Pixel 7a, Android 14 | Josh Hickman, public images | `Android_14_Public_Image.tar.gz` | `2F9578715A315C0897E51EF9C1007F2D` | **Inferred**, see below |
| `anne_a15` | Samsung SM-S911U1, Android 15 | Cellebrite CTF 2025 ("Anne Lockwood") | `2025CellebriteCTF_AnneLockwood.zip` | `D2E42194B1B16E35FBB0F84EEF924FB5` | Extraction metadata |
| `kevin_pocox7_a15` | Xiaomi Poco X7 Pro, Android 15 | Cellebrite CTF 2025 ("Kevin Mallory") | `2025CellebriteCTF_KevinMallory.zip` | `3DBE94D72CB6C76F03E0995F1F20E55E` | Extraction metadata |
| `df020_mavic_pro_android` | Paired phone for a DJI Mavic Pro, Android logical | VTO Labs / NIST CFReDS Drone Forensics Program, ref DF020 | `Android_Logical.zip` | `6BC5CDC147E813F8744C04814A89E18A` | Publisher datasheet |

**`pixel7a_a14` is the one row not to quote as established.** The extraction is a UFED full
filesystem of a Pixel 7a on Android 14 taken 2024-07-28, which is the same date as our copy of
Hickman's iOS 17 extraction, and both were announced in his September 2024 release post. But that
post does not state the Android device model, so the device is not sourced, and the published
`tar.gz` is a different container from the extraction we hold, so no hash comparison is possible.
Treat the link as probable rather than proven.

## Where to download

| Publisher | Source |
| --- | --- |
| Josh Hickman | <https://digitalcorpora.org/corpora/cell-phones/> and the release posts on <https://thebinaryhick.blog/> |
| VTO Labs Drone Forensics Program | <https://cfreds.nist.gov/all/VTO/DroneForensics> and <https://www.vtolabs.com/drone-forensics> |
| Everything above, indexed together | The Evidence Locker, <https://theevidencelocker.github.io/> |

The Evidence Locker is the most convenient single index. It publishes a filename, size, MD5 and
download link per image, and its `data.json` is the same catalog in machine-readable form. The
drone dataset is not in it and comes from NIST CFReDS.

Two things to know before you verify a download against the Evidence Locker. Its `filesize` values
are GiB even though the unit prints as "GB", so compare `bytes / 2**30`. And five of its hash
values carry a stray character (four Cellebrite CTF 2024 entries contain an embedded soft hyphen,
U+00AD, and one Magnet 2023 entry a trailing space). The Cellebrite CTF 2024 hashes above are
reproduced with the soft hyphen removed, which is why they may not look like a byte-for-byte copy
of the site.

## Keys that name non-public images

These appear in `sample_data` and cannot be downloaded. They are recorded so a reader knows the
count came from a real image rather than a synthetic fixture, and so nobody spends time hunting for
a file that was never distributed.

| Key | What it is |
| --- | --- |
| `hc_pixel8pro_a16` | Google Pixel 8 Pro, Android 16, UFED. Not distributed. |
| `hc_pixel8pro_a17` | Google Pixel 8 Pro, Android 17, UFED full filesystem. Not distributed. |
| `s20fe_a13` | Samsung SM-G781U Galaxy S20 FE 5G, Android 13, UFED Inseyets filesystem acquired 2026-07-24. A local acquisition, not a public release. |
| `samsungs20_a13` | Samsung S20 full filesystem, Android 13. Provenance not established. Checked by size against the whole Evidence Locker catalog with no candidate match, so it is not one of the images indexed there. |

If you hold an image that would let one of these counts be reproduced publicly, that is a
genuinely useful contribution.

## The matching iOS document

iLEAPP carries the same mapping for its own keys at
`admin/docs/testing/public_corpus_images.md`. The two cores do not share corpus keys, so neither
document covers the other's.
