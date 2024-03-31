import argparse
import time
import threading
import concurrent.futures
from english_words import get_english_words_set

start_time = time.time()

MIN_WORD_LEN = 4

# Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-m', '--max', type=int, default=8, help='Maximum word length')
parser.add_argument('-w', '--width', type=int, default=80, help='Max char width of the output')
parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
parser.add_argument('-t', '--threads', type=int, default=1, help='Number of threads to use')
args = parser.parse_args()

max_depth = args.max
width = args.width
verbose = args.verbose
num_threads = args.threads

# Load the set of English words once to improve efficiency
english_words_set = get_english_words_set(sources=['web2', 'gcide', 'dwyl'], lower=True, alpha=True)

def generate_words(squares, max_depth, verbose=False, num_threads=1):    
    rows, cols = len(squares), len(squares[0])
    words_by_length = {i: set() for i in range(MIN_WORD_LEN, max_depth + 1)}

    def dfs(x, y, word, visited, verbose):
        logs = []
        if len(word) >= MIN_WORD_LEN:
            log = f"Checking: {word}"
            if verbose:
                logs.append(log)

            if word.lower() in english_words_set:
                if verbose:
                    logs.append(f"Added word: {word}")
                return {len(word): {word}}, logs

        if len(word) == max_depth:
            return {}, logs

        result = {}
        for dx, dy in ((dx, dy) for dx in range(-1, 2) for dy in range(-1, 2) if dx or dy):
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols and (nx, ny) not in visited:
                sub_result, sub_logs = dfs(nx, ny, word + squares[nx][ny], visited | {(nx, ny)}, verbose)
                logs.extend(sub_logs)
                for length, words in sub_result.items():
                    if length in result:
                        result[length].update(words)
                    else:
                        result[length] = words

        return result, logs

    # When executing with ProcessPoolExecutor
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(dfs, i, j, squares[i][j], {(i, j)}, verbose) for i in range(rows) for j in range(cols)]
        for future in concurrent.futures.as_completed(futures):
            sub_result, logs = future.result()
            if verbose:
                for log in logs:
                    print(log)
            for length, words in sub_result.items():
                words_by_length[length].update(words)

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
ourb
isfo
ndaa
gwrg
"""

squares = [list(line) for line in squares.strip().split('\n')]

display_words(
    generate_words(squares, max_depth, verbose, num_threads=num_threads),
    max_depth
)

end_time = time.time()
execution_time = end_time - start_time

print(f"{execution_time:.3f} seconds execution time.")
print()
