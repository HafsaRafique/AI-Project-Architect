from pathlib import Path


class SourceSplitter:

    @staticmethod
    def extract(
        filepath: str,
        start: int,
        end: int
    ) -> str:

        path = Path(filepath)

        if not path.exists():
            return ""

        lines = path.read_text(
            encoding="utf8"
        ).splitlines()

        return "\n".join(
            lines[start - 1:end]
        )