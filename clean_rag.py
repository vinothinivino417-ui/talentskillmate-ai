from rag_engine import clear_all_candidates

deleted_count = clear_all_candidates()

print("=" * 50)
print("RAG DATABASE CLEANUP")
print("=" * 50)
print(f"Deleted records: {deleted_count}")
print("RAG database is now clean.")