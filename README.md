# Python Word Frequency Counter

## Overview
This Python program is a graphical user interface (GUI) application that allows users to count the frequency of words in a text file. It provides various options for case sensitivity, minimum word length, hyphen handling, and encoding. The results can be visualized as a bar chart and saved to a file.

## Features
- Count word frequencies in a text file.
- Options for case sensitivity and minimum word length.
- Option to retain or remove hyphens in words.
- Support for various text encodings.
- Display the top N most frequent words.
- Progress tracking during word counting.
- Visualization of results as a bar chart.
- Save results to a text file.

## Requirements
- Python 3.x
- tkinter

## Installation

1. **Clone the Repository:**
   ```
   git clone https://github.com/Sebdababo/Python-Word-Counter.git
   cd Python-Word-Counter
   ```

2. **Run the Program:**
   ```
   python word_counter.py
   ```

## Usage

1. **Select a File:** Click the "Browse" button and select a text file to analyze.
2. **Configure Options:**
   - Case Sensitive: Check to differentiate between uppercase and lowercase words.
   - Keep Hyphens: Check to retain hyphens in words.
   - Min Word Length: Set the minimum length of words to include in the count.
   - Encoding: Choose the text encoding of the file (e.g., utf-8, ascii).
   - Top N Results: Set the number of top frequent words to display.
3. **Count Words:** Click the "Count Words" button to start the word counting process. The progress will be shown in the progress bar.
4. **Stop Counting:** Click the "Stop" button to stop the word counting process.
5. **Save Results:** Click the "Save Results" button to save the results to a text file.
