import model
import view
from tkinter import (
    Tk, Menu, LabelFrame, filedialog, messagebox, colorchooser, font,
    Text, Scrollbar, StringVar, END, INSERT, WORD
)
from _tkinter import TclError
from typing import Optional

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
        x = 10
        y = 38
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
        x = 120
        y = 38
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
        x = 230
        y = 38
        view.create_label(master=settings_frame, text="Отмена:", x=x, y=y)
        view.create_button(master=settings_frame, text="↺", 
                           command=lambda: self.undo_action(),
                           x=x, y=y + 22, height=25, width=25)
        view.create_button(master=settings_frame, text="↻", 
                           command=lambda: self.redo_action(),
                           x=x + 30, y=y + 22, height=25, width=25)

        # Блок страниц
        x = 330
        y = 65
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
        x = 330
        y = 10
        view.create_button(master=settings_frame, text="Цвет текста", 
                           command=lambda: self.choose_text_color(),
                           x=x, y=y, height=20, width=80)
        self.text_color = view.get_frame(master=settings_frame, bg="#000000", 
                                         x=x + 90, y=y, width=20, height=20)
        x = 330
        y = 35
        view.create_button(master=settings_frame, text="Цвет фона", 
                           command=lambda: self.choose_background_color(),
                           x=x, y=y, height=20, width=80)
        self.background_color = view.get_frame(master=settings_frame, bg="#ffffff", 
                                               x=x + 90, y=y, width=20, height=20)

        # Окно статистики
        info_frame: LabelFrame = LabelFrame(master=self.window, text="Параметры текста")
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
            self.pages = model.check_and_open_file(file_path)
            self.page_num.config(from_=1, to=len(self.pages))
            page_num = int(self.page_num.get()) - 1
            self.text.delete(1.0, END)
            self.curr_file = file_path
            self.update_window_title(file_path.split("/")[-1])
            self.text.insert(INSERT, self.pages[page_num])
            self.update_statistics()
        except FileNotFoundError as e:
            if str(e) == "":
                return
            elif str(e) == "Неверный формат файла":
                messagebox.showerror("Неверный формат файла", "Откройте файл с расширением .txt")
            else:
                print("Что-то пошло не так")
                return

    def save_file(self) -> None:
        """Сохранение текущего файла. Если файл новый, вызывает метод сохранения под новым именем."""
        if self.curr_file is None:
            self.save_file_as()
            return
        model.save_file(self.curr_file, self.text.get(1.0, END))

    def save_file_as(self) -> None:
        """Сохранение файла под новым именем, запрашивая путь у пользователя."""
        file_path = filedialog.asksaveasfilename()
        if file_path == "":
            return
        self.curr_file = file_path
        self.update_window_title(file_path.split("/")[-1])
        model.save_file(self.curr_file, self.text.get(1.0, END))

    def delete_file(self) -> None:
        """Удаление текущего файла и сброс текстового поля."""
        if self.curr_file is None:
            messagebox.showerror("Ошибка файла", "Файла не существует")
            return
        model.delete_file(self.curr_file)
        self.curr_file = None
        self.text.delete(1.0, END)
        self.update_window_title()
        self.page_num.config(from_=0, to=0)

    def update_window_title(self, new_name: Optional[str] = None) -> None:
        """Обновление заголовка окна с именем файла или базовым названием."""
        if new_name is None:
            self.window.title("2M NotePad")
        else:
            self.window.title(f"2M NotePad ― {new_name}")

    def change_page(self) -> None:
        """Изменение текущей страницы текста и обновление интерфейса."""
        try:
            new_page_num = int(self.page_num.get()) - 1
        except ValueError:
            return
        self.text.delete(1.0, END)
        self.change_alignment(self.global_tags["align"])
        self.text.insert(INSERT, self.pages[new_page_num])
        self.update_statistics()
        self.reset_find_text()

    def change_alignment(self, alignment: str) -> None:
        """Изменение выравнивания текста в соответствии с выбранным стилем."""
        self.text.tag_configure("align", justify=alignment)
        self.text.insert(1.0, " ")
        self.text.tag_add("align", "1.0", "end")
        self.global_tags["align"] = alignment

    def update_statistics(self) -> None:
        """Обновление статистики текста: количество страниц, строк и символов."""
        page_count = max(len(self.pages), 1)
        lines_count = self.text.count("0.0", "end", "displaylines")[0]
        letters_count = len(self.text.get(1.0, END))
        self.update_entry(self.pages_counter, page_count)
        self.update_entry(self.lines_counter, lines_count)
        self.update_entry(self.letters_counter, letters_count)

    @staticmethod
    def update_entry(entry, count: int, block: bool = True) -> None:
        """Обновление поля ввода с заданным значением и опциональной блокировкой."""
        entry.config(state="normal")
        entry.delete(0, END)
        entry.insert(0, count)
        if block:
            entry.config(state="readonly")

    def find_text(self) -> None:
        """Поиск и выделение всех вхождений текста, введенного пользователем."""
        self.clear_highlighted_text()
        prev_pos = "1.0"
        count = StringVar()
        str_find = self.finder.get()
        if str_find == "":
            return
        counter = 0
        self.global_tags["finder"] += 1
        finder_tag_version = self.global_tags["finder"]
        while True:
            new_pos = self.text.search(str_find, prev_pos, stopindex="end", count=count)
            if new_pos == "":
                break
            self.text.tag_configure(f"search{finder_tag_version}", background="#00FA9A")
            self.text.tag_add(f"search{finder_tag_version}", new_pos, f"{new_pos} + {count.get()}c")
            prev_pos = model.shift_pos(new_pos, count.get())
            counter += 1
        self.update_entry(self.word_counter, counter)

    def reset_find_text(self) -> None:
        """Сброс выделения найденного текста и очистка поля ввода поиска."""
        self.update_entry(self.word_counter, "")
        self.update_entry(self.finder, "", block=False)
        self.clear_highlighted_text()
        self.global_tags['finder'] = 0

    def clear_highlighted_text(self) -> None:
        """Очистка подсветки выделенного текста."""
        self.text.tag_configure(f"search{self.global_tags['finder']}", background="#ffffff")

    def stylize_text(self, underline: bool = False, style: str = NORMAL, font_type: str = "", font_size: str = "") -> None:
        """Применение стиля к выделенному тексту."""
        if font_type == "":
            font_type = self.font_type.get()
        if font_size == "":
            font_size = self.font_size.get()
        tag_name = self.global_tags["format"] + 1
        self.text.tag_config(tag_name, font=(font_type, font_size, style), underline=underline)
        self.text.tag_add(tag_name, "sel.first", "sel.last")
        self.global_tags["format"] += 1

    def get_font_style(self, style: str = NORMAL, font_type: str = "", font_size: str = "") -> tuple[str, str, str]:
        """Получение текущего стиля шрифта для текста."""
        if font_type == "":
            font_type = self.font_type.get()
        if font_size == "":
            font_size = self.font_size.get()
        return font_type, font_size, style

    def undo_action(self) -> None:
        """Отмена последнего действия пользователя."""
        try:
            self.text.edit_undo()
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
