from app.services.embeddings.huggingface import HuggingFaceEmbeddingProvider

provider = HuggingFaceEmbeddingProvider()

text = """
def add(a, b):
    return a + b
"""

embedding = provider.embed(text)

print(type(embedding))
print(len(embedding))
print(embedding[:10])