import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import json
import asyncio
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import re
from urllib.parse import urljoin, urlparse
from playwright.async_api import async_playwright
from markdown2 import markdown
import html2text

class IntegratedContentCreator:
    def __init__(self, root):
        self.root = root
        self.root.title("Integrated Content Creator - Trend to Blog Post")
        self.root.geometry("1200x900")
        
        # Hardcoded API credentials
        self.openrouter_api_key = "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"
        self.model_name = "qwen/qwen3-coder:free"
        
        # Initialize OpenRouter client - will be created when needed
        self.openrouter_client = None
        
        # Variables to store data between steps
        self.articles_data = []
        self.selected_article = None
        self.article_html = None
        self.article_summary = None
        self.blog_post_counter = 1
        
        self.setup_ui()
        
    def get_openrouter_client(self):
        """Get or create OpenRouter client with proper authentication"""
        if self.openrouter_client is None:
            self.openrouter_client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.openrouter_api_key,
            )
        return self.openrouter_client
        
    def setup_ui(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Search Articles
        self.search_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.search_frame, text="1. Search Trends")
        self.setup_search_tab()
        
        # Tab 2: Article Processing
        self.process_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.process_frame, text="2. Create Content")
        self.setup_process_tab()
        
    def setup_search_tab(self):
        main_frame = ttk.Frame(self.search_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Trend Search to Articles", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0,20))
        
        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="Search Parameters", padding="10")
        input_frame.pack(fill=tk.X, pady=(0,20))
        
        # API Key section
        ttk.Label(input_frame, text="Apify API Token:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.api_key_entry = ttk.Entry(input_frame, width=50, show="*")
        self.api_key_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Keywords section
        ttk.Label(input_frame, text="Search Keywords:").grid(row=1, column=0, sticky=tk.W, pady=5)
        keywords_frame = ttk.Frame(input_frame)
        keywords_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.keywords_listbox = tk.Listbox(keywords_frame, height=3)
        self.keywords_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        keywords_buttons_frame = ttk.Frame(keywords_frame)
        keywords_buttons_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5,0))
        
        self.keyword_entry = ttk.Entry(keywords_buttons_frame, width=20)
        self.keyword_entry.pack(pady=2)
        
        ttk.Button(keywords_buttons_frame, text="Add", command=self.add_keyword).pack(pady=2)
        ttk.Button(keywords_buttons_frame, text="Remove", command=self.remove_keyword).pack(pady=2)
        
        # Add default keyword
        self.keywords_listbox.insert(tk.END, "AI technology")
        
        # Parameters row 1
        params_frame1 = ttk.Frame(input_frame)
        params_frame1.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(params_frame1, text="Max Articles:").grid(row=0, column=0, sticky=tk.W, padx=(0,10))
        self.max_news = ttk.Spinbox(params_frame1, from_=1, to=50, value=10, width=10)
        self.max_news.grid(row=0, column=1, sticky=tk.W, padx=(0,20))
        
        ttk.Label(params_frame1, text="Time Period:").grid(row=0, column=2, sticky=tk.W, padx=(0,10))
        self.time_period = ttk.Combobox(params_frame1, values=["Last hour", "Last 24 hours", "Last week", "Last month"], state="readonly", width=15)
        self.time_period.set("Last 24 hours")
        self.time_period.grid(row=0, column=3, sticky=tk.W)
        
        # Parameters row 2
        params_frame2 = ttk.Frame(input_frame)
        params_frame2.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(params_frame2, text="Region:").grid(row=0, column=0, sticky=tk.W, padx=(0,10))
        self.region_language = ttk.Combobox(params_frame2, values=[
            "United States (English)", "United Kingdom (English)", "Canada (English)",
            "Australia (English)", "Germany (German)", "France (French)"
        ], state="readonly", width=25)
        self.region_language.set("United States (English)")
        self.region_language.grid(row=0, column=1, sticky=tk.W)
        
        # Options
        options_frame = ttk.Frame(input_frame)
        options_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        self.decode_urls = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Decode URLs", variable=self.decode_urls).pack(side=tk.LEFT, padx=(0,20))
        
        self.extract_descriptions = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Extract Descriptions", variable=self.extract_descriptions).pack(side=tk.LEFT)
        
        # Configure grid weights
        input_frame.columnconfigure(1, weight=1)
        
        # Search button
        self.search_button = ttk.Button(main_frame, text="🔍 Search Articles", command=self.search_articles)
        self.search_button.pack(pady=10)
        
        # Status
        self.search_status = ttk.Label(main_frame, text="Ready to search...")
        self.search_status.pack(pady=5)
        
        # Results
        results_frame = ttk.LabelFrame(main_frame, text="Search Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(10,0))
        
        # Articles listbox with scrollbar
        articles_frame = ttk.Frame(results_frame)
        articles_frame.pack(fill=tk.BOTH, expand=True)
        
        self.articles_listbox = tk.Listbox(articles_frame, height=15)
        articles_scrollbar = ttk.Scrollbar(articles_frame, orient=tk.VERTICAL, command=self.articles_listbox.yview)
        self.articles_listbox.configure(yscrollcommand=articles_scrollbar.set)
        
        self.articles_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        articles_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Select article button
        self.select_button = ttk.Button(results_frame, text="Select Article & Process", command=self.select_article, state="disabled")
        self.select_button.pack(pady=10)
        
    def setup_process_tab(self):
        main_frame = ttk.Frame(self.process_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Article Processing & Content Creation", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0,20))
        
        # Selected article info
        self.article_info_frame = ttk.LabelFrame(main_frame, text="Selected Article", padding="10")
        self.article_info_frame.pack(fill=tk.X, pady=(0,20))
        
        self.article_info_label = ttk.Label(self.article_info_frame, text="No article selected", wraplength=800)
        self.article_info_label.pack()
        
        # Processing status
        self.process_status = ttk.Label(main_frame, text="Select an article from the search tab to begin processing")
        self.process_status.pack(pady=10)
        
        # Summary section
        summary_frame = ttk.LabelFrame(main_frame, text="Article Summary", padding="10")
        summary_frame.pack(fill=tk.BOTH, expand=True, pady=(0,20))
        
        self.summary_text = scrolledtext.ScrolledText(summary_frame, height=10, wrap=tk.WORD)
        self.summary_text.pack(fill=tk.BOTH, expand=True)
        
        # Create blog post button
        self.blog_button = ttk.Button(main_frame, text="Use to Create Blog Post", command=self.create_blog_post, state="disabled")
        self.blog_button.pack(pady=10)
        
        # Blog post status
        self.blog_status = ttk.Label(main_frame, text="")
        self.blog_status.pack(pady=5)
        
    def add_keyword(self):
        keyword = self.keyword_entry.get().strip()
        if keyword:
            self.keywords_listbox.insert(tk.END, keyword)
            self.keyword_entry.delete(0, tk.END)
    
    def remove_keyword(self):
        selection = self.keywords_listbox.curselection()
        if selection:
            self.keywords_listbox.delete(selection[0])
    
    def get_time_period_value(self, period):
        mapping = {
            "Last hour": "h",
            "Last 24 hours": "d", 
            "Last week": "w",
            "Last month": "m"
        }
        return mapping.get(period, "d")
    
    def get_region_code(self, region):
        mapping = {
            "United States (English)": "US:en",
            "United Kingdom (English)": "GB:en",
            "Canada (English)": "CA:en",
            "Australia (English)": "AU:en",
            "Germany (German)": "DE:de",
            "France (French)": "FR:fr"
        }
        return mapping.get(region, "US:en")
    
    def search_articles(self):
        api_token = self.api_key_entry.get().strip()
        keywords = [self.keywords_listbox.get(i) for i in range(self.keywords_listbox.size())]
        
        if not api_token:
            messagebox.showerror("Error", "Please enter your Apify API token")
            return
            
        if not keywords:
            messagebox.showerror("Error", "Please add at least one search keyword")
            return
        
        self.search_button.config(state="disabled")
        self.search_status.config(text="Searching articles...")
        self.articles_listbox.delete(0, tk.END)
        
        # Run search in separate thread
        thread = threading.Thread(target=self.run_search, args=(api_token, keywords))
        thread.daemon = True
        thread.start()
    
    def run_search(self, api_token, keywords):
        try:
            from apify_client import ApifyClient
            
            client = ApifyClient(api_token)
            
            max_news = int(self.max_news.get())
            time_period = self.get_time_period_value(self.time_period.get())
            region_code = self.get_region_code(self.region_language.get())
            
            run_input = {
                "keywords": keywords,
                "maxNews": max_news,
                "timePeriod": time_period,
                "regionAndLanguage": region_code,
                "decodeGoogleNewsUrls": self.decode_urls.get(),
                "extractArticleDescriptions": self.extract_descriptions.get(),
                "proxyConfiguration": {"useApifyProxy": True}
            }
            
            self.update_search_status("Calling Apify API...")
            
            run = client.actor("data_xplorer/google-news-scraper-fast").call(run_input=run_input)
            
            self.update_search_status("Fetching results...")
            
            results = []
            for item in client.dataset(run["defaultDatasetId"]).iterate_items():
                results.append(item)
            
            self.articles_data = results
            self.display_search_results(results)
            
        except Exception as e:
            self.update_search_status(f"Error: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Search failed: {str(e)}"))
        finally:
            self.root.after(0, lambda: self.search_button.config(state="normal"))
    
    def update_search_status(self, message):
        self.root.after(0, lambda: self.search_status.config(text=message))
    
    def display_search_results(self, results):
        def update_ui():
            self.articles_listbox.delete(0, tk.END)
            
            if results:
                for i, article in enumerate(results):
                    title = article.get('title', 'No title')[:80]
                    source = article.get('source', 'Unknown')
                    published = article.get('publishedAt', 'Unknown time')
                    display_text = f"{i+1}. {title} - {source} ({published})"
                    self.articles_listbox.insert(tk.END, display_text)
                
                self.search_status.config(text=f"Found {len(results)} articles")
                self.select_button.config(state="normal")
            else:
                self.search_status.config(text="No articles found")
                self.select_button.config(state="disabled")
        
        self.root.after(0, update_ui)
    
    def select_article(self):
        selection = self.articles_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an article first")
            return
        
        article_index = selection[0]
        self.selected_article = self.articles_data[article_index]
        
        # Update article info
        title = self.selected_article.get('title', 'No title')
        source = self.selected_article.get('source', 'Unknown source')
        url = self.selected_article.get('url', 'No URL')
        
        info_text = f"Title: {title}\nSource: {source}\nURL: {url}"
        self.article_info_label.config(text=info_text)
        
        # Switch to processing tab
        self.notebook.select(1)
        
        # Start processing
        self.process_status.config(text="Processing article...")
        self.summary_text.delete(1.0, tk.END)
        self.blog_button.config(state="disabled")
        
        # Run processing in separate thread
        thread = threading.Thread(target=self.process_article)
        thread.daemon = True
        thread.start()
    
    def process_article(self):
        try:
            url = self.selected_article.get('url')
            if not url:
                raise Exception("No URL found for selected article")
            
            # Step 1: Scrape HTML
            self.update_process_status("Scraping article HTML...")
            
            # Try scraping with retries
            max_retries = 3
            html_content = None
            last_error = None
            
            for attempt in range(max_retries):
                try:
                    self.update_process_status(f"Scraping article HTML... (Attempt {attempt + 1}/{max_retries})")
                    html_content = asyncio.run(self.scrape_article_html(url))
                    break  # Success, exit retry loop
                except Exception as e:
                    last_error = e
                    if attempt < max_retries - 1:  # Not the last attempt
                        self.update_process_status(f"Scraping failed, retrying... ({str(e)[:50]}...)")
                        continue
                    else:
                        # Last attempt failed, try alternative approach
                        self.update_process_status("Playwright failed, trying alternative method...")
                        try:
                            html_content = self.scrape_with_requests(url)
                        except Exception as e2:
                            raise Exception(f"All scraping methods failed. Playwright: {str(last_error)[:100]}... Requests: {str(e2)[:100]}...")
            
            if not html_content:
                raise Exception("Failed to retrieve HTML content from the article")
                
            # Step 2: Extract and process content
            self.update_process_status("Extracting article content...")
            article_text = self.extract_main_content(html_content)
            
            if len(article_text) < 200:  # Very short content might indicate scraping issues
                raise Exception("Retrieved content is too short. The article might not have been properly scraped.")
            
            # Step 3: Generate summary
            self.update_process_status("Generating summary...")
            summary = self.generate_summary(article_text)
            
            self.article_summary = summary
            self.article_html = html_content
            
            # Display summary
            self.root.after(0, lambda: self.summary_text.insert(1.0, summary))
            self.root.after(0, lambda: self.blog_button.config(state="normal"))
            self.update_process_status("Article processed successfully! Review the summary and create a blog post.")
            
        except Exception as e:
            error_msg = str(e)
            self.update_process_status(f"Error: {error_msg}")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Processing failed: {error_msg}"))
    
    def scrape_with_requests(self, url):
        """Fallback scraping method using requests"""
        try:
            # Multiple user agents to rotate
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
            ]
            
            import random
            selected_ua = random.choice(user_agents)
            
            headers = {
                'User-Agent': selected_ua,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'DNT': '1',
                'Cache-Control': 'max-age=0',
                'Referer': 'https://www.google.com/'
            }
            
            # Create session for cookie persistence
            session = requests.Session()
            session.headers.update(headers)
            
            # First request
            response = session.get(url, timeout=30, allow_redirects=True)
            response.raise_for_status()
            
            # Check if we got redirected to anti-bot page
            if self.is_anti_bot_page(response.text):
                # Try with different headers and delay
                import time
                time.sleep(2)
                
                # Update headers to look more human
                session.headers.update({
                    'User-Agent': random.choice(user_agents),
                    'Referer': url
                })
                
                response = session.get(url, timeout=30, allow_redirects=True)
                response.raise_for_status()
            
            return response.text
        except Exception as e:
            raise Exception(f"Requests scraping failed: {str(e)}")
    
    async def scrape_article_html(self, url):
        """
        Bulletproof web scraping with multiple anti-bot bypass techniques
        """
        async with async_playwright() as p:
            # Launch browser with stealth mode
            browser = await p.chromium.launch(
                headless=False,  # Use visible browser to avoid headless detection
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=VizDisplayCompositor',
                    '--disable-extensions',
                    '--no-first-run',
                    '--disable-default-apps',
                    '--disable-infobars',
                    '--window-size=1920,1080',
                    '--start-maximized'
                ]
            )
            
            # Create context with realistic settings
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='en-US',
                timezone_id='America/New_York',
                permissions=['geolocation'],
                extra_http_headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Cache-Control': 'max-age=0'
                }
            )
            
            page = await context.new_page()
            
            # Add stealth scripts to avoid detection
            await page.add_init_script("""
                // Remove webdriver property
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                
                // Mock plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                
                // Mock languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
                
                // Mock permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
                
                // Mock chrome runtime
                window.chrome = {
                    runtime: {},
                };
            """)
            
            try:
                # Navigate with realistic behavior
                self.update_process_status("Loading page with stealth mode...")
                await page.goto(url, wait_until='domcontentloaded', timeout=60000)
                
                # Wait for initial load
                await page.wait_for_timeout(3000)
                
                # Check for common anti-bot elements and handle them
                await self.handle_anti_bot_measures(page)
                
                # Wait for content to fully load
                await page.wait_for_timeout(5000)
                
                # Try to find and click "I'm not a robot" if present
                try:
                    captcha_frame = page.frame_locator('iframe[src*="recaptcha"]')
                    if await captcha_frame.locator('.recaptcha-checkbox').is_visible(timeout=2000):
                        self.update_process_status("Detected CAPTCHA, attempting to solve...")
                        await captcha_frame.locator('.recaptcha-checkbox').click()
                        await page.wait_for_timeout(3000)
                except:
                    pass
                
                # Scroll to simulate human behavior
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight/4)")
                await page.wait_for_timeout(1000)
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight/2)")
                await page.wait_for_timeout(1000)
                await page.evaluate("window.scrollTo(0, 0)")
                await page.wait_for_timeout(2000)
                
                # Get final content
                html_content = await page.content()
                
                # Check if we got a real article or anti-bot page
                if self.is_anti_bot_page(html_content):
                    self.update_process_status("Anti-bot page detected, trying alternative method...")
                    # Try with different approach
                    await page.reload(wait_until='networkidle', timeout=30000)
                    await page.wait_for_timeout(8000)  # Longer wait
                    html_content = await page.content()
                
                await browser.close()
                return html_content
                
            except Exception as e:
                await browser.close()
                raise Exception(f"Playwright scraping failed: {str(e)}")
    
    async def handle_anti_bot_measures(self, page):
        """Handle common anti-bot protection measures"""
        try:
            # Check for Cloudflare challenge
            if await page.locator('text="Checking your browser"').is_visible(timeout=2000):
                self.update_process_status("Cloudflare detected, waiting for challenge...")
                await page.wait_for_timeout(10000)  # Wait for Cloudflare to complete
            
            # Check for "Verify you are human" buttons
            verify_selectors = [
                'button:has-text("Verify")',
                'button:has-text("Continue")',
                'input[type="checkbox"][id*="human"]',
                '.verification-button',
                '#challenge-form button'
            ]
            
            for selector in verify_selectors:
                try:
                    if await page.locator(selector).is_visible(timeout=1000):
                        self.update_process_status(f"Found verification element, clicking...")
                        await page.locator(selector).click()
                        await page.wait_for_timeout(3000)
                        break
                except:
                    continue
                    
            # Handle cookie consent
            cookie_selectors = [
                'button:has-text("Accept")',
                'button:has-text("Allow")',
                'button:has-text("I agree")',
                '.cookie-accept',
                '#cookie-accept'
            ]
            
            for selector in cookie_selectors:
                try:
                    if await page.locator(selector).is_visible(timeout=1000):
                        await page.locator(selector).click()
                        await page.wait_for_timeout(1000)
                        break
                except:
                    continue
                    
        except Exception as e:
            # Continue even if anti-bot handling fails
            pass
    
    def is_anti_bot_page(self, html_content):
        """Check if the page is an anti-bot protection page"""
        anti_bot_indicators = [
            'verify you are human',
            'security check',
            'checking your browser',
            'cloudflare',
            'please enable javascript',
            'captcha',
            'bot protection',
            'access denied',
            'blocked',
            'reference id',
            'ray id'
        ]
        
        content_lower = html_content.lower()
        return any(indicator in content_lower for indicator in anti_bot_indicators)
    
    def extract_main_content(self, html_content):
        """Enhanced content extraction with better article detection"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # First check if this is an anti-bot page
        if self.is_anti_bot_page(html_content):
            raise Exception("Unable to bypass anti-bot protection. The page is showing a security verification screen.")
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'advertisement', 'ads', 'social-share']):
            element.decompose()
        
        # Enhanced content selectors (more comprehensive)
        content_selectors = [
            'article',
            '[role="main"]', 
            'main',
            '.article-content',
            '.article-body',
            '.post-content',
            '.entry-content',
            '.story-content',
            '.story-body',
            '.content',
            '#content',
            '.text-content',
            '.article-text',
            '.post-body',
            '.entry-body',
            '[data-module="ArticleBody"]',
            '.paywall-article',
            '.article-wrap'
        ]
        
        main_content = None
        max_content_length = 0
        
        # Try each selector and pick the one with most content
        for selector in content_selectors:
            elements = soup.select(selector)
            for element in elements:
                text_length = len(element.get_text(strip=True))
                if text_length > max_content_length and text_length > 200:
                    max_content_length = text_length
                    main_content = element
        
        # If no specific content area found, try to find the largest text block
        if not main_content:
            # Look for divs/sections with substantial text content
            all_elements = soup.find_all(['div', 'section', 'p'])
            best_element = None
            max_text_length = 0
            
            for element in all_elements:
                # Skip elements that are likely not article content
                if element.get('class'):
                    classes = ' '.join(element.get('class')).lower()
                    if any(skip in classes for skip in ['nav', 'menu', 'sidebar', 'footer', 'header', 'ad', 'social']):
                        continue
                
                text = element.get_text(strip=True)
                if len(text) > max_text_length and len(text) > 500:
                    max_text_length = len(text)
                    best_element = element
            
            main_content = best_element or soup.find('body') or soup
        
        if not main_content:
            raise Exception("Could not find article content on the page")
        
        # Extract and clean text
        text = main_content.get_text(separator=' ', strip=True)
        
        # Enhanced text cleaning
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        
        # Remove common non-article text patterns
        patterns_to_remove = [
            r'Subscribe to.*?newsletter',
            r'Sign up for.*?updates',
            r'Follow us on.*?social media',
            r'Share this article',
            r'Related articles?:.*',
            r'Advertisement',
            r'Sponsored content',
            r'Cookie policy',
            r'Terms of service',
            r'Privacy policy'
        ]
        
        for pattern in patterns_to_remove:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def generate_summary(self, article_text):
        try:
            client = self.get_openrouter_client()
            completion = client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://integrated-content-creator.com",
                    "X-Title": "Integrated Content Creator"
                },
                model=self.model_name,
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
            raise Exception(f"Error generating summary: {str(e)}")
    
    def update_process_status(self, message):
        self.root.after(0, lambda: self.process_status.config(text=message))
    
    def create_blog_post(self):
        if not self.article_summary:
            messagebox.showerror("Error", "No article summary available")
            return
        
        self.blog_button.config(state="disabled")
        self.blog_status.config(text="Creating blog post...")
        
        # Run blog creation in separate thread
        thread = threading.Thread(target=self.generate_blog_post)
        thread.daemon = True
        thread.start()
    
    def generate_blog_post(self):
        try:
            # Extract original article text again for blog post creation
            article_text = self.extract_main_content(self.article_html)
            
            client = self.get_openrouter_client()
            completion = client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://integrated-content-creator.com",
                    "X-Title": "Integrated Content Creator"
                },
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a skilled content writer. Rewrite articles into engaging blog posts that are well-structured, informative, and compelling. Use clear headings, smooth transitions, and maintain all important information while making it more readable and engaging."
                    },
                    {
                        "role": "user",
                        "content": f"Please rewrite the following article into an engaging blog post format:\n\n{article_text}"
                    }
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            blog_post = completion.choices[0].message.content
            
            # Save to file
            filename = f"output{self.blog_post_counter}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Blog Post Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*60 + "\n\n")
                f.write(f"Original Article: {self.selected_article.get('title', 'Unknown')}\n")
                f.write(f"Source: {self.selected_article.get('source', 'Unknown')}\n")
                f.write(f"URL: {self.selected_article.get('url', 'Unknown')}\n\n")
                f.write("="*60 + "\n\n")
                f.write(blog_post)
            
            self.blog_post_counter += 1
            
            self.root.after(0, lambda: self.blog_status.config(text=f"✅ Blog post saved as {filename}"))
            self.root.after(0, lambda: self.blog_button.config(state="normal"))
            self.root.after(0, lambda: messagebox.showinfo("Success", f"Blog post created and saved as {filename}"))
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self.blog_status.config(text=f"Error: {error_msg}"))
            self.root.after(0, lambda: self.blog_button.config(state="normal"))
            self.root.after(0, lambda: messagebox.showerror("Error", f"Blog post creation failed: {error_msg}"))

def main():
    root = tk.Tk()
    app = IntegratedContentCreator(root)
    
    print("🚀 Integrated Content Creator")
    print("="*50)
    print("This app combines trend search, article scraping, and content creation.")
    print("1. Search for trending articles")
    print("2. Select an interesting article")
    print("3. View the summary")
    print("4. Create a blog post")
    print("="*50)
    
    root.mainloop()

if __name__ == "__main__":
    main()