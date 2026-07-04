from uuid import uuid4


class MetadataBuilder:

    @staticmethod
    def build(
        parsed_file,
        repository_id
    ):

        return {

            "chunk_id": str(uuid4()),

            "repository_id": repository_id,

            "imports": parsed_file.get(
                "imports",
                []
            ),

            "language": parsed_file.get(
                "language"
            ),

            "path": parsed_file.get(
                "path"
            )

        }