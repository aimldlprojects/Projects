import tkinter as tk
from tkinter import ttk
import pandas as pd
import random
from datetime import datetime, timedelta

class SpellingTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Spelling Test App")
        
        # Assuming "word_list.csv" contains columns 'word' and possibly 'last_practiced'
        self.word_list = pd.read_csv("word_list.csv")
        
        self.current_word = tk.StringVar()
        self.user_input = tk.StringVar()
        
        self.correct_count = 0
        self.wrong_count = 0
        
        self.setup_gui()
    
    def setup_gui(self):
        ttk.Label(self.root, text="Welcome to Spelling Test App", font=('Helvetica', 16)).grid(row=0, columnspan=3, pady=10)
        
        ttk.Label(self.root, text="Type the spelling of the pronounced word:").grid(row=1, columnspan=3)
        
        ttk.Label(self.root, textvariable=self.current_word, font=('Helvetica', 14)).grid(row=2, columnspan=3, pady=10)
        
        ttk.Entry(self.root, textvariable=self.user_input).grid(row=3, columnspan=3)
        
        ttk.Button(self.root, text="Check", command=self.check_spelling).grid(row=4, column=0, padx=5, pady=5)
        ttk.Button(self.root, text="Next Word", command=self.next_word).grid(row=4, column=1, padx=5, pady=5)
        
        ttk.Label(self.root, text="Stats: Correct - 0, Wrong - 0", font=('Helvetica', 12)).grid(row=5, columnspan=3, pady=10)
        
        # Dropdown for test options
        self.test_options = ttk.Combobox(self.root, values=["Length of the word", "Previous incorrectly spelled words", "Words practiced a week ago"])
        self.test_options.grid(row=6, column=0, pady=5)
        self.test_options.current(0)  # Set default option
        
        # Dropdown for length selection (1-10)
        self.length_options = ttk.Combobox(self.root, values=list(range(1, 11)))
        self.length_options.grid(row=6, column=1, pady=5)
        
        ttk.Button(self.root, text="Start Test", command=self.start_test).grid(row=7, columnspan=3, pady=5)
    
    def start_test(self):
        test_option = self.test_options.get()
        length_option = self.length_options.get()
        
        if test_option == "Length of the word" and length_option.isdigit():
            selected_length = int(length_option)
            self.words_for_test = self.word_list[self.word_list['word'].apply(len) == selected_length]
        elif test_option == "Previous incorrectly spelled words":
            # Load previous incorrect words from CSV (if any)
            try:
                self.words_for_test = pd.read_csv("previous_incorrect_words.csv")
            except FileNotFoundError:
                self.words_for_test = pd.DataFrame(columns=['word'])  # Empty DataFrame if file doesn't exist
        elif test_option == "Words practiced a week ago":
            week_ago = datetime.now() - timedelta(weeks=1)
            self.words_for_test = self.word_list[self.word_list['last_practiced'] == week_ago.strftime('%Y-%m-%d')]
        else:
            self.words_for_test = pd.DataFrame()  # Empty DataFrame for default
        
        self.words_for_test = self.words_for_test['word'].tolist()
        self.next_word()
    
    def next_word(self):
        if self.words_for_test:
            self.current_word.set(random.choice(self.words_for_test))
        else:
            self.current_word.set("No more words for the test")
    
    def check_spelling(self):
        correct_word = self.current_word.get()
        user_word = self.user_input.get()
        
        if user_word.strip().lower() == correct_word.strip().lower():
            self.correct_count += 1
            self.update_status("Correct!", "green")
        else:
            self.wrong_count += 1
            self.update_status(f"Wrong! Correct spelling is: {correct_word}", "red")
            # Save incorrect word to CSV
            pd.DataFrame({'word': [correct_word]}).to_csv("previous_incorrect_words.csv", mode='a', header=False, index=False)
        
        self.user_input.set("")
        self.next_word()
        
    def update_status(self, message, color):
        status_label = ttk.Label(self.root, text=message, foreground=color)
        status_label.grid(row=5, columnspan=3, pady=10)
        self.root.after(2000, status_label.destroy)  # Remove status message after 2 seconds

if __name__ == "__main__":
    root = tk.Tk()
    app = SpellingTestApp(root)
    root.mainloop()
