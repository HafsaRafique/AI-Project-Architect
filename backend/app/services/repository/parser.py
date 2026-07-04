from app.services.repository.language import detect_language
from app.services.repository.python_parser import analyze_python


def parse_file(filepath):

    language = detect_language(filepath)

    result = {
        "language": language
    }

    if language == "python":

        result.update(
            analyze_python(filepath)
        )

    return result