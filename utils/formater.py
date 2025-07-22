def format_context(gene_name, genecards_summary, pubmed_abstracts):
    context = f"""You are a genetics assistant. Here's the information about the gene: {gene_name}

GeneCards Summary:
{genecards_summary}

PubMed Abstracts:
{pubmed_abstracts}

Now answer the user's question based on this information.
"""
    return context
