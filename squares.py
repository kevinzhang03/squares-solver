import argparse
import time
from english_words import get_english_words_set

start_time = time.time()

dictionary_api = 'https://api.dictionaryapi.dev/api/v2/entries/en/'

MIN_WORD_LEN = 4

# Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-m', '--max', type=int, default=8, help='Maximum word length')
parser.add_argument('-w', '--width', type=int, default=80, help='Max char width of the output')
parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
args = parser.parse_args()
max_depth = args.max
width = args.width
verbose = args.verbose

# Validate the max_depth to ensure it's at least MIN_WORD_LEN
if max_depth < MIN_WORD_LEN:
    print(f"Maximum word length must be at least {MIN_WORD_LEN}. Searching for words of length {MIN_WORD_LEN}.\n")
    max_depth = MIN_WORD_LEN

# Load the set of English words once to improve efficiency
english_words_set = get_english_words_set(sources=['web2', 'gcide', 'dwyl'], lower=True, alpha=True)


def generate_words(squares, max_depth, verbose=False):    
    rows, cols = len(squares), len(squares[0])
    words_by_length = {i: set() for i in range(MIN_WORD_LEN, max_depth + 1)}
    check_counter = [0]  # Using a list to allow modification within nested function

    def dfs(x, y, word, visited):
        if len(word) >= MIN_WORD_LEN:
            if verbose:
                check_counter[0] += 1
                print(f"{check_counter[0]}: {word}")

        if len(word) >= MIN_WORD_LEN and word.lower() in english_words_set:
            words_by_length[len(word)].add(word)
            if verbose:
                print(f"Added word {word}!")

        if len(word) == max_depth:
            return

        for dx, dy in ((dx, dy) for dx in range(-1, 2) for dy in range(-1, 2) if dx or dy):
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols and (nx, ny) not in visited:
                dfs(nx, ny, word + squares[nx][ny], visited | {(nx, ny)})

    for i in range(rows):
        for j in range(cols):
            dfs(i, j, squares[i][j], {(i, j)})

    return words_by_length


def display_words(words_by_length, max_depth, max_char_width=width):
    print()
    
    total_words_found = sum(len(words) for words in words_by_length.values())

    for length in range(MIN_WORD_LEN, max_depth + 1):
        words = words_by_length.get(length, [])
        num_words = len(words)
        title = f"{length}-letter words ({num_words}):"
        print(title)
        print('-' * len(title))

        if num_words > 0:
            sorted_words = sorted(words)
            line = ""
            for word in sorted_words:
                if len(line) + len(word) + 2 <= max_char_width:  # 2 for padding spaces
                    line += word + "  "
                else:
                    print(line.strip())
                    line = word + "  "
            if line:  # Print remaining line if any
                print(line.strip())
        else:
            print("No words found.")
        print()

    # Final message
    title = "SUMMARY:"
    print(title)
    print('-' * len(title))
    print(f"{total_words_found} words found.")
    print(f"{max_depth} letters max search.")

squares = """
eipa
quen
escs
hseh
"""

squares = [list(line) for line in squares.strip().split('\n')]

display_words(
    generate_words(squares, max_depth, verbose),
    max_depth
)

end_time = time.time()
execution_time = end_time - start_time

print(f"{execution_time:.3f} seconds execution time.")
print()
