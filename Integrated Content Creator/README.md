# Integrated Content Creator

A comprehensive application that transforms trending topics into engaging blog posts through an automated 3-step process.

## Features

🔍 **Trend Search**: Search Google News for trending articles with customizable parameters
📄 **Article Scraping**: Automatically scrape and process selected articles
✨ **Content Creation**: Generate summaries and rewrite articles into engaging blog posts

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Set up Playwright browsers:
```bash
python setup.py
```

Or manually:
```bash
playwright install chromium
```

## Usage

1. **Run the application**:
```bash
python main.py
```

2. **Search for Articles**:
   - Enter your Apify API token
   - Add search keywords (trends you want to follow)
   - Set parameters (max articles, time period, region)
   - Click "Search Articles"

3. **Process Content**:
   - Select an interesting article from the results
   - Review the generated summary
   - Click "Use to Create Blog Post" to generate content
   - Blog posts are saved as `output1.txt`, `output2.txt`, etc.

## Requirements

- **Apify API Token**: Required for Google News scraping
- **Internet Connection**: For API calls and web scraping
- **Python 3.7+**: Required for all dependencies

## API Configuration

The app uses hardcoded OpenRouter credentials for content generation:
- **Model**: qwen/qwen3-coder:free
- **API Key**: Pre-configured (no input required)

## Output

Generated blog posts are saved as numbered text files (`output1.txt`, `output2.txt`, etc.) containing:
- Original article metadata
- Rewritten blog post content
- Timestamp of creation

## Workflow

1. **Trend Search** → Find relevant articles from Google News
2. **Article Selection** → Choose the most interesting/viral content
3. **Content Processing** → Generate summary and blog post
4. **File Output** → Save formatted blog post to text file

## Troubleshooting

- **Playwright Issues**: Run `playwright install chromium`
- **API Errors**: Check your Apify API token
- **Scraping Failures**: Some websites may block automated access
- **Content Generation**: Ensure stable internet connection for OpenRouter API

## File Structure

```
Integrated Content Creator/
├── main.py              # Main application
├── requirements.txt     # Python dependencies
├── setup.py            # Setup script for Playwright
├── README.md           # This file
└── output*.txt         # Generated blog posts
```