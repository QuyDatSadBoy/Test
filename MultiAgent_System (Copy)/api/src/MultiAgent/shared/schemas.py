
# src/agents/shared/schemas.py 
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union, Literal
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, field_validator
from pydantic.types import UUID4
import uuid

# ===== Core Enums =====
class AgentType(str, Enum):
    """Types of agents in the system"""
    ORCHESTRATOR = "orchestrator"
    RAG = "rag"
    ANALYSIS = "analysis"

class TaskStatus(str, Enum):
    """Task execution statuses"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class WorkflowType(str, Enum):
    """Predefined workflow types"""
    RAG_ONLY = "rag_only"
    ANALYSIS_ONLY = "analysis_only"
    RAG_THEN_ANALYSIS = "rag_then_analysis"  # 🆕 Thêm workflow combo
    CUSTOM = "custom"

class AnalysisType(str, Enum):  # 🆕 Analysis types
    """Simple analysis types"""
    SUMMARY = "summary"
    SENTIMENT = "sentiment"
    TREND = "trend"
    CUSTOM = "custom"

# ===== Essential Base Schemas =====
class BaseResponse(BaseModel):
    """Base response schema"""
    success: bool = True
    message: str = "Operation completed successfully"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ===== Core Agent Schemas (MVP) =====
class AgentTaskBase(BaseModel):
    """Base schema for agent tasks"""
    agent_type: AgentType
    input_data: Dict[str, Any]
    priority: int = Field(default=5, ge=1, le=10)

class AgentTaskCreate(AgentTaskBase):
    """Schema for creating agent tasks"""
    pass

class AgentTaskResponse(AgentTaskBase):
    """Schema for agent task responses"""
    model_config = ConfigDict(from_attributes=True)
    id: UUID4
    status: TaskStatus
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

# ===== Essential Workflow Schemas =====
class WorkflowCreate(BaseModel):
    """Schema for creating workflows - simplified"""
    workflow_type: WorkflowType
    name: str = Field(..., min_length=1, max_length=255)
    input_data: Dict[str, Any]

class WorkflowResponse(BaseModel):
    """Schema for workflow responses - simplified"""
    model_config = ConfigDict(from_attributes=True)
    id: UUID4
    workflow_type: WorkflowType
    name: str
    status: TaskStatus
    created_at: datetime

# ===== Simple RAG Schema =====
class RAGRequest(BaseModel):
    """Simple RAG request"""
    query: str = Field(..., min_length=3, max_length=1000)
    limit: int = Field(default=5, ge=1, le=20)

    @field_validator('query')
    @classmethod
    def validate_query(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError('Query must be at least 3 characters long')
        return v

class RAGResponse(BaseModel):
    """Simple RAG response"""
    query: str
    response: str
    sources: List[str] = Field(default_factory=list)
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)

# ===== Simple Analysis Schema 🆕 =====
class AnalysisRequest(BaseModel):
    """Simple analysis request"""
    data: Dict[str, Any] = Field(..., description="Data to analyze")
    analysis_type: AnalysisType = Field(default=AnalysisType.SUMMARY)
    model: str = Field(default="gpt-4", description="LLM model to use")
    custom_prompt: Optional[str] = Field(None, max_length=500, description="Custom analysis instructions")

    @field_validator('data')
    @classmethod
    def validate_data(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        if not v:
            raise ValueError('Data cannot be empty')
        return v

class AnalysisResponse(BaseModel):
    """Simple analysis response"""
    analysis_type: AnalysisType
    results: Dict[str, Any]
    insights: List[str] = Field(default_factory=list)
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    execution_time_ms: Optional[float] = None

# ===== Multi-Agent Workflow Schema 🆕 =====
class MultiAgentWorkflowRequest(BaseModel):
    """Request for multi-agent workflow (RAG + Analysis)"""
    query: str = Field(..., min_length=3, max_length=1000, description="Initial query for RAG")
    analysis_type: AnalysisType = Field(default=AnalysisType.SUMMARY, description="Type of analysis to perform on RAG results")
    rag_limit: int = Field(default=5, ge=1, le=20, description="Number of documents to retrieve")
    custom_analysis_prompt: Optional[str] = Field(None, max_length=500)

    @field_validator('query')
    @classmethod
    def validate_query(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError('Query must be at least 3 characters long')
        return v

class MultiAgentWorkflowResponse(BaseModel):
    """Response from multi-agent workflow"""
    workflow_id: UUID4
    query: str
    rag_result: RAGResponse
    analysis_result: AnalysisResponse
    final_summary: Optional[str] = None
    total_execution_time_ms: Optional[float] = None


# ===== Orchestrator-Specific Schemas =====

class OrchestrationStep(BaseModel):
    """Individual step in orchestration"""
    step_id: str = Field(..., description="Unique step identifier")
    agent_type: AgentType
    action: str = Field(..., description="Action to perform")
    input_data: Dict[str, Any]
    depends_on: List[str] = Field(default_factory=list, description="Step dependencies")
    timeout_seconds: int = Field(default=300)
    retry_count: int = Field(default=3, ge=0, le=10)

class OrchestrationPlan(BaseModel):
    """Complete orchestration execution plan"""
    plan_id: UUID4 = Field(default_factory=uuid.uuid4)
    steps: List[OrchestrationStep]
    execution_mode: Literal["sequential", "parallel", "conditional"] = "sequential"
    total_estimated_time: Optional[int] = None

class OrchestratorRequest(BaseModel):
    """Request schema for Orchestrator agent"""
    task_type: Literal["single_agent", "multi_agent", "custom_workflow"] = "multi_agent"
    target_agents: List[AgentType] = Field(..., min_items=1, description="Agents to orchestrate")
    orchestration_plan: Optional[OrchestrationPlan] = None
    input_data: Dict[str, Any]
    execution_options: Dict[str, Any] = Field(default_factory=dict)
    callback_url: Optional[str] = None

class AgentExecutionResult(BaseModel):
    """Result from individual agent execution"""
    agent_type: AgentType
    step_id: str
    success: bool
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time_seconds: float
    metadata: Dict[str, Any] = Field(default_factory=dict)

class OrchestratorResponse(BaseModel):
    """Response schema for Orchestrator agent"""
    orchestration_id: UUID4
    task_type: str
    overall_status: TaskStatus
    execution_plan: OrchestrationPlan
    agent_results: List[AgentExecutionResult] = Field(default_factory=list)
    final_output: Optional[Dict[str, Any]] = None
    total_execution_time: Optional[float] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

# ===== Predefined Orchestration Templates =====

class OrchestrationTemplate(str, Enum):
    """Predefined orchestration templates"""
    RAG_SEARCH = "rag_search"  # Simple RAG
    DATA_ANALYSIS = "data_analysis"  # Simple Analysis  
    RAG_THEN_ANALYSIS = "rag_then_analysis"  # Sequential RAG -> Analysis
    PARALLEL_RAG_ANALYSIS = "parallel_rag_analysis"  # Parallel RAG + Analysis
    CUSTOM = "custom"

class TemplateRequest(BaseModel):
    """Request using predefined template"""
    template: OrchestrationTemplate
    parameters: Dict[str, Any]
    execution_options: Dict[str, Any] = Field(default_factory=dict)

    @field_validator('parameters')
    @classmethod
    def validate_template_parameters(cls, v: Dict[str, Any], info) -> Dict[str, Any]:
        template = info.data.get('template') if info.data else None
        
        if template == OrchestrationTemplate.RAG_SEARCH:
            if 'query' not in v:
                raise ValueError('RAG_SEARCH template requires "query" parameter')
        elif template == OrchestrationTemplate.DATA_ANALYSIS:
            if 'data' not in v:
                raise ValueError('DATA_ANALYSIS template requires "data" parameter')
        elif template == OrchestrationTemplate.RAG_THEN_ANALYSIS:
            if 'query' not in v:
                raise ValueError('RAG_THEN_ANALYSIS template requires "query" parameter')
        
        return v

class TemplateResponse(BaseModel):
    """Response from template execution"""
    template: OrchestrationTemplate
    orchestration_result: OrchestratorResponse
    template_specific_output: Dict[str, Any] = Field(default_factory=dict)

# ===== Agent Coordination Schemas =====

class AgentStatus(BaseModel):
    """Status of individual agent"""
    agent_type: AgentType
    status: Literal["available", "busy", "error", "offline"]
    current_tasks: int = 0
    last_heartbeat: datetime
    capabilities: List[str] = Field(default_factory=list)

class CoordinationRequest(BaseModel):
    """Request for agent coordination"""
    coordination_type: Literal["check_availability", "assign_task", "get_status"]
    target_agents: List[AgentType]
    task_requirements: Optional[Dict[str, Any]] = None

class CoordinationResponse(BaseModel):
    """Response from agent coordination"""
    available_agents: List[AgentStatus]
    recommendations: List[str] = Field(default_factory=list)
    estimated_wait_time: Optional[int] = None
    

# Export core schemas
__all__ = [
    # Enums
    'AgentType', 'TaskStatus', 'WorkflowType', 'AnalysisType', 'OrchestrationTemplate',
    
    # Base schemas
    'BaseResponse',
    
    # Agent Task schemas
    'AgentTaskBase', 'AgentTaskCreate', 'AgentTaskResponse',
    
    # Workflow schemas
    'WorkflowCreate', 'WorkflowResponse',
    
    # RAG schemas
    'RAGRequest', 'RAGResponse',
    
    # Analysis schemas
    'AnalysisRequest', 'AnalysisResponse',
    
    # Orchestrator schemas
    'OrchestrationStep', 'OrchestrationPlan', 'OrchestratorRequest', 'OrchestratorResponse',
    'AgentExecutionResult', 'TemplateRequest', 'TemplateResponse',
    'AgentStatus', 'CoordinationRequest', 'CoordinationResponse',
    
    # Multi-agent workflow schemas
    'MultiAgentWorkflowRequest', 'MultiAgentWorkflowResponse'
]