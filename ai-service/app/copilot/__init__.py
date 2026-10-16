"""Analyst Copilot package for SecureFlow AI."""
from app.copilot.interfaces import ICopilotAgent
from app.copilot.agent import BankingCopilotAgent, get_copilot_agent

__all__ = ["ICopilotAgent", "BankingCopilotAgent", "get_copilot_agent"]
