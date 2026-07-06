from app.services.vectorstore.collection import CollectionManager

manager = CollectionManager()

manager.create_collection(768)

print("Collection created successfully!")