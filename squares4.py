import argparse
import time
from tabulate import tabulate
import pyautogui
from english_words import get_english_words_set

start_time = time.time()

MIN_WORD_LEN = 4
DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
DIRECTION_NAMES = ['LU', 'U ', 'RU', 'L ', 'R ', 'LD', 'D ', 'RD']

# Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-m', '--max', type=int, default=8, help='Maximum word length')
parser.add_argument('-w', '--width', type=int, default=80, help='Max char width of the output')
parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
parser.add_argument('-d', '--detailed', action='store_true', help='Display detailed output')
args = parser.parse_args()
max_depth = args.max
width = args.width
verbose = args.verbose
detailed_output = args.detailed

# Validate the max_depth to ensure it's at least MIN_WORD_LEN
if max_depth < MIN_WORD_LEN:
    print(f"Maximum word length must be at least {MIN_WORD_LEN}.")
    max_depth = MIN_WORD_LEN

# Load the set of English words once to improve efficiency
english_words_set = get_english_words_set(sources=['web2', 'gcide', 'dwyl'], lower=True, alpha=True)

def generate_words(squares, max_depth, verbose=False):    
    rows, cols = len(squares), len(squares[0])
    words_info = {}

    def dfs(x, y, word, visited, move_sequence, start_position=None):
        if start_position is None:
            start_position = (x, y)

        if len(word) >= MIN_WORD_LEN and word.lower() in english_words_set:
            if word not in words_info:
                words_info[word] = {
                    'word': word,
                    'length': len(word),
                    'paths': [{'start_location': start_position, 'move_sequence': move_sequence.copy()}]
                }
            else:
                words_info[word]['paths'].append({'start_location': start_position, 'move_sequence': move_sequence.copy()})

            if verbose:
                print(f"Added word {word} with path {move_sequence} starting at {start_position}")

        if len(word) == max_depth:
            return

        for i, (dx, dy) in enumerate(DIRECTIONS):
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols and (nx, ny) not in visited:
                dfs(nx, ny, word + squares[nx][ny], visited | {(nx, ny)}, move_sequence + [DIRECTION_NAMES[i]], start_position)

    for i in range(rows):
        for j in range(cols):
            dfs(i, j, squares[i][j], {(i, j)}, [])

    return words_info.values()

def display_words(words_info, max_depth, max_char_width=width, detailed_output=False):
    print()
    
    word_count_by_length = {}
    path_count_by_length = {}

    for word_info in words_info:
        length = word_info['length']
        word_count_by_length[length] = word_count_by_length.get(length, 0) + 1
        path_count_by_length[length] = path_count_by_length.get(length, 0) + len(word_info['paths'])

    total_words_found = sum(word_count_by_length.values())
    total_paths_found = sum(path_count_by_length.values())

    if detailed_output:
        print("Start Positions are denoted as (row, column), top left being (0, 0)")
        print()
        
        for length in range(MIN_WORD_LEN, max_depth + 1):
            words = [word_info for word_info in words_info if word_info['length'] == length]
            num_words = word_count_by_length.get(length, 0)
            num_paths = path_count_by_length.get(length, 0)
            
            if num_words > 0:
                title = f"{length}-letter words ({num_words} words, {num_paths} paths):"
                print(title)
                print('-' * len(title))

                table_data = []
                for word_info in words:
                    start_positions = "\n".join(str(path['start_location']) for path in word_info['paths'])
                    move_sequences = "\n".join(" ".join(path['move_sequence']) for path in word_info['paths'])
                    table_data.append([word_info['word'], start_positions, move_sequences])

                print(tabulate(table_data, headers=["Word", "Start Position", "Moves"], tablefmt="rounded_grid"))
            print()
    else:
        for length in range(MIN_WORD_LEN, max_depth + 1):
            num_words = word_count_by_length.get(length, 0)
            title = f"{length}-letter words ({num_words}):"
            print(title)
            print('-' * len(title))

            if num_words > 0:
                sorted_words = sorted({word_info['word'] for word_info in words_info if word_info['length'] == length})
                line = ""
                for word in sorted_words:
                    if len(line) + len(word) + 2 <= max_char_width:
                        line += word + "  "
                    else:
                        print(line.strip())
                        line = word + "  "
                if line:
                    print(line.strip())
            else:
                print("No words found.")
            print()

    # Final message
    title = "SUMMARY:"
    print(title)
    print('-' * len(title))
    print(f"{total_words_found} unique words found.")
    print(f"{total_paths_found} unique paths found.")
    print(f"{max_depth} letters max search.")
    

def move_mouse_to_play(words_info, grid_top_left, grid_bottom_right):
    grid_width = grid_bottom_right[0] - grid_top_left[0]
    grid_height = grid_bottom_right[1] - grid_top_left[1]
    cell_width = grid_width / 4
    cell_height = grid_height / 4

    MOVE_DURATION = 0.05  # Duration to move between letters

    for word_info in words_info:
        path = word_info['paths'][0]  # Only use the first path
        start_position = path['start_location']
        start_x = grid_top_left[0] + (start_position[1] * cell_width) + (cell_width / 2)
        start_y = grid_top_left[1] + (start_position[0] * cell_height) + (cell_height / 2)

        pyautogui.moveTo(start_x, start_y)
        pyautogui.mouseDown()

        for move in path['move_sequence']:
            dx, dy = DIRECTIONS[DIRECTION_NAMES.index(move)]
            start_x += dx * cell_width
            start_y += dy * cell_height
            pyautogui.moveTo(start_x, start_y, duration=MOVE_DURATION)

        pyautogui.mouseUp()
        time.sleep(0.1)  # Wait a bit before starting the next word


squares = """
eipa
quen
escs
hseh
"""

squares = [list(line) for line in squares.strip().split('\n')]


if __name__ == "__main__":
    words_info = list(generate_words(squares, max_depth, verbose))

    display_words(
        words_info,
        max_depth,
        width,
        detailed_output
    )

    # Wait 5 seconds before starting the mouse movement
    print("waiting 5 seconds before the mouse goes brr...")
    time.sleep(5)
    grid_top_left = (1330, 350)
    grid_bottom_right = (1730, 750)

    move_mouse_to_play(words_info, grid_top_left, grid_bottom_right)

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"{execution_time:.3f} seconds execution time.")