from app.services.graph.analyzer import GraphAnalyzer
from app.services.repository.repository import analyze_repository

repository = analyze_repository("extracted/2e842df4-561f-4281-8196-2dc73e7735f6")

analyzer = GraphAnalyzer()

summary = analyzer.summarize(repository["graph"])

print(summary)