import faiss, pickle, numpy as np, json, re
from sentence_transformers import SentenceTransformer
import anthropic

embed_model = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.read_index("data/redacted/doc_index.faiss")
meta = pickle.load(open("data/redacted/doc_meta.pkl","rb"))
client = anthropic.Anthropic()

def retrieve(query, k=2):
    q_emb = embed_model.encode([query]).astype("float32")
    _, idx = index.search(q_emb, k)
    return [meta["texts"][i] for i in idx[0]]

def run_agent(query):
    context = "\n\n".join(retrieve(query))
    prompt = f"""You are a compliance risk triage assistant. Given the document context below,
do the following as JSON only (no preamble):
1. risk_category: one of ["regulatory","complaint","contract_terms","other"]
2. summary: 1-2 sentence summary
3. confidence: float 0-1
4. needs_human_review: true if confidence < 0.7 or risk_category=="regulatory"

Context:
{context}

Question: {query}
"""
    resp = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=400,
        messages=[{"role":"user","content":prompt}]
    )
    raw = resp.content[0].text
    cleaned = re.sub(r"^```json\s*|```\s*$", "", raw.strip())
    try:
        result = json.loads(cleaned)
    except json.JSONDecodeError:
        result = {"error":"failed to parse", "raw": raw}
    return result

import datetime
def log_interaction(query, result, logfile="data/redacted/audit_log.jsonl"):
    entry = {"timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
             "query": query, "result": result}
    with open(logfile, "a") as f:
        f.write(json.dumps(entry) + "\n")

if __name__ == "__main__":
    for q in ["What is the litigation risk described?",
              "Summarize the customer complaint.",
              "What are the loan's interest terms?"]:
        print("Q:", q)
        result = run_agent(q)
        log_interaction(q, result)
        print(json.dumps(result, indent=2))
        print("---")
