import os
import json
import numpy as np
from pathlib import Path
from datetime import datetime
from openai import OpenAI
from openai import OpenAIError, RateLimitError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError(
        "OPENAI_API_KEY not found in .env file.\n"
        "Please create a .env file with your OpenAI API key:\n"
        "OPENAI_API_KEY=your_key_here"
    )

client = OpenAI(api_key=api_key)

class DocumentManager:
    def __init__(self, docs_dir="documents", embeddings_dir="embeddings"):
        """Initialize the document manager with directories for documents and their embeddings."""
        self.docs_dir = Path(docs_dir)
        self.embeddings_dir = Path(embeddings_dir)
        
        # Create directories if they don't exist
        self.docs_dir.mkdir(exist_ok=True)
        self.embeddings_dir.mkdir(exist_ok=True)

    def generate_embedding(self, text):
        """Generate an embedding for a piece of text."""
        try:
            response = client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        except (RateLimitError, OpenAIError) as e:
            print(f"\nError generating embedding: {str(e)}")
            raise

    def add_document(self, file_path):
        """Add a document and generate its embedding."""
        # Read the document
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Could not find file: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Generate embedding
        embedding = self.generate_embedding(content)

        # Create a document record
        doc_info = {
            "original_filename": file_path.name,
            "content": content,
            "embedding": embedding,
            "added_date": datetime.now().isoformat()
        }

        # Save document info and embedding
        doc_id = file_path.stem
        embedding_path = self.embeddings_dir / f"{doc_id}.json"
        
        with open(embedding_path, "w", encoding="utf-8") as f:
            json.dump(doc_info, f, indent=2)

        return doc_id

    def get_document(self, doc_id):
        """Retrieve a document and its embedding by ID."""
        embedding_path = self.embeddings_dir / f"{doc_id}.json"
        if not embedding_path.exists():
            raise FileNotFoundError(f"No document found with ID: {doc_id}")

        with open(embedding_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def list_documents(self):
        """List all documents in the embeddings directory."""
        docs = []
        for file in self.embeddings_dir.glob("*.json"):
            with open(file, "r", encoding="utf-8") as f:
                doc = json.load(f)
                docs.append({
                    "id": file.stem,
                    "filename": doc["original_filename"],
                    "added_date": doc["added_date"]
                })
        return docs

    def cosine_similarity(self, embedding1, embedding2):
        """Calculate cosine similarity between two embeddings."""
        embedding1 = np.array(embedding1)
        embedding2 = np.array(embedding2)
        return np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))

    def find_similar_documents(self, query_doc_id, threshold=0.7):
        """Find documents similar to the query document."""
        query_doc = self.get_document(query_doc_id)
        query_embedding = query_doc["embedding"]
        
        similar_docs = []
        for file in self.embeddings_dir.glob("*.json"):
            if file.stem == query_doc_id:
                continue
                
            with open(file, "r", encoding="utf-8") as f:
                doc = json.load(f)
                similarity = self.cosine_similarity(query_embedding, doc["embedding"])
                
                if similarity >= threshold:
                    similar_docs.append({
                        "id": file.stem,
                        "filename": doc["original_filename"],
                        "similarity": similarity
                    })
        
        # Sort by similarity score
        similar_docs.sort(key=lambda x: x["similarity"], reverse=True)
        return similar_docs

def main():
    # Initialize document manager
    doc_manager = DocumentManager()
    
    # Example usage
    try:
        # Add some example documents
        print("\nAdding documents...")
        doc1_id = doc_manager.add_document("example.txt")
        print(f"Added document with ID: {doc1_id}")
        
        # List all documents
        print("\nAll documents in the system:")
        for doc in doc_manager.list_documents():
            print(f"- {doc['filename']} (ID: {doc['id']}, Added: {doc['added_date']})")
        
        # If you have multiple documents, you can find similar ones
        if len(doc_manager.list_documents()) > 1:
            print("\nFinding similar documents...")
            similar_docs = doc_manager.find_similar_documents(doc1_id)
            for doc in similar_docs:
                print(f"- {doc['filename']}: {doc['similarity']:.2%} similar")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("Please resolve the above error and try again.")

if __name__ == "__main__":
    main() 