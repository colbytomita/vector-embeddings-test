import os
import json
import numpy as np
from pathlib import Path
from datetime import datetime
from openai import OpenAI
from openai import OpenAIError, RateLimitError, APITimeoutError, APIConnectionError
from dotenv import load_dotenv
import sys
import time
import pickle
from typing import List, Dict, Any

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("❌ OPENAI_API_KEY not found in .env file.")
    print("Please create a .env file with your OpenAI API key:")
    print("OPENAI_API_KEY=your_key_here")
    sys.exit(1)

client = OpenAI(api_key=api_key)

class DocumentManager:
    def __init__(self, knowledge_base_dir="knowledge_base", embeddings_dir="embeddings"):
        """Initialize the document manager with directories for knowledge base and embeddings."""
        self.knowledge_base_dir = Path(knowledge_base_dir)
        self.embeddings_dir = Path(embeddings_dir)
        
        # Cache-related attributes
        self.cache_file = Path("embeddings_cache.pkl")
        self.embeddings_cache = {}
        self.cache_metadata_file = Path("cache_metadata.json")
        
        # Create directories if they don't exist
        try:
            self.knowledge_base_dir.mkdir(exist_ok=True)
            self.embeddings_dir.mkdir(exist_ok=True)
        except PermissionError:
            print("❌ Permission denied: Cannot create directories. Check your permissions.")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error creating directories: {e}")
            sys.exit(1)
        
        # Load or build cache
        self.load_or_build_cache()

    def load_or_build_cache(self):
        """Load embeddings from cache or build them if not available."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "rb") as f:
                    self.embeddings_cache = pickle.load(f)
                print(f"✅ Loaded {len(self.embeddings_cache)} embeddings from cache.")
            except Exception as e:
                print(f"⚠️  Error loading cache: {e}. Rebuilding cache.")
                self.embeddings_cache = {}
        else:
            print("⚠️  Cache file not found. Building cache from scratch.")
            self.embeddings_cache = {}

        if self.cache_metadata_file.exists():
            try:
                with open(self.cache_metadata_file, "r", encoding="utf-8") as f:
                    self.cache_metadata = json.load(f)
                print(f"✅ Loaded cache metadata from {self.cache_metadata_file}")
            except Exception as e:
                print(f"⚠️  Error loading cache metadata: {e}. Starting with empty metadata.")
                self.cache_metadata = {}
        else:
            print(f"⚠️  Cache metadata file not found: {self.cache_metadata_file}. Starting with empty metadata.")
            self.cache_metadata = {}
        
        # Check if cache is valid and rebuild if necessary
        if not self.is_cache_valid():
            print("🔄 Cache is invalid, rebuilding...")
            self.build_cache()

    def save_cache(self):
        """Save embeddings and cache metadata to files."""
        try:
            with open(self.cache_file, "wb") as f:
                pickle.dump(self.embeddings_cache, f)
            print(f"✅ Saved {len(self.embeddings_cache)} embeddings to cache.")
        except Exception as e:
            print(f"❌ Error saving cache: {e}")

    def save_cache_metadata(self):
        """Save cache metadata to a JSON file."""
        try:
            with open(self.cache_metadata_file, "w", encoding="utf-8") as f:
                json.dump(self.cache_metadata, f, indent=2)
            print(f"✅ Saved cache metadata to {self.cache_metadata_file}")
        except Exception as e:
            print(f"❌ Error saving cache metadata: {e}")

    def build_cache(self):
        """Build cache from JSON files in the embeddings directory."""
        print("🔄 Building embeddings cache...")
        self.embeddings_cache = {}
        
        try:
            for file in self.embeddings_dir.glob("*.json"):
                try:
                    with open(file, "r", encoding="utf-8") as f:
                        doc = json.load(f)
                        self.embeddings_cache[file.stem] = doc
                except json.JSONDecodeError:
                    print(f"⚠️  Skipping corrupted file: {file}")
                    continue
                except Exception as e:
                    print(f"⚠️  Error processing {file}: {e}")
                    continue
            
            # Save cache
            self.save_cache()
            
            # Update metadata
            self.cache_metadata = {
                "last_built": datetime.now().isoformat(),
                "total_documents": len(self.embeddings_cache),
                "cache_version": "1.0"
            }
            self.save_cache_metadata()
            
            print(f"✅ Built cache with {len(self.embeddings_cache)} documents")
            
        except Exception as e:
            print(f"❌ Error building cache: {e}")

    def invalidate_cache(self):
        """Rebuild cache when documents change."""
        print("🔄 Invalidating cache...")
        try:
            # Remove old cache files
            if self.cache_file.exists():
                self.cache_file.unlink()
            if self.cache_metadata_file.exists():
                self.cache_metadata_file.unlink()
            
            # Rebuild cache
            self.build_cache()
            print("✅ Cache invalidated and rebuilt")
            
        except Exception as e:
            print(f"❌ Error invalidating cache: {e}")

    def is_cache_valid(self):
        """Check if cache is valid by comparing with actual files."""
        try:
            # Get list of JSON files in embeddings directory
            actual_files = set()
            for file in self.embeddings_dir.glob("*.json"):
                actual_files.add(file.stem)
            
            # Get list of cached documents
            cached_files = set(self.embeddings_cache.keys())
            
            # Check if files match
            if actual_files != cached_files:
                print(f"⚠️  Cache mismatch: {len(actual_files)} files on disk vs {len(cached_files)} in cache")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error checking cache validity: {e}")
            return False

    def check_embedding_dimensions(self):
        """Check and report embedding dimensions across all documents."""
        dimensions = {}
        issues = []
        
        try:
            for doc_id, doc in self.embeddings_cache.items():
                embedding = doc.get("embedding", [])
                dim = len(embedding)
                dimensions[doc_id] = dim
                
                if dim == 0:
                    issues.append(f"❌ {doc_id}: Empty embedding")
                elif dim != 1536:  # OpenAI's text-embedding-ada-002 dimension
                    issues.append(f"⚠️  {doc_id}: {dim} dimensions (expected 1536)")
            
            # Report findings
            if dimensions:
                unique_dims = set(dimensions.values())
                print(f"📊 Embedding dimensions found: {unique_dims}")
                
                if len(unique_dims) > 1:
                    print("⚠️  Multiple embedding dimensions detected!")
                    for doc_id, dim in dimensions.items():
                        print(f"   {doc_id}: {dim} dimensions")
                
                if issues:
                    print("\n🔍 Issues found:")
                    for issue in issues:
                        print(f"   {issue}")
                else:
                    print("✅ All embeddings have consistent dimensions")
            
            return len(unique_dims) == 1 if dimensions else True
            
        except Exception as e:
            print(f"❌ Error checking embedding dimensions: {e}")
            return False

    def get_available_documents(self):
        """Get list of available documents in the knowledge base directory."""
        available_docs = []
        if not self.knowledge_base_dir.exists():
            return available_docs
        
        # Supported file extensions
        supported_extensions = {'.txt', '.md', '.doc', '.docx', '.pdf', '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'}
        
        try:
            # Recursively search for supported files in knowledge_base directory
            for file_path in self.knowledge_base_dir.rglob("*"):
                if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                    # Skip README files
                    if file_path.name.lower() == 'readme.md':
                        continue
                    available_docs.append({
                        'path': file_path,
                        'name': file_path.name,
                        'relative_path': str(file_path.relative_to(self.knowledge_base_dir))
                    })
        except Exception as e:
            print(f"⚠️  Error scanning knowledge base directory: {e}")
        
        return available_docs

    def extract_text_from_pdf(self, file_path):
        """Extract text from PDF files."""
        try:
            import pdfplumber
            
            text_content = []
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(f"Page {page_num}:\n{page_text}")
            
            if not text_content:
                print("⚠️  Warning: No text could be extracted from the PDF.")
                return ""
            
            return "\n\n".join(text_content)
            
        except ImportError:
            print("❌ pdfplumber not installed. Install it with: pip install pdfplumber")
            return ""
        except Exception as e:
            print(f"❌ Error extracting text from PDF: {e}")
            return ""

    def extract_text_from_image(self, file_path):
        """Extract text from image files using OCR."""
        try:
            import pytesseract
            from PIL import Image
            
            # Open the image
            image = Image.open(file_path)
            
            # Extract text using OCR
            text = pytesseract.image_to_string(image)
            
            if not text.strip():
                print("⚠️  Warning: No text could be extracted from the image.")
                return ""
            
            return text.strip()
            
        except ImportError:
            print("❌ pytesseract or Pillow not installed. Install them with: pip install pytesseract Pillow")
            print("Note: You also need to install Tesseract OCR on your system.")
            return ""
        except Exception as e:
            print(f"❌ Error extracting text from image: {e}")
            return ""

    def extract_text_from_file(self, file_path):
        """Extract text from various file types."""
        file_path = Path(file_path)
        file_extension = file_path.suffix.lower()
        
        # Handle different file types
        if file_extension == '.pdf':
            print("📄 Extracting text from PDF...")
            return self.extract_text_from_pdf(file_path)
        
        elif file_extension in {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'}:
            print("🖼️  Extracting text from image using OCR...")
            return self.extract_text_from_image(file_path)
        
        elif file_extension in {'.txt', '.md'}:
            # Handle text files
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return f.read()
            except UnicodeDecodeError:
                print("❌ File encoding error. Please ensure the file is UTF-8 encoded.")
                raise
            except PermissionError:
                print(f"❌ Permission denied: Cannot read file {file_path}")
                raise
            except Exception as e:
                print(f"❌ Error reading file: {e}")
                raise
        
        elif file_extension in {'.doc', '.docx'}:
            print("📝 Attempting to extract text from Word document...")
            # For Word documents, we'll try to read as text first
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return f.read()
            except:
                print("⚠️  Word document processing is limited. Consider converting to PDF or text format.")
                return ""
        
        else:
            print(f"⚠️  Unsupported file type: {file_extension}")
            return ""

    def generate_embedding(self, text, max_retries=3):
        """Generate an embedding for a piece of text with retry logic."""
        for attempt in range(max_retries):
            try:
                response = client.embeddings.create(
                    model="text-embedding-ada-002",
                    input=text
                )
                return response.data[0].embedding
            except RateLimitError:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    print(f"⚠️  Rate limit hit. Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                else:
                    print("❌ Rate limit exceeded. Please try again later.")
                    raise
            except APITimeoutError:
                if attempt < max_retries - 1:
                    print(f"⚠️  API timeout. Retrying... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(1)
                else:
                    print("❌ API timeout after multiple attempts. Please check your internet connection.")
                    raise
            except APIConnectionError:
                if attempt < max_retries - 1:
                    print(f"⚠️  Connection error. Retrying... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(2)
                else:
                    print("❌ Connection failed. Please check your internet connection.")
                    raise
            except OpenAIError as e:
                print(f"❌ OpenAI API error: {str(e)}")
                raise
            except Exception as e:
                print(f"❌ Unexpected error generating embedding: {str(e)}")
                raise

    def add_document(self, file_path):
        """Add a document and generate its embedding."""
        # Extract text from the file
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Could not find file: {file_path}")

        # Extract text content based on file type
        content = self.extract_text_from_file(file_path)
        
        if not content.strip():
            raise ValueError("No text content could be extracted from the file. The file might be empty, corrupted, or in an unsupported format.")

        # Generate embedding
        print(f"🔄 Generating embedding for {file_path.name}...")
        try:
            embedding = self.generate_embedding(content)
        except Exception as e:
            print(f"❌ Failed to generate embedding: {e}")
            raise

        # Create a document record
        doc_info = {
            "original_filename": file_path.name,
            "original_path": str(file_path),
            "file_type": file_path.suffix.lower(),
            "content": content,
            "embedding": embedding,
            "added_date": datetime.now().isoformat()
        }

        # Save document info and embedding
        doc_id = file_path.stem
        embedding_path = self.embeddings_dir / f"{doc_id}.json"
        
        try:
            with open(embedding_path, "w", encoding="utf-8") as f:
                json.dump(doc_info, f, indent=2)
        except PermissionError:
            print(f"❌ Permission denied: Cannot write to {embedding_path}")
            raise
        except Exception as e:
            print(f"❌ Error saving document: {e}")
            raise

        print(f"✅ Successfully added document: {file_path.name}")
        
        # Update cache with new document
        self.embeddings_cache[doc_id] = doc_info
        self.save_cache()
        
        # Update cache metadata
        self.cache_metadata["last_updated"] = datetime.now().isoformat()
        self.cache_metadata["total_documents"] = len(self.embeddings_cache)
        self.save_cache_metadata()

        return doc_id

    def get_document(self, doc_id):
        """Retrieve a document and its embedding by ID."""
        # Try to get from cache first
        if doc_id in self.embeddings_cache:
            return self.embeddings_cache[doc_id]
        
        # Fallback to file system if not in cache
        embedding_path = self.embeddings_dir / f"{doc_id}.json"
        if not embedding_path.exists():
            raise FileNotFoundError(f"No document found with ID: {doc_id}")

        try:
            with open(embedding_path, "r", encoding="utf-8") as f:
                doc = json.load(f)
                # Add to cache for future use
                self.embeddings_cache[doc_id] = doc
                return doc
        except json.JSONDecodeError:
            print(f"❌ Corrupted document file: {embedding_path}")
            raise
        except Exception as e:
            print(f"❌ Error reading document: {e}")
            raise

    def list_documents(self):
        """List all documents in the embeddings directory."""
        docs = []
        try:
            # Use cache for faster listing
            for doc_id, doc in self.embeddings_cache.items():
                docs.append({
                    "id": doc_id,
                    "filename": doc.get("original_filename", "Unknown"),
                    "file_type": doc.get("file_type", "unknown"),
                    "added_date": doc.get("added_date", "Unknown")
                })
        except Exception as e:
            print(f"❌ Error listing documents: {e}")
            raise
        return docs

    def cosine_similarity(self, embedding1, embedding2):
        """Calculate cosine similarity between two embeddings."""
        try:
            embedding1 = np.array(embedding1)
            embedding2 = np.array(embedding2)
            
            # Check for dimension mismatch
            if embedding1.shape != embedding2.shape:
                print(f"❌ Dimension mismatch: {embedding1.shape} vs {embedding2.shape}")
                print("   This usually happens when embeddings were generated with different models.")
                return 0.0
            
            # Check for zero vectors
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
                
            return np.dot(embedding1, embedding2) / (norm1 * norm2)
        except Exception as e:
            print(f"❌ Error calculating similarity: {e}")
            return 0.0

    def find_similar_documents(self, query_doc_id, threshold=0.7):
        """Find documents similar to the query document."""
        try:
            query_doc = self.get_document(query_doc_id)
            query_embedding = query_doc.get("embedding")
            if not query_embedding:
                print(f"❌ No embedding found for document: {query_doc_id}")
                return []
        except Exception as e:
            print(f"❌ Error getting query document: {e}")
            return []
        
        similar_docs = []
        try:
            # Use cache for faster search
            for doc_id, doc in self.embeddings_cache.items():
                if doc_id == query_doc_id:
                    continue
                
                doc_embedding = doc.get("embedding")
                if not doc_embedding:
                    print(f"⚠️  Skipping document {doc_id}: No embedding found")
                    continue
                
                similarity = self.cosine_similarity(query_embedding, doc_embedding)
                
                if similarity >= threshold:
                    similar_docs.append({
                        "id": doc_id,
                        "filename": doc.get("original_filename", "Unknown"),
                        "file_type": doc.get("file_type", "unknown"),
                        "similarity": similarity
                    })
            
            # Sort by similarity score
            similar_docs.sort(key=lambda x: x["similarity"], reverse=True)
            return similar_docs
        except Exception as e:
            print(f"❌ Error finding similar documents: {e}")
            return []

    def search_by_query(self, query_text, threshold=0.7):
        """Search for documents similar to a query text."""
        try:
            # Generate embedding for the query
            query_embedding = self.generate_embedding(query_text)
        except Exception as e:
            print(f"❌ Error generating query embedding: {e}")
            return []
        
        similar_docs = []
        try:
            # Use cache for faster search
            for doc_id, doc in self.embeddings_cache.items():
                doc_embedding = doc.get("embedding")
                if not doc_embedding:
                    print(f"⚠️  Skipping document {doc_id}: No embedding found")
                    continue
                
                similarity = self.cosine_similarity(query_embedding, doc_embedding)
                
                if similarity >= threshold:
                    similar_docs.append({
                        "id": doc_id,
                        "filename": doc.get("original_filename", "Unknown"),
                        "file_type": doc.get("file_type", "unknown"),
                        "similarity": similarity,
                        "content": doc.get("content", "")[:2000] + "..." if len(doc.get("content", "")) > 2000 else doc.get("content", "")
                    })
            
            # Sort by similarity score
            similar_docs.sort(key=lambda x: x["similarity"], reverse=True)
            return similar_docs
        except Exception as e:
            print(f"❌ Error searching documents: {e}")
            return []

class ChatBot:
    def __init__(self, doc_manager):
        self.doc_manager = doc_manager

    def chat(self, user_input, max_retries=3):
        """Chat with the bot using the vectorized documents as context."""
        for attempt in range(max_retries):
            try:
                # Search for relevant documents with a lower threshold for better recall
                relevant_docs = self.doc_manager.search_by_query(user_input, threshold=0.3)
                
                if not relevant_docs:
                    return "I don't have enough relevant information to answer that question. Try adding more documents or rephrasing your question."
                
                # Create context from relevant documents
                context = "Based on the following documents:\n\n"
                for i, doc in enumerate(relevant_docs[:3], 1):  # Use top 3 most relevant
                    file_type_icon = "📄" if doc.get("file_type") in [".txt", ".md"] else "🖼️" if doc.get("file_type") in [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff"] else "📄"
                    context += f"{i}. {file_type_icon} {doc['filename']} (similarity: {doc['similarity']:.2%})\n"
                    # Truncate content if too long to avoid token limits
                    content = doc['content']
                    if len(content) > 4000:
                        content = content[:4000] + "..."
                    context += f"   Content: {content}\n\n"
                
                # Create the prompt
                prompt = f"{context}\n\nUser question: {user_input}\n\nPlease provide a comprehensive answer based on the information in the documents above. Include all relevant details and be thorough in your response. If the documents don't contain enough information to answer the question completely, say so."
                
                # Get response from OpenAI
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided documents. Provide comprehensive and detailed answers. If you need to list multiple items, be thorough and complete."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1500,
                    temperature=0.7
                )
                
                return response.choices[0].message.content
                
            except RateLimitError:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    print(f"⚠️  Rate limit hit. Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                else:
                    return "Sorry, I'm experiencing high demand. Please try again in a few minutes."
            except APITimeoutError:
                if attempt < max_retries - 1:
                    print(f"⚠️  API timeout. Retrying... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(1)
                else:
                    return "Sorry, the request timed out. Please try again."
            except APIConnectionError:
                if attempt < max_retries - 1:
                    print(f"⚠️  Connection error. Retrying... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(2)
                else:
                    return "Sorry, I'm having trouble connecting. Please check your internet connection."
            except OpenAIError as e:
                return f"Sorry, I encountered an API error: {str(e)}"
            except Exception as e:
                return f"Sorry, I encountered an unexpected error: {str(e)}"

def print_banner():
    """Print the application banner."""
    print("=" * 60)
    print("🤖 Vector Embeddings Document Manager & Chat Bot")
    print("=" * 60)

def print_menu():
    """Print the main menu."""
    print("\n📋 Main Menu:")
    print("1. 📄 Add a document")
    print("2. 📚 List all documents")
    print("3. 🔍 Search for similar documents")
    print("4. 💬 Chat with the bot")
    print("5. ⚙️  Cache management")
    print("6. 🚪 Exit")
    print("-" * 40)

def validate_file_path(file_path):
    """Validate if a file path is reasonable and safe."""
    if not file_path or not file_path.strip():
        return False, "File path cannot be empty"
    
    # Check for potentially dangerous paths
    dangerous_patterns = ['..', '~', '/etc', '/var', 'C:\\Windows']
    file_path_lower = file_path.lower()
    for pattern in dangerous_patterns:
        if pattern in file_path_lower:
            return False, f"File path contains potentially dangerous pattern: {pattern}"
    
    # Check file extension (optional safety measure)
    supported_extensions = {'.txt', '.md', '.doc', '.docx', '.pdf', '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'}
    if not any(file_path.lower().endswith(ext) for ext in supported_extensions):
        print("⚠️  Warning: File doesn't have a supported extension")
    
    return True, ""

def add_document_interactive(doc_manager):
    """Interactive document addition."""
    print("\n📄 Add Document")
    print("-" * 20)
    
    # Show available documents in knowledge base
    available_docs = doc_manager.get_available_documents()
    if available_docs:
        print("📁 Available documents in knowledge base:")
        for i, doc in enumerate(available_docs, 1):
            file_type_icon = "📄" if doc['name'].lower().endswith(('.txt', '.md', '.doc', '.docx', '.pdf')) else "🖼️"
            print(f"   {i}. {file_type_icon} {doc['relative_path']}")
        print()
    
    while True:
        file_path = input("Enter the path to the document file (or 'back' to return): ").strip()
        
        if file_path.lower() == 'back':
            return
        
        if not file_path:
            print("❌ Please enter a valid file path.")
            continue
        
        # Validate file path
        is_valid, error_msg = validate_file_path(file_path)
        if not is_valid:
            print(f"❌ {error_msg}")
            continue
        
        try:
            doc_id = doc_manager.add_document(file_path)
            print(f"✅ Document added successfully with ID: {doc_id}")
            break
        except FileNotFoundError as e:
            print(f"❌ {e}")
        except ValueError as e:
            print(f"❌ {e}")
        except PermissionError as e:
            print(f"❌ {e}")
        except Exception as e:
            print(f"❌ Error adding document: {e}")

def list_documents_interactive(doc_manager):
    """Interactive document listing."""
    print("\n📚 Document Library")
    print("-" * 30)
    
    try:
        docs = doc_manager.list_documents()
    except Exception as e:
        print(f"❌ Error listing documents: {e}")
        return
    
    if not docs:
        print("📭 No documents found. Add some documents first!")
        return
    
    print(f"📖 Found {len(docs)} document(s):\n")
    for i, doc in enumerate(docs, 1):
        file_type_icon = "📄" if doc.get("file_type") in [".txt", ".md", ".doc", ".docx", ".pdf"] else "🖼️" if doc.get("file_type") in [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff"] else "📄"
        print(f"{i}. {file_type_icon} {doc['filename']}")
        print(f"   ID: {doc['id']}")
        print(f"   Type: {doc.get('file_type', 'unknown')}")
        print(f"   Added: {doc.get('added_date', 'Unknown')}")
        print()

def get_valid_choice(prompt, max_value, allow_back=True):
    """Get a valid numeric choice from user input."""
    while True:
        choice = input(prompt).strip()
        
        if allow_back and choice.lower() == 'back':
            return None
        
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < max_value:
                return choice_idx
            else:
                print(f"❌ Invalid selection. Please enter a number between 1 and {max_value}.")
        except ValueError:
            print("❌ Please enter a valid number.")

def get_valid_threshold():
    """Get a valid similarity threshold from user input."""
    while True:
        threshold_input = input("Enter similarity threshold (0.0-1.0, default 0.7): ").strip()
        if not threshold_input:
            return 0.7
        try:
            threshold = float(threshold_input)
            if 0.0 <= threshold <= 1.0:
                return threshold
            else:
                print("❌ Threshold must be between 0.0 and 1.0")
        except ValueError:
            print("❌ Please enter a valid number.")

def search_similar_interactive(doc_manager):
    """Interactive similarity search."""
    print("\n🔍 Search for Similar Documents")
    print("-" * 35)
    
    try:
        docs = doc_manager.list_documents()
    except Exception as e:
        print(f"❌ Error loading documents: {e}")
        return
    
    if len(docs) < 2:
        print("❌ Need at least 2 documents to perform similarity search.")
        print("Add more documents first!")
        return
    
    print("Available documents:")
    for i, doc in enumerate(docs, 1):
        file_type_icon = "📄" if doc.get("file_type") in [".txt", ".md", ".doc", ".docx", ".pdf"] else "🖼️" if doc.get("file_type") in [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff"] else "📄"
        print(f"{i}. {file_type_icon} {doc['filename']} (ID: {doc['id']})")
    
    choice_idx = get_valid_choice(f"\nSelect a document (1-{len(docs)}) or 'back': ", len(docs))
    if choice_idx is None:
        return
    
    selected_doc = docs[choice_idx]
    threshold = get_valid_threshold()
    
    print(f"\n🔍 Finding documents similar to '{selected_doc['filename']}'...")
    try:
        similar_docs = doc_manager.find_similar_documents(selected_doc['id'], threshold)
    except Exception as e:
        print(f"❌ Error finding similar documents: {e}")
        return
    
    if not similar_docs:
        print(f"❌ No documents found with similarity >= {threshold:.1%}")
    else:
        print(f"\n✅ Found {len(similar_docs)} similar document(s):\n")
        for i, doc in enumerate(similar_docs, 1):
            file_type_icon = "📄" if doc.get("file_type") in [".txt", ".md", ".doc", ".docx", ".pdf"] else "🖼️" if doc.get("file_type") in [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff"] else "📄"
            print(f"{i}. {file_type_icon} {doc['filename']}")
            print(f"   Similarity: {doc['similarity']:.2%}")
            print()

def chat_interactive(chat_bot):
    """Interactive chat with the bot."""
    print("\n💬 Chat with Document Bot")
    print("-" * 30)
    print("Ask questions about your documents! Type 'back' to return to main menu.")
    print("The bot will search through your documents to find relevant information.")
    print()
    
    while True:
        try:
            user_input = input("🤔 You: ").strip()
        except KeyboardInterrupt:
            print("\n\n👋 Chat session ended.")
            break
        except EOFError:
            print("\n\n👋 Chat session ended.")
            break
        
        if user_input.lower() == 'back':
            break
        
        if not user_input:
            print("❌ Please enter a question.")
            continue
        
        print("🤖 Bot: ", end="")
        try:
            response = chat_bot.chat(user_input)
            print(response)
        except KeyboardInterrupt:
            print("\n\n👋 Chat session ended.")
            break
        except Exception as e:
            print(f"❌ Error in chat: {e}")
        print()

def cache_management_interactive(doc_manager):
    """Interactive cache management."""
    print("\n⚙️  Cache Management")
    print("-" * 25)
    
    while True:
        print("\nCache Options:")
        print("1. 📊 Show cache status")
        print("2. 🔄 Rebuild cache")
        print("3. 🗑️  Clear cache")
        print("4. ✅ Validate cache")
        print("5. 📏 Check embedding dimensions")
        print("6. ↩️  Back to main menu")
        
        choice = input("\nSelect an option (1-6): ").strip()
        
        if choice == "1":
            # Show cache status
            print(f"\n📊 Cache Status:")
            print(f"   Documents in cache: {len(doc_manager.embeddings_cache)}")
            if hasattr(doc_manager, 'cache_metadata') and doc_manager.cache_metadata:
                print(f"   Last built: {doc_manager.cache_metadata.get('last_built', 'Unknown')}")
                print(f"   Cache version: {doc_manager.cache_metadata.get('cache_version', 'Unknown')}")
            else:
                print("   No cache metadata available")
            
            # Check cache validity
            is_valid = doc_manager.is_cache_valid()
            print(f"   Cache valid: {'✅ Yes' if is_valid else '❌ No'}")
            
        elif choice == "2":
            # Rebuild cache
            print("\n🔄 Rebuilding cache...")
            try:
                doc_manager.build_cache()
                print("✅ Cache rebuilt successfully!")
            except Exception as e:
                print(f"❌ Error rebuilding cache: {e}")
                
        elif choice == "3":
            # Clear cache
            print("\n🗑️  Clearing cache...")
            try:
                doc_manager.embeddings_cache = {}
                if doc_manager.cache_file.exists():
                    doc_manager.cache_file.unlink()
                if doc_manager.cache_metadata_file.exists():
                    doc_manager.cache_metadata_file.unlink()
                print("✅ Cache cleared successfully!")
            except Exception as e:
                print(f"❌ Error clearing cache: {e}")
                
        elif choice == "4":
            # Validate cache
            print("\n✅ Validating cache...")
            try:
                is_valid = doc_manager.is_cache_valid()
                if is_valid:
                    print("✅ Cache is valid!")
                else:
                    print("❌ Cache is invalid. Consider rebuilding.")
            except Exception as e:
                print(f"❌ Error validating cache: {e}")
                
        elif choice == "5":
            # Check embedding dimensions
            print("\n📏 Checking embedding dimensions...")
            try:
                doc_manager.check_embedding_dimensions()
            except Exception as e:
                print(f"❌ Error checking embedding dimensions: {e}")
                
        elif choice == "6":
            # Back to main menu
            break
            
        else:
            print("❌ Invalid choice. Please enter a number between 1 and 6.")

def main():
    """Main application loop."""
    print_banner()
    
    # Initialize document manager and chat bot
    try:
        doc_manager = DocumentManager()
        chat_bot = ChatBot(doc_manager)
    except Exception as e:
        print(f"❌ Failed to initialize application: {e}")
        sys.exit(1)
    
    while True:
        try:
            print_menu()
            
            choice = input("Enter your choice (1-5): ").strip()
            
            if choice == "1":
                add_document_interactive(doc_manager)
            elif choice == "2":
                list_documents_interactive(doc_manager)
            elif choice == "3":
                search_similar_interactive(doc_manager)
            elif choice == "4":
                chat_interactive(chat_bot)
            elif choice == "5":
                cache_management_interactive(doc_manager)
            elif choice == "6":
                print("\n👋 Goodbye! Thanks for using the Vector Embeddings Manager!")
                break
            else:
                print("❌ Invalid choice. Please enter a number between 1-6.")
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Thanks for using the Vector Embeddings Manager!")
            break
        except EOFError:
            print("\n\n👋 Goodbye! Thanks for using the Vector Embeddings Manager!")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            print("Please try again.")

if __name__ == "__main__":
    main() 