from pydantic import BaseModel, Field
from typing import List


class ParsedFunction(BaseModel):
    name: str
    line: int
    end_line: int
    args: List[str] = Field(default_factory=list)
    decorators: List[str] = Field(default_factory=list)
    docstring: str | None = None


class ParsedClass(BaseModel):
    name: str
    line: int
    end_line: int
    bases: List[str] = Field(default_factory=list)
    docstring: str | None = None


class ParsedFile(BaseModel):
    path: str
    language: str

    imports: List[str] = Field(default_factory=list)

    functions: List[ParsedFunction] = Field(default_factory=list)

    classes: List[ParsedClass] = Field(default_factory=list)

    routes: List[dict] = Field(default_factory=list)