from article_processor import ArticleProcessor
import sys

def interactive_demo():
    """
    Interactive demo of the article processor
    """
    print("🤖 Article Processor Interactive Demo")
    print("="*50)
    
    # Get API key
    api_key = input("Enter your OpenRouter API key: ").strip()
    if not api_key:
        print("❌ API key is required!")
        return
    
    # Get model choice
    print("\nAvailable models (examples):")
    print("1. qwen/qwen3-coder:free (Free)")
    print("2. anthropic/claude-3-haiku")
    print("3. openai/gpt-3.5-turbo")
    print("4. meta-llama/llama-3-8b-instruct")
    
    model_choice = input("\nEnter model name (or press Enter for default): ").strip()
    if not model_choice:
        model_choice = "qwen/qwen3-coder:free"
    
    # Initialize processor
    try:
        processor = ArticleProcessor(api_key, model_choice)
        print(f"✅ Initialized with model: {model_choice}")
    except Exception as e:
        print(f"❌ Error initializing processor: {e}")
        return
    
    while True:
        print("\n" + "="*50)
        print("Choose an option:")
        print("1. Process article from URL")
        print("2. Process article from HTML file")
        print("3. Process article from HTML text")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            url = input("Enter the URL: ").strip()
            if url:
                try:
                    result = processor.process_article(url, is_url=True)
                    display_results(result)
                except Exception as e:
                    print(f"❌ Error: {e}")
        
        elif choice == "2":
            file_path = input("Enter the HTML file path: ").strip()
            if file_path:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    result = processor.process_article(html_content, is_url=False)
                    display_results(result)
                except Exception as e:
                    print(f"❌ Error: {e}")
        
        elif choice == "3":
            print("Enter HTML content (press Ctrl+D or Ctrl+Z when done):")
            try:
                html_content = sys.stdin.read()
                result = processor.process_article(html_content, is_url=False)
                display_results(result)
            except Exception as e:
                print(f"❌ Error: {e}")
        
        elif choice == "4":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please try again.")

def display_results(result):
    """Display processing results"""
    print("\n" + "="*80)
    print("📋 SUMMARY")
    print("="*80)
    print(result['summary'])
    
    print("\n" + "="*80)
    print("✨ REWRITTEN ARTICLE")
    print("="*80)
    print(result['rewritten'])
    
    # Ask if user wants to save
    save = input("\n💾 Save results to file? (y/n): ").strip().lower()
    if save == 'y':
        filename = input("Enter filename (default: article_results.txt): ").strip()
        if not filename:
            filename = "article_results.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("ARTICLE PROCESSING RESULTS\n")
                f.write("="*50 + "\n\n")
                f.write("SUMMARY:\n")
                f.write(result['summary'])
                f.write("\n\n" + "="*50 + "\n\n")
                f.write("REWRITTEN ARTICLE:\n")
                f.write(result['rewritten'])
            print(f"✅ Results saved to: {filename}")
        except Exception as e:
            print(f"❌ Error saving file: {e}")

if __name__ == "__main__":
    interactive_demo()
