from app.services.vectorstore.retriever import RepositoryRetriever

retriever = RepositoryRetriever()

results = retriever.retrieve(

    query="How does the server start?",

    repository_id="test"

)

print(len(results))

for r in results:

    print("-"*60)

    print(r.payload["path"])

    print(r.payload["name"])

    print(r.score)