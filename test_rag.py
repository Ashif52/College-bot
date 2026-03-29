import sys
sys.path.insert(0, r"c:\projects\aashif\student-project")

# Test Weaviate connection + collection object count
from chatbot.weaviate_client import get_client
from chatbot.config import COLLECTION_NAME

client = get_client()
collection = client.collections.get(COLLECTION_NAME)

# Count objects
count_result = collection.aggregate.over_all(total_count=True)
print(f"Collection '{COLLECTION_NAME}' has {count_result.total_count} objects")

if count_result.total_count == 0:
    print("WARNING: Collection is EMPTY — ingest has not been run or failed.")
else:
    print("OK: Data is present, testing retrieval...")
    from chatbot.retriever import retrieve
    chunks = retrieve("MCA eligibility criteria admission", top_k=3)
    print(f"Retrieved {len(chunks)} chunks for 'MCA eligibility'")
    for i, c in enumerate(chunks[:2]):
        print(f"\n--- Chunk {i+1} (score={c.score:.3f}) ---")
        print(c.content[:300])

client.close()
