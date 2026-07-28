import os
import requests
from db.database import SessionLocal
from sqlalchemy import text

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
# We'll use nomic-embed-text for embeddings, or any other Ollama embedding model
EMBEDDING_MODEL = "nomic-embed-text" 

def get_embedding(text_to_embed: str) -> list[float]:
    """Get vector embedding from Ollama."""
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/embeddings",
            json={"model": EMBEDDING_MODEL, "prompt": text_to_embed}
        )
        response.raise_for_status()
        return response.json().get("embedding", [])
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return []

try:
    from sentence_transformers import CrossEncoder
    # Using a small, fast cross-encoder for reranking
    reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
except ImportError:
    reranker = None
    print("Warning: sentence-transformers not installed, reranking disabled.")

def retrieve_similar_post_mortems(query_text: str, limit: int = 3) -> str:
    """Hybrid RAG Tool: Search pgvector (Dense) + tsvector (Sparse) and Rerank."""
    embedding = get_embedding(query_text)
    
    db = SessionLocal()
    candidates = {} # id -> row dict
    
    try:
        # 1. Vector Search (Dense)
        if embedding:
            embedding_str = "[" + ",".join(map(str, embedding)) + "]"
            dense_query = text("""
                SELECT id, title, root_cause, resolution, 1 - (embedding <=> :emb) AS score 
                FROM post_mortems 
                ORDER BY embedding <=> :emb 
                LIMIT :limit
            """)
            dense_results = db.execute(dense_query, {"emb": embedding_str, "limit": limit * 2}).fetchall()
            for r in dense_results:
                candidates[r.id] = {"title": r.title, "root_cause": r.root_cause, "resolution": r.resolution, "dense_score": r.score}

        # 2. Keyword Search (Sparse)
        sparse_query = text("""
            SELECT id, title, root_cause, resolution, ts_rank(text_search, plainto_tsquery('english', :query)) AS score
            FROM post_mortems
            WHERE text_search @@ plainto_tsquery('english', :query)
            ORDER BY score DESC
            LIMIT :limit
        """)
        sparse_results = db.execute(sparse_query, {"query": query_text, "limit": limit * 2}).fetchall()
        for r in sparse_results:
            if r.id not in candidates:
                candidates[r.id] = {"title": r.title, "root_cause": r.root_cause, "resolution": r.resolution, "sparse_score": r.score}
            else:
                candidates[r.id]["sparse_score"] = r.score

        if not candidates:
            return "No similar historical incidents found."

        # 3. Rerank using CrossEncoder
        candidate_list = list(candidates.values())
        if reranker:
            # Pair query with each candidate document's text
            pairs = [[query_text, f"{c['title']} {c['root_cause']} {c['resolution']}"] for c in candidate_list]
            scores = reranker.predict(pairs)
            for i, score in enumerate(scores):
                candidate_list[i]["rerank_score"] = float(score)
            
            # Sort by rerank score descending
            candidate_list.sort(key=lambda x: x.get("rerank_score", 0), reverse=True)
        else:
            # Fallback naive scoring if reranker is missing
            candidate_list.sort(key=lambda x: x.get("dense_score", 0) + x.get("sparse_score", 0), reverse=True)

        # 4. Return top K
        top_candidates = candidate_list[:limit]
        
        context_parts = []
        for row in top_candidates:
            context_parts.append(
                f"Incident: {row['title']}\n"
                f"Root Cause: {row['root_cause']}\n"
                f"Resolution: {row['resolution']}\n"
            )
            
        return "\n---\n".join(context_parts)
    except Exception as e:
        print(f"Hybrid RAG Error: {e}")
        return f"Error retrieving context: {str(e)}"
    finally:
        db.close()

def detect_visual_anomaly(image_path: str) -> str:
    """Computer Vision Tool: Analyze a dashboard chart for anomalies."""
    try:
        from models.vision_inference import ChartAnomalyDetector
        detector = ChartAnomalyDetector()
        
        result = detector.analyze_chart(image_path)
        if "error" in result:
            return f"Visual Analysis Failed: {result['error']}"
            
        prediction = result["prediction"]
        confidence = result["confidence"]
        
        analysis_text = f"Visual Dashboard Analysis: The chart appears {prediction} with {confidence*100:.2f}% confidence."
        if prediction == "anomalous":
            analysis_text += " This suggests a sudden spike, drop, or erratic behavior in the metrics."
            
        return analysis_text
    except ImportError:
        return "Visual Analysis Failed: CV dependencies (torch, torchvision) not installed or models module missing."
    except Exception as e:
        return f"Visual Analysis Failed: {str(e)}"
