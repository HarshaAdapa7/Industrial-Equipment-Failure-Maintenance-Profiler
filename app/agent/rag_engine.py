import os
import glob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class SOPVectorRAGStore:
    _instance = None

    def __init__(self):
        self.documents = []
        self.doc_metadata = []
        self.vectorizer = None
        self.tfidf_matrix = None
        self.load_and_index_sops()

    def load_and_index_sops(self):
        sops_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'sops')
        sop_files = glob.glob(os.path.join(sops_dir, "*.md"))

        self.documents = []
        self.doc_metadata = []

        for file_path in sop_files:
            filename = os.path.basename(file_path)
            mode_key = filename.split('_')[0]  # TWF, HDF, PWF, OSF, RNF, General

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            self.documents.append(content)
            self.doc_metadata.append({
                'title': filename.replace('.md', ''),
                'mode_key': mode_key,
                'file_path': file_path,
                'content': content
            })

        if self.documents:
            self.vectorizer = TfidfVectorizer(stop_words='english')
            self.tfidf_matrix = self.vectorizer.fit_transform(self.documents)
            print(f"RAG Engine indexed {len(self.documents)} SOP documents.")

    def query_sops(self, query_str, top_k=2):
        if not self.vectorizer or self.tfidf_matrix is None:
            return []

        query_vec = self.vectorizer.transform([query_str])
        sims = cosine_similarity(query_vec, self.tfidf_matrix)[0]
        top_indices = sims.argsort()[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = float(sims[idx])
            meta = self.doc_metadata[idx]
            results.append({
                'title': meta['title'],
                'mode_key': meta['mode_key'],
                'similarity_score': round(score, 4),
                'content_snippet': meta['content'][:500] + "..." if len(meta['content']) > 500 else meta['content'],
                'full_content': meta['content']
            })
        return results

def get_rag_store():
    if SOPVectorRAGStore._instance is None:
        SOPVectorRAGStore._instance = SOPVectorRAGStore()
    return SOPVectorRAGStore._instance
