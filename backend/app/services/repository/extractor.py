import os
import uuid
import zipfile
from app.services.repository.repository import analyze_repository
from app.services.chunking.chunker import ChunkBuilder

from fastapi import UploadFile
from app.services.embeddings.service import EmbeddingService
from app.services.vectorstore.qdrant import QdrantService

embedder = EmbeddingService()
qdrant = QdrantService()

UPLOAD_DIR = "uploads"
EXTRACT_DIR = "extracted"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(EXTRACT_DIR, exist_ok=True)


def build_tree(path, root):
    nodes = []

    for item in sorted(os.listdir(path)):
        full_path = os.path.join(path, item)
        relative_path = os.path.relpath(full_path, root)

        if os.path.isdir(full_path):
            nodes.append({
                "name": item,
                "type": "folder",
                "path": relative_path,
                "children": build_tree(full_path, root)
            })
        else:
            nodes.append({
                "name": item,
                "path": relative_path,
                "type": "file"
            })

    return nodes


async def save_and_extract_zip(file: UploadFile):

    repo_id = str(uuid.uuid4())

    zip_location = os.path.join(
        UPLOAD_DIR,
        f"{repo_id}.zip"
    )

    extract_location = os.path.join(
        EXTRACT_DIR,
        repo_id
    )

    with open(zip_location, "wb") as f:
        f.write(await file.read())

    with zipfile.ZipFile(zip_location) as zip_ref:
        zip_ref.extractall(extract_location)

    tree = build_tree(extract_location, extract_location)
    

    repository = analyze_repository(extract_location)

    builder = ChunkBuilder()

    chunks = builder.build_chunks(
        repository_id=repo_id,
        repository_root=extract_location,
        analysis=repository["files"]
    )

    BATCH_SIZE = 25

    print(f"Total chunks: {len(chunks)}")

    for i in range(0, len(chunks), BATCH_SIZE):

            batch = chunks[i:i + BATCH_SIZE]

            print(
                f"Embedding batch {i//BATCH_SIZE + 1} "
                f"({len(batch)} chunks)"
            )

            embedded_batch = embedder.embed_chunks(batch)

            print("Uploading batch to Qdrant...")

            qdrant.upsert_chunks(embedded_batch)

            print(
                f"Indexed {min(i + BATCH_SIZE, len(chunks))}"
                f"/"
                f"{len(chunks)} chunks"
            )
    return {
        "repository_id": repo_id,
        "tree": tree,
        "analysis": repository["files"],
        "graph": repository["graph"],
        "chunks": [chunk.model_dump() for chunk in chunks]
    }
    