def read_file_in_chunks(file_path, chunk_size=8192):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            while True:
                chunk = file.read(chunk_size)
                if not chunk:
                    break
                yield chunk
    except UnicodeDecodeError:
        print(f"Error: Unable to decode file '{file_path}' with UTF-8 encoding. Try a different encoding.")
        return
    except Exception as e:
        print(f"Error reading file '{file_path}': {str(e)}")
        return

def is_word(token, min_length=1):
    return len(token) >= min_length and any(char.isalpha() for char in token)

def clean_word(word, preserve_case=False, keep_hyphens=True):
    cleaned = ''.join(char if char.isalnum() or (keep_hyphens and char == '-') else ' ' for char in word)
    return cleaned if preserve_case else cleaned.lower()

def count_word_frequency(file_path, case_sensitive=False, min_word_length=1, keep_hyphens=True):
    word_counts = {}
    total_words = 0
    try:
        for i, chunk in enumerate(read_file_in_chunks(file_path)):
            if i % 100 == 0:
                print(f"Processing chunk {i}... ({total_words} words processed)")
            
            words = chunk.split()
            for word in words:
                cleaned_word = clean_word(word, case_sensitive, keep_hyphens)
                if is_word(cleaned_word, min_word_length):
                    word_counts[cleaned_word] = word_counts.get(cleaned_word, 0) + 1
                    total_words += 1
    
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return
    except IOError:
        print(f"Error: Unable to read file '{file_path}'.")
        return

    print(f"Finished processing. Total words: {total_words}")
    return word_counts

def display_results(word_counts, top_n=None, output_file=None):
    sorted_word_counts = sorted(word_counts.items(), key=lambda x: (-x[1], x[0]))
    
    if top_n:
        sorted_word_counts = sorted_word_counts[:top_n]
    
    output = '\n'.join(f"{word}: {count}" for word, count in sorted_word_counts)
    
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as file:
                file.write(output)
            print(f"Results written to {output_file}")
        except IOError:
            print(f"Error: Unable to write to file '{output_file}'.")
            print(output)
    else:
        print(output)

file_path = input("Enter the path to the file to analyze: ")
word_counts = count_word_frequency(file_path, case_sensitive=False, min_word_length=2, keep_hyphens=True)
if word_counts:
    display_results(word_counts, top_n=10, output_file='word_counts.txt')