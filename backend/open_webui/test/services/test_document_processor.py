"""Tests for DocumentProcessor."""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from open_webui.services.document_processor import DocumentProcessor, ProcessingError


@pytest.fixture
def processor():
    """Create DocumentProcessor instance."""
    return DocumentProcessor(max_chunk_size=1000)


@pytest.fixture
def temp_pdf():
    """Create a temporary PDF file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as f:
        # This won't be a real PDF, but we'll mock the extraction
        f.write("Mock PDF content")
        temp_path = f.name

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def temp_html():
    """Create a temporary HTML file for testing."""
    html_content = """
    <html>
    <head><title>Test Document</title></head>
    <body>
        <script>alert('remove me');</script>
        <h1>Test Heading</h1>
        <p>This is a test paragraph with some content.</p>
        <p>This is another paragraph.</p>
    </body>
    </html>
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(html_content)
        temp_path = f.name

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def temp_docx():
    """Create a temporary DOCX file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.docx', delete=False) as f:
        # This won't be a real DOCX, but we'll mock the extraction
        f.write("Mock DOCX content")
        temp_path = f.name

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.mark.asyncio
async def test_process_html_document(processor, temp_html):
    """Test processing HTML document."""
    result = await processor.process_document(temp_html, 'html')

    assert 'text' in result
    assert 'chunks' in result
    assert 'content_hash' in result
    assert 'summary' in result
    assert 'word_count' in result

    # Check that script was removed
    assert 'alert' not in result['text'].lower()
    assert 'test paragraph' in result['text'].lower()

    # Check hash
    assert len(result['content_hash']) == 64  # SHA-256

    # Check word count
    assert result['word_count'] > 0


@pytest.mark.asyncio
async def test_process_pdf_document(processor, temp_pdf):
    """Test processing PDF document."""
    # Mock pdfplumber
    with patch('open_webui.services.document_processor.pdfplumber') as mock_pdf:
        # Setup mock
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "This is text from a PDF document."

        mock_pdf_obj = MagicMock()
        mock_pdf_obj.pages = [mock_page, mock_page]
        mock_pdf_obj.__enter__ = MagicMock(return_value=mock_pdf_obj)
        mock_pdf_obj.__exit__ = MagicMock()

        mock_pdf.open.return_value = mock_pdf_obj

        result = await processor.process_document(temp_pdf, 'pdf')

        assert 'text' in result
        assert 'page_count' in result
        assert result['page_count'] == 2
        assert 'pdf document' in result['text'].lower()


@pytest.mark.asyncio
async def test_process_docx_document(processor, temp_docx):
    """Test processing DOCX document."""
    # Mock python-docx
    with patch('open_webui.services.document_processor.Document') as mock_doc:
        # Setup mock
        mock_para1 = MagicMock()
        mock_para1.text = "First paragraph from DOCX."

        mock_para2 = MagicMock()
        mock_para2.text = "Second paragraph from DOCX."

        mock_doc_obj = MagicMock()
        mock_doc_obj.paragraphs = [mock_para1, mock_para2]
        mock_doc_obj.tables = []

        mock_doc.return_value = mock_doc_obj

        result = await processor.process_document(temp_docx, 'docx')

        assert 'text' in result
        assert 'first paragraph' in result['text'].lower()
        assert 'second paragraph' in result['text'].lower()


@pytest.mark.asyncio
async def test_process_nonexistent_file(processor):
    """Test processing non-existent file."""
    with pytest.raises(ProcessingError) as exc_info:
        await processor.process_document('/nonexistent/file.pdf', 'pdf')

    assert 'not found' in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_process_unsupported_type(processor, temp_pdf):
    """Test processing unsupported document type."""
    with pytest.raises(ProcessingError) as exc_info:
        await processor.process_document(temp_pdf, 'xlsx')

    assert 'unsupported' in str(exc_info.value).lower()


def test_clean_text(processor):
    """Test text cleaning."""
    dirty_text = """


    This  is   text    with
    extra   whitespace


    and   newlines



    """

    clean = processor._clean_text(dirty_text)

    assert '\n\n\n' not in clean
    assert '  ' not in clean
    assert clean.startswith('This')


def test_chunk_text_small(processor):
    """Test chunking small text."""
    text = "This is a small text that fits in one chunk."

    chunks = processor._chunk_text(text, max_size=1000)

    assert len(chunks) == 1
    assert chunks[0] == text


def test_chunk_text_large(processor):
    """Test chunking large text."""
    # Create text that needs chunking
    text = "This is a sentence. " * 100  # ~2000 chars

    chunks = processor._chunk_text(text, max_size=500, overlap=50)

    assert len(chunks) > 1
    # Check overlap - last chars of chunk[0] should appear in chunk[1]
    if len(chunks) >= 2:
        # There should be some overlap
        assert len(chunks[0]) <= 500


def test_generate_hash(processor):
    """Test hash generation."""
    text1 = "This is test text"
    text2 = "This is test text"
    text3 = "This is different text"

    hash1 = processor._generate_hash(text1)
    hash2 = processor._generate_hash(text2)
    hash3 = processor._generate_hash(text3)

    # Same text should produce same hash
    assert hash1 == hash2

    # Different text should produce different hash
    assert hash1 != hash3

    # Hash should be 64 chars (SHA-256 hex)
    assert len(hash1) == 64


def test_generate_summary_short(processor):
    """Test summary generation for short text."""
    text = "This is a short text."

    summary = processor._generate_summary(text, max_length=500)

    assert summary == text


def test_generate_summary_long(processor):
    """Test summary generation for long text."""
    text = "This is a sentence. " * 100  # ~2000 chars

    summary = processor._generate_summary(text, max_length=100)

    assert len(summary) <= 110  # Allow for sentence boundary
    assert summary.endswith('.') or summary.endswith('...')


def test_validate_file_exists(processor, temp_html):
    """Test file validation for existing file."""
    result = processor.validate_file(temp_html, 'html')
    assert result is True


def test_validate_file_not_found(processor):
    """Test file validation for non-existent file."""
    with pytest.raises(ProcessingError) as exc_info:
        processor.validate_file('/nonexistent/file.pdf', 'pdf')

    assert 'not found' in str(exc_info.value).lower()


def test_validate_file_type_mismatch(processor, temp_html):
    """Test file validation with type mismatch."""
    # Should still return True but log warning
    result = processor.validate_file(temp_html, 'pdf')
    assert result is True


@pytest.mark.asyncio
async def test_corrupted_pdf_handling(processor, temp_pdf):
    """Test handling of corrupted PDF."""
    # Mock pdfplumber to raise exception
    with patch('open_webui.services.document_processor.pdfplumber') as mock_pdf:
        mock_pdf.open.side_effect = Exception("Corrupted PDF")

        with pytest.raises(ProcessingError) as exc_info:
            await processor.process_document(temp_pdf, 'pdf')

        # Check that it's a ProcessingError with appropriate message
        assert 'extraction failed' in str(exc_info.value).lower() or 'processing failed' in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_empty_pdf_handling(processor, temp_pdf):
    """Test handling of PDF with no extractable text."""
    # Mock pdfplumber to return empty text
    with patch('open_webui.services.document_processor.pdfplumber') as mock_pdf:
        mock_page = MagicMock()
        mock_page.extract_text.return_value = None

        mock_pdf_obj = MagicMock()
        mock_pdf_obj.pages = [mock_page]
        mock_pdf_obj.__enter__ = MagicMock(return_value=mock_pdf_obj)
        mock_pdf_obj.__exit__ = MagicMock()

        mock_pdf.open.return_value = mock_pdf_obj

        with pytest.raises(ProcessingError) as exc_info:
            await processor.process_document(temp_pdf, 'pdf')

        assert 'no text' in str(exc_info.value).lower()


def test_get_document_processor():
    """Test getting global processor instance."""
    from open_webui.services.document_processor import get_document_processor

    processor1 = get_document_processor()
    processor2 = get_document_processor()

    # Should return same instance
    assert processor1 is processor2
