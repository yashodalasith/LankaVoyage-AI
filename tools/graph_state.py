"""State definition for LangGraph-based multi-agent orchestration."""

from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field


class PlanningState(BaseModel):
    """Shared state passed through the LangGraph workflow.
    
    This state accumulates outputs from each agent node and is passed
    to subsequent nodes, enabling stateful multi-agent orchestration.
    """

    # Initial user input
    query: str = Field(..., description="User travel planning request")
    model: str = Field(default="llama3.2", description="Ollama model name")
    limit: int = Field(default=10, description="Max records to fetch from DB")
    output_filename: str = Field(default="itinerary.md", description="Output filename")

    # Research Agent outputs
    research_records: List[Dict[str, Any]] = Field(default_factory=list)
    research_summary: str = Field(default="")
    research_model_used: str = Field(default="")
    research_used_fallback: bool = Field(default=False)

    # Optimizer Agent outputs
    preferences: Dict[str, Any] = Field(default_factory=dict)
    optimized_plan: Dict[str, Any] = Field(default_factory=dict)
    optimizer_summary: str = Field(default="")
    optimizer_model_used: str = Field(default="")
    optimizer_used_fallback: bool = Field(default=False)

    # Personalizer Agent outputs
    personalized_plan: Dict[str, Any] = Field(default_factory=dict)
    personalized_summary: str = Field(default="")
    report_path: str = Field(default="")
    personalizer_model_used: str = Field(default="")
    personalizer_used_fallback: bool = Field(default=False)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for JSON serialization."""
        return self.model_dump()
