def count_word_frequency(file_path):
    with open(file_path, 'r') as file:
        text = file.read()
    
    text = text.lower()
    for char in ".,!?:;\"'()[]{}":
        text = text.replace(char, '')
    words = text.split()
    
    word_counts = {}
    for word in words:
        if word in word_counts:
            word_counts[word] += 1
        else:
            word_counts[word] = 1
    
    sorted_word_counts = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    
    for word, count in sorted_word_counts:
        print(f"{word}: {count}")

file_path = input("Enter the path to the file: ")
count_word_frequency(file_path)