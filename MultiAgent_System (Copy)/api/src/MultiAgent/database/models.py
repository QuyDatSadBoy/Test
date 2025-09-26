import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from ....core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    username = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    fullname = Column(String(255))
    role = Column(String(50), nullable=False, default="user", index=True)
    meta_data = Column(JSONB)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(UTC), index=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(UTC), onupdate=datetime.now(UTC), index=True)

    domains = relationship("Domain", back_populates="user", lazy="noload", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", lazy="noload", cascade="all, delete-orphan")


class Agent(Base):
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text)
    version = Column(String(50), index=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(UTC), index=True)

    conversations = relationship("Conversation", back_populates="agent", lazy="noload")
    steps = relationship("AgentStep", back_populates="agent", lazy="noload", cascade="all, delete")


class Tool(Base):
    __tablename__ = "tools"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(UTC), index=True)

    steps = relationship("AgentStep", back_populates="tool", lazy="noload", cascade="all, delete")


class Domain(Base):
    __tablename__ = "domains"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(UTC), index=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(UTC), onupdate=datetime.now(UTC), index=True)

    user = relationship("User", back_populates="domains", lazy="select")
    subdomains = relationship("Subdomain", back_populates="domain", lazy="noload", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="domains_user_name_uk"),
        Index("idx_domains_user_id", "user_id"),
    )


class Subdomain(Base):
    __tablename__ = "subdomains"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    domain_id = Column(UUID(as_uuid=True), ForeignKey("domains.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(UTC), index=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(UTC), onupdate=datetime.now(UTC), index=True)

    domain = relationship("Domain", back_populates="subdomains", lazy="select")
    documents = relationship("Document", back_populates="subdomain", lazy="noload", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("domain_id", "name", name="subdomains_domain_name_uk"),
        Index("idx_subdomains_domain_id", "domain_id"),
    )


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    subdomain_id = Column(UUID(as_uuid=True), ForeignKey("subdomains.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    path = Column(String(1024), nullable=False, index=True)
    file_type = Column(String(50), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(UTC), index=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(UTC), onupdate=datetime.now(UTC), index=True)

    subdomain = relationship("Subdomain", back_populates="documents", lazy="select")
    chunks = relationship("DocumentChunk", back_populates="document", lazy="noload", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("subdomain_id", "name", name="documents_subdomain_name_uk"),
        UniqueConstraint("path", name="documents_path_uk"),
        Index("idx_documents_subdomain_id", "subdomain_id"),
    )


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(UTC), index=True)

    document = relationship("Document", back_populates="chunks", lazy="select")

    __table_args__ = (
        UniqueConstraint("document_id", "chunk_index", name="document_chunks_doc_chunkidx_uk"),
        CheckConstraint("chunk_index >= 0", name="document_chunks_chunkidx_ck"),
        Index("idx_document_chunks_document_id", "document_id"),
    )


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(255), nullable=False, default="New chat", index=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(UTC), index=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(UTC), onupdate=datetime.now(UTC), index=True)

    user = relationship("User", back_populates="conversations", lazy="select")
    agent = relationship("Agent", back_populates="conversations", lazy="select")
    summaries = relationship("ConversationSummary", back_populates="conversation", lazy="noload", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="conversation", lazy="noload", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_conversations_user_id", "user_id"),
        Index("idx_conversations_agent_id", "agent_id"),
    )


class ConversationSummary(Base):
    __tablename__ = "conversation_summaries"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    index = Column(Integer, nullable=False, index=True)
    content = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(UTC), index=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(UTC), onupdate=datetime.now(UTC), index=True)

    conversation = relationship("Conversation", back_populates="summaries", lazy="select")

    __table_args__ = (
        UniqueConstraint("conversation_id", "index", name="conversation_summaries_conv_idx_uk"),
        CheckConstraint('"index" >= 0', name="conversation_summaries_idx_ck"),
        Index("idx_conversation_summaries_conversation_id", "conversation_id"),
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    list_agent_id = Column(JSONB)  # có thể lưu mảng UUIDs dạng JSON
    content = Column(Text, nullable=False)
    index = Column(Integer, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(UTC), index=True)

    conversation = relationship("Conversation", back_populates="messages", lazy="select")
    steps = relationship("AgentStep", back_populates="message", lazy="noload", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("conversation_id", "index", name="messages_conv_idx_uk"),
        CheckConstraint('"index" >= 0', name="messages_idx_ck"),
        Index("idx_messages_conversation_id", "conversation_id"),
    )


class AgentStep(Base):
    __tablename__ = "agent_steps"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    tool_id = Column(UUID(as_uuid=True), ForeignKey("tools.id", ondelete="CASCADE"), nullable=False, index=True)
    step = Column(Integer, nullable=False, index=True)
    step_retry = Column(Integer, nullable=False, default=0, index=True)
    tool_input = Column(JSONB)
    tool_output = Column(JSONB)
    meta_data = Column(JSONB)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(UTC), index=True)

    message = relationship("Message", back_populates="steps", lazy="select")
    agent = relationship("Agent", back_populates="steps", lazy="select")
    tool = relationship("Tool", back_populates="steps", lazy="select")

    __table_args__ = (
        UniqueConstraint("message_id", "step", name="agent_steps_msg_step_uk"),
        CheckConstraint("step >= 1", name="agent_steps_step_ck"),
        CheckConstraint("step_retry >= 0", name="agent_steps_step_retry_ck"),
        Index("idx_agent_steps_message_id", "message_id"),
        Index("idx_agent_steps_agent_id", "agent_id"),
        Index("idx_agent_steps_tool_id", "tool_id"),
    )
