import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import chromadb
from groq import Groq
from memory import UserMemory

class Assistant:
    def __init__(self, cfg):
        self.cfg = cfg
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.client = chromadb.PersistentClient(path=cfg["paths"]["chroma"])
        self.col = self.client.get_or_create_collection(cfg["rag"]["collection"])
        self.memory = UserMemory()

    def retrieve(self, question, k=5):
        try:
            # Pakai Groq buat ubah teks jadi angka
            res = self.groq_client.embeddings.create(
                model="nomic-embed-text-v1_5",
                input=question
            )
            q_emb = res.data[0].embedding
            
            results = self.col.query(query_embeddings=[q_emb], n_results=k)
            docs = results.get("documents", [[]])[0]
            metas = results.get("metadatas", [[]])[0]
            return list(zip(docs, metas))
        except Exception as e:
            print(f"Error retrieve: {e}")
            return []

    def build_context(self, question, user_id):
        hits = self.retrieve(question)
        sys_prompt = self.memory.build_system_prompt(user_id)
        context = "\n\n".join(f"[{m.get('source')}] {d}" for d, m in hits) if hits else "Konteks tidak ditemukan."
        return {
            "system": sys_prompt,
            "context": context,
            "question": question
        }
