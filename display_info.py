import json
import customtkinter as ctk
from tkinter import messagebox
import threading
import requests
from datetime import datetime
import yfinance as tf  # Add this import for stock data
import current_user  # Import the current_user module
import time

# Set appearance mode and default color theme
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")

# Sample news headlines by category (as a fallback if API fails)
# In a real app, these would come from a news API
SAMPLE_NEWS = {
    "Sports": [
        "Lakers win championship in dramatic overtime game",
        "Olympic committee announces new sports for 2028",
        "Record-breaking run at track and field championship"
    ],
    "Politics": [
        "New legislation passed addressing climate change",
        "International summit concludes with new trade agreements",
        "Presidential approval ratings show significant shift"
    ],
    "Business": [
        "Tech giant announces breakthrough AI model",
        "Stock market reaches all-time high",
        "Major merger creates new industry leader"
    ],
    "Science": [
        "Researchers discover potential cure for common disease",
        "Space telescope captures images of distant galaxy",
        "Breakthrough in renewable energy storage announced"
    ]
}

# Sample stock data (as a fallback if API fails)
SAMPLE_STOCKS = {
    "AAPL": {"price": "185.92", "change": "+1.25", "percent": "+0.68%"},
    "MSFT": {"price": "417.56", "change": "-2.34", "percent": "-0.56%"},
    "GOOGL": {"price": "147.78", "change": "+0.89", "percent": "+0.61%"},
    "AMZN": {"price": "178.45", "change": "+3.21", "percent": "+1.83%"},
    "TSLA": {"price": "175.34", "change": "-5.67", "percent": "-3.13%"},
    "META": {"price": "475.89", "change": "+8.45", "percent": "+1.81%"}
}

# Function to fetch news headlines from News API
def fetch_news_headlines(categories):
    headlines = {}
    API_KEY = "e5ead44f35a544138f2fb5a2993bca15"

    def fetch_news_for_category(category):
        try:
            query = category.lower()
            url = f"https://newsapi.org/v2/top-headlines?country=us&category={query}&apiKey={API_KEY}"
            response = requests.get(url, timeout=5)  # Set a timeout for the request

            if response.status_code == 200:
                news_data = response.json()
                articles = news_data.get('articles', [])
                return [article['title'] for article in articles[:3]]  # Get top 3 headlines
            else:
                print(f"API request failed for {category} with status code {response.status_code}")
        except Exception as e:
            print(f"Error fetching {category} news: {e}")
        return SAMPLE_NEWS.get(category, ["No headlines available"])  # Fallback to sample data

    # Use threading to enforce a 10-second timeout for all categories
    threads = []
    results = {}

    def fetch_and_store(category):
        results[category] = fetch_news_for_category(category)

    for category in categories:
        thread = threading.Thread(target=fetch_and_store, args=(category,))
        threads.append(thread)
        thread.start()

    # Wait for threads to complete or timeout after 10 seconds
    start_time = time.time()
    for thread in threads:
        thread.join(timeout=10 - (time.time() - start_time))

    # Ensure all categories have data, fallback to sample if not
    for category in categories:
        if category not in results:
            results[category] = SAMPLE_NEWS.get(category, ["No headlines available"])

    return results

# Function to fetch stock data using yfinance
def fetch_stock_data(tickers):
    stock_data = {}
    
    for ticker in tickers:
        try:
            # Try to get real-time data from Yahoo Finance
            stock = tf.Ticker(ticker)
            info = stock.info
            
            # Get the current price
            current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
            if current_price is None:
                current_price = 0
                
            # Get the previous close price to calculate change
            prev_close = info.get('previousClose', current_price)
            if prev_close is None or prev_close == 0:
                prev_close = current_price
                
            # Calculate change and percent change
            change = current_price - prev_close
            percent_change = (change / prev_close) * 100 if prev_close != 0 else 0
            
            # Format the data
            stock_data[ticker] = {
                "price": f"{current_price:.2f}",
                "change": f"{change:.2f}",
                "percent": f"{percent_change:.2f}%",
                "name": info.get('shortName', ticker),
                "currency": info.get('currency', 'USD')
            }
            
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            # Fallback to sample data
            if ticker in SAMPLE_STOCKS:
                stock_data[ticker] = SAMPLE_STOCKS[ticker]
            else:
                stock_data[ticker] = {
                    "price": "N/A", 
                    "change": "0.00", 
                    "percent": "0.00%",
                    "name": ticker,
                    "currency": "USD"
                }
    
    return stock_data

# Function to find a person by name in the people.json data
def find_person_by_name(people_data, name):
    for person in people_data:
        if person["name"].lower() == name.lower():
            return person
    return None

# Function to load user data based on the current recognized user
def load_user_data():
    try:
        # Get the current recognized user
        current_name = current_user.get_current_user()
        
        # Load all people data
        with open('people.json', 'r') as file:
            people_data = json.load(file)
        
        # Find the person that matches the current user
        person = find_person_by_name(people_data, current_name)
        
        # If no match found, use the first person as default
        if not person and people_data:
            person = people_data[0]
            print(f"No match found for '{current_name}', using first person as default")
        
        if not person:
            raise ValueError("No user data found")
        
        return person
    except (FileNotFoundError, json.JSONDecodeError, IndexError) as e:
        print(f"Error loading user data: {e}")
        return None

class DashboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Dashboard")
        self.root.geometry("1920x1080")
        
        # Initialize main frames
        self.init_main_frames()
        
        # Load initial user data
        self.current_user = None
        self.load_and_display_user()
        
        # Start monitoring for user changes
        self.start_user_monitor()
    
    def init_main_frames(self):
        # Create a scrollable frame
        self.main_scrollable_frame = ctk.CTkScrollableFrame(self.root)
        self.main_scrollable_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create a main container with grid layout
        self.main_container = ctk.CTkFrame(self.main_scrollable_frame, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(1, weight=1)
        
        # Create header frame for welcome message
        self.welcome_frame = ctk.CTkFrame(self.main_container, fg_color="#3a7ebf", corner_radius=0)
        self.welcome_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        
        # Create subheader frame for gender/age
        self.gender_age_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.gender_age_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 30))
        
        # Create left container for news
        self.left_container = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.left_container.grid(row=2, column=0, sticky="nw", padx=40, pady=10)
        
        # Create right container for to-do list and stocks
        self.right_container = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.right_container.grid(row=2, column=1, sticky="ne", padx=40, pady=10)
        
        # Add refresh button
        self.refresh_button = ctk.CTkButton(
            self.welcome_frame, 
            text="↻ Refresh Data",
            command=self.refresh_dashboard,
            width=120,
            height=32,
            corner_radius=8
        )
        self.refresh_button.pack(side="right", padx=20)
    
    def refresh_dashboard(self):
        """Force refresh all dynamic content"""
        self.load_and_display_user()
    
    def clear_container(self, container):
        """Clear all widgets from a container"""
        for widget in container.winfo_children():
            widget.destroy()
    
    def load_and_display_user(self):
        """Load user data and update the UI"""
        # Load current user data
        person = load_user_data()
        
        if not person:
            # Show error message if data can't be loaded
            self.clear_container(self.welcome_frame)
            error_label = ctk.CTkLabel(
                self.welcome_frame,
                text="Error loading user data",
                font=ctk.CTkFont(family="Arial", size=32, weight="bold"),
                text_color="white",
                pady=15
            )
            error_label.pack()
            return
        
        # Store current user name
        current_name = person["name"]
        is_new_user = (self.current_user != current_name)
        
        # Always update current user
        self.current_user = current_name
        
        # Extract user data
        name = person["name"]
        age = person["age"]
        gender = person["gender"]
        todo_list = person.get("todo_list", [])
        news_interest = person.get("news_interest", False)
        news_categories = person.get("news_categories", [])
        stock_interest = person.get("stock_interest", False)
        stock_tickers = person.get("stock_tickers", [])
        
        # If new user, update welcome message and gender/age info
        if is_new_user:
            # Update welcome message
            self.clear_container(self.welcome_frame)
            welcome_label = ctk.CTkLabel(
                self.welcome_frame,
                text=f"Welcome, {name}!",
                font=ctk.CTkFont(family="Arial", size=32, weight="bold"),
                text_color="white",
                pady=15
            )
            welcome_label.pack()
            
            # Update gender and age display
            self.clear_container(self.gender_age_frame)
            gender_age_text = f"{gender}, {age} years old"
            gender_age_label = ctk.CTkLabel(
                self.gender_age_frame,
                text=gender_age_text,
                font=ctk.CTkFont(size=26, weight="bold"),
                text_color="#3a7ebf",
            )
            gender_age_label.pack(anchor="center")
            
            # Clear existing content
            self.clear_container(self.left_container)
            self.clear_container(self.right_container)
            
            # Add To-Do List
            self.display_todo_list(todo_list)
        
        # Always update dynamic content regardless of user change
        # Add Stock Market Section
        if stock_interest and stock_tickers:
            # Clear right container only below the todo list
            for widget in self.right_container.winfo_children():
                if widget.winfo_y() > 300:  # Approximate position after todo list
                    widget.destroy()
            self.display_stocks(stock_tickers)
        
        # Add News Section
        if news_interest and news_categories:
            self.clear_container(self.left_container)
            self.display_news(news_categories)
        elif not news_interest:
            self.clear_container(self.left_container)
            self.display_no_news_message()
    
    def display_todo_list(self, todo_list):
        """Display the to-do list"""
        # Title for the sticky note
        todo_title = ctk.CTkLabel(
            self.right_container,
            text="My To-Do List",
            font=ctk.CTkFont(family="Comic Sans MS", size=24, weight="bold"),
            text_color="#3a7ebf",
        )
        todo_title.pack(anchor="center", pady=(0, 20))
        
        if todo_list:
            # Create the sticky note with yellow background
            sticky_note = ctk.CTkFrame(
                self.right_container, 
                fg_color="#fff9b1",  # Yellow sticky note color
                corner_radius=2,
                border_width=1,
                border_color="#e0e0e0",  # Light border
                width=500,  # Fixed width for square shape
                height=250  # Height
            )
            sticky_note.pack(pady=20)
            
            # Add padding inside the note
            note_padding = ctk.CTkFrame(sticky_note, fg_color="#fff9b1")
            note_padding.pack(fill="both", expand=True, padx=30, pady=20)
            
            # Title inside note
            note_header = ctk.CTkLabel(
                note_padding,
                text="Tasks:",
                font=ctk.CTkFont(family="Comic Sans MS", size=18, weight="bold"),
                text_color="#333333",
                fg_color="#fff9b1",
            )
            note_header.pack(anchor="w", pady=(0, 5))
            
            # Add a separator that looks like a pencil line
            separator = ctk.CTkFrame(note_padding, height=2, fg_color="#cccccc")
            separator.pack(fill="x", pady=5)
            
            # Create a scrollable frame for tasks
            tasks_scrollable = ctk.CTkScrollableFrame(note_padding, fg_color="#fff9b1", 
                                                     height=150, width=400)
            tasks_scrollable.pack(fill="both", expand=True)
            
            # List each task with bullet points
            for i, item in enumerate(todo_list):
                task_frame = ctk.CTkFrame(tasks_scrollable, fg_color="#fff9b1")
                task_frame.pack(fill="x", pady=3)
                
                bullet = ctk.CTkLabel(
                    task_frame,
                    text="•",
                    font=ctk.CTkFont(family="Comic Sans MS", size=16),
                    text_color="#333333",
                    fg_color="#fff9b1",
                    width=20
                )
                bullet.pack(side="left")
                
                todo_item = ctk.CTkLabel(
                    task_frame,
                    text=f"{item}",
                    font=ctk.CTkFont(family="Comic Sans MS", size=16, slant="italic"),
                    text_color="#333333",
                    fg_color="#fff9b1",
                    anchor="w"
                )
                todo_item.pack(side="left", fill="x", expand=True)
        else:
            # If no tasks, show an empty sticky note
            empty_note = ctk.CTkFrame(
                self.right_container, 
                fg_color="#fff9b1", 
                corner_radius=2,
                width=500,  # Fixed width for square shape
                height=250   # Height
            )
            empty_note.pack(pady=20)
            empty_note.pack_propagate(False)  # Prevent children from changing size
            
            empty_message = ctk.CTkLabel(
                empty_note,
                text="No tasks yet. Enjoy your free time!",
                font=ctk.CTkFont(family="Comic Sans MS", size=18, slant="italic"),
                text_color="#333333",
                fg_color="#fff9b1",
            )
            empty_message.pack(expand=True)
    
    def display_stocks(self, stock_tickers):
        """Display the stock information"""
        # Stock section header
        stock_title = ctk.CTkLabel(
            self.right_container,
            text="Stock Portfolio",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#3a7ebf",
        )
        stock_title.pack(anchor="center", pady=(40, 20))
        
        # Loading indicator for stocks
        stock_loading_frame = ctk.CTkFrame(self.right_container)
        stock_loading_frame.pack(fill="x", pady=10)
        
        stock_loading_label = ctk.CTkLabel(
            stock_loading_frame,
            text="Loading stock data...",
            font=ctk.CTkFont(size=14),
        )
        stock_loading_label.pack(pady=10)
        
        # Function to update UI with stock data
        def update_stock_ui(stock_data):
            # Remove loading indicator
            stock_loading_frame.destroy()
            
            # Create main stock display frame
            stock_display = ctk.CTkFrame(self.right_container, fg_color="#e6ffe6", corner_radius=8)
            stock_display.pack(fill="x", pady=10)
            
            # Add column headers
            header_frame = ctk.CTkFrame(stock_display, fg_color="#006600")
            header_frame.pack(fill="x", padx=10, pady=(10, 0))
            
            # Create header grid
            header_frame.grid_columnconfigure(0, weight=2)
            header_frame.grid_columnconfigure(1, weight=1)
            header_frame.grid_columnconfigure(2, weight=1)
            
            # Header labels
            symbol_header = ctk.CTkLabel(
                header_frame,
                text="Symbol",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="white",
            )
            symbol_header.grid(row=0, column=0, padx=5, pady=5, sticky="w")
            
            price_header = ctk.CTkLabel(
                header_frame,
                text="Price",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="white",
            )
            price_header.grid(row=0, column=1, padx=5, pady=5, sticky="w")
            
            change_header = ctk.CTkLabel(
                header_frame,
                text="Change",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="white",
            )
            change_header.grid(row=0, column=2, padx=5, pady=5, sticky="w")
            
            # Create a container for stock rows
            stocks_container = ctk.CTkFrame(stock_display, fg_color="#e6ffe6")
            stocks_container.pack(fill="x", padx=10, pady=10)
            
            # Set up column configuration
            stocks_container.grid_columnconfigure(0, weight=2)
            stocks_container.grid_columnconfigure(1, weight=1)
            stocks_container.grid_columnconfigure(2, weight=1)
            
            # Add each stock
            for i, ticker in enumerate(stock_tickers):
                if ticker in stock_data:
                    data = stock_data[ticker]
                    
                    # Alternate row colors
                    row_color = "#d1e8d1" if i % 2 == 0 else "#e6ffe6"
                    
                    # Symbol and name
                    symbol_label = ctk.CTkLabel(
                        stocks_container,
                        text=f"{ticker}\n{data.get('name', '')}",
                        font=ctk.CTkFont(size=14, weight="bold"),
                        text_color="#003300",
                        fg_color=row_color,
                    )
                    symbol_label.grid(row=i, column=0, padx=5, pady=8, sticky="w")
                    
                    # Price
                    price_label = ctk.CTkLabel(
                        stocks_container,
                        text=f"{data['price']} {data.get('currency', 'USD')}",
                        font=ctk.CTkFont(size=14),
                        text_color="#003300",
                        fg_color=row_color,
                    )
                    price_label.grid(row=i, column=1, padx=5, pady=8, sticky="w")
                    
                    # Change amount and percentage
                    change = float(data['change'].replace('+', '').replace('-', ''))
                    is_positive = '-' not in data['change']
                    
                    change_color = "#007700" if is_positive else "#CC0000"
                    change_prefix = "+" if is_positive else "-"
                    
                    if data['change'] == "0.00":
                        change_prefix = ""
                        change_color = "#666666"
                    
                    change_label = ctk.CTkLabel(
                        stocks_container,
                        text=f"{change_prefix}${change:.2f} ({data['percent']})",
                        font=ctk.CTkFont(size=14, weight="bold"),
                        text_color=change_color,
                        fg_color=row_color,
                    )
                    change_label.grid(row=i, column=2, padx=5, pady=8, sticky="w")
            
            # Add last updated time
            now = datetime.now().strftime("%H:%M:%S")
            stocks_updated = ctk.CTkLabel(
                stock_display,
                text=f"Updated at {now}",
                font=ctk.CTkFont(size=10, slant="italic"),
                text_color="gray",
                fg_color="#e6ffe6",
            )
            stocks_updated.pack(anchor="e", padx=10, pady=(0, 10))
        
        # Fetch stock data in separate thread
        def fetch_stocks_thread():
            stock_data = fetch_stock_data(stock_tickers)
            self.root.after(0, lambda: update_stock_ui(stock_data))
        
        threading.Thread(target=fetch_stocks_thread, daemon=True).start()
    
    def display_news(self, news_categories):
        """Display news headlines"""
        # News section header
        news_header = ctk.CTkLabel(
            self.left_container,
            text="Your News Headlines",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#3a7ebf",
        )
        news_header.pack(anchor="w", pady=(0, 15))
        
        # Loading indicator
        loading_frame = ctk.CTkFrame(self.left_container)
        loading_frame.pack(fill="x", pady=10)
        
        loading_label = ctk.CTkLabel(
            loading_frame,
            text="Loading news headlines...",
            font=ctk.CTkFont(size=14),
        )
        loading_label.pack(pady=10)
        
        # Dictionary to store news frames for each category
        news_frames = {}
        
        # Function to update UI with news headlines
        def update_news_ui(headlines):
            # Remove loading indicator
            loading_frame.destroy()
            
            # Display headlines for each category
            for category, category_headlines in headlines.items():
                # Create a frame for this category
                category_frame = ctk.CTkFrame(self.left_container)
                category_frame.pack(fill="x", pady=10, anchor="w")
                
                # Category title
                category_title = ctk.CTkLabel(
                    category_frame,
                    text=f"{category} News",
                    font=ctk.CTkFont(size=18, weight="bold"),
                    text_color="white",
                    fg_color="#3a7ebf",
                    corner_radius=8,
                )
                category_title.pack(fill="x", pady=(0, 10), padx=10)
                
                # Headlines for this category - improved colors for better visibility
                headlines_frame = ctk.CTkFrame(category_frame, fg_color="#e1effe")
                headlines_frame.pack(fill="x", padx=10)
                
                for i, headline in enumerate(category_headlines[:3]):  # Limit to top 3
                    # Different color backgrounds for alternating headlines
                    bg_color = "#d1e5ff" if i % 2 == 0 else "#e1effe"
                    
                    headline_frame = ctk.CTkFrame(headlines_frame, fg_color=bg_color)
                    headline_frame.pack(fill="x", padx=5, pady=3)
                    
                    headline_label = ctk.CTkLabel(
                        headline_frame,
                        text=f"{i+1}. {headline}",
                        font=ctk.CTkFont(size=14, weight="bold"),
                        text_color="#00366e",
                        fg_color=bg_color,
                        anchor="w",
                        justify="left",
                        wraplength=600  # Allow wrapping for long headlines
                    )
                    headline_label.pack(anchor="w", pady=5, padx=10, fill="x")
                
                # Add a "last updated" timestamp
                now = datetime.now().strftime("%H:%M:%S")
                updated_label = ctk.CTkLabel(
                    category_frame,
                    text=f"Updated at {now}",
                    font=ctk.CTkFont(size=10, slant="italic"),
                    text_color="gray",
                )
                updated_label.pack(anchor="e", padx=10, pady=(5, 10))
                
                # Save reference to prevent garbage collection
                news_frames[category] = category_frame
        
        # Fetch news in separate thread to keep UI responsive
        def fetch_news_thread():
            headlines = fetch_news_headlines(news_categories)
            self.root.after(0, lambda: update_news_ui(headlines))
        
        threading.Thread(target=fetch_news_thread, daemon=True).start()
    
    def display_no_news_message(self):
        """Display message when news is disabled"""
        no_news_frame = ctk.CTkFrame(self.left_container, fg_color="#f0f0f0", corner_radius=10)
        no_news_frame.pack(pady=20)
        
        no_news_label = ctk.CTkLabel(
            no_news_frame,
            text="News updates disabled.\nEnable them in your profile settings.",
            font=ctk.CTkFont(size=16),
            pady=20,
            padx=20
        )
        no_news_label.pack()
    
    def start_user_monitor(self):
        """Start the monitoring thread to detect user changes"""
        def monitor_thread():
            last_user = None
            last_refresh = time.time()
            refresh_interval = 30  # Refresh every 30 seconds
            
            while True:
                current = current_user.get_current_user()
                current_time = time.time()
                
                # Refresh if user changed or timer expired
                if current != last_user or (current_time - last_refresh > refresh_interval):
                    last_user = current
                    last_refresh = current_time
                    self.root.after(0, self.load_and_display_user)
                
                time.sleep(1)  # Check every second
        
        # Start monitoring thread
        threading.Thread(target=monitor_thread, daemon=True).start()

# Create and run the application
if __name__ == "__main__":
    root = ctk.CTk()
    app = DashboardApp(root)
    root.mainloop()