from fastapi import FastAPI, Query
from sentence_transformers import SentenceTransformer
import faiss
import json
import uvicorn
import os
from openai import OpenAI

INDEX_FILE = "PPB.index"
META_FILE = "PPB_metadata.json"

app = FastAPI()

model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')


if not os.path.exists(INDEX_FILE) or not os.path.exists(META_FILE):
    raise FileNotFoundError("Brakuje conquest.index lub conquest_metadata.json. Użyj --build najpierw.")

index = faiss.read_index(INDEX_FILE)
with open(META_FILE, encoding="utf-8") as f:
    chunks = json.load(f)


@app.get("/")
def root():
    return {"status": "OK", "message": "PPB Embedding API"}


@app.get("/query")
def query(q: str = Query(..., description="Pytanie użytkownika"), top_k: int = 3):
    vec = model.encode(q).reshape(1, -1).astype("float32")
    # Jeśli używasz cosine similarity:
    # faiss.normalize_L2(vec)

    D, I = index.search(vec, 10)
    threshold = 0.75  # dla cosine similarity (jeśli IndexFlatIP); jeśli L2, daj np. 1.0

    selected_indices = set()
    for dist, idx in zip(D[0], I[0]):
        if dist < threshold:
            # Dodaj chunk i 10 sąsiadów w każdą stronę
            for offset in range(-10, 11):
                neighbor_idx = idx + offset
                if 0 <= neighbor_idx < len(chunks):
                    selected_indices.add(neighbor_idx)

    # Fallback: jeśli nic nie przeszło progu, bierz sąsiadów z top_k
    if not selected_indices:
        for idx in I[0][:top_k]:
            for offset in range(-10, 11):
                neighbor_idx = idx + offset
                if 0 <= neighbor_idx < len(chunks):
                    selected_indices.add(neighbor_idx)

    # Posortuj po indeksach i zbuduj kontekst
    context_chunks = [chunks[i]["content"] for i in sorted(selected_indices)]
    context_text = "\n\n".join(context_chunks)

    return {"question": q, "results": context_text}

# openAi api key
client = OpenAI(api_key="")


@app.get("/prompt")
def prompt(q: str = Query(...), top_k: int = 6):
    vec = model.encode(q).reshape(1, -1).astype("float32")
    # Jeśli używasz cosine similarity:
    # faiss.normalize_L2(vec)

    D, I = index.search(vec, 10)
    threshold = 0.75  # dla cosine similarity (jeśli IndexFlatIP); jeśli L2, daj np. 1.0

    selected_indices = set()
    for dist, idx in zip(D[0], I[0]):
        if dist < threshold:
            # Dodaj chunk i 10 sąsiadów w każdą stronę
            for offset in range(-10, 11):
                neighbor_idx = idx + offset
                if 0 <= neighbor_idx < len(chunks):
                    selected_indices.add(neighbor_idx)

    # Fallback: jeśli nic nie przeszło progu, bierz sąsiadów z top_k
    if not selected_indices:
        for idx in I[0][:top_k]:
            for offset in range(-10, 11):
                neighbor_idx = idx + offset
                if 0 <= neighbor_idx < len(chunks):
                    selected_indices.add(neighbor_idx)

    # Posortuj po indeksach i zbuduj kontekst
    context_chunks = [chunks[i]["content"] for i in sorted(selected_indices)]
    context_text = "\n\n".join(context_chunks)

    # Prompt dla GPT
    generated_prompt = f"""Jesteś asystentem, masz podane dane z prezentacji w celu pomocy użytkownikowi w zdaniu egzaminu.
Na podstawie poniższych fragmentów stron, odpowiedz na pytanie użytkownika. Odpowiedź sformułuj rzeczowo, używając języka naturalnego.

### KONTEKST:
{context_text}

### PYTANIE:
{q}

### ODPOWIEDŹ:"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Odpowiadasz na pytania na podstawie kontekstu prezentacji."},
            {"role": "user", "content": generated_prompt}
        ],
        temperature=0.2,
        max_tokens=8000
    )

    answer = response.choices[0].message.content.strip()
    return {"answer": answer}


if __name__ == "__main__":
    uvicorn.run("embedding_api:app", host="127.0.0.1", port=8000, reload=True)
