import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import heapq
import threading

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
        self.stop_requested = False

    def read_file_in_chunks(self, chunk_size=8192):
        try:
            with open(self.file_path, 'r', encoding=self.encoding) as file:
                while True:
                    if self.stop_requested:
                        break
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
        for i, (count, w) in enumerate(self.word_heap):
            if w == word:
                self.word_heap[i] = (count + 1, w)
                heapq.heapify(self.word_heap)
                return
        if len(self.word_heap) < self.top_n:
            heapq.heappush(self.word_heap, (1, word))
        elif self.word_heap[0][0] < 1:
            heapq.heapreplace(self.word_heap, (1, word))

    def process_chunk(self, chunk):
        words = chunk.split()
        for word in words:
            if self.stop_requested:
                break
            cleaned_word = self.clean_word(word)
            if self.is_word(cleaned_word):
                self.update_heap(cleaned_word)
                self.total_words += 1

    def count_words(self, progress_callback=None):
        file_size = os.path.getsize(self.file_path)
        bytes_read = 0
        
        try:
            for chunk in self.read_file_in_chunks():
                if self.stop_requested:
                    break
                bytes_read += len(chunk.encode(self.encoding))
                if progress_callback:
                    progress_callback(bytes_read / file_size * 100)
                self.process_chunk(chunk)
        
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Error processing file: {str(e)}")

    def get_results(self):
        sorted_counts = sorted(self.word_heap, key=lambda x: (-x[0], x[1]))
        return [(word, count) for count, word in sorted_counts], self.total_words

    def stop(self):
        self.stop_requested = True

class SimpleBarChart(tk.Canvas):
    def __init__(self, master, width, height):
        super().__init__(master, width=width, height=height)
        self.width = width
        self.height = height

    def plot(self, data):
        self.delete("all")
        if not data:
            return

        max_value = max(count for _, count in data)
        bar_width = self.width / len(data)
        scale = (self.height - 20) / max_value

        for i, (word, count) in enumerate(data):
            x0 = i * bar_width
            y0 = self.height - (count * scale)
            x1 = (i + 1) * bar_width
            y1 = self.height
            self.create_rectangle(x0, y0, x1, y1, fill="blue")
            self.create_text(x0 + bar_width/2, self.height - 10, text=word, angle=90, anchor="e")

        self.create_text(10, 10, text=f"Max: {max_value}", anchor="nw")

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
        
        self.create_widgets()

        self.word_counter = None
        self.results = None
        self.count_thread = None

    def create_widgets(self):
        tk.Label(self.master, text="File:").grid(row=0, column=0, sticky='e')
        tk.Entry(self.master, textvariable=self.file_path, width=50).grid(row=0, column=1)
        tk.Button(self.master, text="Browse", command=self.browse_file).grid(row=0, column=2)
        
        tk.Checkbutton(self.master, text="Case Sensitive", variable=self.case_sensitive).grid(row=1, column=0, columnspan=2, sticky='w')
        tk.Checkbutton(self.master, text="Keep Hyphens", variable=self.keep_hyphens).grid(row=2, column=0, columnspan=2, sticky='w')
        
        tk.Label(self.master, text="Min Word Length:").grid(row=3, column=0, sticky='e')
        tk.Entry(self.master, textvariable=self.min_word_length, width=5).grid(row=3, column=1, sticky='w')
        
        tk.Label(self.master, text="Encoding:").grid(row=4, column=0, sticky='e')
        encodings = ['utf-8', 'ascii', 'iso-8859-1', 'utf-16']
        ttk.Combobox(self.master, textvariable=self.encoding, values=encodings).grid(row=4, column=1, sticky='w')
        
        tk.Label(self.master, text="Top N Results:").grid(row=5, column=0, sticky='e')
        tk.Entry(self.master, textvariable=self.top_n, width=5).grid(row=5, column=1, sticky='w')
        
        self.count_button = tk.Button(self.master, text="Count Words", command=self.start_count_words)
        self.count_button.grid(row=6, column=0)
        self.stop_button = tk.Button(self.master, text="Stop", command=self.stop_count_words, state=tk.DISABLED)
        self.stop_button.grid(row=6, column=1)
        tk.Button(self.master, text="Save Results", command=self.save_results).grid(row=6, column=2)
        
        self.progress = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.master, variable=self.progress, maximum=100, length=300)
        self.progress_bar.grid(row=7, column=0, columnspan=3, pady=10)
        
        self.result_text = tk.Text(self.master, height=20, width=50)
        self.result_text.grid(row=8, column=0, columnspan=3)

        self.chart = SimpleBarChart(self.master, width=400, height=200)
        self.chart.grid(row=0, column=3, rowspan=9, padx=10)

    def browse_file(self):
        filename = filedialog.askopenfilename()
        self.file_path.set(filename)

    def update_progress(self, value):
        self.progress.set(value)
        self.master.update_idletasks()

    def start_count_words(self):
        file_path = self.file_path.get()
        if not file_path:
            messagebox.showerror("Error", "Please select a file.")
            return
        
        self.word_counter = WordCounter(
            file_path, 
            self.case_sensitive.get(),
            self.min_word_length.get(),
            self.keep_hyphens.get(),
            self.encoding.get(),
            self.top_n.get()
        )
        
        self.count_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress.set(0)
        self.result_text.delete('1.0', tk.END)
        
        self.count_thread = threading.Thread(target=self.count_words_thread)
        self.count_thread.start()

    def count_words_thread(self):
        try:
            self.word_counter.count_words(progress_callback=self.update_progress)
            self.master.after(0, self.display_results)
        except Exception as e:
            self.master.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.master.after(0, self.reset_buttons)

    def stop_count_words(self):
        if self.word_counter:
            self.word_counter.stop()

    def reset_buttons(self):
        self.count_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def display_results(self):
        self.results, total_words = self.word_counter.get_results()
        
        self.result_text.delete('1.0', tk.END)
        self.result_text.insert(tk.END, f"Total words: {total_words}\n\n")
        for word, count in self.results:
            self.result_text.insert(tk.END, f"{word}: {count}\n")
        
        self.chart.plot(self.results[:10])

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