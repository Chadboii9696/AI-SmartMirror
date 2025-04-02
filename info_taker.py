import customtkinter as ctk
import json
import os
from tkinter import messagebox

class InfoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("User Information")
        self.root.geometry("1920x1080")
        
        # Set appearance mode and default color theme
        ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
        ctk.set_default_color_theme("blue")
        
        # Create a scrollable frame
        self.scrollable_frame = ctk.CTkScrollableFrame(self.root)
        self.scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10) # Fill the window
        
        # Create main frame inside scrollable frame
        self.main_frame = ctk.CTkFrame(self.scrollable_frame)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)   # Fill the scrollable frame
        
        # Title label
        self.title_label = ctk.CTkLabel(
            self.main_frame, 
            text="User Information Form", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.pack(pady=10) # Add padding on the y-axis
        
        # Create form fields
        self.create_form_fields()
        
        # Create news preference section
        self.create_news_section()
        
        # Create stock market interest section
        self.create_stock_section()
        
        # Create to-do list section
        self.create_todo_section()
        
        # Create buttons
        self.create_buttons()
    
    def toggle_fullscreen(self, event=None):
        """Toggle between fullscreen and windowed mode"""
        is_fullscreen = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not is_fullscreen)
        return "break"  # Prevents the event from propagating
        
    def create_form_fields(self):
        # Name field
        self.name_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent") # Frame for the name field
        self.name_frame.pack(fill="x", pady=5)
        
        self.name_label = ctk.CTkLabel(self.name_frame, text="Name:", width=100) # Label for the name field
        self.name_label.pack(side="left", padx=5) 
        
        self.name_entry = ctk.CTkEntry(self.name_frame, width=300)
        self.name_entry.pack(side="left", padx=5)
        
        # Age field
        self.age_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.age_frame.pack(fill="x", pady=5)
        
        self.age_label = ctk.CTkLabel(self.age_frame, text="Age:", width=100)
        self.age_label.pack(side="left", padx=5)
        
        self.age_entry = ctk.CTkEntry(self.age_frame, width=300)
        self.age_entry.pack(side="left", padx=5)
        
        # Gender field
        self.gender_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.gender_frame.pack(fill="x", pady=5)
        
        self.gender_label = ctk.CTkLabel(self.gender_frame, text="Gender:", width=100)
        self.gender_label.pack(side="left", padx=5)
        
        self.gender_var = ctk.StringVar(value="Male")
        self.gender_combobox = ctk.CTkComboBox( # For options like dropdowns
            self.gender_frame, 
            values=["Male", "Female", "Other"],
            variable=self.gender_var,
            width=300
        )
        self.gender_combobox.pack(side="left", padx=5)
    
    def create_news_section(self):
        # News preferences section
        self.news_label = ctk.CTkLabel(
            self.main_frame, 
            text="News Preferences", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.news_label.pack(pady=(15, 5))
        
        # News interest checkbox
        self.news_interest_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent") 
        self.news_interest_frame.pack(fill="x", pady=5)
        
        self.news_interest_var = ctk.BooleanVar(value=False) # Creates a boolean variable initially set to False
        self.news_interest_checkbox = ctk.CTkCheckBox(
            self.news_interest_frame, 
            text="Interested in news updates?",
            variable=self.news_interest_var, # Binds the checkbox state to self.news_interest_var. When the checkbox is checked or unchecked
            command=self.toggle_news_options # Calls toggle_news_options when the checkbox is clicked
        )
        self.news_interest_checkbox.pack(pady=5)
        
        # News categories frame
        self.news_categories_frame = ctk.CTkFrame(self.main_frame)
        self.news_categories_frame.pack(fill="x", pady=5)
        
        # News category checkboxes
        self.news_categories = ["Sports", "Politics", "Business", "Science"]
        self.news_category_vars = {category: ctk.BooleanVar(value=False) for category in self.news_categories}
        self.news_checkboxes = {} # A dictionary where each key is a category and each value is a BooleanVar initialized to False. This variable will store the state (checked or unchecked) of each checkbox.
        
        for i, category in enumerate(self.news_categories):
            self.news_checkboxes[category] = ctk.CTkCheckBox(
                self.news_categories_frame,
                text=category,
                variable=self.news_category_vars[category] #Binds the checkbox state to the corresponding BooleanVar
            )
            self.news_checkboxes[category].grid(row=i//2, column=i%2, padx=20, pady=5, sticky="w")
            '''
            Determines the row number (two checkboxes per row).
            column=i%2: Determines the column number (0 or 1).
            padx=20, pady=5: Adds padding around the checkbox.
            sticky="w": Aligns the checkbox to the west (left) side of the cell.
            '''
        
        # Initially disable news categories
        self.toggle_news_options()
        '''
        Calls the toggle_news_options method to initially disable the news category 
        checkboxes. This method will enable or disable the checkboxes based on the 
        state of the news_interest_var
        '''
    
    def create_stock_section(self):
        # Stock market interest section
        self.stock_label = ctk.CTkLabel(
            self.main_frame, 
            text="Stock Market Interest", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.stock_label.pack(pady=(15, 5))
        
        # Stock market interest checkbox
        self.stock_interest_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.stock_interest_frame.pack(fill="x", pady=5)
        
        self.stock_interest_var = ctk.BooleanVar(value=False)
        self.stock_interest_checkbox = ctk.CTkCheckBox(
            self.stock_interest_frame, 
            text="Interested in stock market?",
            variable=self.stock_interest_var, # Binds the checkbox state to self.stock_interest_var
            command=self.toggle_stock_options # Calls toggle_stock_options when the checkbox is clicked
        )
        self.stock_interest_checkbox.pack(pady=5)
        
        # Stock ticker symbols frame
        self.stock_tickers_frame = ctk.CTkFrame(self.main_frame)
        self.stock_tickers_frame.pack(fill="x", pady=5)
        
        # Create ticker symbol input fields
        self.ticker_entries = []
        '''
        Initializes an empty list to store the ticker entry fields. 
        This list will be used later to access the values entered 
        by the user.
        '''
        for i in range(3): # iterates to create 3 ticker entry fields
            ticker_frame = ctk.CTkFrame(self.stock_tickers_frame, fg_color="transparent")
            ticker_frame.pack(fill="x", pady=5)
            
            ticker_label = ctk.CTkLabel(ticker_frame, text=f"Ticker #{i+1}:", width=100)
            ticker_label.pack(side="left", padx=5)
            
            ticker_entry = ctk.CTkEntry(ticker_frame, width=300, placeholder_text="e.g., AAPL, MSFT, GOOGL")
            ticker_entry.pack(side="left", padx=5)
            self.ticker_entries.append(ticker_entry) # Store the entry field in the list
        
        # Initially disable ticker entry fields
        self.toggle_stock_options()
    
    def toggle_news_options(self):
        state = "normal" if self.news_interest_var.get() else "disabled"
        '''
        Sets the state variable to "normal" if news_interest_var is True 
        (checked), otherwise sets it to "disabled".
        '''
        for checkbox in self.news_checkboxes.values():
            if state == "disabled":
                checkbox.deselect()
            checkbox.configure(state=state)
            '''
            Sets the state of the checkbox to either "normal" or 
            "disabled" based on the value of the state variable.
            '''
    
    def toggle_stock_options(self):
        state = "normal" if self.stock_interest_var.get() else "disabled"
        '''
        Sets the state variable to "normal" if stock_interest_var is True 
        (checked), otherwise sets it to "disabled".
        '''
        for ticker_entry in self.ticker_entries:
            if state == "disabled":
                ticker_entry.delete(0, 'end')
            ticker_entry.configure(state=state)
            '''
            Sets the state of the ticker entry field to either "normal" or
            "disabled" based on the value of the state variable.
            '''
    
    def create_todo_section(self):
        # To-Do List section
        self.todo_label = ctk.CTkLabel(
            self.main_frame, 
            text="To-Do List", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.todo_label.pack(pady=(15, 5))
        
        # To-Do input field
        self.todo_input_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.todo_input_frame.pack(fill="x", pady=5)
        
        self.todo_entry = ctk.CTkEntry(self.todo_input_frame, width=300)
        self.todo_entry.pack(side="left", padx=5)
        
        self.todo_add_button = ctk.CTkButton(
            self.todo_input_frame, 
            text="Add Task", 
            command=self.add_todo_item
        )
        self.todo_add_button.pack(side="left", padx=5)
        
        # To-Do list display
        self.todo_frame = ctk.CTkFrame(self.main_frame)
        self.todo_frame.pack(fill="both", expand=True, pady=10)
        
        self.todo_list = ctk.CTkTextbox(self.todo_frame, width=400, height=120)
        self.todo_list.pack(padx=10, pady=10, fill="both", expand=True)
        
        # Initialize empty task list
        self.tasks = []
    
    def create_buttons(self):
        self.button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.button_frame.pack(fill="x", pady=15)
        
        self.save_button = ctk.CTkButton(
            self.button_frame, 
            text="Save Information", 
            command=self.save_info
        )
        self.save_button.pack(side="left", padx=5, expand=True)
        
        self.clear_button = ctk.CTkButton(
            self.button_frame, 
            text="Clear Form", 
            command=self.clear_form
        )
        self.clear_button.pack(side="left", padx=5, expand=True)
    
    def add_todo_item(self):
        task = self.todo_entry.get()
        if task.strip(): # Removes any leading and trailing whitespace from the task string. If the task is not empty after removing whitespace, it is added to the list.
            self.tasks.append(task)
            '''
            Adds the task to the tasks list, self.tasks = [],
            which stores all the to-do items.
            '''
            self.update_todo_list()
            '''
            Calls the update_todo_list method to refresh the 
            display of the to-do list with the updated tasks.
            '''
            self.todo_entry.delete(0, 'end')
            '''
            Clears the text in the todo_entry field, 
            making it ready for the next input.
            '''
        else:
            messagebox.showwarning("Empty Task", "Please enter a task.")
    
    def update_todo_list(self):
        self.todo_list.delete("0.0", "end")
        '''
        Deletes all the text in the todo_list text box. The "0.0" index 
        refers to the very beginning of the text box, and "end" refers 
        to the end of the text box. This effectively clears the entire 
        content of the text box.
        '''
        for i, task in enumerate(self.tasks, 1):
            '''
            Iterates over the tasks list, with i as the index (starting from 1) 
            and task as the task string. The enumerate function is used to get 
            both the index and the task, and the 1 argument makes the index 
            start from 1 instead of 0
            '''
            self.todo_list.insert("end", f"{i}. {task}\n") # (e.g., "1. Task 1\n", "2. Task 2\n")
    
    def save_info(self):
        # Check if name and age are filled in
        if not self.name_entry.get().strip():
            messagebox.showerror("Error", "Name is required")
            return
            
        try:
            age = int(self.age_entry.get())
            if age <= 0:
                raise ValueError("Age must be positive")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid age")
            return
        
        # Get the current name (converted to lowercase for case-insensitive comparison)
        current_name = self.name_entry.get().strip().lower()
        
        # Define the filename
        filename = "people.json"
        
        # Check if file exists and load existing data
        people_data = [] #  Initializes an empty list to store the user data.
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    '''
                    opens the file in read mode ('r') 
                    and assigns the file object to the 
                    variable f
                    '''
                    people_data = json.load(f)
                    if not isinstance(people_data, list):
                        people_data = []
                    '''
                    Checks if the loaded data is not a list.
                    people_data = []: If the loaded data is 
                    not a list, reinitializes people_data as 
                    an empty list to avoid errors.
                    '''
                    
                    # Check if name already exists (case-insensitive)
                    for person in people_data:
                        if person.get("name", "").strip().lower() == current_name:
                            messagebox.showerror(
                                "Duplicate Name", 
                                f"A user with the name '{self.name_entry.get()}' already exists.\n"
                                "Please use a different name."
                            )
                            return  # Exit the function without saving
            except (json.JSONDecodeError, FileNotFoundError):
                '''
                checks if the file contains invalid JSON or FileNotFoundError
                people_data = []: If an error occurs while reading the file,
                reinitializes people_data as an empty list to avoid errors.
                '''
                people_data = []
        
        # Get selected news categories
        selected_news_categories = []
        if self.news_interest_var.get():
            for category, var in self.news_category_vars.items():
                if var.get():
                    selected_news_categories.append(category)
        
        # Get stock ticker symbols
        stock_tickers = []
        if self.stock_interest_var.get():
            for ticker_entry in self.ticker_entries:
                ticker = ticker_entry.get().strip()
                if ticker:
                    stock_tickers.append(ticker.upper())  # Convert to uppercase
        
        # Get all the information
        user_info = {
            "name": self.name_entry.get(),
            "age": self.age_entry.get(),
            "gender": self.gender_var.get(),
            "news_interest": self.news_interest_var.get(),
            "news_categories": selected_news_categories,
            "stock_interest": self.stock_interest_var.get(),
            "stock_tickers": stock_tickers,
            "todo_list": self.tasks
        }
        
        # Add the new user info (we already checked for duplicates)
        people_data.append(user_info)
        
        # Save the updated information to people.json
        with open(filename, 'w') as f: # with statement ensures that the file is properly closed after its suite finishes, even if an exception is raised.
            json.dump(people_data, f, indent=4)
            '''
            his argument specifies the indentation level 
            for the JSON data, making it more readable by 
            adding four spaces of indentation for each 
            nested level.
            '''
        
        # Print a message confirming the save
        print(f"Information saved to {filename}")
        
        # Run face_data.py
        import subprocess
        import sys
        
        try:
            # Using the same Python interpreter that's running this script
            subprocess.Popen([sys.executable, "face_data.py"])
            print("Started face_data.py")
        except Exception as e:
            print(f"Error running face_data.py: {e}")
        
        # Close the GUI and exit the application
        self.root.quit()
        self.root.destroy()
    
    def clear_form(self):
        self.name_entry.delete(0, 'end')
        self.age_entry.delete(0, 'end')
        self.gender_var.set("Male")
        self.news_interest_var.set(False)
        for category_var in self.news_category_vars.values():
            category_var.set(False)
        self.toggle_news_options()  # Update the UI state
        self.stock_interest_var.set(False)
        self.toggle_stock_options()  # Update stock fields UI state
        self.tasks = []
        self.update_todo_list()

if __name__ == "__main__":
    root = ctk.CTk()
    app = InfoApp(root)
    root.mainloop()