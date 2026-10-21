import ast
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock


ROOT_DIR = Path(__file__).resolve().parents[2]
GUI_PATH = ROOT_DIR / "aleappGUI.py"


def load_show_history_menu(menu):
    tree = ast.parse(GUI_PATH.read_text(encoding="utf-8"))
    function = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "show_history_menu"
    )
    module = ast.Module(body=[function], type_ignores=[])
    code = compile(ast.fix_missing_locations(module), str(GUI_PATH), "exec")
    namespace = {
        "history": SimpleNamespace(is_history_enabled=lambda: False),
        "input_entry": Mock(),
        "main_window": object(),
        "tk": SimpleNamespace(Menu=Mock(return_value=menu)),
    }
    namespace["input_entry"].winfo_rootx.return_value = 20
    # Importing aleappGUI creates a Tk root and enters mainloop; run this function only.
    exec(code, namespace)  # pylint: disable=exec-used
    return namespace["show_history_menu"]


class TestHistoryMenuAnchor(unittest.TestCase):
    def test_history_disabled_menu_is_anchored_to_clicked_button(self):
        menu = Mock()
        button = Mock()
        button.winfo_rootx.return_value = 420
        button.winfo_rooty.return_value = 115
        button.winfo_height.return_value = 24

        load_show_history_menu(menu)(button, "output")

        menu.add_command.assert_called_once_with(
            label="(History Disabled - Enable in Settings)", state="disabled"
        )
        menu.post.assert_called_once_with(420, 139)


if __name__ == "__main__":
    unittest.main()
