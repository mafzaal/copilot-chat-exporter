"""
Copilot Chat History Exporter

A tool to export chat history from GitHub Copilot Chat in VS Code.
"""

from copilot_chat_exporter.core.models import ChatMessage, ChatSession
from copilot_chat_exporter.core.exporter import CopilotChatExporter

__version__ = "0.1.0"
__all__ = ["CopilotChatExporter", "ChatMessage", "ChatSession"]
