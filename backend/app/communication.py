"""
Inter-Agent Communication Protocol

Enables fire and sanitation agents to communicate and coordinate decisions.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Types of inter-agent messages"""
    REQUEST_ASSISTANCE = "request_assistance"
    OFFER_SUPPORT = "offer_support"
    STATUS_UPDATE = "status_update"
    RESOURCE_ALLOCATION = "resource_allocation"
    COORDINATION_NEEDED = "coordination_needed"
    ACKNOWLEDGEMENT = "acknowledgement"


class MessagePriority(Enum):
    """Message priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class AgentMessage:
    """Message structure for inter-agent communication"""
    
    def __init__(
        self,
        from_agent: str,
        to_agent: str,
        message_type: MessageType,
        priority: MessagePriority,
        content: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ):
        self.id = f"{from_agent}_{datetime.now().timestamp()}"
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.message_type = message_type
        self.priority = priority
        self.content = content
        self.context = context or {}
        self.timestamp = datetime.now()
        self.status = "pending"
        self.response = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            "id": self.id,
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "message_type": self.message_type.value,
            "priority": self.priority.value,
            "content": self.content,
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status,
            "response": self.response
        }


class MessageBus:
    """Central message bus for inter-agent communication"""
    
    def __init__(self):
        self.messages: List[AgentMessage] = []
        self.subscribers: Dict[str, List] = {}
        logger.info("✓ Message Bus initialized")
    
    def publish(self, message: AgentMessage) -> None:
        """Publish a message to the bus"""
        self.messages.append(message)
        logger.info(
            f"📨 Message published: {message.from_agent} → {message.to_agent} "
            f"[{message.message_type.value}] Priority: {message.priority.name}"
        )
    
    def get_messages_for_agent(
        self, 
        agent_name: str, 
        status: Optional[str] = "pending"
    ) -> List[AgentMessage]:
        """Get all messages for a specific agent"""
        messages = [
            msg for msg in self.messages
            if msg.to_agent == agent_name and msg.status == status
        ]
        return messages
    
    def acknowledge_message(self, message_id: str, response: Dict[str, Any]) -> None:
        """Acknowledge a message with a response"""
        for msg in self.messages:
            if msg.id == message_id:
                msg.status = "acknowledged"
                msg.response = response
                logger.info(f"✓ Message {message_id} acknowledged")
                break
    
    def get_all_messages(self) -> List[Dict[str, Any]]:
        """Get all messages as dictionaries"""
        return [msg.to_dict() for msg in self.messages]


# Global message bus instance
_message_bus: Optional[MessageBus] = None


def get_message_bus() -> MessageBus:
    """Get or create global message bus"""
    global _message_bus
    if _message_bus is None:
        _message_bus = MessageBus()
    return _message_bus


def reset_message_bus() -> None:
    """Reset the message bus (useful for testing)"""
    global _message_bus
    _message_bus = MessageBus()
    logger.info("🔄 Message bus reset")
