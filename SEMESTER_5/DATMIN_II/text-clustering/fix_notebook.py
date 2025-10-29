import json

# Read the notebook
with open('text_clustering_analysis.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

# Process each cell
for cell in notebook['cells']:
    if cell['cell_type'] == 'code':
        source = cell['source']
        new_source = []
        skip_next = False
        
        for i, line in enumerate(source):
            # Skip lines with file saving operations
            if ('plt.savefig' in line or 
                'fig.write_html' in line or 
                '.to_csv' in line or
                'print("WordCloud generated and saved as' in line or
                'print("Interactive plot saved as' in line or
                'print("Silhouette plot saved as' in line or
                'print("\\nResults exported to' in line or
                'print("Cluster keywords exported to' in line):
                continue
            
            # Handle multi-line CSV export
            if 'output_df = df[[' in line:
                # Replace CSV export with summary display
                new_source.append('# Display cluster summary\n')
                new_source.append('print("\\n" + "="*80)\n')
                new_source.append('print("CLUSTER KEYWORDS SUMMARY")\n')
                new_source.append('print("="*80)\n')
                new_source.append('\n')
                new_source.append('for cluster_id, keywords in top_keywords.items():\n')
                new_source.append('    count = len(df[df[\'cluster\'] == cluster_id])\n')
                new_source.append('    print(f"\\nCluster {cluster_id} ({count} reviews):")\n')
                new_source.append('    print("Top Keywords:", \', \'.join(keywords[:10]))\n')
                # Skip until we find the end of CSV export block
                j = i + 1
                while j < len(source) and 'print("Cluster keywords exported to' not in source[j]:
                    j += 1
                # Skip past the print statement too
                source = source[:i] + source[j+1:]
                break
            
            # Handle generated files list
            if '# List all generated files' in line:
                new_source.append('print("\\n" + "="*80)\n')
                new_source.append('print("✅ Analysis complete!")\n')
                new_source.append('print("="*80)\n')
                new_source.append('print("\\nAll visualizations and results are displayed above.")\n')
                new_source.append('print("No files were saved to disk.")\n')
                # Skip rest of cell
                break
            
            new_source.append(line)
        
        cell['source'] = new_source

# Write back
with open('text_clustering_analysis.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, ensure_ascii=False, indent=1)

print("Notebook fixed! All file-saving operations removed.")

