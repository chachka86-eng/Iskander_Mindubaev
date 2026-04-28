import json
import os
from tkinter import *
from tkinter import messagebox, ttk

DATA_FILE = "books.json"

class BookTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker - Трекер прочитанных книг")
        self.root.geometry("900x500")

        self.books = []
        self.load_data()

        input_frame = LabelFrame(root, text="Добавить книгу", padx=10, pady=10)
        input_frame.pack(pady=10, fill="x", padx=10)

        Label(input_frame, text="Название книги:").grid(row=0, column=0, sticky="w")
        self.title_entry = Entry(input_frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=5, pady=2)

        Label(input_frame, text="Автор:").grid(row=0, column=2, sticky="w")
        self.author_entry = Entry(input_frame, width=20)
        self.author_entry.grid(row=0, column=3, padx=5, pady=2)

        Label(input_frame, text="Жанр:").grid(row=0, column=4, sticky="w")
        self.genre_entry = Entry(input_frame, width=15)
        self.genre_entry.grid(row=0, column=5, padx=5, pady=2)

        Label(input_frame, text="Кол-во страниц:").grid(row=0, column=6, sticky="w")
        self.pages_entry = Entry(input_frame, width=8)
        self.pages_entry.grid(row=0, column=7, padx=5, pady=2)

        add_btn = Button(input_frame, text="Добавить книгу", command=self.add_book, bg="lightgreen")
        add_btn.grid(row=0, column=8, padx=10)

        filter_frame = LabelFrame(root, text="Фильтрация", padx=10, pady=5)
        filter_frame.pack(pady=5, fill="x", padx=10)

        Label(filter_frame, text="Фильтр по жанру:").grid(row=0, column=0, sticky="w")
        self.genre_filter = Entry(filter_frame, width=20)
        self.genre_filter.grid(row=0, column=1, padx=5)
        self.genre_filter.bind("<KeyRelease>", self.apply_filters)

        Label(filter_frame, text="Страниц >").grid(row=0, column=2, sticky="w", padx=(10, 0))
        self.pages_filter = Entry(filter_frame, width=8)
        self.pages_filter.grid(row=0, column=3, padx=5)
        self.pages_filter.bind("<KeyRelease>", self.apply_filters)

        self.genre_list = ttk.Combobox(filter_frame, values=[], width=15, state="readonly")
        self.genre_list.grid(row=0, column=4, padx=10)
        self.genre_list.bind("<<ComboboxSelected>>", self.on_genre_select)

        Button(filter_frame, text="Сбросить фильтры", command=self.reset_filters).grid(row=0, column=5, padx=10)

        columns = ("Название", "Автор", "Жанр", "Страницы")
        self.tree = ttk.Treeview(root, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

        btn_frame = Frame(root)
        btn_frame.pack(pady=5)
        Button(btn_frame, text="Сохранить в JSON", command=self.save_data).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Загрузить из JSON", command=self.load_data).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Удалить выбранную", command=self.delete_book, bg="salmon").pack(side=LEFT, padx=5)

        self.update_display()
        self.update_genre_list()

    def add_book(self):
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        genre = self.genre_entry.get().strip()
        pages = self.pages_entry.get().strip()

        if not title or not author or not genre or not pages:
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
            return
        try:
            pages = int(pages)
            if pages <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Количество страниц должно быть положительным числом!")
            return

        self.books.append({
            "title": title,
            "author": author,
            "genre": genre,
            "pages": pages
        })
        self.clear_entries()
        self.update_display()
        self.update_genre_list()
        self.save_data()

    def delete_book(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите книгу для удаления!")
            return
        item = self.tree.item(selected[0])
        values = item["values"]
        for book in self.books:
            if book["title"] == values[0] and book["author"] == values[1]:
                self.books.remove(book)
                break
        self.update_display()
        self.update_genre_list()
        self.save_data()

    def apply_filters(self, event=None):
        self.update_display()

    def reset_filters(self):
        self.genre_filter.delete(0, END)
        self.pages_filter.delete(0, END)
        self.genre_list.set("")
        self.update_display()

    def on_genre_select(self, event):
        self.genre_filter.delete(0, END)
        self.genre_filter.insert(0, self.genre_list.get())
        self.apply_filters()

    def update_genre_list(self):
        genres = sorted(set(book["genre"] for book in self.books))
        self.genre_list["values"] = genres

    def get_filtered_books(self):
        genre_filter = self.genre_filter.get().strip().lower()
        pages_filter = self.pages_filter.get().strip()

        filtered = self.books[:]
        if genre_filter:
            filtered = [b for b in filtered if genre_filter in b["genre"].lower()]
        if pages_filter:
            try:
                pages_limit = int(pages_filter)
                filtered = [b for b in filtered if b["pages"] > pages_limit]
            except ValueError:
                pass
        return filtered

    def update_display(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        filtered = self.get_filtered_books()
        for book in filtered:
            self.tree.insert("", END, values=(book["title"], book["author"], book["genre"], book["pages"]))

    def clear_entries(self):
        self.title_entry.delete(0, END)
        self.author_entry.delete(0, END)
        self.genre_entry.delete(0, END)
        self.pages_entry.delete(0, END)

    def save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.books, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Успех", f"Данные сохранены в {DATA_FILE}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def load_data(self):
        if not os.path.exists(DATA_FILE):
            return
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                self.books = json.load(f)
            self.update_display()
            self.update_genre_list()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить: {e}")

if __name__ == "__main__":
    root = Tk()
    app = BookTracker(root)
    root.mainloop()
