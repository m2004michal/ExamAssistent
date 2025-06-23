🚀 Features

    🔍 Semantic Search using SentenceTransformers + FAISS

    🧾 Context-Aware Answering with OpenAI's GPT-4o

    📄 Automatic Chunking of PDF pages into manageable knowledge units

    🧠 Neighbor-aware Context Retrieval (±10 surrounding chunks)

    🌐 FastAPI backend with /query and /prompt endpoints

How to use: 
  1. make sure to put openAi API key in python file and path to your folder with pdf files in jupyter
  2. install all the required packages
  3. execute every step in jupyter file
  4. launch python file 

📡 Endpointy API
1. GET /

Opis: Endpoint testowy, sprawdza status aplikacji
Zwraca:

{
  "status": "OK",
  "message": "PPB Embedding API"
}

2. GET /query

Opis: Wyszukiwanie semantyczne wektorowe bez GPT
Parametry:

    q: pytanie użytkownika (string)

    top_k: liczba głównych trafień do rozszerzenia o sąsiadów (default: 3)

Zachowanie:

    Wygenerowany embedding pytania jest porównywany z indeksem

    Dla każdego trafienia dołączane są sąsiednie chunki (±10)

    Zwracany jest połączony kontekst

Zwraca:

{
  "question": "Jak zarejestrować spółkę cywilną?",
  "results": "Uzyskanie wpisu w CEIDG...\n\nZawarcie umowy spółki cywilnej..."
}

3. GET /prompt

Opis: Odpowiedź generowana przez GPT-4o na podstawie kontekstu
Parametry:

    q: pytanie użytkownika (string)

    top_k: liczba głównych trafień do rozszerzenia o sąsiadów (default: 6)

Zachowanie:

    Zapytanie semantyczne do FAISS (top 10)

    Filtrowanie wyników wg progu threshold = 0.75

    Dołączenie ±10 sąsiednich chunków do każdego trafienia

    Sklejony kontekst trafia do prompta dla GPT-4o

    Zwracana jest wygenerowana odpowiedź

Zwraca:

{
  "answer": "Aby zarejestrować spółkę cywilną, należy: 1) Uzyskać wpis w CEIDG, 2) Zawrzeć umowę na piśmie..."
}
