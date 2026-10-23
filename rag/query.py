import chromadb
from google import genai
import os
from memory import UserMemory

class Assistant:
    def __init__(self, cfg):
        self.cfg = cfg
        # Pake API Gemini buat nyari data (super ringan, ga butuh sentence-transformers)
        self.genai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.client = chromadb.PersistentClient(path=cfg["paths"]["chroma"])
        self.col = self.client.get_or_create_collection(cfg["rag"]["collection"])
        self.memory = UserMemory()

    def retrieve(self, question, k=5):
        try:
            # Ubah pertanyaan jadi angka pakai API Gemini
            res = self.genai_client.models.embed_content(
                model="text-embedding-004",
                contents=question
            )
            q_emb = res.embeddings[0].values
            
            # Cari di database
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
