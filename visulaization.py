"""Generates graph.png for documentation purposes."""
from main import app 

app.get_graph().draw_mermaid_png(output_file_path="graph.png")