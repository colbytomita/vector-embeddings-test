# Knowledge Base

This folder contains documents that serve as the knowledge base for the Vector Embeddings Document Manager & Chat Bot.

## Purpose

The documents in this folder will be processed by the application to:

- Generate vector embeddings for similarity search
- Provide context for the AI chat bot
- Enable document-based question answering

## Supported File Types

The application now supports a wide range of file formats:

### 📄 Text Documents

- `.txt` - Plain text files
- `.md` - Markdown files
- `.doc` - Word documents (limited support)
- `.docx` - Word documents (limited support)

### 📄 PDF Documents

- `.pdf` - PDF files with text extraction

### 🖼️ Image Files (OCR Support)

- `.png` - PNG images
- `.jpg` - JPEG images
- `.jpeg` - JPEG images
- `.gif` - GIF images
- `.bmp` - Bitmap images
- `.tiff` - TIFF images

## Current Documents

- `sample_document.txt` - Machine learning fundamentals
- `ai_basics.txt` - Artificial intelligence basics
- `technology_overview.txt` - Modern software development overview
- `example.txt` - Test document for embeddings
- `similar_example.txt` - Similar test document

## Adding New Documents

To add new knowledge base documents:

1. Place your files in this folder
2. Run the application: `python src/main.py`
3. Choose option 1: "Add a document"
4. Enter the path to your file (e.g., `knowledge_base/your_document.pdf`)

## File Processing Features

### PDF Processing

- **Text Extraction**: Automatically extracts text from PDF pages
- **Page Numbering**: Preserves page structure in extracted content
- **Multi-page Support**: Handles PDFs with multiple pages

### Image OCR (Optical Character Recognition)

- **Text Recognition**: Extracts text from images using OCR
- **Multiple Formats**: Supports common image formats
- **Quality Dependent**: OCR accuracy depends on image quality and text clarity

### Text Documents

- **Direct Reading**: Reads text files directly
- **Encoding Support**: Handles UTF-8 encoded files
- **Markdown Support**: Processes markdown formatting

## Installation Requirements

For full functionality, install the additional dependencies:

```bash
pip install PyPDF2 Pillow pytesseract pdfplumber
```

### System Requirements for OCR

- **Windows**: Install Tesseract OCR from https://github.com/UB-Mannheim/tesseract/wiki
- **macOS**: `brew install tesseract`
- **Linux**: `sudo apt-get install tesseract-ocr`

## Best Practices

### For Text Documents

- Use clear, descriptive filenames
- Ensure files are UTF-8 encoded
- Keep documents focused on specific topics for better similarity matching

### For PDFs

- Use text-based PDFs for best results
- Scanned PDFs may require OCR processing
- Ensure PDFs are not password-protected

### For Images

- Use high-quality images with clear text
- Ensure good contrast between text and background
- Avoid heavily stylized fonts
- Use images with minimal background noise

### General Guidelines

- Keep documents focused on specific topics
- Use plain text format for best compatibility
- Avoid very large files (recommend under 10MB per file)
- Test OCR quality with sample images before adding many image files

## File Organization

You can create subfolders within this directory to organize documents by topic:

```
knowledge_base/
├── technology/
│   ├── machine_learning.txt
│   └── artificial_intelligence.pdf
├── business/
│   ├── marketing.png
│   └── finance.docx
└── general/
    └── miscellaneous.txt
```

The application will recursively search for supported files in this directory structure.

## Troubleshooting

### PDF Issues

- If text extraction fails, the PDF might be image-based (scanned)
- Consider converting scanned PDFs to images for OCR processing

### Image OCR Issues

- Ensure Tesseract OCR is properly installed
- Check image quality and text clarity
- Try different image formats if OCR fails

### Word Document Issues

- Limited support for .doc/.docx files
- Consider converting to PDF or text format for better compatibility
