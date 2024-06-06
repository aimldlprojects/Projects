import tkinter as tk
from tkinter import ttk
import pandas as pd
import random
from datetime import datetime, timedelta

from gtts import gTTS
from playsound import playsound
import os
import tempfile


# Custom style for rounded buttons if desired
def rounded_button(canvas, x, y, width, height, corner_radius, **kwargs):
    """Function to create rounded rectangle (for buttons, etc.)"""
    points = [x+corner_radius, y,
              x+width-corner_radius, y,
              x+width, y,
              x+width, y+height,
              x+width-corner_radius, y+height,
              x+corner_radius, y+height,
              x, y+height,
              x, y]
    return canvas.create_polygon(points, **kwargs, smooth=True)

class SpellingTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Spelling Test App")
        self.root.geometry("800x600")  # Set window size to 800x600 for more space

        # Load word list
        self.word_list = pd.read_csv("word_list.csv")

        self.current_word = tk.StringVar()
        self.user_input = tk.StringVar()

        self.correct_count = 0
        self.wrong_count = 0
        self.auto_advance = tk.BooleanVar(value=False)  # Default to not automatically advancing
        self.auto_hide_test_options = tk.BooleanVar(value=False)
        self.setup_gui()
    
    def pronounce_current_word(self):
        current_word = self.current_word.get()  # Assuming this is how you access the word to be spelled
        tts = gTTS(text=current_word, lang='en')
        with tempfile.NamedTemporaryFile(delete=True) as fp:
            temp_filename = fp.name + '.mp3'
            tts.save(temp_filename)
            playsound(temp_filename)
            os.remove(temp_filename)  # Clean up the temporary file
            
    def setup_gui(self):
        # Configure the main window's style
        self.style = ttk.Style(self.root)
        self.style.theme_use('clam')

        # Customizing widget styles
        self.style.configure('TLabel', font=('Helvetica', 14))
        self.style.configure('TButton', font=('Helvetica', 12), background='#f0f0f0')
        self.style.configure('TEntry', font=('Helvetica', 12), fieldbackground='#f0f0f0')
        self.style.configure('TCombobox', font=('Helvetica', 12), fieldbackground='#f0f0f0')
        self.style.configure('Bold.TCheckbutton', font=('Helvetica', 12, 'bold'))  # Configure a bold style for checkbuttons

        # Main content frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Sidebar separator
        separator = ttk.Separator(main_frame, orient=tk.VERTICAL)
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # Side panel for test options
        side_panel = ttk.Frame(main_frame, width=200)  # Define the width of the side panel
        side_panel.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Auto-hide checkbox
        auto_hide_checkbox = ttk.Checkbutton(
            side_panel,
            text="Auto-Hide Test Options",
            variable=self.auto_hide_test_options,
            onvalue=True,
            offvalue=False,
            command=self.toggle_test_options_visibility,
            style='Bold.TCheckbutton'  # Apply the bold style
        )
        auto_hide_checkbox.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=5)

        # Test options frame
        self.test_options_frame = ttk.Frame(side_panel)
        self.test_options_frame.grid(row=1, column=0, columnspan=2, pady=5, sticky="w")

        # Test options label
        test_options_label = ttk.Label(self.test_options_frame, text="Test Options", font=('Helvetica', 14))
        test_options_label.grid(row=0, column=0, sticky="w")

        # Auto Advance checkbox
        auto_advance_checkbox = ttk.Checkbutton(
            self.test_options_frame,
            text="Auto Advance to Next Word",
            variable=self.auto_advance,
            onvalue=True,
            offvalue=False
        )
        auto_advance_checkbox.grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=5)

        # Combobox for selecting test options
        self.test_options = ttk.Combobox(self.test_options_frame, values=["Length of the word", "Previous incorrectly spelled words", "Words practiced a week ago"], state="readonly")
        self.test_options.grid(row=2, column=0, padx=5, pady=5)
        self.test_options.current(0)

        # Combobox for length options
        self.length_options = ttk.Combobox(self.test_options_frame, values=list(range(1, 11)), state="readonly")
        self.length_options.grid(row=3, column=0, padx=5, pady=5)  # Adjust to use grid
        self.length_options.current(1)  # Assuming you want the first item as default

        # Start test button
        ttk.Button(self.test_options_frame, text="Start Test", command=self.start_test).grid(row=4, column=0, columnspan=2, padx=10, pady=10)



        # App title
        ttk.Label(main_frame, text="Welcome to Spelling Test App", font=('Helvetica', 18)).pack(pady=20)

        # Instruction label
        ttk.Label(main_frame, text="Type the spelling of the pronounced word:").pack()

        # Dedicated frame for the "Hear Word" button and status message
        self.dynamic_frame = ttk.Frame(main_frame)
        self.dynamic_frame.pack(pady=(5, 20))  # Adjust as needed

        # "Hear Word" button in the dynamic frame
        ttk.Button(self.dynamic_frame, text="Hear Word", command=self.pronounce_current_word).pack(side=tk.LEFT, padx=(10, 5))

        # Placeholder frame for status message with a fixed height
        self.status_frame = ttk.Frame(main_frame)  # Adjust height as needed
        self.status_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        # Display current word to spell
        ttk.Label(main_frame, textvariable=self.current_word, font=('Helvetica', 16)).pack(pady=10)

        # User input entry
        ttk.Entry(main_frame, textvariable=self.user_input, font=('Helvetica', 14)).pack(pady=10)

        # Frame for check and next buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)  # Add some padding to separate from the entry widget

        # Check button with delayed pronunciation
        ttk.Button(button_frame, text="Check", command=lambda: [self.check_spelling()]).pack(side=tk.LEFT, padx=5)

        # Next word button with delayed pronunciation
        ttk.Button(button_frame, text="Next Word", command=lambda: [self.next_word()]).pack(side=tk.LEFT)

        # Display stats
        self.status_label = ttk.Label(main_frame, text=f"Status: Correct - {self.correct_count}, Wrong - {self.wrong_count}", font=('Helvetica', 14))
        self.status_label.pack(pady=10)

    def toggle_test_options_visibility(self):
        if self.auto_hide_test_options.get():
            # Hide test options
            self.test_options_frame.grid_remove()
        else:
            # Show test options
            self.test_options_frame.grid(row=5, column=0, columnspan=2, pady=5, sticky="w")


    def start_test(self):
        # Implementation remains the same as previous
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



    def check_spelling(self):
        # Implementation remains the same as previous
        correct_word = self.current_word.get()
        user_word = self.user_input.get()
        
        if user_word.strip().lower() == correct_word.strip().lower():
            self.correct_count += 1
            self.update_status("Correct!", "green",500)
        else:
            self.wrong_count += 1
            self.update_status(f"Wrong! Correct spelling is: {correct_word}", "red",5000)
            # Save incorrect word to CSV
            pd.DataFrame({'word': [correct_word]}).to_csv("previous_incorrect_words.csv", mode='a', header=False, index=False)
            
    def next_word(self):
        # Implementation remains the same as previous
        if self.words_for_test:
            # Clear any existing status messages first
            for widget in self.status_frame.winfo_children():
                widget.destroy()
            # Optionally, maintain the space with an empty label if desired
            ttk.Label(self.status_frame).pack()
            
            self.current_word.set(random.choice(self.words_for_test))
            self.pronounce_current_word()
        else:
            self.current_word.set("No more words for the test")

    def update_status(self, message, color, status_time):
        # Clear the status frame of any widgets
        for widget in self.status_frame.winfo_children():
            widget.destroy()

        # Create and pack a new status label within the status frame
        self.status_message = ttk.Label(self.status_frame, text=message, foreground=color)
        self.status_message.pack()

        # Schedule removal of the status message after 2 seconds
        def clear_status():
            self.status_message.destroy()
            # Optionally create an empty label to preserve the space
            ttk.Label(self.status_frame).pack()
            
        # Update the status label
        self.status_label.config(text=f"Status: Correct - {self.correct_count}, Wrong - {self.wrong_count}")

        
        self.user_input.set("")

        if self.auto_advance.get():  # Check if auto-advance is enabled
            # After 2 seconds, proceed to the next word
            self.root.after(status_time, clear_status)
            # Introduce a delay before advancing to the next word if needed
            self.root.after(status_time+500, self.next_word)  # Adjust the delay as needed
        else:
            # Do not automatically advance to the next word
            pass
        
        

# The main part of the program
if __name__ == "__main__":
    root = tk.Tk()
    app = SpellingTestApp(root)
    root.mainloop()
