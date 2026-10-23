import os, json, uuid
import chromadb
from sentence_transformers import SentenceTransformer

def chunk_text(text, size, overlap):
    words = text.split()
    if len(words) <= size:
        yield text
        return
    step = size - overlap
    for i in range(0, len(words), step):
        yield " ".join(words[i:i + size])

def ingest(cfg):
    print("Memuat model embedding (bisa makan waktu)...")
    embed_model = SentenceTransformer(cfg["rag"]["embedding_model"])
    client = chromadb.PersistentClient(path=cfg["paths"]["chroma"])
    col = client.get_or_create_collection(cfg["rag"]["collection"])
    proc = cfg["paths"]["processed"]

    for fn in os.listdir(proc):
        if not fn.endswith(".jsonl"):
            continue
        path = os.path.join(proc, fn)
        ids, docs, metas = [], [], []
        with open(path, encoding="utf-8") as f:
            for line in f:
                rec = json.loads(line)
                for ch in chunk_text(rec["text"], cfg["rag"]["chunk_size"], cfg["rag"]["chunk_overlap"]):
                    ids.append(str(uuid.uuid4()))
                    docs.append(ch)
                    metas.append({"source": rec.get("source"), "lang": rec.get("lang", "")})
        if not docs:
            continue
        print(f"Sedang embed {len(docs)} potongan dari {fn}...")
        # Batch processing biar RAM aman
        batch_size = 500
        for i in range(0, len(docs), batch_size):
            embeds = embed_model.encode(docs[i:i+batch_size], show_progress_bar=False).tolist()
            col.add(ids=ids[i:i+batch_size], documents=docs[i:i+batch_size], embeddings=embeds, metadatas=metas[i:i+batch_size])
        print(f"[ingest] {fn} selesai!")
