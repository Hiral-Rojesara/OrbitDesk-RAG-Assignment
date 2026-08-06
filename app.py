
import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import Optional

from graph import OrbitDeskGraph

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("OrbitDeskApp")


class OrbitDeskApplication:
    """
    Enterprise-Grade OrbitDesk Support Assistant Application.

    Features:
    - Robust CLI using argparse
    - Interactive Terminal Mode & Single Query Mode
    - Execution Latency Tracking
    - Safe Error Recovery & Structured JSON Outputs
    """

    def __init__(self, debug_mode: bool = False) -> None:
        if debug_mode:
            logger.setLevel(logging.DEBUG)
            logger.debug("Debug mode enabled.")
            
        logger.info("Initializing OrbitDesk Application core...")
        self.start_time = time.time()
        
        try:
            self.graph = OrbitDeskGraph()
            logger.info("OrbitDeskGraph pipeline successfully attached.")
        except Exception as e:
            logger.critical(f"Failed to initialize RAG Graph pipeline: {e}")
            raise

    def process_query(self, question: str) -> dict:
        """
        Executes the complete RAG workflow and tracks execution telemetry.
        """
        query_start = time.time()
        logger.info(f"Processing query: '{question[:50]}...'")

        try:
            response = self.graph.run(question)
            result_dict = response.model_dump()
            
            # Inject performance metadata into warnings or logs if needed
            elapsed = time.time() - query_start
            logger.info(f"Query processed successfully in {elapsed:.2f} seconds.")
            return result_dict

        except Exception as e:
            logger.exception("An unhandled exception occurred during RAG pipeline execution.")
            return {
                "classification": "safe_failure",
                "answer": "An internal application error occurred while processing your request.",
                "sources": [],
                "confidence": 0.0,
                "requires_human": True,
                "reason": str(e),
                "clarification_question": None,
                "warnings": ["Critical application exception caught in wrapper."]
            }

    def interactive_mode(self) -> None:
        """
        Runs an interactive REPL loop for continuous developer/user testing.
        """
        print("\n" + "=" * 65)
        print(" 🚀 OrbitDesk Enterprise Support Assistant (Interactive Mode)")
        print("=" * 65)
        print(" Instructions:")
        print(" - Type your query directly and press Enter.")
        print(" - Type 'exit', 'quit', or press Ctrl+C to shutdown.\n")

        while True:
            try:
                question = input("\nUser > ").strip()

                if question.lower() in ["exit", "quit"]:
                    print("\nShutting down OrbitDesk Assistant. Goodbye!")
                    break

                if not question:
                    continue

                start_t = time.time()
                result = self.process_query(question)
                duration = time.time() - start_t

                print("\n" + "-" * 20 + f" Assistant Response ({duration:.2f}s) " + "-" * 20)
                print(json.dumps(result, indent=2))
                print("-" * 65)

            except KeyboardInterrupt:
                print("\n\nSession interrupted by user. Shutting down cleanly.")
                break
            except Exception as e:
                logger.error(f"Runtime anomaly in interactive loop: {e}")
                print(f"\n[Error] {e}")

    def single_query_mode(self, question: str) -> None:
        """
        Executes a standalone query, prints clean JSON output, and exits.
        """
        result = self.process_query(question)
        print(json.dumps(result, indent=2))


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="OrbitDesk RAG Support Assistant CLI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "query",
        nargs="*",
        type=str,
        help="Optional single query string to execute directly."
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable verbose debug logging."
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    app = OrbitDeskApplication(debug_mode=args.debug)

    if args.query:
        question_str = " ".join(args.query)
        app.single_query_mode(question_str)
    else:
        app.interactive_mode()


if __name__ == "__main__":
    main()
