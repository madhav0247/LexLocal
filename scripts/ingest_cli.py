import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import argparse
from src.ingest.loader import load_document
from src.hierarchy.builder import build_tree
from src.hierarchy.metadata import encode_metadata
from src.hierarchy.xref import detect_xrefs, resolve_xrefs
from src.storage.trees import save_tree
from src.indexing.vector_store import ingest_clauses
from src.indexing.bm25_index import build_bm25

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="File to ingest")
    parser.add_argument("--doc-id", required=True)
    parser.add_argument("--title", required=True)
    args = parser.parse_args()
    
    print(f"Loading {args.file}...")
    lines = load_document(args.file)
    
    print("Building tree...")
    nodes = build_tree(args.doc_id, args.title, lines)
    
    print("Encoding metadata...")
    encode_metadata(args.file, nodes)
    
    print("Resolving xrefs...")
    detect_xrefs(nodes)
    resolve_xrefs(nodes)
    
    print("Saving tree...")
    save_tree(args.doc_id, nodes)
    
    print("Ingesting clauses (LanceDB)...")
    ingest_clauses(nodes)
    
    print("Building BM25 index...")
    build_bm25(nodes)
    
    print("Done!")

if __name__ == "__main__":
    main()
