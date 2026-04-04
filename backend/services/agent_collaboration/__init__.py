"""
Agent Collaboration Package
Enables sophisticated agent-to-agent communication and orchestration
"""
from .collaboration_protocol import (
    AgentRole,
    MessageType,
    AgentMessage,
    AgentCollaborationHub,
    EnhancedPromptTemplate,
    collaboration_hub
)

__all__ = [
    'AgentRole',
    'MessageType',
    'AgentMessage',
    'AgentCollaborationHub',
    'EnhancedPromptTemplate',
    'collaboration_hub'
]
