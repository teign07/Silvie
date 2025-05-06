import os
import json
import chromadb
import hashlib
# Assuming get_embedding is defined here or imported correctly
# from your_main_script import get_embedding # Example import
# Make sure you define or import get_embedding function properly!
# Also, make sure genai is configured if get_embedding uses it directly.
import google.generativeai as genai
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") # Need API key for embedding
genai.configure(api_key=GOOGLE_API_KEY)

# --- NEW Diary RAG Constants (Copied Here) ---
DIARY_DB_PATH = "./silvie_diary_rag_db"
DIARY_COLLECTION_NAME = "silvie_diary_entries"
DIARY_FILE = "silvie_diary.json"
EMBEDDING_MODEL = "models/text-embedding-004" # Reuse embedding model

# --- Embedding Function (Example, ensure yours is here or imported) ---
def get_embedding(text_to_embed, model=EMBEDDING_MODEL):
    # Your actual get_embedding implementation...
    # Simplified placeholder:
    print(f"Embedding (Diary Indexer): '{text_to_embed[:50]}...'")
    try:
        if not text_to_embed or not isinstance(text_to_embed, str) or len(text_to_embed.strip()) == 0: return None
        result = genai.embed_content(model=model, content=text_to_embed)
        return result.get('embedding')
    except Exception as e:
        print(f"Error embedding diary content: {e}")
        return None

# --- Indexing Logic ---
print(f"--- Starting Diary Indexing for {DIARY_FILE} ---")
print(f"Target Database Path: {DIARY_DB_PATH}")
print(f"Target Collection Name: {DIARY_COLLECTION_NAME}")

# Load Diary Data
try:
    with open(DIARY_FILE, 'r', encoding='utf-8') as f:
        diary_entries = json.load(f)
    if not isinstance(diary_entries, list):
         print(f"Error: Content in {DIARY_FILE} is not a list.")
         exit() # Stop if diary file is invalid
    print(f"Loaded {len(diary_entries)} entries from {DIARY_FILE}")
except FileNotFoundError:
    print(f"Error: Diary file not found at {DIARY_FILE}")
    exit()
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from {DIARY_FILE}")
    exit()

# Connect to the specific DIARY database path
client = chromadb.PersistentClient(path=DIARY_DB_PATH)

# Get or create the specific DIARY collection
print(f"Accessing collection '{DIARY_COLLECTION_NAME}'...")
collection = client.get_or_create_collection(
    name=DIARY_COLLECTION_NAME,
    metadata={"hnsw:space": "cosine"} # Or your preferred distance metric
)

# Prepare data for batch upsert
batch_size = 100
batch_ids = []
batch_embeddings = []
batch_documents = []
batch_metadatas = []
indexed_count = 0
skipped_count = 0

for entry in diary_entries:
    entry_timestamp = entry.get('timestamp', 'unknown_ts')
    entry_content = entry.get('content', '')

    if not entry_content or len(entry_content) < 10: # Skip empty/tiny entries
        skipped_count += 1
        continue

    embedding = get_embedding(entry_content) # Embed the content

    if embedding:
        # Generate ID (Example using timestamp + hash)
        content_hash_short = hashlib.sha256(entry_content.encode()).hexdigest()[:16]
        unique_id = f"diary_{entry_timestamp}_{content_hash_short}"

        # Add to batch
        batch_ids.append(unique_id)
        batch_embeddings.append(embedding)
        batch_documents.append(entry_content)
        batch_metadatas.append({"timestamp": entry_timestamp})

        # Upsert batch if full
        if len(batch_ids) >= batch_size:
            try:
                print(f"Upserting batch of {len(batch_ids)} diary entries...")
                collection.upsert(
                    ids=batch_ids,
                    embeddings=batch_embeddings,
                    documents=batch_documents,
                    metadatas=batch_metadatas
                )
                indexed_count += len(batch_ids)
                batch_ids, batch_embeddings, batch_documents, batch_metadatas = [], [], [], [] # Clear batch
            except Exception as e:
                print(f"Error upserting batch: {e}")
                skipped_count += len(batch_ids) # Count failed batch as skipped
                batch_ids, batch_embeddings, batch_documents, batch_metadatas = [], [], [], [] # Clear batch
    else:
        print(f"Warning: Failed to get embedding for entry timestamped {entry_timestamp}. Skipping.")
        skipped_count += 1

# Upsert any remaining entries in the last batch
if batch_ids:
    try:
        print(f"Upserting final batch of {len(batch_ids)} diary entries...")
        collection.upsert(
            ids=batch_ids,
            embeddings=batch_embeddings,
            documents=batch_documents,
            metadatas=batch_metadatas
        )
        indexed_count += len(batch_ids)
    except Exception as e:
        print(f"Error upserting final batch: {e}")
        skipped_count += len(batch_ids) # Count failed batch as skipped

print("--- Diary Indexing Complete ---")
print(f"Successfully Indexed/Updated: {indexed_count}")
print(f"Skipped Entries: {skipped_count}")
