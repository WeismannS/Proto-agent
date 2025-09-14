import unittest
from proto_agent import Agent, AgentConfig


class TestAgent(unittest.TestCase):
    """Test agent creation and basic functionality"""

    def test_agent_config_creation(self):
        config = AgentConfig(
            api_key="test_key",
            working_directory="./test_dir",
            model="gemini/gemini-2.0-flash-001",
        )
        self.assertEqual(config.api_key, "test_key")
        self.assertTrue(str(config.working_directory).endswith("test_dir"))
        self.assertEqual(config.model, "gemini/gemini-2.0-flash-001")

    def test_agent_initialization(self):
        config = AgentConfig(
            api_key="test_key",
            working_directory="./test_dir",
            model="gemini/gemini-2.0-flash-001",
        )
        agent = Agent(config)
        self.assertIsNotNone(agent)
        self.assertEqual(agent.settings.api_key, "test_key")

    def test_agent_library_import(self):
        self.assertTrue(callable(Agent))
        self.assertTrue(callable(AgentConfig))
