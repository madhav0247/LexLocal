from typing import List, Dict
from src.models import ClauseNode, Hit, ContextBundle, ContextItem
from src.storage.trees import load_tree
from src.hierarchy.metadata import citation_str
from src.config import settings

def assemble_context(query: str, hits: List[Hit], mode: str = "hierarchical") -> ContextBundle:
    trees = {}
    
    def get_node(node_id: str) -> ClauseNode:
        doc_id = node_id.split(':')[0]
        if doc_id not in trees:
            trees[doc_id] = {n.node_id: n for n in load_tree(doc_id)}
        return trees[doc_id].get(node_id)
        
    items = []
    total_tokens = 0
    
    for hit in hits:
        if total_tokens > settings.context.max_tokens:
            break
            
        node = get_node(hit.node_id)
        if not node:
            continue
            
        parent_chain = []
        curr = node
        while curr.parent_id:
            parent = get_node(curr.parent_id)
            if parent:
                parent_chain.insert(0, parent)
                curr = parent
            else:
                break
                
        xref_clauses = []
        for xref_id in node.xrefs_resolved[:settings.context.max_xrefs_per_hit]:
            xref_node = get_node(xref_id)
            if xref_node:
                xref_clauses.append(xref_node)
                
        cite_str = citation_str(node)
        
        item_tokens = node.token_count
        for p in parent_chain:
            item_tokens += 10
            
        for x in xref_clauses:
            item_tokens += int(len(x.text.split()) * 1.3)
            
        if total_tokens + item_tokens > settings.context.max_tokens and items:
            continue
            
        total_tokens += item_tokens
        
        items.append(ContextItem(
            clause=node,
            parent_chain=parent_chain,
            xref_clauses=xref_clauses,
            citation_str=cite_str
        ))
        
    return ContextBundle(
        query=query,
        mode=mode,
        hits=hits,
        items=items,
        total_tokens=total_tokens
    )
