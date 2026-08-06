
from pathlib import Path
import sys
import importlib.util

# Project root ko path me add karein taaki module easily import ho sake
current_dir = Path.cwd()
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

# Graph class ko import karne ka safe tareeqa (hyphen handling ke sath)
try:
    from OrbitDesk_RAG_Assignment.graph import OrbitDeskGraph
except ImportError:
    spec = importlib.util.spec_from_file_location("graph", "OrbitDesk-RAG-Assignment/graph.py")
    graph_module = importlib.util.module_from_spec(spec)
    sys.modules["graph"] = graph_module
    spec.loader.exec_module(graph_module)
    OrbitDeskGraph = graph_module.OrbitDeskGraph

def generate_graph_image():
    print("Initializing OrbitDeskGraph...")
    orbit_graph = OrbitDeskGraph()

    try:
        # LangGraph ke built-in method se mermaid png data nikalna
        print("Generating Mermaid PNG diagram...")
        png_data = orbit_graph.graph.get_graph().draw_mermaid_png()

        output_path = Path("OrbitDesk-RAG-Assignment/graph_diagram.png")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "wb") as f:
            f.write(png_data)
            
        print(f"Graph diagram successfully saved to {output_path.absolute()}")
        
    except Exception as e:
        print(f"Error generating diagram: {e}")
        print("Note: Ensure pygraphviz or grandalf is installed, or use Mermaid live editor.")

if __name__ == "__main__":
    generate_graph_image()
