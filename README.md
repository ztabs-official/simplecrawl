# SimpleCrawl

Simplecrawl is an open-source project that wraps the powerful [crawl4ai](https://github.com/unclecode/crawl4ai) library in a FastAPI-powered API. It provides an efficient, scalable, and easy-to-integrate solution for web crawling.

## Features

- **Web Scraping**: Extract content from websites in various formats (markdown, HTML, etc.)
- **Structured Data Extraction**: Extract JSON data using schemas or prompts
- **Screenshot Capture**: Take screenshots of web pages
- **Page Actions**: Perform actions like clicking, waiting, and typing before scraping
- **Location Simulation**: Simulate requests from different countries and languages

## Installation

```bash
# Clone the repository
git clone https://github.com/ztabs-official/simplecrawl.git
cd simplecrawl

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Application

```bash
# Set the Python path and run the application
PYTHONPATH=. python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at http://localhost:8000. You can access the interactive API documentation at http://localhost:8000/docs.

## Running Tests

The project includes both unit tests and integration tests:

```bash
# Run all tests
PYTHONPATH=. pytest tests/ -v

# Run only unit tests
PYTHONPATH=. pytest tests/unit/ -v

# Run only integration tests
PYTHONPATH=. pytest tests/integration/ -v

# Run tests with coverage report
PYTHONPATH=. pytest tests/ --cov=app
```

## CI/CD Pipeline

The project uses GitHub Actions for continuous integration and deployment:

1. When code is pushed to the main branch, GitHub Actions automatically runs all tests
2. If all tests pass, the code is deployed to the production server
3. The deployment process updates dependencies and restarts the service

## API Endpoints

### `/v1/scrape`

Scrape a URL and return the content in specified formats.

**Supported Formats:**
- `markdown`: Clean markdown content
- `html`: Processed HTML content
- `rawHtml`: Raw unprocessed HTML
- `links`: List of all links on the page
- `json`: Structured data extraction (requires json_options)
- `screenshot`: Regular screenshot
- `screenshot@fullPage`: Full page screenshot

See the API documentation for more details and examples.

## Architecture

SimpleCrawl is built with a clean, modular architecture:

- **FastAPI**: Provides the web framework for the API endpoints
- **crawl4ai**: Powers the core web crawling and scraping functionality
- **Pydantic**: Handles data validation and serialization
- **pytest**: Ensures code quality through comprehensive testing

## Acknowledgments

This project wouldn't be possible without these amazing open-source projects:

- [crawl4ai](https://github.com/unclecode/crawl4ai) - An open-source LLM-friendly web crawler and scraper that powers the core functionality of SimpleCrawl
- [FastAPI](https://fastapi.tiangolo.com/) - A modern, fast web framework for building APIs
- [Pydantic](https://docs.pydantic.dev/) - Data validation and settings management
- [pytest](https://docs.pytest.org/) - Testing framework

## License

This project is licensed under the terms of the license included in the repository.
