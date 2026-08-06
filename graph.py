import logging
from typing import Dict, Any

from langgraph.graph import StateGraph, END

from schema import AgentState, Classification, SupportResponse
from classifier import QueryClassifier
from retriever import OrbitDeskRetriever
from generator import SupportGenerator

logger = logging.getLogger(__name__)


class OrbitDeskGraph:
    """
    Enterprise-grade LangGraph orchestrator for OrbitDesk support RAG.
    """

    def __init__(self):
        logger.info("Initializing OrbitDeskGraph...")
        self.classifier = QueryClassifier()
        self.retriever = OrbitDeskRetriever()
        self.generator = SupportGenerator()

        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("classify", self.classify_node)
        workflow.add_node("retrieve", self.retrieve_node)
        workflow.add_node("generate", self.generate_node)

        # Entry point
        workflow.set_entry_point("classify")

        # Conditional routing based on classification/retrieval flag
        workflow.add_conditional_edges(
            "classify",
            self.route_after_classification,
            {
                "retrieve": "retrieve",
                "generate": "generate",
            },
        )

        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", END)

        self.graph = workflow.compile()

    def classify_node(self, state: AgentState) -> Dict[str, Any]:
        """Node 1: Classifies user query."""
        query = state["question"]
        result = self.classifier.classify(query)

        # Safely extract classification value based on schema enum definition
        classification_val = (
            result.classification.value 
            if hasattr(result.classification, "value") 
            else result.classification
        )

        return {
            "classification": Classification(classification_val),
            "reason": result.reasoning,
            "confidence": result.confidence,
            "requires_retrieval": result.requires_retrieval,
        }

    def route_after_classification(self, state: AgentState) -> str:
        """Router: Routes to retrieve if category is answerable or requires retrieval."""
        classification = state.get("classification")
        
        # Check explicit classification or retrieval flag
        if classification == Classification.ANSWERABLE or state.get("requires_retrieval", False):
            return "retrieve"

        return "generate"

    def retrieve_node(self, state: AgentState) -> Dict[str, Any]:
        """Node 2: Fetches documents from Knowledge Base."""
        docs = self.retriever.search(state["question"], top_k=3)
        return {
            "retrieved_docs": docs
        }

    def generate_node(self, state: AgentState) -> Dict[str, Any]:
        """Node 3: Generates the final grounded support response."""
        response = self.generator.generate(
            question=state["question"],
            classification=state.get("classification"),
            retrieved_docs=state.get("retrieved_docs", []),
        )

        # Return dictionary mapping to AgentState fields
        return {
            "answer": response.answer,
            "sources": response.sources,
            "confidence": response.confidence,
            "requires_human": response.requires_human,
            "reason": response.reason,
            "clarification_question": response.clarification_question,
            "warnings": response.warnings,
        }

    def run(self, question: str) -> SupportResponse:
        """Executes the end-to-end RAG graph workflow."""
        initial_state = {
            "question": question,
            "classification": None,
            "retrieved_docs": [],
            "answer": None,
            "sources": [],
            "confidence": None,
            "requires_human": False,
            "reason": None,
            "clarification_question": None,
            "warnings": [],
        }

        result = self.graph.invoke(initial_state)

        # Re-pack into official SupportResponse Pydantic model for clean presentation
        return SupportResponse(
            classification=result.get("classification"),
            answer=result.get("answer"),
            sources=result.get("sources", []),
            confidence=result.get("confidence", 0.0),
            requires_human=result.get("requires_human", False),
            reason=result.get("reason"),
            clarification_question=result.get("clarification_question"),
            warnings=result.get("warnings", []),
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    graph = OrbitDeskGraph()
    response = graph.run("How do I create an API credential?")

    print("\n--- End-to-End Graph Execution Result ---")
    print(response.model_dump_json(indent=2))
