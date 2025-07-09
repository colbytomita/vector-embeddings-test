# Debug Scripts

This folder contains debug scripts for troubleshooting the vector embeddings application.

## Files

- `debug_chat.py` - Debug script to test chat bot responses

## Usage

### Running the Debug Script

From the project root directory:

```bash
python debug/debug_chat.py
```

Or from within the debug folder:

```bash
cd debug
python debug_chat.py
```

### What it does

The debug script will:

1. Initialize the DocumentManager and ChatBot
2. Search for relevant documents using the taxonomy question
3. Display found documents and their similarity scores
4. Show the full chat bot response
5. Help identify issues with content processing or response generation

### Prerequisites

Make sure you have:

1. All dependencies installed: `pip install -r requirements.txt`
2. A valid `.env` file with your OpenAI API key
3. Some documents in the `knowledge_base` folder

### Troubleshooting

If you encounter import errors:

- Make sure you're running from the project root directory
- Check that all dependencies are installed
- Verify your Python environment is activated

If the chat bot isn't finding documents:

- Check that documents have been processed and embeddings generated
- Verify the similarity threshold is appropriate (0.3 is used in debug)
- Look at the document content to ensure it matches your queries
