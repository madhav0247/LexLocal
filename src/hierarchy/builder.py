from typing import List, Dict
from src.models import ClauseNode, NodeType, Line
from src.parsing.heading_detect import detect_headings

def infer_node_type(pattern_type: str) -> NodeType:
    mapping = {
        "keyword": NodeType.chapter,
        "decimal_1": NodeType.section,
        "decimal_2": NodeType.subsection,
        "decimal_3": NodeType.clause,
        "bare_num": NodeType.section,
        "letter": NodeType.clause,
        "roman": NodeType.subclause,
        "paren_num": NodeType.subsection,
        "proviso": NodeType.paragraph,
        "style_based": NodeType.section
    }
    return mapping.get(pattern_type, NodeType.paragraph)

def build_tree(doc_id: str, doc_title: str, lines: List[Line]) -> List[ClauseNode]:
    headings_info = detect_headings(lines)
    
    heading_count = sum(1 for h in headings_info if h["is_heading"])
    
    if heading_count < 3:
        return build_flat_tree(doc_id, doc_title, lines)
        
    nodes = {}
    
    root_node = ClauseNode(
        node_id=f"{doc_id}:root",
        doc_id=doc_id,
        doc_title=doc_title,
        node_type=NodeType.root,
        level=0,
        label="",
        heading=doc_title,
        text="",
        order=0,
        line_start=1,
        line_end=lines[-1].line_idx if lines else 1,
        version="v1",
        token_count=0
    )
    nodes[root_node.node_id] = root_node
    
    stack = [root_node]
    pattern_stack = ["root"]
    order_counter = 1
    
    for h_info in headings_info:
        line = h_info["line"]
        
        if h_info["is_heading"]:
            pattern_type = h_info["pattern_type"]
            
            if pattern_type in pattern_stack:
                idx = pattern_stack.index(pattern_type)
                stack = stack[:idx+1]
                pattern_stack = pattern_stack[:idx+1]
                parent = stack[-1]
            else:
                if pattern_type == "proviso":
                    # Attach to current deepest
                    parent = stack[-1]
                else:
                    parent = stack[-1]
                    pattern_stack.append(pattern_type)
            
            node_id = f"{doc_id}:{order_counter}"
            node_type = infer_node_type(pattern_type)
            
            path_append = h_info["label"] if h_info["label"] else (h_info["heading_text"][:10] if h_info["heading_text"] else f"n{order_counter}")
            
            new_node = ClauseNode(
                node_id=node_id,
                doc_id=doc_id,
                doc_title=doc_title,
                node_type=node_type,
                level=len(stack),
                label=h_info["label"] or "",
                heading=h_info["heading_text"],
                text="",
                parent_id=parent.node_id,
                path=parent.path + [path_append],
                order=order_counter,
                page_start=line.page,
                page_end=line.page,
                line_start=line.line_idx,
                line_end=line.line_idx,
                version="v1",
                token_count=0
            )
            
            nodes[node_id] = new_node
            parent.children_ids.append(node_id)
            
            if pattern_type != "proviso":
                stack.append(new_node)
                
            order_counter += 1
        else:
            current_node = stack[-1]
            if current_node.text:
                current_node.text += " " + line.text
            else:
                current_node.text = line.text
                
            current_node.line_end = line.line_idx
            if line.page:
                current_node.page_end = max(current_node.page_end or 0, line.page)
                
    return list(nodes.values())

def build_flat_tree(doc_id: str, doc_title: str, lines: List[Line]) -> List[ClauseNode]:
    root_node = ClauseNode(
        node_id=f"{doc_id}:root",
        doc_id=doc_id,
        doc_title=doc_title,
        node_type=NodeType.root,
        level=0,
        label="",
        heading=doc_title,
        text="",
        order=0,
        line_start=1,
        line_end=lines[-1].line_idx if lines else 1,
        version="v1",
        token_count=0
    )
    
    nodes = [root_node]
    order_counter = 1
    
    for line in lines:
        node_id = f"{doc_id}:flat_{order_counter}"
        flat_node = ClauseNode(
            node_id=node_id,
            doc_id=doc_id,
            doc_title=doc_title,
            node_type=NodeType.flat,
            level=1,
            label="",
            text=line.text,
            parent_id=root_node.node_id,
            path=["flat"],
            order=order_counter,
            page_start=line.page,
            page_end=line.page,
            line_start=line.line_idx,
            line_end=line.line_idx,
            version="v1",
            token_count=0
        )
        nodes.append(flat_node)
        root_node.children_ids.append(node_id)
        order_counter += 1
        
    return nodes
