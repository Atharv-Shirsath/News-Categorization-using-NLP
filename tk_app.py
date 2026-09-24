from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import webbrowser

window = Tk()
window.title("News")
window.geometry("300x120")  # was 50x50 — too small to fit the buttons below

CATEGORY_COLORS = {
    "Business & Economy": "#dbeafe",
    "Crime & Law/Judiciary": "#fecaca",
    "Defence & Security": "#e5e7eb",
    "Education & Recruitment": "#fef9c3",
    "Entertainment & Lifestyle": "#fce7f3",
    "Health": "#dcfce7",
    "International/World": "#e0e7ff",
    "Other": "#f3f4f6",
    "Politics & Government": "#fde68a",
    "Society, Religion & Culture": "#ede9fe",
    "Sports": "#bbf7d0",
    "Weather & Disaster": "#bae6fd",
}


def click():
    try:
        import newschori
    except Exception as e:
        messagebox.showerror("Error", f"failed to load news:\n{e}")
        return

    if not newschori.l:
        messagebox.showwarning("No Data", "No news found.")
        return

    wn = Toplevel()
    wn.title("Categorized News")
    wn.geometry("900x500")
    wn.grid_rowconfigure(1, weight=1)
    wn.grid_columnconfigure(0, weight=1)

    # --- category filter row ---
    filter_frame = Frame(wn)
    filter_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))

    Label(filter_frame, text="Category:").pack(side=LEFT, padx=(0, 6))

    categories = sorted({item.get("category", "Other") for item in newschori.l})
    filter_var = StringVar(value="All")
    filter_box = ttk.Combobox(
        filter_frame, textvariable=filter_var, values=["All"] + categories,
        state="readonly", width=30
    )
    filter_box.pack(side=LEFT)

    # --- table ---
    columns = ("heading", "category", "link")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", font=("Arial", 12), rowheight=28)
    style.configure("Treeview.Heading", font=("Arial", 12, "bold"))

    tree = ttk.Treeview(wn, columns=columns, show="headings", height=15)
    tree.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

    tree.heading("heading", text="Heading")
    tree.heading("category", text="Category")
    tree.heading("link", text="Link")

    tree.column("heading", width=480)
    tree.column("category", width=180)
    tree.column("link", width=200)

    for cat, color in CATEGORY_COLORS.items():
        tree.tag_configure(cat, background=color)

    def populate(filter_category="All"):
        tree.delete(*tree.get_children())
        items = sorted(
            newschori.l, key=lambda x: x["title"].lstrip("'\"‘’“”").lower()
        )
        for item in items:
            cat = item.get("category", "Other")
            if filter_category != "All" and cat != filter_category:
                continue
            tree.insert(
                "", END,
                values=(item["title"], cat, item["link"]),
                tags=(cat,),
            )

    def on_filter_change(event=None):
        populate(filter_var.get())

    filter_box.bind("<<ComboboxSelected>>", on_filter_change)

    def open_link(event):
        try:
            selected = tree.focus()
            values = tree.item(selected, "values")

            if values:
                link = values[2]

                if link.startswith("./"):
                    link = "https://news.google.com/" + link[2:]

                webbrowser.open(link)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open link:\n{e}")

    tree.bind("<Double-1>", open_link)

    populate("All")


def txt():
    try:
        import newschori
    except Exception as e:
        messagebox.showerror("Error", f"failed to load news:\n{e}")
        return

    if not newschori.l:
        messagebox.showwarning("No Data", "No news found.")
        return

    items = sorted(newschori.l, key=lambda x: x["title"].lstrip("'\"‘’“”").lower())

    with open("News.txt", "w", encoding="utf-8") as file:
        for news in items:
            title = news.get("title", "")
            category = news.get("category", "Other")
            file.write(f"[{category}] {title}\n")

    messagebox.showinfo("Saved", "Saved to News.txt")


button = Button(window, text="Get NEWS")
button.config(command=click)
button.config(width=30)
button.pack(pady=(15, 5))

button1 = Button(window, text="Get in txt")
button1.config(command=txt)
button1.config(width=30)
button1.pack(pady=5)

window.mainloop()
