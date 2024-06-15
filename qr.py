import os
import sqlite3
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import qrcode
from PIL import Image, ImageTk


# Function to create or connect to the database
def create_db():
    conn = sqlite3.connect('generated_qr_codes.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS qr_codes (
            id INTEGER PRIMARY KEY,
            filename TEXT,
            filepath TEXT
        )
    ''')
    conn.commit()
    conn.close()


# Function to add a QR code file to the database
def add_file_to_db(filename, filepath):
    conn = sqlite3.connect('generated_qr_codes.db')
    c = conn.cursor()
    c.execute('INSERT INTO qr_codes (filename, filepath) VALUES (?, ?)', (filename, filepath))
    conn.commit()
    conn.close()


# Function to get all QR code files from the database
def get_files_from_db():
    conn = sqlite3.connect('generated_qr_codes.db')
    c = conn.cursor()
    c.execute('SELECT * FROM qr_codes')
    files = c.fetchall()
    conn.close()
    return files


# Function to delete a QR code file from the database
def delete_file_from_db(file_id):
    conn = sqlite3.connect('generated_qr_codes.db')
    c = conn.cursor()
    c.execute('DELETE FROM qr_codes WHERE id = ?', (file_id,))
    conn.commit()
    conn.close()


# Function to generate and display the QR code
def generate_qr_code():
    link = link_var.get()
    output_directory = output_directory_var.get()
    file_name = file_name_var.get()

    if not link or not output_directory or not file_name:
        messagebox.showerror("Error", "Please provide a URL, an output directory, and a file name.")
        return

    output_file_path = os.path.join(output_directory, file_name + ".png")

    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(link)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')

        # Resize the QR code to 1080x1080 pixels
        img = img.resize((1080, 1080), Image.LANCZOS)
        img.save(output_file_path)

        # Display the QR code in the GUI
        img = img.resize((200, 200), Image.LANCZOS)  # Resize for display
        img = ImageTk.PhotoImage(img)
        qr_code_label.config(image=img)
        qr_code_label.image = img

        # Add the file to the database
        add_file_to_db(file_name + ".png", output_file_path)

        # Refresh the file list in the table
        refresh_file_list()

        messagebox.showinfo("Success", f"QR code generated and saved to {output_file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


# Function to select the output directory
def select_output_directory():
    directory_path = filedialog.askdirectory()
    if directory_path:  # Update the variable only if a directory was selected
        output_directory_var.set(directory_path)


# Function to refresh the file list in the table
def refresh_file_list():
    for row in tree.get_children():
        tree.delete(row)
    for file in get_files_from_db():
        tree.insert("", "end", values=(file[0], file[1], file[2]))


# Function to open a file
def open_file(file_path):
    try:
        os.startfile(file_path)
    except Exception as e:
        messagebox.showerror("Error", f"Could not open file: {e}")


# Function to delete selected file
def on_delete_button_click():
    selected_items = tree.selection()
    if not selected_items:
        messagebox.showerror("Error", "You have not selected a file to delete!")
        return
    selected_item = selected_items[0]
    file_id = tree.item(selected_item, 'values')[0]
    delete_file_from_db(file_id)
    refresh_file_list()


# Function to open selected file
def on_open_button_click():
    selected_items = tree.selection()
    if not selected_items:
        messagebox.showerror("Error", "You have not selected a file to open!")
        return
    selected_item = selected_items[0]
    file_path = tree.item(selected_item, 'values')[2]
    open_file(file_path)


# Function to display QR code of selected file
def on_select_file(event):
    selected_items = tree.selection()
    if not selected_items:
        return
    selected_item = selected_items[0]
    file_path = tree.item(selected_item, 'values')[2]
    try:
        img = Image.open(file_path)
        img = img.resize((200, 200), Image.LANCZOS)
        img = ImageTk.PhotoImage(img)
        qr_code_label.config(image=img)
        qr_code_label.image = img
    except Exception as e:
        messagebox.showerror("Error", f"Could not display QR code: {e}")


# Function to exit fullscreen mode
def exit_fullscreen(event=None):
    root.state('normal')


# Create the main application window
root = tk.Tk()
root.title("QR Code Generator")

# Maximize the window to the screen size
root.state('zoomed')

# Create the database
create_db()

# Variables to hold the link, output directory, and file name
link_var = tk.StringVar()
output_directory_var = tk.StringVar()
file_name_var = tk.StringVar()

# Create and place the widgets
top_frame = tk.Frame(root, bg='#1E5AAF', height=60)
top_frame.pack(side='top', fill='x')

title_label = tk.Label(top_frame, text="QR Code Generator", bg='#1E5AAF', fg='white', font=("Arial", 18, "bold"))
title_label.pack(pady=10)

main_frame = tk.Frame(root, bg='white')
main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

# Left side frame for input fields and buttons
left_frame = tk.Frame(main_frame, bg='white')
left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

# Right side frame for QR code preview
right_frame = tk.Frame(main_frame, bg='white')
right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

tk.Label(left_frame, text="Generate a QR code from a URL", bg='white', fg='black', font=("Arial", 12)).grid(row=0,
                                                                                                            column=0,
                                                                                                            columnspan=3,
                                                                                                            pady=(
                                                                                                            10, 5))

tk.Label(left_frame, text="URL", bg='white', fg='black', font=("Arial", 10)).grid(row=1, column=0, padx=10, pady=5,
                                                                                  sticky="e")
url_entry = tk.Entry(left_frame, textvariable=link_var, width=50, font=("Arial", 10))
url_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew", columnspan=2)

tk.Label(left_frame, text="Output Directory", bg='white', fg='black', font=("Arial", 10)).grid(row=2, column=0, padx=10,
                                                                                               pady=5, sticky="e")
output_directory_entry = tk.Entry(left_frame, textvariable=output_directory_var, width=50, font=("Arial", 10))
output_directory_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
tk.Button(left_frame, text="Browse", command=select_output_directory, bg='#1E5AAF', fg='white',
          font=("Arial", 10)).grid(row=2, column=2, padx=10, pady=5)

tk.Label(left_frame, text="File Name", bg='white', fg='black', font=("Arial", 10)).grid(row=3, column=0, padx=10,
                                                                                        pady=5, sticky="e")
file_name_entry = tk.Entry(left_frame, textvariable=file_name_var, width=50, font=("Arial", 10))
file_name_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew", columnspan=2)

tk.Button(left_frame, text="Generate QR Code", command=generate_qr_code, bg='#1E5AAF', fg='white',
          font=("Arial", 10)).grid(row=4, column=0, columnspan=3, pady=10)

# Label to display the generated QR code in the right frame
qr_code_label = tk.Label(right_frame, bg='white')
qr_code_label.pack(pady=(10, 5))

# Create the table to display generated QR codes
table_frame = tk.Frame(main_frame, bg='white')
table_frame.grid(row=1, column=0, columnspan=2, pady=(5, 10), sticky="ew")

columns = ("ID", "Filename", "Filepath")
tree = ttk.Treeview(table_frame, columns=columns, show='headings', yscrollcommand=lambda f, l: scrollbar.set(f, l))

# Define headings
tree.heading("ID", text="ID")
tree.heading("Filename", text="Filename")
tree.heading("Filepath", text="Filepath")

# Define columns
tree.column("ID", anchor="w", width=30)
tree.column("Filename", anchor="w", width=150)
tree.column("Filepath", anchor="w", width=300)

# Add a scrollbar
scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
tree.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

# Bind the select event to display QR code
tree.bind('<<TreeviewSelect>>', on_select_file)

# Refresh the file list when the application starts
refresh_file_list()

# Add an "Open File" button
open_button = tk.Button(main_frame, text="Open File", command=on_open_button_click, bg='#1E5AAF', fg='white',
                        font=("Arial", 10))
open_button.grid(row=2, column=0, pady=5)

# Add a "Delete File" button
delete_button = tk.Button(main_frame, text="Delete File", command=on_delete_button_click, bg='#1E5AAF', fg='white',
                          font=("Arial", 10))
delete_button.grid(row=2, column=1, pady=5)

bottom_frame = tk.Frame(root, bg='#1E5AAF', height=30)
bottom_frame.pack(side='bottom', fill='x')

footer_label = tk.Label(bottom_frame, text="Copyright © Developed By Sudarshan Gautam", bg='#1E5AAF', fg='white',
                        font=("Arial", 8))
footer_label.pack(pady=5)

# Bind the escape key to exit fullscreen mode
root.bind("<Escape>", exit_fullscreen)

# Make the entry fields expand with the window
main_frame.columnconfigure(0, weight=1)
main_frame.columnconfigure(1, weight=1)
left_frame.columnconfigure(1, weight=1)

# Run the application
root.mainloop()
