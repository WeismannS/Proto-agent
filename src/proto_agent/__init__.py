"""
this package provides an ai agent framework that can be used both as a CLI tool
and imported as a library for custom apps.
"""

from .agent import Agent
from .agent_settings import AgentConfig


__version__ = "0.1.0"
__all__ = ["Agent", "AgentConfig"]
