#!/usr/bin/env python3
import logging
from pathlib import Path
from rdflib import Graph

BASE_DIR = Path(__file__).resolve().parent.parent
TTL_INPUT_PATH = BASE_DIR / "drafts" / "lac.ttl"

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def validate_turtle_file() -> bool:
    """Parses a Turtle file to validate its syntax and integrity."""
    if not TTL_INPUT_PATH.exists():
        logging.error(f"Target file not found at: {TTL_INPUT_PATH}")
        return False

    logging.info(f"Validating syntax for: {TTL_INPUT_PATH.name}...")
    g = Graph()
    
    try:
        # Attempt to parse the file; invalid syntax will raise an exception
        g.parse(source=TTL_INPUT_PATH, format="turtle")
        
        triple_count = len(g)
        logging.info("Validation passed successfully.")
        logging.info(f"Total statements verified: {triple_count}")
        return True
        
    except Exception as e:
        logging.error("Validation failed. Syntax or formatting error detected:")
        logging.error(str(e))
        return False


if __name__ == "__main__":
    validate_turtle_file()