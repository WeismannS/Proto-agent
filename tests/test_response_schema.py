import unittest
from dotenv import load_dotenv
from platformdirs import user_config_dir
from pydantic import BaseModel, Field
from proto_agent import Agent, AgentConfig
import os


class User(BaseModel):
    name: str
    age: int = Field(gt=0)


class ListOfUsers(BaseModel):
    users: list[User]


class TestResponseSchema(unittest.TestCase):
    """Test response schema functionality with Pydantic models"""

    def setUp(self):
        load_dotenv(dotenv_path=user_config_dir("proto-agent") + "/.env")
        self.agent_config = AgentConfig(
            api_key=os.getenv("API_KEY"),
            model="gemini/gemini-2.0-flash-001",
            working_directory=".",
        )
        self.agent = Agent(self.agent_config)

    def test_response_schema_filtering(self):
        """Test that response schema correctly filters users with missing required fields"""
        response = self.agent.generate_content(
            "the cinema has 3 users in the database: billy aged 13, willhiam aged 10, and emily (no age provided - age is unknown). Only include users where ALL required fields are available.",
            verbose=True,
            response_model=ListOfUsers,
        )

        expected_data = {
            "users": [{"name": "billy", "age": 13}, {"name": "willhiam", "age": 10}]
        }
        self.assertEqual(response.response_object.extracted_content, expected_data)
