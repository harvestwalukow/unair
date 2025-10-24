import pandas as pd

# Load the groundtruth CSV file
df = pd.read_csv('data halodoc - groundtruth_results.csv')

# Group by query and extract doc IDs
query_ids = {}

for query in df['query'].unique():
    # Get all doc IDs for this query
    doc_ids = df[df['query'] == query]['doc_id'].tolist()
    query_ids[query] = doc_ids

# Display results in the requested format
print("=== DOC IDs UNTUK SETIAP QUERY ===")
print()

for query, ids in query_ids.items():
    print(f"Query: '{query}'")
    print(f"Doc IDs: {', '.join(map(str, ids))}")
    print(f"Total: {len(ids)} obat")
    print()

# Also save to a text file for easy copy-paste
with open('query_doc_ids.txt', 'w', encoding='utf-8') as f:
    f.write("=== DOC IDs UNTUK SETIAP QUERY ===\n\n")
    
    for query, ids in query_ids.items():
        f.write(f"Query: '{query}'\n")
        f.write(f"Doc IDs: {', '.join(map(str, ids))}\n")
        f.write(f"Total: {len(ids)} obat\n\n")

print("Hasil juga disimpan ke file 'query_doc_ids.txt'")

# Create a summary table
print("\n=== RINGKASAN ===")
summary_df = pd.DataFrame([
    {
        'Query': query,
        'Jumlah Obat': len(ids),
        'Doc IDs': ', '.join(map(str, ids))
    }
    for query, ids in query_ids.items()
])

print(summary_df.to_string(index=False))
