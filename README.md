# Vector Embeddings Document Manager & Chat Bot

An interactive command-line application that uses OpenAI's embedding API to manage documents, perform similarity searches, and chat with an AI bot that uses your vectorized documents as knowledge base.

## Features

- 📄 **Document Management**: Add and store text documents with vector embeddings
- 🔍 **Similarity Search**: Find documents similar to each other or to your queries
- 💬 **AI Chat Bot**: Ask questions and get answers based on your document collection
- 🎯 **Interactive Interface**: Clean, user-friendly command-line interface
- 💾 **Persistent Storage**: Documents and embeddings are saved locally
- 📁 **Organized Knowledge Base**: Dedicated folder for knowledge base documents

## Prerequisites

- Python 3.7+
- OpenAI API key

## Setup

1. Clone this repository:

```bash
git clone <your-repo-url>
cd vector-embeddings-test
```

2. Create and activate a virtual environment (recommended):

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory and add your OpenAI API key:

```
OPENAI_API_KEY=your_openai_key_here
```

## Usage

Run the interactive application:

```bash
python src/main.py
```

### Main Menu Options

1. **📄 Add a document**: Add text files to your knowledge base
2. **📚 List all documents**: View all documents in your collection
3. **🔍 Search for similar documents**: Find documents similar to a selected document
4. **💬 Chat with the bot**: Ask questions about your documents
5. **🚪 Exit**: Close the application

### How to Use

1. **Adding Documents**:

   - Choose option 1 from the main menu
   - Enter the path to your text file (e.g., `knowledge_base/my_document.txt`)
   - The system will generate embeddings and store the document

2. **Similarity Search**:

   - Choose option 3 from the main menu
   - Select a document from your collection
   - Set a similarity threshold (0.0-1.0)
   - View similar documents with scores

3. **Chat with Bot**:
   - Choose option 4 from the main menu
   - Ask questions about your documents
   - The bot will search through your documents and provide answers based on the content

## Project Structure

```
vector-embeddings-test/
├── .env                # API key configuration (not in repo)
├── .gitignore         # Git ignore rules
├── README.md          # This file
├── requirements.txt   # Python dependencies
├── knowledge_base/    # Knowledge base documents
│   ├── README.md     # Knowledge base documentation
│   ├── sample_document.txt
│   ├── ai_basics.txt
│   ├── example.txt
│   └── similar_example.txt
├── documents/         # Directory for original documents
├── embeddings/        # Directory for stored embeddings
└── src/
    └── main.py        # Main interactive application
```

## Knowledge Base Organization

The `knowledge_base/` folder contains all the documents that serve as your AI's knowledge base:

- **Sample Documents**: Pre-loaded example documents for testing
- **Custom Documents**: Add your own text files here
- **Subfolder Organization**: Create topic-based subfolders for better organization

### Adding Your Own Documents

1. Place your text files in the `knowledge_base/` folder
2. Run the application and choose "Add a document"
3. Enter the path (e.g., `knowledge_base/my_document.txt`)
4. The document will be processed and added to your knowledge base

## Example Workflow

1. **Add Documents**:

   ```
   📄 Add Document
   Enter the path to the document file: knowledge_base/my_document.txt
   ✅ Successfully added document: my_document.txt
   ```

2. **Search Similar Documents**:

   ```
   🔍 Search for Similar Documents
   Available documents:
   1. my_document.txt (ID: my_document)
   2. ai_basics.txt (ID: ai_basics)

   Select a document (1-2): 1
   Enter similarity threshold (0.0-1.0, default 0.7): 0.8

   ✅ Found 1 similar document(s):
   1. 📄 ai_basics.txt
      Similarity: 85.23%
   ```

3. **Chat with Bot**:
   ```
   💬 Chat with Document Bot
   🤔 You: What is the main topic of my documents?
   🤖 Bot: Based on your documents, the main topic appears to be...
   ```

## Security Notes

- Never commit your `.env` file
- Keep your API key secure
- The `.gitignore` file is configured to prevent sensitive files from being committed

## Contributing

Feel free to submit issues and enhancement requests!

## License

[MIT License](LICENSE)
