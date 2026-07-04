from pathlib import Path

from app.models.chunk import CodeChunk

from app.services.chunking.splitter import SourceSplitter
from app.services.chunking.metadata import MetadataBuilder


class ChunkBuilder:

    def build_chunks(
        self,
        repository_id: str,
        repository_root: str,
        analysis: list
    ):

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