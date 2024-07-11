import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import heapq

class WordCounter:
    def __init__(self, file_path, case_sensitive, min_word_length, keep_hyphens, encoding, top_n):
        self.file_path = file_path
        self.case_sensitive = case_sensitive
        self.min_word_length = min_word_length
        self.keep_hyphens = keep_hyphens
        self.encoding = encoding
        self.top_n = top_n
        self.total_words = 0
        self.word_heap = []

    def read_file_in_chunks(self, chunk_size=8192):
        try:
            with open(self.file_path, 'r', encoding=self.encoding) as file:
                while True:
                    chunk = file.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
        except UnicodeDecodeError:
            raise ValueError(f"Unable to decode file with {self.encoding} encoding. Try a different encoding.")

    def is_word(self, token):
        return len(token) >= self.min_word_length and any(char.isalpha() for char in token)

    def clean_word(self, word):
        cleaned = ''.join(char if char.isalnum() or (self.keep_hyphens and char == '-') else ' ' for char in word)
        return cleaned if self.case_sensitive else cleaned.lower()

    def update_heap(self, word):
        if len(self.word_heap) < self.top_n:
            heapq.heappush(self.word_heap, (1, word))
        else:
            heapq.heappushpop(self.word_heap, (1, word))

    def process_chunk(self, chunk):
        words = chunk.split()
        for word in words:
            cleaned_word = self.clean_word(word)
            if self.is_word(cleaned_word):
                self.update_heap(cleaned_word)
                self.total_words += 1

    def count_words(self, progress_callback=None):
        file_size = os.path.getsize(self.file_path)
        bytes_read = 0
        
        try:
            for chunk in self.read_file_in_chunks():
                bytes_read += len(chunk.encode(self.encoding))
                if progress_callback:
                    progress_callback(bytes_read / file_size * 100)
                self.process_chunk(chunk)
        
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Error processing file: {str(e)}")

    def get_results(self):
        word_counts = {}
        for count, word in self.word_heap:
            word_counts[word] = word_counts.get(word, 0) + 1
        sorted_counts = sorted(word_counts.items(), key=lambda x: (-x[1], x[0]))
        return sorted_counts, self.total_words

class WordCounterGUI:
    def __init__(self, master):
        self.master = master
        master.title("Word Frequency Counter")
        
        self.file_path = tk.StringVar()
        self.case_sensitive = tk.BooleanVar()
        self.min_word_length = tk.IntVar(value=1)
        self.keep_hyphens = tk.BooleanVar(value=True)
        self.encoding = tk.StringVar(value='utf-8')
        self.top_n = tk.IntVar(value=10)
        
        tk.Label(master, text="File:").grid(row=0, column=0, sticky='e')
        tk.Entry(master, textvariable=self.file_path, width=50).grid(row=0, column=1)
        tk.Button(master, text="Browse", command=self.browse_file).grid(row=0, column=2)
        
        tk.Checkbutton(master, text="Case Sensitive", variable=self.case_sensitive).grid(row=1, column=0, columnspan=2, sticky='w')
        tk.Checkbutton(master, text="Keep Hyphens", variable=self.keep_hyphens).grid(row=2, column=0, columnspan=2, sticky='w')
        
        tk.Label(master, text="Min Word Length:").grid(row=3, column=0, sticky='e')
        tk.Entry(master, textvariable=self.min_word_length, width=5).grid(row=3, column=1, sticky='w')
        
        tk.Label(master, text="Encoding:").grid(row=4, column=0, sticky='e')
        tk.Entry(master, textvariable=self.encoding, width=10).grid(row=4, column=1, sticky='w')
        
        tk.Label(master, text="Top N Results:").grid(row=5, column=0, sticky='e')
        tk.Entry(master, textvariable=self.top_n, width=5).grid(row=5, column=1, sticky='w')
        
        tk.Button(master, text="Count Words", command=self.count_words).grid(row=6, column=0, columnspan=2)
        tk.Button(master, text="Save Results", command=self.save_results).grid(row=6, column=2)
        
        self.progress = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(master, variable=self.progress, maximum=100, length=300)
        self.progress_bar.grid(row=7, column=0, columnspan=3, pady=10)
        
        self.result_text = tk.Text(master, height=20, width=50)
        self.result_text.grid(row=8, column=0, columnspan=3)

        self.word_counter = None
        self.results = None

    def browse_file(self):
        filename = filedialog.askopenfilename()
        self.file_path.set(filename)

    def update_progress(self, value):
        self.progress.set(value)
        self.master.update_idletasks()

    def count_words(self):
        file_path = self.file_path.get()
        if not file_path:
            messagebox.showerror("Error", "Please select a file.")
            return
        
        try:
            self.word_counter = WordCounter(
                file_path, 
                self.case_sensitive.get(),
                self.min_word_length.get(),
                self.keep_hyphens.get(),
                self.encoding.get(),
                self.top_n.get()
            )
            
            self.word_counter.count_words(progress_callback=self.update_progress)
            self.results, total_words = self.word_counter.get_results()
            
            self.result_text.delete('1.0', tk.END)
            self.result_text.insert(tk.END, f"Total words: {total_words}\n\n")
            for word, count in self.results:
                self.result_text.insert(tk.END, f"{word}: {count}\n")
        
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def save_results(self):
        if not self.results:
            messagebox.showerror("Error", "No results to save. Please count words first.")
            return
        
        file_path = filedialog.asksaveasfilename(defaultextension=".txt")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(f"Total words: {self.word_counter.total_words}\n\n")
                    for word, count in self.results:
                        file.write(f"{word}: {count}\n")
                messagebox.showinfo("Success", "Results saved successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save results: {str(e)}")

root = tk.Tk()
gui = WordCounterGUI(root)
root.mainloop()