def read_file_in_chunks(file_path, chunk_size=4096):
    with open(file_path, 'r', encoding='utf-8') as file:
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            yield chunk

def is_word(token):
    return any(char.isalpha() for char in token)

def count_word_frequency(file_path):
    word_counts = {}
    try:
        for chunk in read_file_in_chunks(file_path):
            cleaned_chunk = ''.join(char.lower() if char.isalnum() or char.isspace() else ' ' for char in chunk)
            words = cleaned_chunk.split()
            
            for word in words:
                if is_word(word):
                    word_counts[word] = word_counts.get(word, 0) + 1
    
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return
    except IOError:
        print(f"Error: Unable to read file '{file_path}'.")
        return

    sorted_word_counts = sorted(word_counts.items(), key=lambda x: (-x[1], x[0]))
    
    for word, count in sorted_word_counts:
        print(f"{word}: {count}")

file_path = input("Enter the path to the file: ")
count_word_frequency(file_path)