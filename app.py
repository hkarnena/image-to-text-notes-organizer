import openai
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import pytesseract
from PIL import Image
import os
from datetime import datetime

# ---------------- OCR Setup ----------------
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ---------------- Default Notes Folder ----------------
notes_dir = os.path.join(os.getcwd(), "notes")
if not os.path.exists(notes_dir):
    os.makedirs(notes_dir)


# ---------------- Functions ----------------

def load_notes():
    notes_list.delete(0, tk.END)
    if os.path.exists(notes_dir):
        for file in os.listdir(notes_dir):
            if file.endswith(".txt"):
                notes_list.insert(tk.END, file)


def upload_and_extract():
    file_path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp")])
    if file_path:
        try:
            img = Image.open(file_path)
            extracted_text = pytesseract.image_to_string(img)
            text_box.delete("1.0", tk.END)
            text_box.insert(tk.END, extracted_text)
        except Exception as e:
            messagebox.showerror("Error", str(e))


def save_note():
    global notes_dir
    text = text_box.get("1.0", tk.END).strip()
    
    if not text:
        messagebox.showwarning("Empty Note", "No text to save!")
        return

    if not os.path.exists(notes_dir):
        os.makedirs(notes_dir)

    filename = f"note_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    filepath = os.path.join(notes_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)

    load_notes()
    messagebox.showinfo("Saved", f"Note saved:\n{filepath}")


def load_note(event=None):
    try:
        selected = notes_list.get(notes_list.curselection())
        filepath = os.path.join(notes_dir, selected)

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        text_box.delete("1.0", tk.END)
        text_box.insert(tk.END, content)
    except:
        pass


def delete_note():
    try:
        selected = notes_list.get(notes_list.curselection())
        filepath = os.path.join(notes_dir, selected)
        os.remove(filepath)
        load_notes()
        text_box.delete("1.0", tk.END)
        messagebox.showinfo("Deleted", f"Deleted: {selected}")
    except:
        messagebox.showwarning("Warning", "Select a note to delete")


def rename_note():
    try:
        selected = notes_list.get(notes_list.curselection())
        old_path = os.path.join(notes_dir, selected)

        new_name = simpledialog.askstring("Rename Note", "Enter new name:")
        if not new_name:
            return

        new_name = f"{new_name}.txt"
        new_path = os.path.join(notes_dir, new_name)

        if os.path.exists(new_path):
            messagebox.showerror("Error", "File already exists!")
            return

        os.rename(old_path, new_path)
        load_notes()
        messagebox.showinfo("Renamed", f"Renamed to {new_name}")
    except:
        messagebox.showwarning("Warning", "Select a note to rename")


def search_notes(event=None):
    global notes_dir
    search_text = search_entry.get().lower()
    notes_list.delete(0, tk.END)

    if not os.path.exists(notes_dir):  
        os.makedirs(notes_dir)

    for file in os.listdir(notes_dir):
        if file.endswith(".txt"):
            path = os.path.join(notes_dir, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read().lower()

                if search_text in file.lower() or search_text in content:
                    notes_list.insert(tk.END, file)

            except:
                pass


def choose_save_folder():
    global notes_dir
    new_folder = filedialog.askdirectory()

    if new_folder:
        notes_dir = new_folder
        if not os.path.exists(notes_dir):
            os.makedirs(notes_dir)
        load_notes()
        messagebox.showinfo("Folder Selected", f"Notes folder:\n{notes_dir}")
    else:
        messagebox.showwarning("Folder Not Selected", "Using previous folder")

def summarize_note():
    text = text_box.get("1.0", tk.END).strip()
    
    if not text:
        messagebox.showwarning("Empty Note", "No text to summarize!")
        return

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are an assistant that summarizes notes concisely."},
                {"role": "user", "content": f"Summarize this in bullet points:\n{text}"}
            ],
            max_tokens=200
        )
        
        summary = response.choices[0].message["content"]
        
        text_box.insert(tk.END, "\n\n--- ✨ AI Summary ---\n" + summary)

    except Exception as e:
        messagebox.showerror("AI Error", f"Failed to summarize:\n{e}")

# ---------------- GUI ----------------

root = tk.Tk()
root.title("OCR Notes Organizer")
root.geometry("750x520")
root.configure(bg="#f7f7f7")

title_label = tk.Label(root, text="📄 Image to Text - Notes Organizer", font=("Arial", 16, "bold"), bg="#f7f7f7")
title_label.pack(pady=10)

btn_frame = tk.Frame(root, bg="#f7f7f7")
btn_frame.pack(pady=5)

tk.Button(btn_frame, text="📷 Upload Image & Extract Text", command=upload_and_extract, font=("Arial", 11)).grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="💾 Save Note", command=save_note, font=("Arial", 11)).grid(row=0, column=1, padx=5)
tk.Button(btn_frame, text="🗑 Delete Note", command=delete_note, font=("Arial", 11)).grid(row=0, column=2, padx=5)
tk.Button(btn_frame, text="✏️ Rename Note", command=rename_note, font=("Arial", 11)).grid(row=0, column=3, padx=5)
tk.Button(btn_frame, text="📂 Choose Save Folder", command=choose_save_folder, font=("Arial", 11)).grid(row=0, column=4, padx=5)
tk.Button(btn_frame, text="✨ Summarize Note", command=summarize_note, font=("Arial", 11)).grid(row=0, column=5, padx=5)

search_entry = tk.Entry(root, font=("Arial", 11))
search_entry.pack(pady=5)
search_entry.insert(0, "Search notes...")
search_entry.bind("<KeyRelease>", search_notes)

notes_label = tk.Label(root, text="📂 Saved Notes", font=("Arial", 12, "bold"), bg="#f7f7f7")
notes_label.pack()

notes_list = tk.Listbox(root, height=9, width=50, font=("Arial", 10))
notes_list.pack()
notes_list.bind("<<ListboxSelect>>", load_note)

text_box = tk.Text(root, wrap="word", height=12, font=("Arial", 11))
text_box.pack(padx=10, pady=10, fill="both", expand=True)

load_notes()
root.mainloop()
