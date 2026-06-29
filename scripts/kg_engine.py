#!/usr/bin/env python3
from pathlib import Path
from rdflib import Graph, Namespace

# Resolve structural paths relative to this file
BASE_DIR = Path(__file__).resolve().parent.parent
SCHEMAS_DIR = BASE_DIR / "schemas"

# Establish explicit shortcut namespaces for your workspace
NS_MAP = {
    "dcterms": Namespace("http://purl.org/dc/terms/"),
    "dcat": Namespace("http://www.w3.org/ns/dcat#"),
    "org": Namespace("http://www.w3.org/ns/org#"),
    "prov": Namespace("http://www.w3.org/ns/prov#"),
    "foaf": Namespace("http://xmlns.com/foaf/0.1/"),
    "skos": Namespace("http://www.w3.org/2004/02/skos/core#"),
    "schema": Namespace("https://schema.org/"),
    "untp": Namespace("https://vocabulary.uncefact.org/untp/"),
    "owl": Namespace("https://www.w3.org/2002/07/owl#"),
    # Add your own custom draft namespace prefix here
    "lac": Namespace("https://www.canada.ca/en/library-archives.html/#"),
    "h2": Namespace("https://heidi2o.cc/#"),
}

def load_knowledge_base() -> Graph:
    """Loads all local Turtle schemas into a combined, queryable graph environment."""
    kb = Graph()
    
    # 1. Bind your preferred prefix shortcuts neatly
    for prefix, ns in NS_MAP.items():
        kb.bind(prefix, ns)
        
    # 2. Automatically ingest all local .ttl files
    ttl_files = list(SCHEMAS_DIR.glob("**/*.ttl"))
    for file_path in ttl_files:
        try:
            # Parse directly into our unified global knowledge base
            kb.parse(str(file_path), format="turtle")
        except Exception as e:
            # Keep failures isolated so one broken layout doesn't crash your workspace
            print(f"Warning: Failed to ingest reference cache {file_path.name}: {e}")
            
    return kb

if __name__ == "__main__":
    # Quick sanity check validation
    base_graph = load_knowledge_base()
    print(f"📦 Workspace loaded successfully! Combined Triples: {len(base_graph)}")

    # Export a consolidated snapshot for quick local inspection
    review_output = BASE_DIR / "output" / "base_review.ttl"
    review_output.parent.mkdir(parents=True, exist_ok=True)
    
    base_graph.serialize(destination=str(review_output), format="turtle")
    print(f"🔍 Exported consolidated baseline for review to: data/processed/base_review.ttl")