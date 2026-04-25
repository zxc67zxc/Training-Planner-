import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class TrainingPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Training Planner")
        self.root.geometry("800x600")

        # Данные тренировок
        self.trainings = []
        self.load_data()

        self.setup_ui()

    def setup_ui(self):
        # Фрейм для формы добавления
        form_frame = ttk.LabelFrame(self.root, text="Добавить тренировку")
        form_frame.pack(padx=10, pady=10, fill="x")

        # Поле даты
        ttk.Label(form_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.date_entry = ttk.Entry(form_frame, width=20)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)

        # Поле типа тренировки
        ttk.Label(form_frame, text="Тип тренировки:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.type_entry = ttk.Entry(form_frame, width=20)
        self.type_entry.grid(row=1, column=1, padx=5, pady=5)

        # Поле длительности
        ttk.Label(form_frame, text="Длительность (мин):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.duration_entry = ttk.Entry(form_frame, width=20)
        self.duration_entry.grid(row=2, column=1, padx=5, pady=5)

        # Кнопка добавления
        ttk.Button(form_frame, text="Добавить тренировку", command=self.add_training).grid(
            row=3, column=0, columnspan=2, pady=10
        )

        # Фрейм для фильтров
        filter_frame = ttk.LabelFrame(self.root, text="Фильтры")
        filter_frame.pack(padx=10, pady=5, fill="x")

        # Фильтр по типу
        ttk.Label(filter_frame, text="Тип:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.type_filter = ttk.Combobox(filter_frame, state="readonly")
        self.type_filter.grid(row=0, column=1, padx=5, pady=5)
        self.type_filter.bind("<<ComboboxSelected>>", self.apply_filters)

        # Фильтр по дате
        ttk.Label(filter_frame, text="Дата:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.date_filter = ttk.Entry(filter_frame, width=15)
        self.date_filter.grid(row=0, column=3, padx=5, pady=5)
        self.date_filter.bind("<KeyRelease>", self.apply_filters)

        # Кнопка сброса фильтров
        ttk.Button(filter_frame, text="Сбросить фильтры", command=self.reset_filters).grid(
            row=0, column=4, padx=5, pady=5
        )

        # Таблица тренировок
        columns = ("Дата", "Тип", "Длительность (мин)")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=15)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)

        self.tree.pack(padx=10, pady=10, fill="both", expand=True)

        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.update_table()
        self.update_filter_options()

    def validate_date(self, date_str):
        """Проверка формата даты ГГГГ-ММ-ДД"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def add_training(self):
        """Добавление новой тренировки"""
        date = self.date_entry.get().strip()
        training_type = self.type_entry.get().strip()
        duration_str = self.duration_entry.get().strip()

        # Проверка корректности ввода
        if not date:
            messagebox.showerror("Ошибка", "Введите дату!")
            return

        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ГГГГ-ММ-ДД")
            return

        if not training_type:
            messagebox.showerror("Ошибка", "Введите тип тренировки!")
            return

        try:
            duration = int(duration_str)
            if duration <= 0:
                messagebox.showerror("Ошибка", "Длительность должна быть положительным числом!")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Длительность должна быть числом!")
            return

        # Добавление в список
        training = {
            "date": date,
            "type": training_type,
            "duration": duration
        }
        self.trainings.append(training)

        # Очистка полей ввода
        self.date_entry.delete(0, tk.END)
        self.type_entry.delete(0, tk.END)
        self.duration_entry.delete(0, tk.END)

        # Обновление интерфейса
        self.save_data()
        self.update_table()
        self.update_filter_options()

        messagebox.showinfo("Успех", "Тренировка добавлена!")

    def update_table(self, filtered_trainings=None):
        """Обновление таблицы тренировок"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Используем отфильтрованные данные или все
        data = filtered_trainings if filtered_trainings else self.trainings

        # Заполнение таблицы
        for training in data:
            self.tree.insert("", "end", values=(
                training["date"],
                training["type"],
                training["duration"]
            ))

    def apply_filters(self, event=None):
        """Применение фильтров"""
        selected_type = self.type_filter.get()
        date_filter = self.date_filter.get().strip()

        filtered = self.trainings

        # Фильтрация по типу
        if selected_type and selected_type != "Все":
            filtered = [t for t in filtered if t["type"] == selected_type]

        # Фильтрация по дате
        if date_filter:
            filtered = [t for t in filtered if date_filter in t["date"]]

        self.update_table(filtered)

    def reset_filters(self):
        """Сброс фильтров"""
        self.type_filter.set("")
        self.date_filter.delete(0, tk.END)
        self.update_table()

    def update_filter_options(self):
        """Обновление опций фильтров"""
        types = list(set(t["type"] for t in self.trainings))
        self.type_filter["values"] = ["Все"] + types

    def save_data(self):
        """Сохранение данных в JSON"""
        with open("trainings.json", "w", encoding="utf-8") as f:
            json.dump(self.trainings, f, ensure_ascii=False, indent=2)

    def load_data(self):
        """Загрузка данных из JSON"""
        if os.path.exists("trainings.json"):
            with open("trainings.json", "r", encoding="utf-8") as f:
                self.trainings =
