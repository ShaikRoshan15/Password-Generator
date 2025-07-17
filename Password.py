import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import random

# Initialize DB
conn = sqlite3.connect('passwords.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS passwords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                strength TEXT NOT NULL)''')
conn.commit()

# Password Strength Check
def get_strength(password):
    if len(password) < 8:
        return "Weak"
    elif len(password) == 8:
        return "Moderate"
    else:
        return "Strong"

# GUI Setup
root = tk.Tk()
root.title("Password Manager")

# Entry Fields
tk.Label(root, text="Username:").grid(row=0, column=0, sticky="e")
entry_username = tk.Entry(root)
entry_username.grid(row=0, column=1)

tk.Label(root, text="No. of Alphabets:").grid(row=1, column=0, sticky="e")
entry_alpha = tk.Entry(root)
entry_alpha.grid(row=1, column=1)

tk.Label(root, text="No. of Numbers:").grid(row=2, column=0, sticky="e")
entry_num = tk.Entry(root)
entry_num.grid(row=2, column=1)

tk.Label(root, text="No. of Special Chars:").grid(row=3, column=0, sticky="e")
entry_sp = tk.Entry(root)
entry_sp.grid(row=3, column=1)

# Password Generation
def generate_password():
    username = entry_username.get()
    try:
        noofalpha = int(entry_alpha.get())
        noofnum = int(entry_num.get())
        noofsp = int(entry_sp.get())
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers.")
        return

    alpa = list("abcdefghijklmnopqrstuvwxyzQWERTYUIOPASDFGHJKLZXCVBNM")
    num = list("0123456789")
    sp = list("!@#$&")

    password = ''.join(random.choices(alpa, k=noofalpha)) + \
               ''.join(random.choices(num, k=noofnum)) + \
               ''.join(random.choices(sp, k=noofsp))
    password = ''.join(random.sample(password, len(password)))

    strength = get_strength(password)

    # Check for existing username and update
    c.execute("SELECT * FROM passwords WHERE username=?", (username,))
    if c.fetchone():
        c.execute("UPDATE passwords SET password=?, strength=? WHERE username=?", (password, strength, username))
    else:
        c.execute("INSERT INTO passwords (username, password, strength) VALUES (?, ?, ?)", (username, password, strength))
    conn.commit()

    messagebox.showinfo("Password", f"Generated Password: {password}\nStrength: {strength}")

# Buttons
tk.Button(root, text="Generate Password", command=generate_password).grid(row=4, columnspan=2, pady=10)

# Search Fields
tk.Label(root, text="Search by:").grid(row=5, column=0, sticky="e")
search_criteria = tk.StringVar()
criteria_menu = ttk.Combobox(root, textvariable=search_criteria, values=["ID", "Username", "Strength"], state="readonly")
criteria_menu.grid(row=5, column=1, sticky="w")
criteria_menu.set("Username")

tk.Label(root, text="Search term:").grid(row=6, column=0, sticky="e")
entry_search = tk.Entry(root)
entry_search.grid(row=6, column=1, sticky="w")

# Treeview Table
treeview = ttk.Treeview(root, columns=("ID", "Username", "Password", "Strength"), show="headings", height=10)
treeview.grid(row=8, column=0, columnspan=2, padx=10, pady=10)
for col in ("ID", "Username", "Password", "Strength"):
    treeview.heading(col, text=col)
    treeview.column(col, width=150)

# Search and Delete
def view_database():
    treeview.delete(*treeview.get_children())
    c.execute("SELECT * FROM passwords")
    for row in c.fetchall():
        treeview.insert('', 'end', values=row)

def search_database():
    term = entry_search.get().strip()
    criteria = search_criteria.get()

    if not term:
        messagebox.showwarning("Search", "Enter a value to search.")
        return

    treeview.delete(*treeview.get_children())

    if criteria == "ID":
        c.execute("SELECT * FROM passwords WHERE id=?", (term,))
    elif criteria == "Username":
        c.execute("SELECT * FROM passwords WHERE username LIKE ?", (f"%{term}%",))
    elif criteria == "Strength":
        c.execute("SELECT * FROM passwords WHERE strength LIKE ?", (f"%{term}%",))
    for row in c.fetchall():
        treeview.insert('', 'end', values=row)

def delete_selected():
    selected = treeview.selection()
    if not selected:
        messagebox.showwarning("Delete", "Select a row to delete.")
        return
    for i in selected:
        item = treeview.item(i)['values']
        c.execute("DELETE FROM passwords WHERE id=?", (item[0],))
        conn.commit()
        treeview.delete(i)

# Buttons Below Table
action_frame = tk.Frame(root)
action_frame.grid(row=9, column=0, columnspan=2)
tk.Button(action_frame, text="View Database", command=view_database).pack(side=tk.LEFT, padx=10)
tk.Button(action_frame, text="Search", command=search_database).pack(side=tk.LEFT, padx=10)
tk.Button(action_frame, text="Delete Selected", command=delete_selected).pack(side=tk.LEFT, padx=10)

root.mainloop()
conn.close()
