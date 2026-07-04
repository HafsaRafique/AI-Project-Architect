from pathlib import Path
from uuid import uuid4

from app.models.chunk import CodeChunk
from app.services.chunking.splitter import SourceSplitter


class ChunkBuilder:

    def build_chunks(
        self,
        repository_id: str,
        repository_root: str,
        analysis: list
    ) -> list[CodeChunk]:

        chunks = []

        for parsed_file in analysis:

            chunks.extend(
                self._build_file_chunks(
                    repository_id,
                    repository_root,
                    parsed_file
                )
            )

        return chunks

    def _build_file_chunks(
        self,
        repository_id: str,
        repository_root: str,
        parsed_file: dict
    ) -> list[CodeChunk]:

        chunks = []

        filepath = Path(repository_root) / parsed_file["path"]

        language = parsed_file.get("language", "unknown")

        # ---------- Module Chunk ----------

        module_doc = parsed_file.get("module_docstring")

        if module_doc:

            chunks.append(

                CodeChunk(

                    id=str(uuid4()),

                    repository_id=repository_id,

                    path=parsed_file["path"],

                    language=language,

                    chunk_type="module",

                    name=filepath.name,

                    content=module_doc,

                    metadata={

                        "imports": parsed_file.get("imports", [])

                    }

                )

            )

        # ---------- Function Chunks ----------

        for function in parsed_file.get("functions", []):

            source = SourceSplitter.extract(

                str(filepath),

                function["line"],

                function["end_line"]

            )

            chunks.append(

                CodeChunk(

                    id=str(uuid4()),

                    repository_id=repository_id,

                    path=parsed_file["path"],

                    language=language,

                    chunk_type="function",

                    name=function["name"],

                    content=source,

                    metadata={

                        "line": function["line"],

                        "end_line": function["end_line"],

                        "args": function.get("args", []),

                        "decorators": function.get("decorators", []),

                        "imports": parsed_file.get("imports", [])

                    }

                )

            )

        # ---------- Class Chunks ----------

        for cls in parsed_file.get("classes", []):

            source = SourceSplitter.extract(

                str(filepath),

                cls["line"],

                cls["end_line"]

            )

            chunks.append(

                CodeChunk(

                    id=str(uuid4()),

                    repository_id=repository_id,

                    path=parsed_file["path"],

                    language=language,

                    chunk_type="class",

                    name=cls["name"],

                    content=source,

                    metadata={

                        "line": cls["line"],

                        "end_line": cls["end_line"],

                        "bases": cls.get("bases", []),

                        "imports": parsed_file.get("imports", [])

                    }

                )

            )

        return chunks