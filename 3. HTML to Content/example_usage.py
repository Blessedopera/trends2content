from article_processor import ArticleProcessor
import os

def example_usage():
    """
    Example usage of the ArticleProcessor class
    """
    # You'll need to set your OpenRouter API key
    API_KEY = "your-openrouter-api-key-here"  # Replace with your actual API key
    
    # Initialize the processor
    processor = ArticleProcessor(
        openrouter_api_key=API_KEY,
        model="qwen/qwen3-coder:free"  # You can change this to any OpenRouter model
    )
    
    # Example 1: Process from URL
    try:
        print("Example 1: Processing article from URL")
        url = "https://example-news-site.com/article"  # Replace with actual URL
        result = processor.process_article(url, is_url=True)
        
        print("Summary:", result['summary'][:200] + "...")
        print("Rewritten excerpt:", result['rewritten'][:200] + "...")
        
    except Exception as e:
        print(f"Error processing URL: {e}")
    
    # Example 2: Process from HTML string
    sample_html = """
    <html>
    <body>
        <article>
            <h1>The Future of Artificial Intelligence</h1>
            <p>Artificial Intelligence (AI) has been rapidly evolving over the past decade, 
            transforming industries and reshaping how we interact with technology. From 
            machine learning algorithms that can predict consumer behavior to natural 
            language processing systems that can understand and generate human-like text, 
            AI is becoming increasingly sophisticated.</p>
            
            <p>One of the most significant developments in recent years has been the 
            emergence of large language models like GPT and Claude. These models have 
            demonstrated remarkable capabilities in understanding context, generating 
            coherent text, and even solving complex problems across various domains.</p>
            
            <p>As we look toward the future, AI is expected to play an even more prominent 
            role in our daily lives. From autonomous vehicles to personalized healthcare, 
            the applications are virtually limitless. However, with great power comes great 
            responsibility, and it's crucial that we develop AI systems that are ethical, 
            transparent, and beneficial to humanity as a whole.</p>
        </article>
    </body>
    </html>
    """
    
    try:
        print("\nExample 2: Processing article from HTML string")
        result = processor.process_article(sample_html, is_url=False)
        
        print("\n📋 SUMMARY:")
        print(result['summary'])
        
        print("\n✨ REWRITTEN ARTICLE:")
        print(result['rewritten'])
        
    except Exception as e:
        print(f"Error processing HTML: {e}")

if __name__ == "__main__":
    example_usage()
