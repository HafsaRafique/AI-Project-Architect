import os
import subprocess
import uuid



def clone_repository(url:str):

    repo_id = str(uuid.uuid4())


    path = f"repositories/{repo_id}"


    os.makedirs(
        "repositories",
        exist_ok=True
    )


    subprocess.run(
        [
            "git",
            "clone",
            url,
            path
        ],
        check=True
    )


    return {
        "repository_id": repo_id,
        "path": path
    }