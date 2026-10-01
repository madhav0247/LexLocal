import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import argparse
from src.retrieval.hybrid import hybrid_search
from src.retrieval.context_assembler import assemble_context
from src.retrieval.prompt_builder import build_prompt

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="Question to ask")
    args = parser.parse_args()
    
    print(f"Searching for: '{args.query}'\n")
    
    hits = hybrid_search(args.query)
    
    if not hits:
        print("No results found.")
        return
        
    print(f"Found {len(hits)} hits. Assembling context...\n")
    
    bundle = assemble_context(args.query, hits)
    prompt = build_prompt(bundle)
    
    print("=== ASSEMBLED PROMPT ===")
    print(prompt)
    print("========================")

if __name__ == "__main__":
    main()
