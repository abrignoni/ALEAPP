import importlib
import unittest


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

    def test_imagetk_imports_when_tkinter_is_available(self):
        try:
            import tkinter  # noqa: F401
        except ModuleNotFoundError:
            self.skipTest("tkinter is not available in this Python build")

        from PIL import ImageTk  # noqa: F401


if __name__ == "__main__":
    unittest.main()
