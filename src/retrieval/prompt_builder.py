from src.models import ContextBundle

def build_prompt(bundle: ContextBundle) -> str:
    instructions = (
        "You are a precise legal assistant. Use the provided context clauses to answer the user's question.\n"
        "Cite your sources using the node_ids in brackets, e.g., [doc_id:2.3].\n"
        "If the answer is not found in the context, say 'not found in the provided clauses'.\n\n"
        "Context:\n"
    )
    
    context_blocks = []
    
    for item in bundle.items:
        node = item.clause
        cite_tag = f"[CITE: {node.node_id} | {item.citation_str}]"
        
        breadcrumb = ""
        if item.parent_chain:
            path_parts = [p.heading or p.label for p in item.parent_chain]
            breadcrumb = "In " + " > ".join(filter(None, path_parts)) + ":\n"
            
        text = node.text
        
        if item.xref_clauses:
            text += "\n\nReferenced Clauses:\n"
            for x in item.xref_clauses:
                text += f" - [{x.node_id}]: {x.text[:200]}...\n"
                
        block = f"{cite_tag}\n{breadcrumb}{text}\n"
        context_blocks.append(block)
        
    context_str = "\n---\n".join(context_blocks)
    
    question_str = f"\n\nQuestion: {bundle.query}\nAnswer format required: markdown with inline [node_id] citations.\nAnswer:"
    
    return instructions + context_str + question_str
