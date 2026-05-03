import tkinter as tk
from tkinter import messagebox
import random
import json
import os

# --- НАЧАЛЬНЫЕ ДАННЫЕ ---
# Список предопределенных задач. Каждая задача — это словарь.
PREDEFINED_TASKS = [
    {"name": "Решить задачу", "category": "учёба"},
    {"name": "Выполнить упражнения", "category": "спорт"},
    {"name": "Составить план", "category": "работа"},
    {"name": "Написать ЭССЕ", "category": "учёба"},
    {"name": "Написать отчет по выполненной работе", "category": "работа"},
]

# Имя файла для сохранения истории
HISTORY_FILE = "tasks.json"


class TaskGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Task Generator")
        self.root.geometry("450x500")
        self.root.resizable(False, False)

        # Загружаем историю из файла при запуске
        self.history = self.load_history()

        # --- ВИДЖЕТЫ ИНТЕРФЕЙСА (с новыми цветами и шрифтами) ---

        # Текущая задача
        self.task_label = tk.Label(
            root,
            text="Ваша задача:",
            font=("Helvetica", 16, "bold"),
            fg="#2c3e50",  # тёмно‑синий цвет текста
            bg="#ecf0f1"  # светло‑серый фон
        )
        self.task_label.pack(pady=15)

        self.task_display = tk.Label(
            root,
            text="",
            font=("Georgia", 18, "italic"),
            fg="#e74c3c",  # красный цвет текста
            bg="#ffffff",  # белый фон
            wraplength=380,
            relief="solid",
            borderwidth=2,
            padx=10,
            pady=8
        )
        self.task_display.pack(pady=10)

        # Кнопка генерации
        self.generate_btn = tk.Button(
            root,
            text="Сгенерировать задачу",
            font=("Arial", 14, "bold"),
            bg="#3498db",  # синий цвет фона
            fg="white",  # белый цвет текста
            activebackground="#2980b9",  # цвет при нажатии
            activeforeground="white",
            relief="raised",
            borderwidth=3,
            padx=20,
            pady=8,
            command=self.generate_task
        )
        self.generate_btn.pack(pady=15)

        # Фильтр по категории
        filter_frame = tk.Frame(root, bg="#d5dbdb")
        filter_frame.pack(pady=12, fill=tk.X, padx=20)

        tk.Label(
            filter_frame,
            text="Фильтр по типу:",
            font=("Arial", 12),
            bg="#d5dbdb",
            fg="#2c3e50"
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.category_var = tk.StringVar(value="все")
        categories = ["все"] + sorted(list({task["category"] for task in PREDEFINED_TASKS}))

        self.category_menu = tk.OptionMenu(
            filter_frame, self.category_var, *categories,
            command=self.filter_history
        )
        self.category_menu.config(
            font=("Arial", 11),
            bg="#f8f9fa",
            fg="#2c3e50",
            width=12
        )
        self.category_menu.pack(side=tk.LEFT, padx=5)

        # История задач
        history_frame = tk.Frame(root)
        history_frame.pack(pady=15, fill=tk.BOTH, expand=True, padx=20)

        self.history_label = tk.Label(
            history_frame,
            text="История:",
            font=("Arial", 14, "bold"),
            fg="#2c3e50"
        )
        self.history_label.pack(anchor="w", pady=(0, 5))

        self.history_listbox = tk.Listbox(
            history_frame,
            width=50,
            height=10,
            font=("Consolas", 11),
            bg="#2c3e50",  # тёмно‑синий фон
            fg="#ecf0f1",  # светло‑серый текст
            selectbackground="#3498db",
            selectforeground="white",
            relief="flat"
        )
        self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(history_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.history_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.history_listbox.yview)

        # Добавление новой задачи
        add_frame = tk.Frame(root, bg="#ecf0f1")
        add_frame.pack(pady=15, fill=tk.X, padx=20)

        self.new_task_entry = tk.Entry(
            add_frame,
            width=30,
            font=("Arial", 12),
            bg="white",
            fg="#2c3e50",
            relief="solid",
            borderwidth=2
        )
        self.new_task_entry.pack(side=tk.LEFT, padx=8, pady=5)

        self.category_new_var = tk.StringVar(value="другое")
        self.category_new_menu = tk.OptionMenu(
            add_frame, self.category_new_var, "другое", "учёба", "спорт", "работа"
        )
        self.category_new_menu.config(
            font=("Arial", 11),
            bg="#f8f9fa",
            fg="#2c3e50",
            width=10
        )
        self.category_new_menu.pack(side=tk.LEFT, padx=8, pady=5)

        self.add_task_btn = tk.Button(
            add_frame,
            text="Добавить задачу",
            font=("Arial", 12, "bold"),
            bg="#27ae60",  # зелёный цвет фона
            fg="white",
            activebackground="#219a52",
            activeforeground="white",
            relief="raised",
            borderwidth=2,
            padx=15,
            pady=5,
            command=self.add_task
        )
        self.add_task_btn.pack(side=tk.LEFT, padx=8, pady=5)

    # --- ЛОГИКА ПРИЛОЖЕНИЯ ---

    def generate_task(self):
        """Генерирует случайную задачу из предопределенного списка."""
        if not PREDEFINED_TASKS:
            messagebox.showwarning("Нет задач", "Список предопределенных задач пуст. Добавьте новые задачи.")
            return

        task = random.choice(PREDEFINED_TASKS)

        # Добавляем в историю (копируем словарь, чтобы не было ссылок)
        self.history.append(task.copy())

        # Сохраняем историю на диск
        self.save_history()

        # Обновляем отображение истории и текущей задачи
        self.update_history_display()
        self.task_display.config(text=task["name"])

    def add_task(self):
        """Добавляет новую задачу в список предопределенных."""
        name = self.new_task_entry.get().strip()

        # Проверка на пустую строку (валидация ввода)
        if not name:
            messagebox.showerror("Ошибка ввода", "Поле задачи не может быть пустым.")
            return

        category = self.category_new_var.get()

        # Добавляем в список и в историю сразу (как будто она была сгенерирована)
        new_task = {"name": name, "category": category}

        PREDEFINED_TASKS.append(new_task.copy())

        # Очищаем поле ввода
        self.new_task_entry.delete(0, tk.END)

        # Добавляем в историю и сохраняем
        self.history.append(new_task.copy())
        self.save_history()

        # Обновляем интерфейс
        self.update_history_display()

    def filter_history(self, value):
        """Фильтрует отображение истории по выбранной категории."""
        self.update_history_display(category=value)

    def update_history_display(self, category=None):
        """Обновляет виджет Listbox с историей задач."""
        self.history_listbox.delete(0, tk.END)

        for task in self.history:
            # Если фильтр не задан или категория совпадает с фильтром
            if category is None or category == "все" or task["category"] == category:
                display_text = f"{task['name']} ({task['category']})"
                self.history_listbox.insert(tk.END, display_text)

    def save_history(self):
        """Сохраняет историю задач в файл JSON."""
        try:
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить историю: {e}")

    def load_history(self):
        """Загружает историю задач из файла JSON."""
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                messagebox.showerror("Ошибка загрузки", f"Не удалось загрузить историю: {e}")
                return []
        return []


if __name__ == "__main__":
    root = tk.Tk()
    app = TaskGeneratorApp(root)
    root.mainloop()
