import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import re
from urllib.parse import urljoin, urlparse
import argparse
import os
from typing import Optional, Dict, Any

class ArticleProcessor:
    def __init__(self, openrouter_api_key: str, model: str = "qwen/qwen3-coder:free"):
        """
        Initialize the Article Processor
        
        Args:
            openrouter_api_key: Your OpenRouter API key
            model: The model to use for processing (default: qwen/qwen3-coder:free)
        """
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=openrouter_api_key,
        )
        self.model = model
    
    def fetch_html(self, url: str) -> str:
        """
        Fetch HTML content from a URL
        
        Args:
            url: The URL to fetch
            
        Returns:
            HTML content as string
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise Exception(f"Error fetching URL: {e}")
    
    def extract_main_content(self, html_content: str) -> str:
        """
        Extract the main article content from HTML
        
        Args:
            html_content: Raw HTML content
            
        Returns:
            Extracted article text
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'advertisement']):
            element.decompose()
        
        # Try to find main content using common selectors
        content_selectors = [
            'article',
            '[role="main"]',
            'main',
            '.article-content',
            '.post-content',
            '.entry-content',
            '.content',
            '#content',
            '.article-body',
            '.story-body'
        ]
        
        main_content = None
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                main_content = elements[0]
                break
        
        # If no specific content area found, try to find the largest text block
        if not main_content:
            # Look for divs with substantial text content
            divs = soup.find_all('div')
            best_div = None
            max_text_length = 0
            
            for div in divs:
                text = div.get_text(strip=True)
                if len(text) > max_text_length and len(text) > 500:  # Minimum length threshold
                    max_text_length = len(text)
                    best_div = div
            
            main_content = best_div
        
        if not main_content:
            # Fallback: use body content
            main_content = soup.find('body') or soup
        
        # Extract and clean text
        text = main_content.get_text(separator=' ', strip=True)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        
        return text.strip()
    
    def summarize_article(self, article_text: str) -> str:
        """
        Generate a summary of the article using OpenRouter
        
        Args:
            article_text: The article text to summarize
            
        Returns:
            Article summary
        """
        try:
            completion = self.client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://your-site.com",  # Optional
                    "X-Title": "Article Processor",  # Optional
                },
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at creating concise, informative summaries. Provide a clear summary that captures the main points and key insights of the article."
                    },
                    {
                        "role": "user",
                        "content": f"Please provide a comprehensive summary of the following article:\n\n{article_text}"
                    }
                ],
                max_tokens=500,
                temperature=0.3
            )
            return completion.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error generating summary: {e}")
    
    def rewrite_article(self, article_text: str) -> str:
        """
        Rewrite the article in a beautiful, engaging format
        
        Args:
            article_text: The original article text
            
        Returns:
            Rewritten article
        """
        try:
            completion = self.client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://your-site.com",  # Optional
                    "X-Title": "Article Processor",  # Optional
                },
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a skilled writer and editor. Rewrite articles to be more engaging, well-structured, and beautifully written while maintaining all the original information and facts. Use clear headings, smooth transitions, and compelling language."
                    },
                    {
                        "role": "user",
                        "content": f"Please rewrite the following article to make it more engaging and beautifully written, while preserving all the original information:\n\n{article_text}"
                    }
                ],
                max_tokens=2000,
                temperature=0.7
            )
            return completion.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error rewriting article: {e}")
    
    def process_article(self, html_source: str, is_url: bool = True) -> Dict[str, str]:
        """
        Complete article processing pipeline
        
        Args:
            html_source: Either a URL or HTML content string
            is_url: Whether html_source is a URL (True) or HTML content (False)
            
        Returns:
            Dictionary containing original text, summary, and rewritten version
        """
        print("🔄 Processing article...")
        
        # Get HTML content
        if is_url:
            print(f"📥 Fetching content from: {html_source}")
            html_content = self.fetch_html(html_source)
        else:
            html_content = html_source
        
        # Extract main content
        print("🔍 Extracting main article content...")
        article_text = self.extract_main_content(html_content)
        
        if len(article_text) < 100:
            raise Exception("Could not extract sufficient article content. The page might not contain a main article.")
        
        print(f"📝 Extracted {len(article_text)} characters of content")
        
        # Generate summary
        print("📋 Generating summary...")
        summary = self.summarize_article(article_text)
        
        # Rewrite article
        print("✨ Rewriting article...")
        rewritten = self.rewrite_article(article_text)
        
        return {
            'original': article_text,
            'summary': summary,
            'rewritten': rewritten
        }

def main():
    parser = argparse.ArgumentParser(description='Process HTML articles with AI')
    parser.add_argument('source', help='URL or path to HTML file')
    parser.add_argument('--api-key', required=True, help='OpenRouter API key')
    parser.add_argument('--model', default='qwen/qwen3-coder:free', help='Model to use (default: qwen/qwen3-coder:free)')
    parser.add_argument('--output', help='Output file path (optional)')
    
    args = parser.parse_args()
    
    try:
        processor = ArticleProcessor(args.api_key, args.model)
        
        # Determine if source is URL or file
        is_url = args.source.startswith(('http://', 'https://'))
        
        if not is_url:
            # Read from file
            with open(args.source, 'r', encoding='utf-8') as f:
                html_content = f.read()
            result = processor.process_article(html_content, is_url=False)
        else:
            result = processor.process_article(args.source, is_url=True)
        
        # Display results
        print("\n" + "="*80)
        print("📋 SUMMARY")
        print("="*80)
        print(result['summary'])
        
        print("\n" + "="*80)
        print("✨ REWRITTEN ARTICLE")
        print("="*80)
        print(result['rewritten'])
        
        # Save to file if specified
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write("ARTICLE PROCESSING RESULTS\n")
                f.write("="*50 + "\n\n")
                f.write("SUMMARY:\n")
                f.write(result['summary'])
                f.write("\n\n" + "="*50 + "\n\n")
                f.write("REWRITTEN ARTICLE:\n")
                f.write(result['rewritten'])
            print(f"\n💾 Results saved to: {args.output}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    print("\n✅ Processing complete!")
    return 0

if __name__ == "__main__":
    exit(main())
