import importlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import bcrypt
import bencoding
import blackboxprotobuf
import fitdecode
import folium
import polyline
import pytz
import simplekml
import xlsxwriter
import xmltodict
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim
from packaging import version
from PIL import Image
from google.protobuf import descriptor
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


THIRD_PARTY_IMPORTS = (
    "bcrypt",
    "bs4",
    "bencoding",
    "blackboxprotobuf",
    "fitdecode",
    "folium",
    "geopy",
    "packaging",
    "PIL",
    "polyline",
    "google.protobuf",
    "Crypto",
    "pytz",
    "simplekml",
    "wheel",
    "xlsxwriter",
    "xmltodict",
)

REPO_ROOT = Path(__file__).resolve().parents[3]

CORE_MODULES = (
    "aleapp",
    "scripts.ilapfuncs",
    "scripts.plugin_loader",
    "scripts.artifacts.notification_history_pb.notificationhistory_pb2",
    "scripts.artifacts.usagestats_pb.usagestatsservice_pb2",
)


class TestDependencyCompatibility(unittest.TestCase):
    def test_declared_packages_are_importable(self):
        for module_name in THIRD_PARTY_IMPORTS:
            with self.subTest(module_name=module_name):
                importlib.import_module(module_name)

    def test_core_modules_import_under_supported_python(self):
        for module_name in CORE_MODULES:
            with self.subTest(module_name=module_name):
                importlib.import_module(module_name)

    def test_plugin_loader_imports_artifact_modules(self):
        from scripts.plugin_loader import PluginLoader

        loader = PluginLoader()
        self.assertGreater(len(loader), 0)

    def test_dependency_runtime_smoke_behaviors(self):
        self.assertTrue(bcrypt.checkpw(b"pw", bcrypt.hashpw(b"pw", bcrypt.gensalt())))

        self.assertEqual(bencoding.bdecode(bencoding.bencode({b"a": 1})), {b"a": 1})

        message, types = blackboxprotobuf.decode_message(b"\x08\x96\x01")
        self.assertEqual(message["1"], 150)
        self.assertEqual(types["1"]["type"], "int")

        self.assertTrue(hasattr(fitdecode, "FitReader"))

        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as html_file:
            try:
                folium.Map(location=[0, 0], zoom_start=1).save(html_file.name)
                self.assertGreater(os.path.getsize(html_file.name), 0)
            finally:
                os.unlink(html_file.name)

        self.assertEqual(Nominatim(user_agent="aleapp-test").scheme, "https")
        self.assertLess(version.parse("1.2.3"), version.parse("2.0.0"))

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as image_file:
            try:
                Image.new("RGB", (2, 2), color="red").save(image_file.name)
                with Image.open(image_file.name) as reopened:
                    self.assertEqual(reopened.size, (2, 2))
            finally:
                os.unlink(image_file.name)

        encoded = polyline.encode([(38.5, -120.2), (40.7, -120.95)])
        self.assertEqual(polyline.decode(encoded), [(38.5, -120.2), (40.7, -120.95)])

        self.assertIsNotNone(descriptor)

        key = b"0123456789abcdef"
        cipher = AES.new(key, AES.MODE_ECB)
        ciphertext = cipher.encrypt(pad(b"hello world", AES.block_size))
        self.assertEqual(unpad(cipher.decrypt(ciphertext), AES.block_size), b"hello world")

        self.assertEqual(pytz.timezone("UTC").zone, "UTC")

        with tempfile.NamedTemporaryFile(suffix=".kml", delete=False) as kml_file:
            try:
                kml = simplekml.Kml()
                kml.newpoint(name="x", coords=[(0, 0)])
                kml.save(kml_file.name)
                self.assertGreater(os.path.getsize(kml_file.name), 0)
            finally:
                os.unlink(kml_file.name)

        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as xlsx_file:
            try:
                workbook = xlsxwriter.Workbook(xlsx_file.name)
                worksheet = workbook.add_worksheet("Sheet1")
                worksheet.write(0, 0, "ok")
                workbook.close()
                self.assertGreater(os.path.getsize(xlsx_file.name), 0)
            finally:
                os.unlink(xlsx_file.name)

        self.assertEqual(xmltodict.parse("<root><a>1</a></root>")["root"]["a"], "1")
        self.assertEqual(BeautifulSoup("<p>hi</p>", "html.parser").p.text, "hi")

    def test_cli_help_runs_under_supported_python(self):
        result = subprocess.run(
            [sys.executable, "aleapp.py", "--help"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("ALEAPP: Android Logs, Events, and Protobuf Parser.", result.stdout)

    def test_imagetk_imports_when_tkinter_is_available(self):
        try:
            importlib.import_module("tkinter")
        except ModuleNotFoundError:
            self.skipTest("tkinter is not available in this Python build")

        importlib.import_module("PIL.ImageTk")


if __name__ == "__main__":
    unittest.main()
