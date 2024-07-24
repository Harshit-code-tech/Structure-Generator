# Structure-Generator
This Program is used to generate the structure of a folder.. from root to end.. 

# Folder Tree Structure Viewer

This is a simple Python application built using Tkinter that allows you to browse a folder and save its tree structure to a text file.

## Requirements

- Python 3.x
- Tkinter (usually included with Python)
- os (standard library)
- tkinter (standard library)

## Installation

1. Ensure you have Python installed. You can download it from [python.org](https://www.python.org/).
2. Tkinter is usually included with Python. If not, you can install it using the following command:
    ```sh
    sudo apt-get install python3-tk
    ```

## How to Use

1. Run the script:
    ```sh
    python Structure_generator.py
    ```
2. Select a folder:
    - Click on the "Browse" button to open a dialog box.
    - Navigate to the folder you want to analyze and select it.
3. Save the tree structure:
    - Click on the "Save Tree Structure" button.
    - Choose the location and name for the text file that will contain the tree structure.

## Script Details

### Functions

- `browse_folder()`: Opens a directory selection dialog and sets the selected folder path.
- `save_tree_structure()`: Generates the tree structure of the selected folder and saves it to a text file.
- `get_tree_structure(folder)`: Recursively generates a tree structure of the specified folder.

### Main Window

The main window contains:

- An entry field to display the selected folder path.
- A "Browse" button to select a folder.
- A "Save Tree Structure" button to save the folder's tree structure to a text file.

## Example Output

The tree structure is saved in a format similar to:

```sh
├── folder_name/
    ├── subfolder1/
        ├── file1.txt
        ├── file2.txt
    ├── subfolder2/
        ├── file3.txt
