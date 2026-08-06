
import logging
from typing import List, Optional

from schema import (
    RetrievedDoc,
    SourceItem,
    SupportResponse,
    Classification,
)

logger = logging.getLogger(__name__)


class SupportGenerator:
    """
    OrbitDesk Response Generator.

    Converts classification + retrieved documents
    into a final SupportResponse object.
    """

    def __init__(self) -> None:
        logger.info("SupportGenerator initialized.")

    def generate(
        self,
        question: str,
        classification: Classification,
        retrieved_docs: Optional[List[RetrievedDoc]] = None,
    ) -> SupportResponse:

        docs = retrieved_docs or []

        try:

            # ANSWERABLE
            if classification == Classification.ANSWERABLE:

                if not docs:
                    return SupportResponse(
                        classification=Classification.SAFE_FAILURE,
                        answer="No supporting knowledge base content was available to answer this request.",
                        sources=[],
                        confidence=0.0,
                        requires_human=False,
                        reason="Answerable route selected but retrieval returned no documents.",
                        warnings=["No retrieval results found."]
                    )

                sources = [
                    SourceItem(
                        source_id=doc.source_id,
                        passage=doc.passage[:500]
                    )
                    for doc in docs
                ]

                # Use best retrieved document
                top_doc = docs[0]

                # Clean markdown formatting
                cleaned_passage = (
                    top_doc.passage[:800]
                    .replace("## ", "")
                    .replace("# ", "")
                    .strip()
                )

                answer = (
                    f"Based on the OrbitDesk knowledge base:\n\n"
                    f"{cleaned_passage}"
                )

                # Confidence calibration
                raw_score = max(doc.score for doc in docs)

                confidence = round(
                    max(0.80, min(raw_score + 0.20, 0.95)),
                    2
                )

                return SupportResponse(
                    classification=Classification.ANSWERABLE,
                    answer=answer,
                    sources=sources,
                    confidence=confidence,
                    requires_human=False,
                    reason="Response synthesized cleanly from knowledge base documents.",
                    warnings=[]
                )

            # REQUIRES CLARIFICATION
            if classification == Classification.REQUIRES_CLARIFICATION:

                return SupportResponse(
                    classification=Classification.REQUIRES_CLARIFICATION,
                    answer=(
                        "I need a little more information before I can help."
                    ),
                    sources=[],
                    confidence=0.85,
                    requires_human=False,
                    reason="The query was too vague to identify the exact issue.",
                    clarification_question=(
                        "Could you provide the exact error message, affected feature, and steps that caused the issue?"
                    ),
                    warnings=[]
                )

            # REQUIRES ESCALATION
            if classification == Classification.REQUIRES_ESCALATION:

                return SupportResponse(
                    classification=Classification.REQUIRES_ESCALATION,
                    answer=(
                        "This issue appears to require investigation by the engineering team."
                    ),
                    sources=[],
                    confidence=0.95,
                    requires_human=True,
                    reason="Persistent failure or critical issue detected.",
                    warnings=["Escalation recommended."]
                )

            # OUT OF SCOPE
            if classification == Classification.OUT_OF_SCOPE:

                return SupportResponse(
                    classification=Classification.OUT_OF_SCOPE,
                    answer=(
                        "This request is outside the scope of OrbitDesk product support."
                    ),
                    sources=[],
                    confidence=0.90,
                    requires_human=False,
                    reason="Query is unrelated to OrbitDesk support operations.",
                    warnings=[]
                )

            # SAFE FAILURE
            return SupportResponse(
                classification=Classification.SAFE_FAILURE,
                answer=(
                    "We were unable to process the request safely."
                ),
                sources=[],
                confidence=0.0,
                requires_human=False,
                reason="Safe fallback route executed.",
                warnings=["Safe failure triggered."]
            )

        except Exception as e:

            logger.exception("Generator failed")

            return SupportResponse(
                classification=Classification.SAFE_FAILURE,
                answer=(
                    "An internal processing error occurred."
                ),
                sources=[],
                confidence=0.0,
                requires_human=False,
                reason=f"Generator exception: {str(e)}",
                warnings=["Internal generator exception."]
            )


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    generator = SupportGenerator()

    docs = [
        RetrievedDoc(
            source_id="05_api_credentials",
            passage="API credentials can be created from Settings > Developer > API Credentials.",
            score=0.92,
        )
    ]

    result = generator.generate(
        question="How do I create an API credential?",
        classification=Classification.ANSWERABLE,
        retrieved_docs=docs,
    )

    print(result.model_dump_json(indent=2))
