import tkinter.messagebox as messagebox

class SpellingTestApp:
    def start_test(self):
        # Check if a user ID is selected
        if not self.user_id_var.get():
            messagebox.showinfo("User ID Required", "Please select a user ID before starting the test.")
            return

        # Implementation remains the same as before
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
