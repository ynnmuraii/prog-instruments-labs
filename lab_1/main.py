from tkinter import Tk, Menu, LabelFrame, filedialog, messagebox, colorchooser, font, Text, Scrollbar, StringVar, END, INSERT, WORD
from _tkinter import TclError
from typing import Optional, Tuple
import model
import view

# Константы для конфигурации окна и виджетов
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FONT_LIST = ["arial", "arial black", "calibri", "comic sans ms", "courier new", "times new roman"]

class Window:
    def __init__(self) -> None:
        """Инициализация рабочего окна и настройка интерфейса."""
        self.window: Tk = Tk()
        self.window.title("2M NotePad")
        view.config_window(self.window, WINDOW_WIDTH, WINDOW_HEIGHT)

        # Глобальные значения редактора
        self.curr_file: Optional[str] = None
        self.pages: list[str] = []
        self.global_tags: dict[str, int | str] = {"align": "left", "finder": 0, "format": 0}

        # Создание меню
        self.main_menu: Menu = Menu(master=self.window)
        view.config_main_menu(self.window, self.main_menu)
        self.file_menu: Menu = Menu(master=self.main_menu, tearoff=0)
        view.config_file_menu(
            self.file_menu, self.main_menu,
            {"Открыть": self.open_file, "Сохранить": self.save_file,
             "Сохранить как": self.save_file_as, "Удалить": self.delete_file}
        )

        # Окно настроек
        settings_frame: LabelFrame = LabelFrame(master=self.window, text="Настройки текста")
        view.place_obj(settings_frame, x=10, y=10, 
                       height=WINDOW_HEIGHT / 6 + 10, width=WINDOW_WIDTH - 340)

        # Блок форматирования
        x, y = 10, 38
        view.create_label(master=settings_frame, text="Шрифт:", x=x, y=y)
        view.create_button(master=settings_frame, text="B", 
                           command=lambda: self.stylize_text(style=font.BOLD),
                           x=x, y=y + 22, height=25, width=25)
        view.create_button(master=settings_frame, text="I", 
                           command=lambda: self.stylize_text(style=font.ITALIC),
                           x=x + 30, y=y + 22, height=25, width=25)
        view.create_button(master=settings_frame, text="U", 
                           command=lambda: self.stylize_text(underline=True),
                           x=x + 60, y=y + 22, height=25, width=25)
        
        # Блок выравнивания
        x, y = 120, 38
        view.create_label(master=settings_frame, text="Выравнивание:", x=x, y=y)
        view.create_button(master=settings_frame, text="L", 
                           command=lambda: self.change_alignment("left"),
                           x=x, y=y + 22, height=25, width=25)
        view.create_button(master=settings_frame, text="C", 
                           command=lambda: self.change_alignment("center"),
                           x=x + 30, y=y + 22, height=25, width=25)
        view.create_button(master=settings_frame, text="R", 
                           command=lambda: self.change_alignment("right"),
                           x=x + 60, y=y + 22, height=25, width=25)

        # Блок undo/redo
        x, y = 230, 38
        view.create_label(master=settings_frame, text="Отмена:", x=x, y=y)
        view.create_button(master=settings_frame, text="↺", 
                           command=lambda: self.undo_action(),
                           x=x, y=y + 22, height=25, width=25)
        view.create_button(master=settings_frame, text="↻", 
                           command=lambda: self.redo_action(),
                           x=x + 30, y=y + 22, height=25, width=25)

        # Блок страниц
        x, y = 330, 65
        view.create_label(master=settings_frame, text="Страница", x=x, y=y)
        self.page_num = view.get_spinbox(x=x + 80, y=y, width=30,
                                         master=settings_frame, from_=0, to=0,
                                         state="readonly", 
                                         command=self.change_page)
        
        # Блок шрифта
        self.font_type = view.get_combobox(
            master=settings_frame, values=FONT_LIST, state="readonly", x=10, y=10, current=2
        )
        self.font_size = view.get_combobox(
            master=settings_frame, values=list(range(10, 61, 4)), 
            x=160, y=10, width=40, current=3, state="readonly"
        )
        view.create_button(master=settings_frame, text="Применить",
                           command=lambda: self.text.config(font=self.get_font_style()),
                           x=210, y=10, height=20, width=80)

        # Блок цветов
        x, y = 330, 10
        view.create_button(master=settings_frame, text="Цвет текста", 
                           command=lambda: self.choose_text_color(),
                           x=x, y=y, height=20, width=80)
        self.text_color = view.get_frame(master=settings_frame, bg="#000000", 
                                         x=x + 90, y=y, width=20, height=20)
        x, y = 330, 35
        view.create_button(master=settings_frame, text="Цвет фона", 
                           command=lambda: self.choose_background_color(),
                           x=x, y=y, height=20, width=80)
        self.background_color = view.get_frame(master=settings_frame, bg="#ffffff", 
                                               x=x + 90, y=y, width=20, height=20)

        # Окно статистики
        info_frame = LabelFrame(master=self.window, text="Параметры текста")
        view.place_obj(info_frame, x=WINDOW_WIDTH - 320, y=10, 
                       height=WINDOW_HEIGHT / 6 + 10, width=310)
        view.create_button(master=info_frame, text="Обновить", 
                           command=lambda: self.update_statistics(),
                           x=35, y=67, height=20)
        view.create_label(master=info_frame, text="Страниц:", x=10, y=5)
        self.pages_counter = view.get_entry(master=info_frame, state="readonly", 
                                            x=75, y=5, width=50)
        view.create_label(master=info_frame, text="Строк:", x=10, y=25)
        self.lines_counter = view.get_entry(master=info_frame, state="readonly", 
                                            x=75, y=25, width=50)
        view.create_label(master=info_frame, text="Символов:", x=10, y=45)
        self.letters_counter = view.get_entry(master=info_frame, state="readonly", 
                                              x=75, y=45, width=50)
        self.finder = view.get_entry(master=info_frame, state="normal", x=160, y=10)
        view.create_button(master=info_frame, text="Найти все", 
                           command=lambda: self.find_text(),
                           x=150, y=40, height=20)
        view.create_button(master=info_frame, text="Сбросить", 
                           command=lambda: self.reset_find_text(),
                           x=230, y=40, height=20)
        view.create_label(master=info_frame, text="Нашлось слов: ", x=165, y=65)
        self.word_counter = view.get_entry(master=info_frame, x=255, y=67, 
                                           state="readonly", width=25)

        # Окно ввода текста
        self.text = Text(master=self.window, undo=True, font=self.get_font_style(), wrap=WORD)
        view.place_obj(self.text, x=10, y=WINDOW_HEIGHT / 5 + 10, 
                       height=WINDOW_HEIGHT * 4 / 5 - 40, width=WINDOW_WIDTH - 35)
        scroll_text_ver = Scrollbar(master=self.window, orient="vertical", command=self.text.yview)
        view.place_obj(scroll_text_ver, x=775, y=WINDOW_HEIGHT / 5 + 10, 
                       height=WINDOW_HEIGHT * 4 / 5 - 40)
        self.text["yscrollcommand"] = scroll_text_ver.set

        # Горячие клавиши
        view.create_bind(self.text, "<Control-o>", lambda _: self.open_file())
        view.create_bind(self.text, "<Control-s>", lambda _: self.save_file())
        view.create_bind(self.text, "<Control-d>", lambda _: self.delete_file())

        # Установка стартовых значений
        self.update_window_title()
        self.update_statistics()

    def show(self) -> None:
        """Запуск главного цикла интерфейса."""
        self.window.mainloop()

    def open_file(self) -> None:
        """Открытие файла и загрузка его содержимого в текстовое поле."""
        file_path = filedialog.askopenfilename()
        try:
            self.pages = model
        except TclError:
            pass

    def redo_action(self) -> None:
        """Повтор последнего отмененного действия."""
        try:
            self.text.edit_redo()
        except TclError:
            pass

    def choose_text_color(self) -> None:
        """Выбор и применение цвета текста."""
        (rgb, hx) = colorchooser.askcolor()
        self.text_color.config(bg=hx)
        self.text.config(fg=hx)

    def choose_background_color(self) -> None:
        """Выбор и применение цвета фона текста."""
        (rgb, hx) = colorchooser.askcolor()
        self.background_color.config(bg=hx)
        self.text.config(bg=hx)
