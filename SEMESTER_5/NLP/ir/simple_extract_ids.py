import pandas as pd

# Load the groundtruth CSV file
df = pd.read_csv('data halodoc - groundtruth_results.csv')

print("=== DOC IDs UNTUK SETIAP QUERY ===")
print()

# Group by query and extract doc IDs
for query in df['query'].unique():
    # Get all doc IDs for this query
    doc_ids = df[df['query'] == query]['doc_id'].tolist()
    
    print(f"Query: '{query}'")
    print(f"Doc IDs: {', '.join(map(str, doc_ids))}")
    print(f"Total: {len(doc_ids)} obat")
    print()
