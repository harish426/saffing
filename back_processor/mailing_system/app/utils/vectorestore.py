import faiss
import numpy as np
import pickle
import os
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
import pdfplumber
import concurrent.futures

class LocalFAISSStore:
    def __init__(self, model_name='all-MiniLM-L6-v2', folder_path="faiss_store"):
        self.model = SentenceTransformer(model_name)
        self.folder_path = folder_path
        self.index_file = os.path.join(folder_path, "index.faiss")
        self.meta_file = os.path.join(folder_path, "metadata.pkl")
        
        # Initialize or Load
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            # 384 is the dimension for all-MiniLM-L6-v2
            self.index = faiss.IndexFlatL2(384)
            self.metadata = []
        else:
            self.index = faiss.read_index(self.index_file)
            with open(self.meta_file, 'rb') as f:
                self.metadata = pickle.load(f)

    def add_texts(self, texts, category="doc"):
        # 1. Create embeddings
        embeddings = self.model.encode(texts)
        # 2. Add to FAISS index
        self.index.add(np.array(embeddings).astype('float32'))
        # 3. Store text/metadata separately (FAISS only stores numbers)
        for t in texts:
            self.metadata.append({"text": t, "type": category})
        # 4. Save to disk
        faiss.write_index(self.index, self.index_file)
        with open(self.meta_file, 'wb') as f:
            pickle.dump(self.metadata, f)

    def add_document(self, document):
        self.add_texts([document], category="document")

    def add_chat(self, chat):
        self.add_texts([chat], category="conversation")

    def search(self, query, k=2):
        query_vector = self.model.encode([query]).astype('float32')
        distances, indices = self.index.search(query_vector, k)
        
        results = []
        for idx in indices[0]:
            if idx != -1:
                results.append(self.metadata[idx])
        return results

    @staticmethod
    def get_pdf_chunks(pdf_path, chunk_size=500, chunk_overlap=50):
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
            
            # Simple recursive chunking
            chunks = []
            for i in range(0, len(text), chunk_size - chunk_overlap):
                chunks.append(text[i:i + chunk_size])
            return chunks

    def extract_text_from_pdf(self, pdf_path):
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"Error reading PDF {pdf_path}: {e}")
            return None

    def ingest_pdf(self, pdf_path, category="resume"):
        # Use the chunking method
        chunks = self.get_pdf_chunks(pdf_path)
        if chunks:
            self.add_texts(chunks, category=category)
            print(f"Successfully ingested and chunked PDF: {pdf_path}")
            return True
        return False

    def ingest_multiple_pdfs(self, pdf_paths, max_workers=4):
        """
        Ingests multiple PDFs in parallel using threads.
        """
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks to the pool
            future_to_pdf = {executor.submit(self.ingest_pdf, path): path for path in pdf_paths}
            
            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_pdf):
                pdf_path = future_to_pdf[future]
                try:
                    success = future.result()
                    results.append((pdf_path, success))
                    if success:
                        print(f"Done: {pdf_path}")
                except Exception as exc:
                    print(f"{pdf_path} generated an exception: {exc}")
                    results.append((pdf_path, False))
        return results

# Usage Example
if __name__ == "__main__":
    store = LocalFAISSStore()
    
    # # Ingest a PDF (if it exists)
    # pdf_path = "D:\Downloads\HARISH JAMALLAMUDI_Sr_ Data Scientist. final.pdf"
    # if os.path.exists(pdf_path):
    #     print(f"Ingesting {pdf_path}...")
    #     store.ingest_pdf(pdf_path, category="resume")
        
    #     # Search
    #     print("\nSearching for 'AI implementation'...")
    #     hits = store.search("AI implementation details")
    #     for h in hits:
    #         print(f"Found: {h['text'][:200]}...") # Print first 200 chars
    # else:
    #     print("PDF not found for testing.")
    store.search("AI implementation details", k=3)

    