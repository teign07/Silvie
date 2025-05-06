import os
import json
import chromadb
import hashlib
import uuid # For generating chunk IDs, though hash-based could also work

# Assuming get_embedding is defined here or imported correctly
# You'll need your GOOGLE_API_KEY for this to work if get_embedding uses Gemini.
import google.generativeai as genai
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    print("CRITICAL ERROR: GOOGLE_API_KEY environment variable not set. Embeddings will fail.")
    # exit(1) # Or handle more gracefully depending on how you want to run this
else:
    genai.configure(api_key=GOOGLE_API_KEY)

# --- RAG Constants (from your Silvie script) ---
CHROMA_DB_PATH = "./silvie_rag_db"        # Path for conversation history DB
COLLECTION_NAME = "conversation_history" # Collection name for conversation history
HISTORY_FILE = "silvie_chat_history.json"  # Source of conversation data
EMBEDDING_MODEL = "models/text-embedding-004"

# --- Embedding Function (Ensure this matches your Silvie script's get_embedding) ---
def get_embedding(text_to_embed, model=EMBEDDING_MODEL):
    """Gets embedding for a text chunk using Google AI."""
    print(f"Embedding (History Indexer): '{text_to_embed[:60]}...'")
    try:
        if not text_to_embed or not isinstance(text_to_embed, str) or len(text_to_embed.strip()) == 0:
            print("Warning: Attempted to embed empty or invalid text. Returning None.")
            return None
        result = genai.embed_content(model=model, content=text_to_embed)
        # Ensure the result structure is what you expect, e.g., result['embedding']
        if 'embedding' in result and result['embedding']:
            return result['embedding']
        else:
            print(f"Warning: Embedding result missing or empty for: '{text_to_embed[:60]}...'")
            return None
    except Exception as e:
        print(f"Error getting embedding for '{text_to_embed[:60]}...': {type(e).__name__} - {e}")
        return None

# --- Indexing Logic ---
print(f"--- Starting Conversation History Indexing for {HISTORY_FILE} ---")
print(f"Target Database Path: {CHROMA_DB_PATH}")
print(f"Target Collection Name: {COLLECTION_NAME}")

# Load Conversation History Data
try:
    if os.path.exists(HISTORY_FILE) and os.path.getsize(HISTORY_FILE) > 0:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            full_history_lines = json.load(f) # Expects a list of strings
        if not isinstance(full_history_lines, list):
            print(f"Error: Content in {HISTORY_FILE} is not a list of strings.")
            exit()
        print(f"Loaded {len(full_history_lines)} lines from {HISTORY_FILE}")
    else:
        print(f"History file {HISTORY_FILE} not found or is empty. No data to index, but will ensure collection exists.")
        full_history_lines = [] # Proceed with empty list to ensure DB/collection creation

except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from {HISTORY_FILE}")
    exit()
except FileNotFoundError: # Should be caught by os.path.exists, but good to have
    print(f"Error: History file not found at {HISTORY_FILE}")
    full_history_lines = []


# Connect to the specific CONVERSATION HISTORY database path
client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

# Get or create the specific CONVERSATION HISTORY collection
print(f"Accessing collection '{COLLECTION_NAME}'...")
try:
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"} # Or your preferred distance metric
    )
    print(f"Collection '{COLLECTION_NAME}' ready.")
except Exception as e:
    print(f"CRITICAL ERROR: Could not get or create collection '{COLLECTION_NAME}': {e}")
    exit()


# --- Prepare Chunks from History Lines ---
# (This logic is adapted from your rag_updater_worker)
history_chunks = []
if len(full_history_lines) >= 2: # Need at least one pair
    # Process lines in pairs (User/Silvie)
    for i in range(0, len(full_history_lines) - 1, 2):
        user_turn_raw = full_history_lines[i]
        silvie_turn_raw = full_history_lines[i+1]

        if isinstance(user_turn_raw, str) and isinstance(silvie_turn_raw, str):
            # Parse out timestamps and speaker (same logic as your RAG updater)
            user_ts = user_turn_raw.split("] ", 1)[0] + "]" if user_turn_raw.startswith("[") else "[Unknown Time]"
            user_text = user_turn_raw.split("] ", 1)[1] if user_turn_raw.startswith("[") else user_turn_raw
            
            silvie_ts = silvie_turn_raw.split("] ", 1)[0] + "]" if silvie_turn_raw.startswith("[") else "[Unknown Time]"
            # Determine Silvie's prefix (Silvie: or Silvie ✨:)
            silvie_prefix_marker = "Silvie ✨" if "Silvie ✨" in silvie_turn_raw else "Silvie" # Handle both cases
            # Correctly extract text after potential "Silvie (status):" or "Silvie:"
            silvie_text_part = silvie_turn_raw.split("] ", 1)[1] if silvie_turn_raw.startswith("[") else silvie_turn_raw
            
            # Try to split by the determined marker first
            if f"{silvie_prefix_marker}:" in silvie_text_part:
                 silvie_text = silvie_text_part.split(f"{silvie_prefix_marker}:", 1)[1].strip()
            elif f"{silvie_prefix_marker} (" in silvie_text_part and "):" in silvie_text_part: # Handle "Silvie ✨ (status_info):"
                 silvie_text = silvie_text_part.split("):",1)[1].strip()
            else: # Fallback if neither specific prefix is found
                 silvie_text = silvie_text_part # Or a more robust generic split if needed

            # Form the combined chunk text
            chunk_text = f"{user_ts} User: {user_text}\n{silvie_ts} {silvie_prefix_marker}: {silvie_text}"
            
            # Generate a unique ID for this chunk
            # Using a hash of the content can help with idempotency if desired,
            # but UUID is simpler for ensuring uniqueness if content might be re-indexed.
            # For initial bulk indexing from a static file, UUID is fine.
            chunk_id = str(uuid.uuid4())

            history_chunks.append({
                "id": chunk_id,
                "text": chunk_text,
                "user_timestamp_str": user_ts.strip("[] "), # Store cleaned timestamp
                "silvie_timestamp_str": silvie_ts.strip("[] ") # Store cleaned timestamp
            })
        else:
            print(f"Warning: Skipping invalid turn pair at line index {i} in {HISTORY_FILE}")
else:
    print(f"Not enough lines in {HISTORY_FILE} to form conversation pairs. Found {len(full_history_lines)} lines.")

print(f"Prepared {len(history_chunks)} conversation chunks for indexing.")

# Prepare data for batch upsert
batch_size = 50 # Smaller batch size might be okay for history if it's not massive
batch_ids = []
batch_embeddings = []
batch_documents = []
batch_metadatas = []
indexed_count = 0
skipped_count = 0

if not history_chunks:
    print("No conversation chunks to index.")
else:
    for i, chunk_data in enumerate(history_chunks):
        chunk_id = chunk_data.get("id")
        chunk_text = chunk_data.get("text")
        user_ts = chunk_data.get("user_timestamp_str", "N/A")
        silvie_ts = chunk_data.get("silvie_timestamp_str", "N/A")

        if not chunk_id or not chunk_text or len(chunk_text.strip()) < 20: # Skip empty/tiny chunks
            print(f"Skipping chunk ID {chunk_id} due to missing data or short content.")
            skipped_count += 1
            continue

        embedding = get_embedding(chunk_text)

        if embedding:
            batch_ids.append(chunk_id)
            batch_embeddings.append(embedding)
            batch_documents.append(chunk_text)
            batch_metadatas.append({
                "user_ts_str": user_ts,
                "silvie_ts_str": silvie_ts
            })

            if len(batch_ids) >= batch_size or i == len(history_chunks) - 1: # Process if batch full or last item
                if batch_ids: # Ensure there's something to process
                    try:
                        print(f"Upserting batch of {len(batch_ids)} history chunks...")
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
                        batch_ids, batch_embeddings, batch_documents, batch_metadatas = [], [], [], []
        else:
            print(f"Warning: Failed to get embedding for chunk ID {chunk_id}. Skipping.")
            skipped_count += 1

# Upsert any remaining entries (already handled by `i == len(history_chunks) - 1` in the loop)

print("--- Conversation History Indexing Complete ---")
print(f"Successfully Indexed/Updated: {indexed_count} chunks.")
print(f"Skipped Chunks: {skipped_count}")
