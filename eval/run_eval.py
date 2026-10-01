import sys
import os
import json
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.retrieval.hybrid import hybrid_search, search_dense

def compute_metrics(hits, gold_node_ids):
    hit_ids = [h.node_id for h in hits]
    metrics = {"R@1": 0.0, "R@3": 0.0, "R@5": 0.0, "MRR": 0.0}
    
    for i, hid in enumerate(hit_ids):
        if hid in gold_node_ids:
            if i < 1: metrics["R@1"] = 1.0
            if i < 3: metrics["R@3"] = 1.0
            if i < 5: metrics["R@5"] = 1.0
            if metrics["MRR"] == 0:
                metrics["MRR"] = 1.0 / (i + 1)
                
    return metrics

def run_evaluation():
    questions_path = os.path.join(os.path.dirname(__file__), 'questions.jsonl')
    if not os.path.exists(questions_path):
        print("No questions.jsonl found.")
        return
        
    results = []
    
    with open(questions_path, 'r') as f:
        for line in f:
            if not line.strip(): continue
            q = json.loads(line)
            
            h_dense = search_dense(q["question"])
            m_h_dense = compute_metrics(h_dense, q["gold_node_ids"])
            
            h_hybrid = hybrid_search(q["question"])
            m_h_hybrid = compute_metrics(h_hybrid, q["gold_node_ids"])
            
            n_dense = search_dense(q["question"], table_name="naive_chunks")
            m_n_dense = compute_metrics(n_dense, q["gold_node_ids"])
            
            results.append({
                "mode": "hierarchical+dense",
                "qid": q["qid"],
                **m_h_dense
            })
            results.append({
                "mode": "hierarchical+hybrid",
                "qid": q["qid"],
                **m_h_hybrid
            })
            results.append({
                "mode": "naive+dense",
                "qid": q["qid"],
                **m_n_dense
            })
            
    if not results:
        print("No evaluations ran.")
        return
        
    df = pd.DataFrame(results)
    agg = df.groupby('mode')[["R@1", "R@3", "R@5", "MRR"]].mean().reset_index()
    
    out_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(out_dir, exist_ok=True)
    agg.to_csv(os.path.join(out_dir, 'metrics.csv'), index=False)
    
    print("Evaluation completed. Metrics saved.")

if __name__ == "__main__":
    run_evaluation()
