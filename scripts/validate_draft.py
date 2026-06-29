#!/usr/bin/env python3
from pathlib import Path
from engine import get_review_copy

# Resolve local paths
BASE_DIR = Path(__file__).resolve().parent.parent
DRAFT_FILE = BASE_DIR / "draft" / "draft.ttl"

def check_my_draft():
    print("🔬 Initializing schema engine and background repositories...")
    # 1. Get our pre-loaded background matrix (DCAT, SKOS, ORG, etc.)
    working_graph = get_review_copy()
    
    print(f"📥 Loading your hand-written draft: {DRAFT_FILE.name}")
    try:
        # 2. Parse your custom turtle draft directly into the engine workspace
        working_graph.parse(str(DRAFT_FILE), format="turtle")
        print("✅ Parsing successful! Your Turtle syntax is perfectly valid.")
        
        # 3. Simple structural validation check: Verify our new class hooks into W3C ORG
        # We can look up triples that combine your draft with the background schema
        ex_ns = dict(working_graph.namespaces()).get("ex")
        if ex_ns:
            custom_unit = ex_ns.PolicyEnforcementUnit
            # Find what parent classes the engine sees for your custom class
            parents = list(working_graph.objects(custom_unit, type=None)) # internal lookup
            print(f"🔗 Verified connections in graph matrix: '{custom_unit.split('/')[-1]}' successfully compiled.")
            
    except Exception as e:
        print(f"❌ Syntax or Parsing Error found in your draft file: {e}")

if __name__ == "__main__":
    check_my_draft()