import streamlit as st
from graph import OrbitDeskGraph
import time

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="OrbitDesk AI Support Agent",
    page_icon="🤖",
    layout="wide"
)

st.caption(
    "AI Engineer Assignment • RAG Pipeline • Semantic Search • Enterprise Support Automation"
)

# --------------------------------------------------
# Load Graph Once
# --------------------------------------------------

@st.cache_resource
def load_graph():
    return OrbitDeskGraph()

graph = load_graph()

# --------------------------------------------------
# Header
# --------------------------------------------------

st.markdown("""
# 🤖 OrbitDesk AI Support Agent

### Enterprise Retrieval-Augmented Support Assistant

Powered by:

- LangGraph
- FAISS Vector Search
- Sentence Transformers
- Pydantic Validation
- Semantic Knowledge Retrieval

Designed to classify support requests, retrieve relevant knowledge-base content, and generate structured support responses.
""")

st.markdown("---")

# --------------------------------------------------
# Sidebar
# --------------------------------------------------

with st.sidebar:

    st.header("System Overview")

    st.info(
        """
        OrbitDesk AI Support Agent helps support teams by:

        • Classifying support requests

        • Retrieving relevant KB articles

        • Generating structured responses

        • Detecting escalation scenarios

        • Providing confidence scores

        • Returning validated JSON outputs
        """
    )

    st.divider()

    st.subheader("System Metrics")

    st.metric("Knowledge Base Files", "10")
    st.metric("Embedding Model", "MiniLM-L6-v2")
    st.metric("Vector Store", "FAISS")

    st.divider()

    st.subheader("Sample Queries")

    st.code(
        "I am a read-only Viewer. Can I create an API credential?"
    )

    st.code(
        "Our data sync is not working. Can you tell me how to fix it?"
    )

    st.code(
        "Two export runs failed with render_failed. What should we do next?"
    )

# --------------------------------------------------
# Query Input
# --------------------------------------------------

st.subheader("Submit Support Request")

query = st.text_area(
    label="Support Request",
    placeholder="Describe your issue, question, or support request here...",
    height=180
)

col1, col2 = st.columns([1, 5])

with col1:
    run_button = st.button(
        "Analyze",
        use_container_width=True
    )

# --------------------------------------------------
# Processing
# --------------------------------------------------

if run_button:

    if not query.strip():

        st.warning(
            "Please enter a support request before running analysis."
        )

        st.stop()

    with st.spinner(
        "Running classification, retrieval, and response generation..."
    ):

        start_time = time.time()

        response = graph.run(query)

        runtime = round(
            time.time() - start_time,
            2
        )

    st.success(
        f"Request processed successfully in {runtime} seconds"
    )

    st.markdown("---")

    # --------------------------------------------------
    # Metrics Dashboard
    # --------------------------------------------------

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.metric(
            "Classification",
            response.classification
        )

    with m2:
        st.metric(
            "Confidence",
            f"{response.confidence:.2f}"
        )

    with m3:
        st.metric(
            "Human Escalation",
            "Yes" if response.requires_human else "No"
        )

    with m4:
        st.metric(
            "Sources Retrieved",
            len(response.sources)
        )

    # --------------------------------------------------
    # Generated Response
    # --------------------------------------------------

    st.markdown("## Generated Response")

    st.write(response.answer)

    st.markdown("---")

    # --------------------------------------------------
    # Retrieved Sources
    # --------------------------------------------------

    st.markdown("## Retrieved Knowledge Sources")

    if response.sources:

        for idx, source in enumerate(
            response.sources,
            start=1
        ):

            source_id = (
                source["source_id"]
                if isinstance(source, dict)
                else source.source_id
            )

            passage = (
                source["passage"]
                if isinstance(source, dict)
                else source.passage
            )

            with st.expander(
                f"Source {idx}: {source_id}"
            ):
                st.write(passage)

    else:

        st.info(
            "No supporting documents were retrieved."
        )

    st.markdown("---")

    # --------------------------------------------------
    # Reasoning Section
    # --------------------------------------------------

    st.markdown("## Decision Reason")

    st.info(
        response.reason
    )

    # --------------------------------------------------
    # Clarification
    # --------------------------------------------------

    if response.clarification_question:

        st.markdown("## Clarification Required")

        st.warning(
            response.clarification_question
        )

    # --------------------------------------------------
    # Warnings
    # --------------------------------------------------

    if response.warnings:

        st.markdown("## Warnings")

        for warning in response.warnings:

            st.warning(warning)

    st.markdown("---")

    # --------------------------------------------------
    # JSON Output
    # --------------------------------------------------

    with st.expander(
        "View Structured JSON Output"
    ):
        st.json(
            response.model_dump()
        )

# --------------------------------------------------
# Footer
# --------------------------------------------------

st.markdown("---")

st.caption(
    "Built for the OrbitDesk AI Engineer Assignment • LangGraph • FAISS • Sentence Transformers • Pydantic"
)
