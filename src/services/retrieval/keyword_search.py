import spacy
from rank_bm25 import BM25Okapi
from rapidfuzz import process
from src.database.database import get_images_table, get_audio_table, get_video_table, get_documents_table

nlp = spacy.load("en_core_web_sm")

# Example
# documents = [
#     "the quick brown fox jumps over the lazy dog near the river bank",
#     "machine learning and deep learning are subfields of artificial intelligence",
#     "the stock market crashed due to rising inflation and interest rates",
#     "climate change is causing rising sea levels and extreme weather events",
#     "python is a popular programming language used in data science and web development",
# ]

# ocr_texts = [
#     "Invoice #1042 Total Amount $250.00 Date 2025-01-15",
#     "WARNING: Do not operate heavy machinery while taking this medication",
#     "Chapter 3: Introduction to Neural Networks and Backpropagation",
#     "Annual Report 2024 Revenue Growth 15% Net Profit $2.3M",
#     "def train_model(data): model.fit(data) return model",
# ]

def tokenize(text):
    doc = nlp(text)
    tokens = [t.text for t in doc]
    return tokens
    
def get_vocab(tokenized_docs):
    vocabulary = set()

    for tokens in tokenized_docs:
        vocabulary.update(tokens)

    vocabulary = list(vocabulary)
    return vocabulary

def build_index(tokenized_docs):
    bm25 = BM25Okapi(tokenized_docs)
    return bm25


def search(query, bm25, vocabulary):
    tokenized_query = tokenize(query)
    expanded = []

    for word in tokenized_query:

        matches = process.extract(
            word,
            vocabulary,
            limit=3,
            score_cutoff=70
        )

        expanded.extend([match for match, score, idx in matches])

    expanded_query = list(set(tokenized_query + expanded))
    scores = bm25.get_scores(expanded_query)

    best = sorted(
        enumerate(scores),
        key=lambda x: x[1],
        reverse=True
    )

    return best

def _bm25_search_on_df(query, df, text_col, page_col=None):
    if df.empty:
        return []
    
    # Try to join with files table
    try:
        from src.database.database import get_files_table
        files_df = get_files_table().to_pandas()
        if not files_df.empty:
            df = df.merge(files_df[['id', 'file_name', 'storage_path']], left_on='file_id', right_on='id', suffixes=('', '_file'))
    except Exception:
        pass
        
    import pandas as pd
    non_empty_indices = []
    for i, t in enumerate(df[text_col].tolist()):
        if pd.isna(t) or t is None:
            continue
        t_str = str(t).strip()
        if not t_str or t_str.lower() in ("nan", "none"):
            continue
        non_empty_indices.append(i)

    if not non_empty_indices:
        return []
        
    non_empty_docs = [str(df.iloc[i][text_col]) for i in non_empty_indices]
    tokenized_docs = [tokenize(doc) for doc in non_empty_docs]
    vocabulary = get_vocab(tokenized_docs)
    bm25 = build_index(tokenized_docs)
    
    ranked_indices = search(query, bm25, vocabulary)
    
    results = []
    for rank_idx, score in ranked_indices:
        if score > 0:
            orig_idx = non_empty_indices[rank_idx]
            row = df.iloc[orig_idx]
            res = {
                "text": row[text_col],
                "score": float(score),
                "file_name": row.get('file_name', 'Unknown'),
                "storage_path": row.get('storage_path', '')
            }
            if page_col and page_col in row and row[page_col] is not None:
                res["page_number"] = int(row[page_col])
            results.append(res)
    return results

def search_documents_keyword(query):
    return _bm25_search_on_df(query, get_documents_table().to_pandas(), 'text_content', 'page_number')

def search_audio_transcript_keyword(query):
    return _bm25_search_on_df(query, get_audio_table().to_pandas(), 'transcript')

def search_video_transcript_keyword(query):
    return _bm25_search_on_df(query, get_video_table().to_pandas(), 'transcript')

def search_ocr_keyword(query):
    return _bm25_search_on_df(query, get_images_table().to_pandas(), 'ocr_text')

def search_text(query):
    return {
        "documents": search_documents_keyword(query),
        "transcript_audio": search_audio_transcript_keyword(query),
        "transcript_video": search_video_transcript_keyword(query),
        "ocr": search_ocr_keyword(query)
    }