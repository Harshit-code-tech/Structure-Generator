import os
import tkinter as tk
from tkinter import filedialog, messagebox

def browse_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        folder_path.set(folder_selected)

def save_tree_structure():
    folder = folder_path.get()
    if not folder:
        messagebox.showerror("Error", "Please select a folder first!")
        return

    # Generate the tree structure
    tree_structure = get_tree_structure(folder)

    # Save the tree structure to a text file
    save_file = filedialog.asksaveasfilename(
        initialfile=f'structure_{os.path.basename(folder)}.txt',
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )

    if save_file:
        with open(save_file, 'w',encoding ='utf-8') as file:
            file.write(tree_structure)
        messagebox.showinfo("Success", f"Tree structure saved to {save_file}")

def get_tree_structure(folder):
    tree_lines = []
    for root, dirs, files in os.walk(folder):
        level = root.replace(folder, '').count(os.sep)
        indent = ' ' * 4 * level + '├── '
        tree_lines.append(f"{indent}{os.path.basename(root)}/")
        sub_indent = ' ' * 4 * (level + 1) + '├── '
        for f in files:
            tree_lines.append(f"{sub_indent}{f}")
    return "\n".join(tree_lines)

# Create the main window
root = tk.Tk()
root.title("Folder Tree Structure")

# Folder path variable
folder_path = tk.StringVar()

# Create and place the widgets
frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

label = tk.Label(frame, text="Selected Folder:")
label.pack(side=tk.LEFT)

entry = tk.Entry(frame, textvariable=folder_path, width=50)
entry.pack(side=tk.LEFT, padx=5)

browse_button = tk.Button(frame, text="Browse", command=browse_folder)
browse_button.pack(side=tk.LEFT)

save_button = tk.Button(root, text="Save Tree Structure", command=save_tree_structure)
save_button.pack(pady=5)

# Run the application
root.mainloop()
