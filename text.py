#!/usr/bin/env python3
import os
import subprocess
import datetime
from datetime import date, timedelta
import random
import time # Added for potential delays if needed

# --- Character Map (5 Rows High, Variable Width) ---
# 'X' = commit, ' ' = no commit
# Designed to be drawn Monday-Friday (rows 1-5) on the GitHub graph.
# Row 0 (Sunday) and Row 6 (Saturday) are unused by this map.
CHAR_MAP = {
    # Letters (Uppercase) - Mostly 3 wide
    'A': ["XXX", "X X", "XXX", "X X", "X X"],
    'B': ["XX ", "X X", "XX ", "X X", "XX "],
    'C': ["XXX", "X  ", "X  ", "X  ", "XXX"],
    'D': ["XX ", "X X", "X X", "X X", "XX "],
    'E': ["XXX", "X  ", "XX ", "X  ", "XXX"],
    'F': ["XXX", "X  ", "XX ", "X  ", "X  "],
    'G': ["XXX", "X  ", "X X", "X X", "XXX"],
    'H': ["X X", "X X", "XXX", "X X", "X X"],
    'I': ["XXX", " X ", " X ", " X ", "XXX"],
    'J': [" XX", "  X", "  X", "X X", "XX "],
    'K': ["X X", "X X", "X  ", "X X", "X X"], # Adjusted K
    'L': ["X  ", "X  ", "X  ", "X  ", "XXX"],
    'M': ["X   X", "XX XX", "X X X", "X   X", "X   X"], # 5 wide
    'N': ["X   X", "XX  X", "X X X", "X  XX", "X   X"], # 5 wide (adjusted N)
    'O': ["XXX", "X X", "X X", "X X", "XXX"],
    'P': ["XXX", "X X", "XXX", "X  ", "X  "],
    'Q': ["XXX", "X X", "X X", "X XX", " XXX"], # Adjusted Q (4 wide)
    'R': ["XXX", "X X", "XX ", "X X", "X X"],
    'S': ["XXX", "X  ", "XXX", "  X", "XXX"],
    'T': ["XXX", " X ", " X ", " X ", " X "],
    'U': ["X X", "X X", "X X", "X X", "XXX"],
    'V': ["X X", "X X", "X X", " X ", " X "],
    'W': ["X   X", "X   X", "X X X", "X X X", " X X "], # 5 wide
    'X': ["X X", " X ", " X ", " X ", "X X"],
    'Y': ["X X", "X X", " X ", " X ", " X "],
    'Z': ["XXX", "  X", " X ", "X  ", "XXX"],

    # Numbers - Mostly 3 wide
    '0': ["XXX", "X X", "X X", "X X", "XXX"],
    '1': [" X ", "XX ", " X ", " X ", "XXX"],
    '2': ["XXX", "  X", "XXX", "X  ", "XXX"],
    '3': ["XXX", "  X", "XXX", "  X", "XXX"],
    '4': ["X X", "X X", "XXX", "  X", "  X"],
    '5': ["XXX", "X  ", "XXX", "  X", "XXX"],
    '6': ["XXX", "X  ", "XXX", "X X", "XXX"],
    '7': ["XXX", "  X", "  X", " X ", " X "],
    '8': ["XXX", "X X", "XXX", "X X", "XXX"],
    '9': ["XXX", "X X", "XXX", "  X", "XXX"],

    # Symbols - Width varies
    ' ': ["   ", "   ", "   ", "   ", "   "], # Space (3 wide)
    '!': ["X", "X", "X", " ", "X"], # 1 wide
    '.': [" ", " ", " ", " ", "X"], # 1 wide
    '?': ["XXX", "  X", " XX", " ", " X "], # 3 wide
    '+': ["   ", " X ", "XXX", " X ", "   "], # 3 wide
    '-': ["   ", "   ", "XXX", "   ", "   "], # 3 wide
    '=': ["   ", "XXX", "   ", "XXX", "   "], # 3 wide
    ':': [" ", "X", " ", "X", " "], # 1 wide
    ';': [" ", "X", " ", "X", " "], # 1 wide (Made consistent)
    '"': ["X X", "X X", "   ", "   ", "   "], # 3 wide
    "'": ["X", "X", " ", " ", " "], # 1 wide
    '/': ["  X", " X ", " X ", " X ", "X  "], # 3 wide
    '\\':["X  ", " X ", " X ", " X ", "  X"], # 3 wide
    '_': ["   ", "   ", "   ", "   ", "XXX"], # 3 wide
    '<': [" X", "X ", "X ", "X ", " X"], # 2 wide
    '>': ["X ", " X", " X", " X", "X "], # 2 wide
    '(': [" X", "X ", "X ", "X ", " X"], # 2 wide
    ')': ["X ", " X", " X", " X", "X "], # 2 wide
    '*': ["   ", "X X", " X ", "X X", "   "], # 3 wide
    '#': [" X ", "XXX", " X ", "XXX", " X "], # 3 wide
    '@': ["XXX", "X X", "XX ", "X  ", "XXX"], # 3 wide (simplified)
    '$': [" X ", "XXX", "X X", "XXX", " X "], # 3 wide (simplified)
    '%': ["X X", "  X", " X ", "X  ", "X X"], # 3 wide
    '^': [" X ", "X X", "   ", "   ", "   "], # 3 wide
    '&': ["XX ", "X X", "XX ", "X X", "XX "], # 3 wide (simplified)
    '|': ["X", "X", "X", "X", "X"], # 1 wide
    '~': ["X X", " X ", "   ", "   ", "   "], # 3 wide (simplified)
}

# Add lowercase letters mapping to uppercase
for char_code in range(ord('a'), ord('z') + 1):
    char = chr(char_code)
    upper_char = char.upper()
    if upper_char in CHAR_MAP:
        CHAR_MAP[char] = CHAR_MAP[upper_char]

CHAR_HEIGHT = 5 # Explicitly define height (corresponds to Monday-Friday)

# --- Git Helper Functions ---

def run_git_command(command, repo_path, env=None, verbose=False):
    """
    Runs a Git command using subprocess in the specified repository path
    and handles errors.
    """
    try:
        # Execute commands within the target repository directory
        result = subprocess.run(command, check=True, capture_output=True, text=True, env=env, cwd=repo_path)
        if verbose:
             print(f"DEBUG: Ran '{' '.join(command)}' in '{repo_path}'. Output:\n{result.stdout}\n{result.stderr}")
        return result
    except subprocess.CalledProcessError as e:
        # Print detailed error information
        print(f"\n--- Git Command Error ---", flush=True)
        print(f"Command: {' '.join(command)}")
        print(f"Path: {repo_path}")
        if env:
            print(f"Environment: GIT_AUTHOR_DATE={env.get('GIT_AUTHOR_DATE')}, GIT_COMMITTER_DATE={env.get('GIT_COMMITTER_DATE')}")
        print(f"Return Code: {e.returncode}")
        print(f"Stderr: {e.stderr.strip()}")
        print(f"Stdout: {e.stdout.strip()}")
        print(f"-------------------------\n", flush=True)
        # Exit on critical initialization errors
        if command[1] == 'init' or (command[1] == 'commit' and 'Initial commit' in command[-1]):
             print("Critical error during repository initialization or first commit. Exiting.", flush=True)
             exit(1)
        print("Error occurred for this commit, attempting to continue with others...", flush=True)
        return None # Indicate failure for this specific command
    except FileNotFoundError:
        print("Error: 'git' command not found. Make sure Git is installed and in your system's PATH.", flush=True)
        exit(1)
    except Exception as e:
        print(f"An unexpected error occurred while running git command: {e}", flush=True)
        print(f"Command: {' '.join(command)}")
        print(f"Path: {repo_path}")
        return None


def create_commit(repo_path, commit_date, commits_per_dot, message_suffix="", verbose=False):
    """
    Creates one or more empty Git commits for a specific date in the specified repository.
    Returns True if at least one commit was successfully created, False otherwise.
    """
    base_time_sec = random.randint(0, 59)
    commit_count_success = 0

    for i in range(commits_per_dot):
        # Vary commit times slightly to look more 'natural'
        commit_hour = random.randint(10, 19) # Simulate business hours
        commit_min = random.randint(0, 59)
        # Ensure seconds are distinct within the same minute for multiple dots
        commit_sec = (base_time_sec + i) % 60

        # Format date string for Git environment variables
        date_str = f"{commit_date.isoformat()} {commit_hour:02d}:{commit_min:02d}:{commit_sec:02d}"
        message = f"Art commit {message_suffix} ({i+1}/{commits_per_dot})"

        # Set Git environment variables for author and committer dates
        env = os.environ.copy()
        env['GIT_AUTHOR_DATE'] = date_str
        env['GIT_COMMITTER_DATE'] = date_str

        # Prepare and run the git commit command
        commit_command = ['git', 'commit', '--allow-empty', '-m', message, '--date', date_str]
        result = run_git_command(commit_command, repo_path, env=env, verbose=verbose)

        if result:
            commit_count_success += 1
            if verbose:
                print(f"  Commit {i+1}/{commits_per_dot} created for {date_str}", flush=True)
        else:
            # If one commit fails, stop trying for this specific dot/date
            print(f"  Failed to create commit {i+1}/{commits_per_dot} for {date_str}. Stopping for this day.", flush=True)
            return False # Indicate failure for this dot

    return commit_count_success > 0 # Return True if any commits succeeded for this dot

# --- Core Logic ---

def get_start_date(year):
    """
    Find the date of the Sunday of the first week to align with GitHub's graph.
    GitHub contribution graphs start on a Sunday.
    """
    jan_1 = date(year, 1, 1)
    # weekday() returns 0 for Monday, 6 for Sunday.
    # We want the offset from Sunday (0). (jan_1.weekday() + 1) % 7 gives Sunday=0, Monday=1, etc.
    day_of_week_sun_0 = (jan_1.weekday() + 1) % 7
    # Subtract the offset to get the previous Sunday
    start_date = jan_1 - timedelta(days=day_of_week_sun_0)
    print(f"Calculated graph start date (Sunday): {start_date}")
    return start_date

def initialize_repo(repo_path, year, verbose=False):
    """
    Initializes a Git repository at the specified path if it doesn't exist.
    Creates the directory if necessary.
    Adds an initial commit if the repository is empty.
    """
    print("\n--- Initializing Repository ---", flush=True)
    repo_path = os.path.abspath(repo_path) # Ensure we have an absolute path

    # Create directory if it doesn't exist
    if not os.path.exists(repo_path):
        try:
            os.makedirs(repo_path)
            print(f"Created directory: {repo_path}", flush=True)
        except OSError as e:
            print(f"Error: Could not create directory: {repo_path}", flush=True)
            print(f"Reason: {e}", flush=True)
            exit(1)
    elif not os.path.isdir(repo_path):
         print(f"Error: The specified path '{repo_path}' exists but is not a directory.", flush=True)
         exit(1)

    git_dir = os.path.join(repo_path, ".git")

    # Initialize Git repo if .git directory doesn't exist
    if not os.path.isdir(git_dir):
        print("'.git' directory not found. Initializing a new Git repository...", flush=True)
        init_result = run_git_command(['git', 'init'], repo_path=repo_path, verbose=verbose)
        if not init_result:
             exit(1) # Exit if git init fails
    else:
        if verbose: print("Existing '.git' directory found.", flush=True)

    # Check if the repository has any commits
    has_commits = False
    try:
        # Use rev-parse HEAD which fails in an empty repo
        run_git_command(['git', 'rev-parse', '--verify', 'HEAD'], repo_path=repo_path, verbose=False)
        has_commits = True
        if verbose: print("Repository already has commits.", flush=True)
    except subprocess.CalledProcessError:
        if verbose: print("No existing commits found (or HEAD is unborn).", flush=True)
    except Exception as e:
        print(f"Error checking for existing commits: {e}", flush=True)
        # Decide if we should continue or exit? Let's try to continue.

    # Create an initial commit if the repository is empty
    if not has_commits:
        print("Creating an initial commit...", flush=True)
        readme_path = os.path.join(repo_path, "README.md")
        try:
            # Create a simple README.md
            with open(readme_path, "w") as f:
                f.write(f"# GitHub Contribution Art\n\nRepository initialized for GitHub contribution art ({year}).\nGenerated by script.\n")
            if verbose: print(f"Created {readme_path}", flush=True)

            # Add the README
            add_result = run_git_command(['git', 'add', 'README.md'], repo_path=repo_path, verbose=verbose)
            if not add_result:
                 print("Failed to git add README.md. Cannot create initial commit.", flush=True)
                 # Consider cleanup? For now, we might continue, but painting will likely fail.
            else:
                # Create the initial commit with a date slightly before the target year starts
                initial_commit_date = date(year, 1, 1) - timedelta(days=3)
                initial_date_str = f"{initial_commit_date.isoformat()} 12:00:00"
                env = os.environ.copy()
                env['GIT_AUTHOR_DATE'] = initial_date_str
                env['GIT_COMMITTER_DATE'] = initial_date_str

                commit_result = run_git_command(
                    ['git', 'commit', '-m', f'Initial commit ({year})'],
                    repo_path=repo_path,
                    env=env,
                    verbose=verbose
                )
                if commit_result:
                    print(f"Initial commit created for date {initial_commit_date.isoformat()}.", flush=True)
                else:
                    print(f"Failed to create initial commit.", flush=True)
                    # Exit here as subsequent commits will likely fail without a HEAD
                    exit(1)

        except Exception as e:
            print(f"Error creating initial commit files: {e}", flush=True)
            exit(1)
    else:
        print("Repository is not empty. Skipping initial commit.", flush=True)

    print("--- Initialization Complete ---", flush=True)


def paint_text(repo_path, text, year, start_column, commits_per_dot, spacing, verbose=False):
    """
    Generates Git commits in the specified repository to paint the text onto
    the GitHub contribution graph for the given year.
    """
    print(f"\n--- Generating Commits ---", flush=True)
    print(f"Painting '{text}' in year {year}...", flush=True)
    repo_path = os.path.abspath(repo_path) # Ensure absolute path

    base_date = get_start_date(year) # Sunday of the first week
    current_col = start_column       # Starting week column (0-52)
    total_commits_made = 0
    max_cols = 53                    # GitHub graph has 53 columns (weeks)
    # Row offsets map CHAR_MAP rows (0-4) to GitHub graph days (1-5: Mon-Fri)
    # CHAR_MAP row 0 -> Monday (day index 1)
    # CHAR_MAP row 1 -> Tuesday (day index 2)
    # ...
    # CHAR_MAP row 4 -> Friday (day index 5)
    row_offset_start = 1 # Start drawing on Monday

    print(f"Processing text: '{text}'", flush=True)
    print("Progress: [", end="", flush=True) # Start progress indicator
    progress_bar_width = 50
    last_progress_ticks = 0

    total_chars = len(text)
    processed_chars = 0

    # Iterate through each character in the input text
    for char_index, char in enumerate(text):
        if char not in CHAR_MAP:
            if verbose: print(f"\nWarning: Character '{char}' not found in CHAR_MAP, treating as space.", flush=True)
            char = ' ' # Default to space if character not defined

        pattern = CHAR_MAP[char]

        # Determine the width of the character pattern
        if not pattern:
             char_width = 0 # Handle potential empty patterns gracefully
             if verbose: print(f"\nWarning: Empty pattern found for character '{char}'. Skipping.", flush=True)
        else:
             # Width is determined by the length of the first row string
             char_width = len(pattern[0])

        if verbose:
             print(f"\nProcessing char '{char}' (Index: {char_index}, Width: {char_width}), Target start column: {current_col}", flush=True)

        # Check if the character would start beyond the graph's width
        if current_col >= max_cols:
            print(f"]\nWarning: Starting column {current_col} for char '{char}' is at or beyond the maximum {max_cols} columns. Stopping.", flush=True)
            break # Stop processing further characters

        char_commits = 0
        # Iterate through each row of the character pattern (0 to CHAR_HEIGHT-1)
        for pattern_row_index in range(CHAR_HEIGHT):
            # Check if the pattern definition has this many rows
            if pattern_row_index >= len(pattern): continue

            pattern_row_str = pattern[pattern_row_index]
            # Iterate through each column within the character's pattern row
            for pattern_col_offset in range(char_width):
                 # Check if the pattern string is long enough for this column
                if pattern_col_offset >= len(pattern_row_str): continue

                # Check if this position in the pattern requires a commit ('X')
                if pattern_row_str[pattern_col_offset] == 'X':
                    # Calculate the target column (week) on the GitHub graph
                    commit_col = current_col + pattern_col_offset
                    # Ensure the commit column is within the graph bounds
                    if commit_col >= max_cols:
                         if verbose: print(f"  Skipping dot at pattern row {pattern_row_index}, col offset {pattern_col_offset} because target column {commit_col} >= {max_cols}")
                         continue # Skip if this dot falls outside the graph weeks

                    # Calculate the day of the week offset (1=Mon, 2=Tue, ..., 5=Fri)
                    # This maps the pattern row index to the desired day on the graph
                    day_of_week_offset = row_offset_start + pattern_row_index

                    # Calculate the exact date for the commit
                    commit_date = base_date + timedelta(weeks=commit_col, days=day_of_week_offset)

                    # Crucially, only make commits for the target year
                    if commit_date.year == year:
                        if verbose: print(f"  Target commit date: {commit_date} (Week: {commit_col}, Day: {day_of_week_offset})")
                        # Create the specified number of commits for this 'dot'
                        if create_commit(repo_path, commit_date, commits_per_dot, message_suffix=f"char='{char}' pos={char_index}", verbose=verbose):
                           char_commits += commits_per_dot
                        else:
                            # If create_commit failed, we might want to stop or log more seriously
                            if verbose: print(f"  Failed making commits for {commit_date}")
                            # Continue to the next dot for now
                    elif verbose:
                         print(f"  Skipping date {commit_date} because it's not in the target year {year}")

        if verbose and char_commits > 0:
            print(f"  Made {char_commits} commits for character '{char}'.", flush=True)
        total_commits_made += char_commits

        # Advance the current column position for the next character
        # Includes the character width and the spacing between characters
        current_col += char_width + spacing

        # Update progress bar
        processed_chars += 1
        progress_ticks = int(progress_bar_width * processed_chars / total_chars)
        ticks_to_print = progress_ticks - last_progress_ticks
        if ticks_to_print > 0:
            print("=" * ticks_to_print, end="", flush=True)
            last_progress_ticks = progress_ticks


    print("]", flush=True) # End progress indicator
    print(f"\n--- Generation Complete ---", flush=True)
    print(f"Made approximately {total_commits_made} commits in total for '{text}' in year {year}.", flush=True)
    return total_commits_made


def print_final_instructions(repo_path):
    """Prints instructions for the user on how to push the changes to GitHub."""
    print("\n--- Next Steps ---")
    print("1. Navigate to your local repository directory in your terminal:")
    # Use abspath to ensure the user gets the full path
    print(f"   cd \"{os.path.abspath(repo_path)}\"")
    print("\n2. Set your GitHub repository as the remote 'origin' (if you haven't already):")
    print("   git remote add origin <your-repository-url>")
    print("   (Replace <your-repository-url> with the actual URL from GitHub, e.g., git@github.com:username/repo.git or https://...)")
    print("\n3. Push the generated commits to GitHub:")
    print("   !!! IMPORTANT !!!")
    print("   You will likely need to FORCE PUSH. This OVERWRITES the history on GitHub.")
    print("   Ensure this repository is dedicated to this art or you understand the consequences.")
    print("   Use a command like:")
    print("   git push --force origin <your-branch-name>")
    print("   (Replace <your-branch-name> with your branch, often 'main' or 'master')")
    print("\n4. After pushing, check your GitHub profile contribution graph.")
    print("   It might take a few minutes for GitHub to process the commits and update the graph.")
    print("\nSee the README.md file for more detailed information and warnings.")
    print("------------------", flush=True)

def get_user_input():
    """
    Prompts the user for necessary parameters via terminal input and validates them.
    Returns a dictionary containing the validated parameters or None if cancelled.
    """
    print("--- GitHub Contribution Art Configuration ---")
    params = {}
    current_year = datetime.datetime.now().year

    # 1. Repository Path
    while True:
        repo_path = input("Enter the full path to your local Git repository directory: ")
        if repo_path.strip():
            params['repo_path'] = repo_path.strip()
            break
        else:
            print("Repository path cannot be empty.")

    # 2. Text to Paint
    while True:
        text = input("Enter the text to paint on the graph (e.g., 'HELLO WORLD'): ")
        if text.strip():
            params['text'] = text # Keep original spacing if intended
            break
        else:
            print("Text cannot be empty.")

    # 3. Year
    while True:
        year_str = input(f"Enter the target year [{current_year}]: ")
        if not year_str:
            params['year'] = current_year
            break
        try:
            year = int(year_str)
            if year > 1970 and year < 2100: # Reasonable year range
                 params['year'] = year
                 break
            else:
                 print("Please enter a valid year (e.g., between 1971 and 2099).")
        except ValueError:
            print("Invalid input. Please enter a number for the year.")

    # 4. Starting Column
    while True:
        col_str = input("Enter the starting week column (0-52, 0=first week) [1]: ")
        if not col_str:
            params['column'] = 1
            break
        try:
            column = int(col_str)
            if 0 <= column <= 52:
                params['column'] = column
                break
            else:
                print("Column must be between 0 and 52.")
        except ValueError:
            print("Invalid input. Please enter a number for the column.")

    # 5. Commits per Dot
    while True:
        dots_str = input("Enter the number of commits per 'dot' (for intensity) [1]: ")
        if not dots_str:
            params['dots'] = 1
            break
        try:
            dots = int(dots_str)
            if dots >= 1:
                params['dots'] = dots
                break
            else:
                print("Commits per dot must be at least 1.")
        except ValueError:
            print("Invalid input. Please enter a number for dots.")

    # 6. Spacing
    while True:
        spacing_str = input("Enter the space between characters (in columns) [1]: ")
        if not spacing_str:
            params['spacing'] = 1
            break
        try:
            spacing = int(spacing_str)
            if spacing >= 0:
                params['spacing'] = spacing
                break
            else:
                print("Spacing cannot be negative.")
        except ValueError:
            print("Invalid input. Please enter a number for spacing.")

    # 7. Verbose Output
    while True:
        verbose_str = input("Enable detailed verbose output? (y/n) [n]: ").lower()
        if not verbose_str or verbose_str == 'n':
            params['verbose'] = False
            break
        elif verbose_str == 'y':
            params['verbose'] = True
            break
        else:
            print("Please enter 'y' or 'n'.")

    # --- Confirmation ---
    print("\n--- Summary ---")
    print(f"Repository: {params['repo_path']}")
    print(f"Text:       '{params['text']}'")
    print(f"Year:       {params['year']}")
    print(f"Start Col:  {params['column']}")
    print(f"Dots:       {params['dots']}")
    print(f"Spacing:    {params['spacing']}")
    print(f"Verbose:    {params['verbose']}")
    print("---------------")

    while True:
        confirm = input("Proceed with generating commits? (y/n): ").lower()
        if confirm == 'y':
            return params
        elif confirm == 'n':
            print("Operation cancelled by user.")
            return None
        else:
            print("Please enter 'y' or 'n'.")


# --- Main Execution ---
if __name__ == "__main__":
    print("Starting GitHub Contribution Art Script (TUI Mode)...", flush=True)

    # Get configuration from user via interactive prompts
    config = get_user_input()

    if config:
        # If user confirmed, proceed with the operations
        try:
            initialize_repo(config['repo_path'], config['year'], config['verbose'])
            paint_text(config['repo_path'], config['text'], config['year'], config['column'], config['dots'], config['spacing'], config['verbose'])
            print_final_instructions(config['repo_path'])
        except Exception as e:
            print(f"\n--- An Unexpected Error Occurred ---", flush=True)
            print(f"Error: {e}")
            import traceback
            print("\n--- Traceback ---")
            traceback.print_exc()
            print("-----------------", flush=True)
            print("Script execution failed.", flush=True)
            exit(1)
    else:
        # User cancelled during configuration
        print("Exiting script.", flush=True)
        exit(0)

    print("\nScript finished.", flush=True)