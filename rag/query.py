import sys, os
sys.path.insert(0, os.path.dirname(__file__)) # Ngarahin ke folder rag

import chromadb
from sentence_transformers import SentenceTransformer
from memory import UserMemory

class Assistant:
    def __init__(self, cfg):
        self.cfg = cfg
        self.embed_model = SentenceTransformer(cfg["rag"]["embedding_model"])
        self.client = chromadb.PersistentClient(path=cfg["paths"]["chroma"])
        self.col = self.client.get_or_create_collection(cfg["rag"]["collection"])
        self.memory = UserMemory()

    def retrieve(self, question, k=5):
        q = self.embed_model.encode([question]).tolist()
        res = self.col.query(query_embeddings=q, n_results=k)
        docs = res.get("documents", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        return list(zip(docs, metas))

    def build_context(self, question, user_id):
        hits = self.retrieve(question)
        sys_prompt = self.memory.build_system_prompt(user_id)
        context = "\n\n".join(f"[{m.get('source')}] {d}" for d, m in hits)
        return {
            "system": sys_prompt,
            "context": context,
            "question": question
        }
