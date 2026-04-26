from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
from docx import Document
import pandas as pd
import os, uuid, json, time

from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()


QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

COLLECTION_NAME = "travel_data"
DATA_FOLDER = "data"

BATCH_SIZE = 10
CHUNK_SIZE = 300
DELAY_BETWEEN_BATCHES = 1
MAX_RETRIES = 3
CHECKPOINT_FILE = "upload_checkpoint.txt"

if not QDRANT_URL or not QDRANT_API_KEY:
    raise Exception(" QDRANT_URL or QDRANT_API_KEY missing")


print("Connecting to Qdrant Cloud...")
client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    timeout=60
)

print(" Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")


try:
    client.get_collection(COLLECTION_NAME)
    print(" Collection already exists")
except:
    print(" Creating collection...")
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
    )
    print(" Collection created")


def load_txt(p): return open(p, "r", encoding="utf-8").read()

def load_pdf(p):
    reader = PdfReader(p)
    return "".join([pg.extract_text() or "" for pg in reader.pages])

def load_json(p): return json.dumps(json.load(open(p)))

def load_csv(p): return pd.read_csv(p).to_string()

def load_docx(p):
    doc = Document(p)
    return "\n".join([para.text for para in doc.paragraphs])


def chunk_text(text):
    chunks = []
    for i in range(0, len(text), CHUNK_SIZE):
        chunk = text[i:i+CHUNK_SIZE].strip()
        if len(chunk) > 50:
            chunks.append(chunk)
    return chunks

print("\n Loading files...")
all_chunks = []

for file in os.listdir(DATA_FOLDER):
    path = os.path.join(DATA_FOLDER, file)
    print(f" {file}")

    try:
        if file.endswith(".txt"):
            text = load_txt(path)
        elif file.endswith(".pdf"):
            text = load_pdf(path)
            if not text.strip():
                print(" Skipping empty PDF")
                continue
        elif file.endswith(".json"):
            text = load_json(path)
        elif file.endswith(".csv"):
            text = load_csv(path)
        elif file.endswith(".docx"):
            text = load_docx(path)
        else:
            print(" Skipped unsupported file")
            continue

        chunks = chunk_text(text)
        for c in chunks:
            all_chunks.append({"text": c, "source": file})

        print(f"   ➜ {len(chunks)} chunks")

    except Exception as e:
        print(f" Error: {e}")

print(f"\n Total chunks: {len(all_chunks)}")

start_index = 0
if os.path.exists(CHECKPOINT_FILE):
    start_index = int(open(CHECKPOINT_FILE).read())
    print(f"Resuming from batch index {start_index}")

def upload_with_retry(points):
    for attempt in range(MAX_RETRIES):
        try:
            client.upsert(
                collection_name=COLLECTION_NAME,
                points=points
            )
            return True
        except Exception as e:
            print(f" Retry {attempt+1}: {e}")
            time.sleep(2 * (attempt + 1))
    return False


print("\n Upload starting...\n")

for i in tqdm(range(start_index, len(all_chunks), BATCH_SIZE), desc="Uploading"):
    batch = all_chunks[i:i+BATCH_SIZE]

    texts = [c["text"] for c in batch]

    try:
        vectors = model.encode(texts).tolist()
    except Exception as e:
        print(" Embedding failed:", e)
        continue

    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=vectors[j],
            payload={
                "text": batch[j]["text"],
                "source": batch[j]["source"]
            }
        )
        for j in range(len(batch))
    ]

    success = upload_with_retry(points)

    if success:
        print(f" Batch {i//BATCH_SIZE + 1} uploaded")
        with open(CHECKPOINT_FILE, "w") as f:
            f.write(str(i))
    else:
        print(" Skipped batch")

    time.sleep(DELAY_BETWEEN_BATCHES)

print("\n Upload completed!")