import os
import uuid
import zipfile

from fastapi import UploadFile

UPLOAD_DIR = "uploads"
EXTRACT_DIR = "extracted"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(EXTRACT_DIR, exist_ok=True)


def build_tree(path):
    nodes = []

    for item in sorted(os.listdir(path)):
        full_path = os.path.join(path, item)

        if os.path.isdir(full_path):
            nodes.append({
                "name": item,
                "type": "folder",
                "children": build_tree(full_path)
            })
        else:
            nodes.append({
                "name": item,
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

    tree = build_tree(extract_location)

    return {
        "repository_id": repo_id,
        "tree": tree
    }