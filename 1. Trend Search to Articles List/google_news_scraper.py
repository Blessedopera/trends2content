import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import json

# Create the main application
class GoogleNewsScraperUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Google News Scraper (Pay Per Result) - Apify API")
        self.root.geometry("900x750")
        
        # Main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Google News Scraper (Pay Per Result)", font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0,10))
        
        # API Key section
        ttk.Label(main_frame, text="Apify API Token:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.api_key_entry = ttk.Entry(main_frame, width=50, show="*")
        self.api_key_entry.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Keywords section
        ttk.Label(main_frame, text="Search Keywords:").grid(row=2, column=0, sticky=tk.W, pady=5)
        keywords_frame = ttk.Frame(main_frame)
        keywords_frame.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.keywords_listbox = tk.Listbox(keywords_frame, height=4)
        self.keywords_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        keywords_buttons_frame = ttk.Frame(keywords_frame)
        keywords_buttons_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5,0))
        
        self.keyword_entry = ttk.Entry(keywords_buttons_frame, width=20)
        self.keyword_entry.pack(pady=2)
        
        ttk.Button(keywords_buttons_frame, text="Add", command=self.add_keyword).pack(pady=2)
        ttk.Button(keywords_buttons_frame, text="Remove", command=self.remove_keyword).pack(pady=2)
        
        # Add default keyword
        self.keywords_listbox.insert(tk.END, "bitcoin")
        
        # Maximum News
        ttk.Label(main_frame, text="Maximum News:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.max_news = ttk.Spinbox(main_frame, from_=1, to=100, value=10)
        self.max_news.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Time Period
        ttk.Label(main_frame, text="Time Period:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.time_period = ttk.Combobox(main_frame, values=["Last hour", "Last 24 hours", "Last week", "Last month", "Last year"], state="readonly")
        self.time_period.set("Last hour")
        self.time_period.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Region and Language
        ttk.Label(main_frame, text="Region/Language:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.region_language = ttk.Combobox(main_frame, values=[
            "United States (English)",
            "United Kingdom (English)", 
            "Canada (English)",
            "Australia (English)",
            "Germany (German)",
            "France (French)",
            "Spain (Spanish)",
            "Italy (Italian)",
            "Japan (Japanese)",
            "India (English)"
        ], state="readonly")
        self.region_language.set("United States (English)")
        self.region_language.grid(row=5, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Additional Options", padding="5")
        options_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        self.decode_urls = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Decode Google News URLs", variable=self.decode_urls).pack(anchor=tk.W)
        
        self.extract_descriptions = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Extract Article Descriptions", variable=self.extract_descriptions).pack(anchor=tk.W)
        
        self.use_proxy = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Use Apify Proxy", variable=self.use_proxy).pack(anchor=tk.W)
        
        # Run button
        self.run_button = ttk.Button(main_frame, text="🚀 Run Scraper", command=self.run_scraper)
        self.run_button.grid(row=7, column=0, columnspan=3, pady=20)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready to scrape... (Pay per result model)")
        self.status_label.grid(row=8, column=0, columnspan=3, pady=5)
        
        # Results area
        ttk.Label(main_frame, text="Results:").grid(row=9, column=0, sticky=tk.W, pady=(20,5))
        self.results_text = scrolledtext.ScrolledText(main_frame, width=100, height=20)
        self.results_text.grid(row=10, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(10, weight=1)
        
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
            "Last month": "m",
            "Last year": "y"
        }
        return mapping.get(period, "h")
    
    def get_region_code(self, region):
        mapping = {
            "United States (English)": "US:en",
            "United Kingdom (English)": "GB:en",
            "Canada (English)": "CA:en",
            "Australia (English)": "AU:en",
            "Germany (German)": "DE:de",
            "France (French)": "FR:fr",
            "Spain (Spanish)": "ES:es",
            "Italy (Italian)": "IT:it",
            "Japan (Japanese)": "JP:ja",
            "India (English)": "IN:en"
        }
        return mapping.get(region, "US:en")
        
    def run_scraper(self):
        # Get values from UI
        api_token = self.api_key_entry.get().strip()
        keywords = [self.keywords_listbox.get(i) for i in range(self.keywords_listbox.size())]
        max_news = int(self.max_news.get())
        time_period = self.get_time_period_value(self.time_period.get())
        region_code = self.get_region_code(self.region_language.get())
        
        if not api_token:
            messagebox.showerror("Error", "Please enter your Apify API token")
            return
            
        if not keywords:
            messagebox.showerror("Error", "Please add at least one search keyword")
            return
        
        # Disable button and show status
        self.run_button.config(state="disabled")
        self.status_label.config(text="Running scraper... Please wait...")
        self.results_text.delete(1.0, tk.END)
        
        # Run in separate thread to avoid freezing UI
        thread = threading.Thread(target=self.scrape_news, args=(api_token, keywords, max_news, time_period, region_code))
        thread.daemon = True
        thread.start()
    
    def scrape_news(self, api_token, keywords, max_news, time_period, region_code):
        try:
            # Import apify_client
            from apify_client import ApifyClient
            
            # Initialize the ApifyClient
            client = ApifyClient(api_token)
            
            # Prepare the Actor input based on the screenshot parameters
            run_input = {
                "keywords": keywords,
                "maxNews": max_news,
                "timePeriod": time_period,
                "regionAndLanguage": region_code,
                "decodeGoogleNewsUrls": self.decode_urls.get(),
                "extractArticleDescriptions": self.extract_descriptions.get()
            }
            
            # Add proxy configuration if enabled
            if self.use_proxy.get():
                run_input["proxyConfiguration"] = {"useApifyProxy": True}
            
            self.update_status("Calling Apify API...")
            
            # Run the Actor and wait for it to finish
            run = client.actor("data_xplorer/google-news-scraper-fast").call(run_input=run_input)
            
            self.update_status("Fetching results...")
            
            # Fetch results
            results = []
            for item in client.dataset(run["defaultDatasetId"]).iterate_items():
                results.append(item)
            
            # Display results in UI
            self.display_results(results, run["defaultDatasetId"])
            
        except Exception as e:
            self.update_status(f"Error: {str(e)}")
            self.show_error(f"An error occurred: {str(e)}")
        finally:
            # Re-enable button
            self.root.after(0, lambda: self.run_button.config(state="normal"))
    
    def update_status(self, message):
        self.root.after(0, lambda: self.status_label.config(text=message))
    
    def show_error(self, message):
        self.root.after(0, lambda: messagebox.showerror("Error", message))
    
    def display_results(self, results, dataset_id):
        def update_ui():
            self.results_text.delete(1.0, tk.END)
            
            # Add dataset link
            self.results_text.insert(tk.END, f"💾 Dataset URL: https://console.apify.com/storage/datasets/{dataset_id}\n\n")
            
            if results:
                self.results_text.insert(tk.END, f"Found {len(results)} articles:\n")
                self.results_text.insert(tk.END, "=" * 80 + "\n\n")
                
                for i, article in enumerate(results, 1):
                    self.results_text.insert(tk.END, f"📰 Article {i}\n")
                    self.results_text.insert(tk.END, f"Title: {article.get('title', 'N/A')}\n")
                    self.results_text.insert(tk.END, f"Source: {article.get('source', 'N/A')}\n")
                    self.results_text.insert(tk.END, f"Published: {article.get('publishedAt', 'N/A')}\n")
                    self.results_text.insert(tk.END, f"URL: {article.get('url', 'N/A')}\n")
                    
                    if article.get('snippet'):
                        self.results_text.insert(tk.END, f"Snippet: {article.get('snippet')}\n")
                    
                    if article.get('description'):
                        self.results_text.insert(tk.END, f"Description: {article.get('description')}\n")
                        
                    if article.get('imageUrl'):
                        self.results_text.insert(tk.END, f"Image: {article.get('imageUrl')}\n")
                    
                    self.results_text.insert(tk.END, "-" * 80 + "\n\n")
                
                self.status_label.config(text=f"✅ Successfully scraped {len(results)} articles! (Pay per result)")
            else:
                self.results_text.insert(tk.END, "No results found.")
                self.status_label.config(text="No results found.")
        
        self.root.after(0, update_ui)

# Create and run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = GoogleNewsScraperUI(root)
    
    # Add instructions
    instructions = """
🚀 GOOGLE NEWS SCRAPER (PAY PER RESULT) 🚀

INSTRUCTIONS:
1. Install: pip install apify-client
2. Enter your Apify API token
3. Add search keywords (e.g., "bitcoin", "AI", "climate change")
4. Set maximum news articles to fetch
5. Choose time period (last hour, day, week, etc.)
6. Select region/language
7. Toggle additional options if needed
8. Click 'Run Scraper'

💰 PRICING: This uses a pay-per-result model ($4.00 per 1,000 results)
Much better than the $10/month subscription model!

Your $5 credits should get you ~1,250 results to test with.
"""
    
    print(instructions)
    root.mainloop()