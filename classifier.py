import logging
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Enterprise Constants
RETRIEVAL_THRESHOLD = 0.45


class ClassificationEnum(str, Enum):
    """Official OrbitDesk assignment classification enums aligned with schema.py."""
    ANSWERABLE = "answerable"
    REQUIRES_CLARIFICATION = "requires_clarification"
    REQUIRES_ESCALATION = "requires_escalation"
    OUT_OF_SCOPE = "out_of_scope"
    SAFE_FAILURE = "safe_failure"


class QueryCategory(BaseModel):
    """Structured output schema matching assignment routing categories with rich metadata & intent tracking."""
    classification: ClassificationEnum = Field(
        description="The assigned routing category for support query routing."
    )
    confidence: float = Field(
        description="Confidence score of classification between 0.0 and 1.0"
    )
    reasoning: str = Field(
        description="Detailed explanation justifying the routing decision."
    )
    requires_retrieval: bool = Field(
        description="Flag indicating if the graph should execute knowledge base retrieval."
    )
    matched_intent: Optional[str] = Field(
        default=None,
        description="Detected domain intent tag (e.g., 'authentication', 'billing', 'dashboard', 'integration')"
    )


class QueryClassifier:
    """
    Pro-level Retrieval-Aware and Multi-Signal Support Router.
    Features configurable thresholds, intent tracking, safe failure handling, and optimized retrieval flags.
    """

    def __init__(self, retrieval_threshold: float = RETRIEVAL_THRESHOLD) -> None:
        self.retrieval_threshold = retrieval_threshold
        logger.info(f"QueryClassifier initialized with retrieval threshold: {self.retrieval_threshold}")

    def classify(self, query: str, retriever_results: Optional[List] = None) -> QueryCategory:
        """
        Classifies incoming queries using multi-signal heuristics, intent tagging, and retrieval feedback.
        """
        try:
            if not query or not query.strip():
                logger.warning("Empty query received for classification.")
                return QueryCategory(
                    classification=ClassificationEnum.REQUIRES_CLARIFICATION,
                    confidence=0.5,
                    reasoning="Empty query provided; clarification is required.",
                    requires_retrieval=False,
                    matched_intent="empty_query"
                )

            query_lower = query.lower()

            # 1. Security & Prompt Injection Check (Out of Scope)
            injection_keywords = ["ignore previous instructions", "reveal prompt", "system prompt", "hack", "exploit"]
            if any(kw in query_lower for kw in injection_keywords):
                return QueryCategory(
                    classification=ClassificationEnum.OUT_OF_SCOPE,
                    confidence=0.99,
                    reasoning="Adversarial pattern or prompt injection detected.",
                    requires_retrieval=False,
                    matched_intent="security_violation"
                )

            # 2. Multi-Signal Escalation Check
            failure_signals = ["render_failed", "crashes", "down", "broken", "fail", "error", "not working"]
            persistence_signals = ["every morning", "for weeks", "constantly", "persistent", "5 times", "multiple times", "loop", "days"]
            
            has_failure = any(sig in query_lower for sig in failure_signals)
            has_persistence = any(sig in query_lower for sig in persistence_signals)
            
            if (has_failure and has_persistence) or "sev-1" in query_lower or "data loss" in query_lower:
                return QueryCategory(
                    classification=ClassificationEnum.REQUIRES_ESCALATION,
                    confidence=0.94,
                    reasoning="Multi-signal detected: persistent system failure requiring engineering escalation.",
                    requires_retrieval=False,
                    matched_intent="system_escalation"
                )

            # 3. Retrieval-Aware Check (If retriever results are already fetched and match is strong)
            if retriever_results and len(retriever_results) > 0:
                top_score = getattr(retriever_results[0], "score", 0.0)
                if top_score > self.retrieval_threshold:
                    return QueryCategory(
                        classification=ClassificationEnum.ANSWERABLE,
                        confidence=round(min(0.7 + top_score, 0.99), 2),
                        reasoning=f"High-confidence semantic match found in knowledge base (score: {top_score}).",
                        requires_retrieval=False,  # Results already fetched, no need to re-retrieve
                        matched_intent="kb_retrieval_match"
                    )

            # 4. Domain Keyword & Technical Coverage Check (Includes Billing & Intent Tagging)
            intent_mapping = {
                "authentication": ["api", "key", "credential", "token", "authenticate", "password", "reset", "login"],
                "billing": ["billing", "invoice", "payment", "subscription", "refund", "charge"],
                "integration": ["integration", "connect", "salesforce", "webhook", "sync"],
                "workspace_settings": ["setup", "permission", "configure", "workspace", "settings", "role", "admin"],
                "dashboard_rendering": ["dashboard", "export", "render", "report"]
            }

            detected_intent = None
            matched_category = None

            for intent, keywords in intent_mapping.items():
                if any(kw in query_lower for kw in keywords):
                    detected_intent = intent
                    matched_category = ClassificationEnum.ANSWERABLE
                    break

            if matched_category:
                return QueryCategory(
                    classification=matched_category,
                    confidence=0.91,
                    reasoning=f"Query matched domain intent category: '{detected_intent}'.",
                    requires_retrieval=True,
                    matched_intent=detected_intent
                )

            # 5. Clarification Check (Vague inputs - does not require retrieval since query is ambiguous)
            clarification_keywords = ["help", "issue", "problem", "support", "status", "not working"]
            if len(query.split()) <= 3 or any(kw in query_lower for kw in clarification_keywords):
                return QueryCategory(
                    classification=ClassificationEnum.REQUIRES_CLARIFICATION,
                    confidence=0.88,
                    reasoning="Query is too ambiguous or vague; more operational details are needed from the user.",
                    requires_retrieval=False,  # No point searching KB with a vague word like 'help'
                    matched_intent="ambiguous_query"
                )

            # 6. Default Fallback (Out of Scope)
            return QueryCategory(
                classification=ClassificationEnum.OUT_OF_SCOPE,
                confidence=0.75,
                reasoning="Query falls outside the primary scope of OrbitDesk technical support knowledge base.",
                requires_retrieval=False,
                matched_intent="out_of_scope"
            )

        except Exception as e:
            logger.error(f"Error occurred during query classification: {e}")
            # Utilizing SAFE_FAILURE enum gracefully during unhandled system exceptions
            return QueryCategory(
                classification=ClassificationEnum.SAFE_FAILURE,
                confidence=0.0,
                reasoning=f"Classification pipeline encountered an internal error: {str(e)}",
                requires_retrieval=False,
                matched_intent="error_fallback"
            )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    
    classifier = QueryClassifier()
    test_queries = [
        "How do I update my billing invoice?",
        "Dashboard render_failed every morning for three weeks",
        "How do I reset my password?",
        "help"
    ]
    
    print("\n--- Final Polished Classifier Test Results ---")
    for q in test_queries:
        res = classifier.classify(q)
        print(f"Query: '{q}'\nResult: {res.model_dump_json(indent=2)}\n" + "-"*40)
