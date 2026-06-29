#!/usr/bin/env python3
import logging
from pathlib import Path
from rdflib import Graph

# ==========================================
# 1. CONFIGURATION
# ==========================================
# Easily add, remove, or modify target schemas here
SCHEMAS = {
    "dublin-core": {
        "url": "https://www.dublincore.org/specifications/dublin-core/dcmi-terms/dublin_core_terms.ttl",
        "format": "turtle",
    },
    "dcat": {
        "url": "https://www.w3.org/ns/dcat3.ttl", 
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
}

# Paths resolved relative to this script's location
BASE_DIR = Path(__file__).resolve().parent.parent / "schemas"

# ==========================================
# 2. LOGGING SETUP
# ==========================================
# Set to logging.WARNING to omit success messages and only print errors.
# Set to logging.INFO to see standard tracking steps.
logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")


# ==========================================
# 3. PIPELINE LOGIC
# ==========================================
def update_schemas():
    for name, config in SCHEMAS.items():
        output_path = BASE_DIR / f"{name}.ttl"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            g = Graph()
            g.parse(config["url"], format=config["format"])
            g.serialize(destination=str(output_path), format="turtle")
        except Exception as e:
            logging.error(f"Failed to update {name} from {config['url']} - {e}")


if __name__ == "__main__":
    update_schemas()