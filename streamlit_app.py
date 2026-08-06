import streamlit as st
from graph import OrbitDeskGraph
import time

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="OrbitDesk AI Support Agent",
    page_icon="🤖",
    layout="wide"
)

# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>

.main {
    padding-top: 1rem;
}

.metric-card {
    background-color: #111827;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    color: white;
    border: 1px solid #374151;
}

.answer-box {
    padding: 20px;
    border-left: 6px solid #2563eb;
    background-color: #f8fafc;
    border-radius: 10px;
}

.hero {
    padding: 30px;
    border-radius: 16px;
    background: linear-gradient(90deg,#0f172a,#1e293b);
    color: white;
}

.small-text {
    color: #9ca3af;
    font-size: 14px;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# LOAD GRAPH
# --------------------------------------------------

@st.cache_resource
def load_graph():
    return OrbitDeskGraph()

graph = load_graph()

# --------------------------------------------------
# HERO SECTION
# --------------------------------------------------

st.markdown("""
<div class="hero">
    <h1>🤖 OrbitDesk AI Support Agent</h1>
    <h4>Enterprise Retrieval-Augmented Support Assistant</h4>
    <p>
    Powered by LangGraph • FAISS • Sentence Transformers • Pydantic
    </p>
</div>
""", unsafe_allow_html=True)

st.caption(
    "AI Engineer Assignment • Knowledge Grounded Responses • Enterprise Support Automation"
)

st.markdown("---")

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.title("⚙️ System Overview")

    st.info(
        """
        OrbitDesk AI Support Agent performs:

        • Query Classification

        • Semantic Retrieval

        • Knowledge Grounding

        • Escalation Detection

        • Clarification Handling

        • Structured JSON Generation
        """
    )

    st.divider()

    st.subheader("Technology Stack")

    st.markdown("""
    - LangGraph
    - FAISS
    - Sentence Transformers
    - HuggingFace Embeddings
    - Pydantic
    """)

    st.divider()

    st.subheader("Knowledge Base")

    st.metric("KB Documents", "10")
    st.metric("Vector Store", "FAISS")
    st.metric("Embedding Model", "MiniLM-L6-v2")

    st.divider()

    st.subheader("Try Example Queries")

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
# QUERY SECTION
# --------------------------------------------------

st.subheader("📝 Submit Support Request")

query = st.text_area(
    "",
    placeholder="Describe your issue, question, or support request here...",
    height=180
)

col1, col2 = st.columns([1, 5])

with col1:
    run_button = st.button(
        "🚀 Analyze",
        use_container_width=True
    )

# --------------------------------------------------
# PROCESS QUERY
# --------------------------------------------------

if run_button:

    if not query.strip():

        st.warning(
            "Please enter a support request before running analysis."
        )

        st.stop()

    with st.spinner(
        "Running classification, retrieval and response generation..."
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
    # DASHBOARD METRICS
    # --------------------------------------------------

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Classification",
            str(response.classification)
        )

    with c2:
        st.metric(
            "Confidence",
            f"{response.confidence:.2f}"
        )

    with c3:
        st.metric(
            "Human Escalation",
            "Yes" if response.requires_human else "No"
        )

    with c4:
        st.metric(
            "Sources",
            len(response.sources)
        )

    st.markdown("---")

    # --------------------------------------------------
    # GENERATED RESPONSE
    # --------------------------------------------------

    st.markdown("## 📌 Generated Response")

    st.markdown(
        f"""
        <div class="answer-box">
        {response.answer}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    # --------------------------------------------------
    # SOURCES
    # --------------------------------------------------

    st.markdown("## 📚 Retrieved Knowledge Sources")

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
                f"Source {idx} • {source_id}"
            ):
                st.write(passage)

    else:

        st.info(
            "No supporting sources were retrieved."
        )

    st.markdown("---")

    # --------------------------------------------------
    # DECISION REASON
    # --------------------------------------------------

    st.markdown("## 🧠 Decision Reason")

    st.info(
        response.reason
    )

    # --------------------------------------------------
    # CLARIFICATION
    # --------------------------------------------------

    if response.clarification_question:

        st.markdown("## ❓ Clarification Required")

        st.warning(
            response.clarification_question
        )

    # --------------------------------------------------
    # WARNINGS
    # --------------------------------------------------

    if response.warnings:

        st.markdown("## ⚠️ Warnings")

        for warning in response.warnings:
            st.warning(warning)

    st.markdown("---")

    # --------------------------------------------------
    # JSON OUTPUT
    # --------------------------------------------------

    with st.expander(
        "🔍 View Structured JSON Output"
    ):
        st.json(
            response.model_dump()
        )

# --------------------------------------------------
# ARCHITECTURE SECTION
# --------------------------------------------------

st.markdown("---")

st.markdown("""
## 🏗️ System Architecture

```text
User Query
     ↓
Classification
     ↓
FAISS Retrieval
     ↓
Response Generation
     ↓
Structured JSON Output
'''
""")
