import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import json
import tempfile
from filters import filter_by_genre, filter_by_pages
from storage import save_books, load_books

class TestBookTracker(unittest.TestCase):
    
    def setUp(self):
        self.test_books = [
            {"title": "Война и мир", "author": "Толстой", "genre": "Роман", "pages": 1300},
            {"title": "Преступление и наказание", "author": "Достоевский", "genre": "Роман", "pages": 600},
            {"title": "Мастер и Маргарита", "author": "Булгаков", "genre": "Роман", "pages": 400},
            {"title": "1984", "author": "Оруэлл", "genre": "Фантастика", "pages": 300},
            {"title": "Три товарища", "author": "Ремарк", "genre": "Роман", "pages": 450}
        ]

    def test_filter_by_genre_roman(self):
        result = filter_by_genre(self.test_books, "роман")
        self.assertEqual(len(result), 4)
        for book in result:
            self.assertEqual(book["genre"], "Роман")

    def test_filter_by_genre_fantastika(self):
        result = filter_by_genre(self.test_books, "фантастика")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["title"], "1984")

    def test_filter_by_genre_not_found(self):
        result = filter_by_genre(self.test_books, "детектив")
        self.assertEqual(len(result), 0)

    def test_filter_by_pages_more_500(self):
        result = filter_by_pages(self.test_books, 500)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["title"], "Война и мир")
        self.assertEqual(result[1]["title"], "Преступление и наказание")

    def test_filter_by_pages_more_1000(self):
        result = filter_by_pages(self.test_books, 1000)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["title"], "Война и мир")

    def test_filter_by_pages_more_0(self):
        result = filter_by_pages(self.test_books, 0)
        self.assertEqual(len(result), 5)

    def test_filter_by_pages_more_5000(self):
        result = filter_by_pages(self.test_books, 5000)
        self.assertEqual(len(result), 0)

    def test_save_and_load_books(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            tmp_name = tmp.name
        
        original_storage_file = storage.DATA_FILE
        storage.DATA_FILE = tmp_name
        
        try:
            save_books(self.test_books)
            loaded_books = load_books()
            self.assertEqual(len(loaded_books), 5)
            self.assertEqual(loaded_books[0]["title"], "Война и мир")
            self.assertEqual(loaded_books[1]["author"], "Достоевский")
        finally:
            storage.DATA_FILE = original_storage_file
            if os.path.exists(tmp_name):
                os.remove(tmp_name)

    def test_empty_books_save(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            tmp_name = tmp.name
        
        original_storage_file = storage.DATA_FILE
        storage.DATA_FILE = tmp_name
        
        try:
            save_books([])
            loaded_books = load_books()
            self.assertEqual(len(loaded_books), 0)
        finally:
            storage.DATA_FILE = original_storage_file
            if os.path.exists(tmp_name):
                os.remove(tmp_name)

    def test_genre_filter_case_insensitive(self):
        result = filter_by_genre(self.test_books, "РОМАН")
        self.assertEqual(len(result), 4)
        
        result2 = filter_by_genre(self.test_books, "роман")
        self.assertEqual(len(result2), 4)

    def test_pages_filter_integer_only(self):
        result = filter_by_pages(self.test_books, 400)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["title"], "Война и мир")
        self.assertEqual(result[1]["title"], "Преступление и наказание")

    def test_combined_filters(self):
        genre_filtered = filter_by_genre(self.test_books, "роман")
        final_filtered = filter_by_pages(genre_filtered, 500)
        self.assertEqual(len(final_filtered), 2)
        self.assertEqual(final_filtered[0]["title"], "Война и мир")
        self.assertEqual(final_filtered[1]["title"], "Преступление и наказание")

def run_tests():
    unittest.main(argv=[''], verbosity=2, exit=False)

if __name__ == "__main__":
    print("=" * 50)
    print("Запуск тестов Book Tracker")
    print("=" * 50)
    run_tests()
    print("=" * 50)
    print("Тесты завершены")
