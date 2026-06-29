#!/usr/bin/env python3
import csv
import logging
from pathlib import Path
from urllib.parse import unquote, quote
import requests
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, SKOS

CSV_URL = "https://canada.multites.net/cst/EAEAD1E6-7DD2-4997-BE7F-40BFB1CBE8A2/CST20250610.csv"

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_INPUT_PATH = BASE_DIR / "input" / "cst.csv"
TTL_OUTPUT_PATH = BASE_DIR / "schemas" / "cst.ttl"

CST_NS = Namespace("http://www.thesaurus.gc.ca/#")
LAC = Namespace("https://www.canada.ca/en/library-archives.html/#")

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def download_cst_csv() -> bool:
    """Downloads the remote Canadian Subject Thesaurus CSV document raw."""
    try:
        CSV_INPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        logging.info("Downloading remote CST CSV dataset...")
        
        with requests.get(CSV_URL, stream=True, timeout=30) as r:
            r.raise_for_status()
            with open(CSV_INPUT_PATH, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        
        logging.info(f"Saved raw asset to: {CSV_INPUT_PATH.name}")
        return True
    except Exception as e:
        logging.critical(f"Failed to download dataset asset file: {e}")
        return False


def parse_csv_to_skos():
    """Parses 3-column MultiTes relationship matrix logs into clean SKOS triples."""
    if not CSV_INPUT_PATH.exists():
        logging.error(f"Input file not found at: {CSV_INPUT_PATH}")
        return

    logging.info(f"Processing relationship matrix from {CSV_INPUT_PATH.name}...")
    g = Graph()
    g.bind("lac", LAC)
    g.bind("skos", SKOS)

    with open(CSV_INPUT_PATH, mode="r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        
        for row in reader:
            if not row or len(row) < 3:
                continue
                
            term_a = unquote(row[0], encoding="latin-1").strip()
            relation = unquote(row[1], encoding="latin-1").strip()
            term_b = unquote(row[2], encoding="latin-1").strip()

            if not term_a or not relation or not term_b:
                continue

            uri_a = URIRef(f"{CST_NS}{quote(term_a, encoding='latin-1')}")
            uri_b = URIRef(f"{CST_NS}{quote(term_b, encoding='latin-1')}")

            g.add((uri_a, RDF.type, SKOS.Concept))

            # Exclude literal annotation notes from dynamic object-property mapping
            if relation in {"Scope Note", "History note", "History Note"}:
                if "Scope" in relation:
                    g.add((uri_a, SKOS.scopeNote, Literal(term_b, lang="en")))
                else:
                    g.add((uri_a, SKOS.historyNote, Literal(term_b, lang="en")))
                g.add((uri_a, SKOS.prefLabel, Literal(term_a, lang="en")))
                continue

            # Mint and assert custom structural relationship property
            safe_relation_fragment = relation.replace(" ", "")
            uri_rel = URIRef(f"{LAC}{safe_relation_fragment}")
            g.add((uri_a, uri_rel, uri_b))
            g.add((uri_b, RDF.type, SKOS.Concept))

            # Handle explicit routing for structural terminologies
            if relation == "French":
                g.add((uri_a, SKOS.prefLabel, Literal(term_a, lang="en")))
                g.add((uri_a, SKOS.prefLabel, Literal(term_b, lang="fr")))
                
            elif relation == "Use":
                g.add((uri_b, SKOS.prefLabel, Literal(term_b, lang="en")))
                g.add((uri_b, SKOS.altLabel, Literal(term_a, lang="en")))
                
            elif relation == "Used For":
                g.add((uri_a, SKOS.prefLabel, Literal(term_a, lang="en")))
                g.add((uri_a, SKOS.altLabel, Literal(term_b, lang="en")))
                
            else:
                g.add((uri_a, SKOS.prefLabel, Literal(term_a, lang="en")))
                g.add((uri_b, SKOS.prefLabel, Literal(term_b, lang="en")))

    # Post-process unlinked orphan Subject Categories referenced in metadata
    logging.info("Backfilling definitions for referenced Subject Categories...")
    subject_category_predicate = URIRef(f"{LAC}SubjectCategory")
    referenced_categories = set(g.objects(predicate=subject_category_predicate))
    
    for category_uri in referenced_categories:
        if isinstance(category_uri, URIRef):
            g.add((category_uri, RDF.type, SKOS.Concept))
            raw_fragment = str(category_uri).replace(str(CST_NS), "")
            clean_label = unquote(raw_fragment, encoding="latin-1")
            g.add((category_uri, SKOS.prefLabel, Literal(clean_label, lang="en")))

    # Hard-purge defensive cleanup for any misaligned literal properties
    g.remove((None, URIRef(f"{LAC}Historynote"), None))
    g.remove((None, URIRef(f"{LAC}HistoryNote"), None))
    g.remove((None, URIRef(f"{LAC}ScopeNote"), None))

    TTL_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    logging.info(f"Serializing graph asset to: {TTL_OUTPUT_PATH}")
    g.serialize(destination=str(TTL_OUTPUT_PATH), format="turtle")
    logging.info("Graph compilation completed successfully.")


if __name__ == "__main__":
    if download_cst_csv():
        parse_csv_to_skos()