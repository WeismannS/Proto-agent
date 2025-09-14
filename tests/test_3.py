import unittest
import tempfile
from proto_agent.tool_kits import FileOperationToolkit, SystemInfoToolkit
from proto_agent.tool_kit_registry import ToolKitRegistery


class TestToolkits(unittest.TestCase):
    """Test toolkit creation and basic functionality"""

    def setUp(self):
        ToolKitRegistery._functions.clear()
        ToolKitRegistery._schemas.clear()

    def test_file_toolkit_creation(self):
        toolkit = FileOperationToolkit()
        self.assertIsNotNone(toolkit)
        self.assertGreater(len(toolkit.schemas), 0)

    def test_system_toolkit_creation(self):
        toolkit = SystemInfoToolkit()
        self.assertIsNotNone(toolkit)
        self.assertGreater(len(toolkit.schemas), 0)

    def test_toolkit_functionality(self):
        with tempfile.TemporaryDirectory():
            toolkit = FileOperationToolkit()
            self.assertIsNotNone(toolkit.tool)
            self.assertGreater(len(toolkit.tool.function_declarations), 0)

        system_toolkit = SystemInfoToolkit()
        self.assertIsNotNone(system_toolkit.tool)
        self.assertGreater(len(system_toolkit.tool.function_declarations), 0)
