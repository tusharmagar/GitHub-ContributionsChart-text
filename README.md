# GitHub Contribution Art Generator

This Python script allows you to "doodle" custom text messages onto your GitHub contribution graph by generating Git commits on specific dates.

Go from this: 
![Screenshot 2025-04-29 at 22 11 14](https://github.com/user-attachments/assets/61f5e40c-c355-4300-acde-ec3556d61bab)

To this!
![Screenshot 2025-04-29 at 22 25 50](https://github.com/user-attachments/assets/941457fc-c420-4f43-91b7-07a5d4f601ce)


## Features

* **Custom Text:** Spell out words or messages.
* **Year Selection:** Choose the specific year for the contribution art.
* **Positioning:** Control the starting week (column) of your text.
* **Intensity:** Set the number of commits per "dot" to make squares darker or lighter.
* **Spacing:** Adjust the spacing between characters.
* **Interactive Input:** Uses a Terminal User Interface (TUI) to guide you through configuration.
* **Repository Initialization:** Can initialize a new Git repository or use an existing one.

## Requirements

* **Python 3:** The script is written for Python 3.
* **Git:** Git must be installed on your system and accessible from the command line (in your PATH).

## How to Use

1.  **Download/Clone:** Get the `text.py` script onto your local machine.
2.  **Navigate:** Open your terminal or command prompt and navigate to the directory where you saved the script.
    ```bash
    cd /path/to/script/directory
    ```
3.  **Run the Script:** Execute the script using Python 3.
    ```bash
    python text.py
    ```
4.  **Follow Prompts:** The script will interactively ask you for the following information:
    * **Repository Path:** The full path to the *local* Git repository where you want to generate the commits.
        * The script will create this directory if it doesn't exist.
        * **Recommendation:** Use a *new, empty repository* dedicated solely to this contribution art.
    * **Text to doodle:** The message you want to appear on the graph (e.g., `HELLO GITHUB`).
    * **Target Year:** The year the contributions should appear in (defaults to the current year).
    * **Starting Column:** The week number (0-52) where the text should begin (defaults to 1). 0 is the leftmost week column on the graph.
    * **Commits per Dot:** How many commits to generate for each 'X' in the character map (defaults to 1). More commits make the squares appear darker on the graph.
    * **Spacing:** How many empty columns to leave between characters (defaults to 1).
    * **Verbose Output:** Whether to print detailed debugging information (defaults to 'n').
5.  **Confirm:** Review the summary of your settings and confirm ('y') to start generating commits. This process can take a few moments depending on the text length and commits per dot.
6.  **Navigate to Your Repo:** After the script finishes, **change directory** into the repository path you provided:
    ```bash
    cd /full/path/to/your/repo
    ```
7.  **Add GitHub Remote:** If this is a new local repository, link it to a repository on GitHub. Create a new, empty repository on GitHub.com first (do **not** initialize it with a README, .gitignore, or license on GitHub). Then, run:
    ```bash
    git remote add origin <your-repository-url>
    ```
    *(Replace `<your-repository-url>` with the URL from your GitHub repo, like `git@github.com:YourUsername/YourRepoName.git` or `https://github.com/YourUsername/YourRepoName.git`)*.
8.  **Push to GitHub:** Push the generated commits to your GitHub repository.

    **⚠️ WARNING: FORCE PUSH REQUIRED ⚠️**

    You will almost certainly need to **force push** (`--force` or `-f`). This **overwrites the history** of the remote branch on GitHub.
    * **DO NOT** do this on a repository with existing important history unless you fully understand the consequences (it will likely erase that history).
    * This is why using a **dedicated repository** for the art is **strongly recommended**.

    ```bash
    git push --force origin main
    ```
    *(Replace `main` with your branch name if it's different, e.g., `master`)*.

9.  **Check GitHub:** Go to your GitHub profile page. It might take a few minutes (sometimes longer) for GitHub to process the pushed commits and update your contribution graph.

## Important Notes & Warnings

* **⚠️ USE A DEDICATED REPOSITORY:** Seriously. Force pushing can wreak havoc on existing project history. Create a new repository on GitHub just for this purpose.
* **Force Push (`git push --force`):** Understand that this command rewrites the history on the GitHub remote. Use with extreme caution.
* **GitHub Graph Updates:** Be patient; the graph doesn't always update instantly after a push.
* **Existing Commits:** If you run the script on a repository that already has commits in the target year, the script's commits will be added alongside them. This might interfere with the visual clarity of your text.
* **Character Set:** The script supports uppercase letters (A-Z), lowercase letters (a-z), numbers (0-9), and a selection of common symbols (`! . ? + - = : ; " ' / \ _ < > ( ) * # @ $ % ^ & | ~` and space). Unsupported characters will be treated as spaces. You can modify the `CHAR_MAP` in the script to add or change characters.
* **Rate Limiting:** While unlikely for typical messages, generating an enormous number of commits very rapidly *could* potentially trigger GitHub rate limiting, although the script adds commits sequentially.

## Customization

You can customize the appearance of characters by modifying the `CHAR_MAP` dictionary at the beginning of the `text.py` script. Each character is defined by a list of 5 strings, representing the 5 rows (Monday to Friday) of the GitHub graph for that character's columns. 'X' means a commit (a green square), and ' ' means no commit.

## License

This script is released under the MIT License. See the LICENSE file for details (or assume standard MIT terms if no file is present).
