from typing import List, Optional, TypedDict
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict

class Classification(str, Enum):
    ANSWERABLE = "answerable"
    REQUIRES_CLARIFICATION = "requires_clarification"
    REQUIRES_ESCALATION = "requires_escalation"
    OUT_OF_SCOPE = "out_of_scope"
    SAFE_FAILURE = "safe_failure"

class SourceItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    source_id: str = Field(..., description="Knowledge-base document ID or resolved-case ID")
    passage: str = Field(..., description="Relevant excerpt or stable passage identifier")

class RetrievedDoc(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    source_id: str = Field(..., description="Knowledge-base document ID or resolved-case ID")
    passage: str = Field(..., description="Relevant excerpt or stable passage identifier")
    score: float = Field(..., description="Retrieval similarity score")

class AgentState(TypedDict):
    question: str
    classification: Optional[Classification]
    retrieved_docs: List[RetrievedDoc]
    answer: Optional[str]
    sources: List[SourceItem]
    confidence: Optional[float]
    requires_human: bool
    reason: Optional[str]
    clarification_question: Optional[str]
    warnings: List[str]

class SupportResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    classification: Classification = Field(..., description="Classification category of the support response")

    answer: str = Field(..., min_length=1, description="The support answer text")

    sources: List[SourceItem] = Field(default_factory=list, description="List of sources used")

    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0 and 1")

    requires_human: bool = Field(..., description="Whether human escalation is required")

    reason: str = Field(..., min_length=1, max_length=300, description="Brief explanation of the route and confidence")

    clarification_question: Optional[str] = Field(None, description="Clarification question if required")

    warnings: List[str] = Field(default_factory=list, description="Any warnings generated")
