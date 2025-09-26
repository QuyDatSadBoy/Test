# tests/test_schemas.py 
import sys
import os  
import pytest
from datetime import datetime, timezone
import uuid

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, root_path)


from api.src.MultiAgent.shared.schemas import *

def test_agent_type_enum():
    """Test AgentType enum values"""
    assert AgentType.ORCHESTRATOR == "orchestrator"
    assert AgentType.RAG == "rag"
    assert AgentType.ANALYSIS == "analysis"

def test_analysis_type_enum():
    """Test AnalysisType enum"""
    assert AnalysisType.SUMMARY == "summary"
    assert AnalysisType.SENTIMENT == "sentiment"
    assert AnalysisType.TREND == "trend"
    assert len(AnalysisType) == 4

def test_workflow_type_enum():
    """Test WorkflowType includes RAG_ONLY"""
    assert WorkflowType.RAG_ONLY == "rag_only"

def test_analysis_request():
    """Test AnalysisRequest schema validation"""
    # Valid request
    analysis = AnalysisRequest(
        data={"text": "Sample data to analyze"},
        analysis_type="summary",
        model="gpt-4"
    )
    assert analysis.data["text"] == "Sample data to analyze"
    assert analysis.analysis_type == AnalysisType.SUMMARY
    assert analysis.model == "gpt-4"

def test_analysis_request_validation():
    """Test AnalysisRequest validation"""
    # Empty data should fail
    with pytest.raises(ValueError):
        AnalysisRequest(
            data={},  # Empty data
            analysis_type="summary"
        )

def test_analysis_response():
    """Test AnalysisResponse schema"""
    response = AnalysisResponse(
        analysis_type="sentiment",
        results={"sentiment": "positive", "score": 0.8},
        insights=["Text shows positive sentiment"],
        confidence_score=0.85
    )
    
    assert response.analysis_type == AnalysisType.SENTIMENT
    assert response.results["sentiment"] == "positive"
    assert len(response.insights) == 1
    assert response.confidence_score == 0.85

def test_rag_response_with_confidence():
    """Test RAGResponse includes confidence_score"""
    response = RAGResponse(
        query="test query",
        response="test response",
        sources=["source1"],
        confidence_score=0.9
    )
    
    assert response.confidence_score == 0.9

def test_base_response_timezone():
    """Test BaseResponse uses UTC timezone"""
    response = BaseResponse()
    assert response.timestamp.tzinfo is not None  # Has timezone info

# Integration test
def test_full_workflow_schemas():
    """Test schemas work together"""
    # Create workflow
    workflow = WorkflowCreate(
        workflow_type="rag_then_analysis",
        name="Test Multi-Agent Workflow",
        input_data={
            "query": "Analyze AI market trends",
            "analysis_type": "trend"
        }
    )
    
    # Create RAG request from workflow data
    rag_request = RAGRequest(
        query=workflow.input_data["query"],
        limit=5
    )
    
    # Create Analysis request
    analysis_request = AnalysisRequest(
        data={"rag_results": "mock rag data"},
        analysis_type=workflow.input_data["analysis_type"]
    )
    
    assert workflow.workflow_type == WorkflowType.RAG_THEN_ANALYSIS
    assert rag_request.query == "Analyze AI market trends"
    assert analysis_request.analysis_type == AnalysisType.TREND

def test_orchestration_step():
    """Test OrchestrationStep schema"""
    step = OrchestrationStep(
        step_id="step_1",
        agent_type="rag",
        action="search_documents",
        input_data={"query": "AI trends"}
    )
    
    assert step.step_id == "step_1"
    assert step.agent_type == AgentType.RAG
    assert step.timeout_seconds == 300  # default

def test_orchestrator_request():
    """Test OrchestratorRequest schema"""
    request = OrchestratorRequest(
        task_type="multi_agent",
        target_agents=["rag", "analysis"],
        input_data={"query": "Analyze market data"}
    )
    
    assert request.task_type == "multi_agent"
    assert AgentType.RAG in request.target_agents
    assert AgentType.ANALYSIS in request.target_agents

def test_template_request_validation():
    """Test TemplateRequest validation"""
    # Valid RAG template
    template = TemplateRequest(
        template="rag_search",
        parameters={"query": "What is AI?"}
    )
    assert template.template == OrchestrationTemplate.RAG_SEARCH
    
    # Invalid - missing required parameter
    with pytest.raises(ValueError):
        TemplateRequest(
            template="rag_search",
            parameters={}  # Missing 'query'
        )

def test_agent_status():
    """Test AgentStatus schema"""
    status = AgentStatus(
        agent_type="rag",
        status="available",
        current_tasks=2,
        last_heartbeat=datetime.now(timezone.utc),
        capabilities=["search", "generate"]
    )
    
    assert status.agent_type == AgentType.RAG
    assert status.status == "available"
    assert len(status.capabilities) == 2
    
if __name__ == "__main__":
    # Quick test run
    print("Running comprehensive schema tests...")
    test_agent_type_enum()
    test_analysis_type_enum()
    test_analysis_request()
    test_analysis_response()
    test_full_workflow_schemas()
    test_orchestration_step()
    test_orchestrator_request()
    test_template_request_validation()
    test_agent_status()
    print("✅ All tests passed!")