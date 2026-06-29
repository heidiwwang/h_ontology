#!/usr/bin/env python3
import logging
from pathlib import Path
import requests
from rdflib import Graph

# ==========================================
# 1. CONFIGURATION
# ==========================================
SCHEMAS = {
    "dcterms": {
        "url": "https://www.dublincore.org/specifications/dublin-core/dcmi-terms/dublin_core_terms.ttl",
        "format": "turtle",
    },
    "dcat": {
        "url": "https://www.w3.org/ns/dcat", 
        "format": "turtle"
    },
    "org": {
        "url": "https://www.w3.org/ns/org.ttl", 
        "format": "turtle"
    },
    "prov": {
        "url": "https://www.w3.org/ns/prov-o.ttl", 
        "format": "turtle"
    },
    "foaf": {
        "url": "http://xmlns.com/foaf/0.1/", 
        "format": "xml"
    },
    "skos": {
        "url": "https://www.w3.org/2004/02/skos/core", 
        "format": "xml"
    },
    "schema": {
        "url": "https://schema.org/version/latest/schemaorg-current-https.ttl", 
        "format": "turtle"
    },
    "untp": {
        "url": "https://vocabulary.uncefact.org/untp/",
        "format": "json-ld"
    },
    "owl": {
        "url": "https://www.w3.org/2002/07/owl#", 
        "format": "ttl"
    }
}

# Paths resolved relative to project layout roots
BASE_SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "schemas"

# ==========================================
# 2. LOGGING SETUP
# ==========================================
logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")


# ==========================================
# 3. PIPELINE LOGIC
# ==========================================
def update_schemas():
    """Fetches remote vocabularies and saves them into nested local turtle folders."""
    for name, config in SCHEMAS.items():
        # Keep directories nested and clean: schemas/{name}/{name}.ttl
        output_path = BASE_SCHEMAS_DIR / f"{name}.ttl"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            g = Graph()
            
            # Content negotiation branch for APIs that demand explicit content headers
            if config["format"] == "json-ld":
                headers = {"Accept": "application/ld+json"}
                response = requests.get(config["url"], headers=headers, timeout=15)
                response.raise_for_status()
                g.parse(data=response.text, format="json-ld")
            else:
                # Direct streaming parsing for native semantic format documents
                g.parse(config["url"], format=config["format"])

            g.serialize(destination=str(output_path), format="turtle")
            
        except Exception as e:
            logging.error(f"Failed to update {name} from {config['url']} - {e}")


if __name__ == "__main__":
    update_schemas()