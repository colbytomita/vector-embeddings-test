# Vector Embeddings Test Project

This project demonstrates how to use OpenAI's embedding API to generate vector embeddings from text documents. It provides a simple implementation that reads a text file and converts its content into a high-dimensional vector representation.

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

1. Place your text in `example.txt` or modify the file path in `main.py`

2. Run the script:

```bash
python src/main.py
```

The script will output the embedding vector for your text.

## Project Structure

```
vector-embed-test/
├── .env                # API key configuration (not in repo)
├── .gitignore         # Git ignore rules
├── README.md          # This file
├── requirements.txt   # Python dependencies
├── example.txt        # Sample text file
└── src/
    └── main.py        # Main script
```

## Security Notes

- Never commit your `.env` file
- Keep your API key secure
- The `.gitignore` file is configured to prevent sensitive files from being committed

## Contributing

Feel free to submit issues and enhancement requests!

## License

[MIT License](LICENSE)
