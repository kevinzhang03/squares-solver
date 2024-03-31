import argparse
import requests
import concurrent.futures
import threading
from english_words import get_english_words_set

dictionary_api_v2 = 'https://api.dictionaryapi.dev/api/v2/entries/en/'

MIN_WORD_LEN = 4

# Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-m', '--max', type=int, default=8, help='Maximum word length')
parser.add_argument('-t', '--threads', type=int, default=1, help='Number of threads')
args = parser.parse_args()
max_depth = args.max
num_threads = args.threads

# Validate the max_depth to ensure it's at least MIN_WORD_LEN
if max_depth < MIN_WORD_LEN:
    print(f"Maximum word length must be at least {MIN_WORD_LEN}. Searching for words of length {MIN_WORD_LEN}.\n")
    max_depth = MIN_WORD_LEN

# Load the set of English words once to improve efficiency
english_words_set = get_english_words_set(sources=['web2', 'gcide'], lower=True, alpha=True)

squares = """
ourb
isfo
ndaa
gwrg
"""

# Parse the squares grid from a multiline string
squares = [list(line) for line in squares.strip().split('\n')]

# Global API call counter and lock for thread safety
api_call_count = 0
count_lock = threading.Lock()

def word_exists(word):
    global api_call_count
    with count_lock:
        api_call_count += 1
        current_count = api_call_count
    response = requests.get(f"{dictionary_api_v2}{word}")
    print(f"calls: {current_count}, checking: {word}, response: {response.status_code}")
    return response.status_code == 200 and "No Definitions Found" not in response.text, response.status_code

def generate_words(squares, max_depth, num_threads):
    rows, cols = len(squares), len(squares[0])
    words_by_length = {i: set() for i in range(MIN_WORD_LEN, max_depth + 1)}
    all_words = []

    def dfs(x, y, word, visited):
        if len(word) > max_depth:
            return

        if MIN_WORD_LEN <= len(word):
            all_words.append(word.lower())

        for dx, dy in ((dx, dy) for dx in range(-1, 2) for dy in range(-1, 2) if dx or dy):
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols and (nx, ny) not in visited:
                dfs(nx, ny, word + squares[nx][ny], visited | {(nx, ny)})

    for i in range(rows):
        for j in range(cols):
            dfs(i, j, squares[i][j], {(i, j)})

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        future_to_word = {executor.submit(word_exists, word): word for word in set(all_words)}
        for future in concurrent.futures.as_completed(future_to_word):
            word = future_to_word[future]
            exists, _ = future.result()
            if exists:
                words_by_length[len(word)].add(word)

    return words_by_length

def display_words(words_by_length, max_depth):
    num_columns = 6

    for length in range(MIN_WORD_LEN, max_depth + 1):
        words = words_by_length.get(length, [])
        num_words = len(words)
        title = f"{length}-letter words ({num_words}):"
        print(title)
        print('-' * len(title))

        if num_words > 0:
            sorted_words = sorted(words)
            for i in range(0, len(sorted_words), num_columns):
                print("  ".join(sorted_words[i:i + num_columns]))
        else:
            print("No words found.")
        print()

display_words(
  generate_words(squares, max_depth, num_threads),
  max_depth
)