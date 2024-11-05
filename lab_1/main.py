from tkinter import Tk, Menu, LabelFrame, filedialog, messagebox, colorchooser, font, Text, Scrollbar, StringVar, END, INSERT, WORD
from _tkinter import TclError
import model
import view


FONTS = ["arial", "arial black", "calibri", "comic sans ms", "courier new", "times new roman"]

class Window:
    def __init__(self):
        """ Инициализация рабочего окна """

        """ Инициализация окна """
        self.window = Tk()
        self.window.title("2M NotePad")
        width = 800
        height = 600
        view.config_window(self.window, width, height)

        """ Глобальные значения редактора """
        self.curr_file = None
        self.pages = []
        self.global_tags = {"align": "left", "finder": 0, "format": 0}

        """ Cоздание меню """
        self.main_menu = Menu(master=self.window)
        view.config_main_menu(self.window, self.main_menu)
        self.file_menu = Menu(master=self.main_menu, tearoff=0)
        view.config_file_menu(self.file_menu, self.main_menu,
                              {"Открыть": self.open_file, "Сохранить": self.save_file,
                               "Сохранить как": self.save_file_as, "Удалить": self.delete_file})

        """ Окно настроек """
        settings_frame = LabelFrame(master=self.window, text="Настройки текста")
        view.place_obj(settings_frame, x=10, y=10, height=height / 6 + 10, width=width - 340)
        # блок форматирования
        x = 10
        y = 38
        view.create_label(master=settings_frame, text="Шрифт:", x=x, y=y)
        view.create_button(master=settings_frame, text="B", command=lambda: self.stylize_text(style=font.BOLD),
                           x=x, y=y + 22, height=25, width=25)
        view.create_button(master=settings_frame, text="I", command=lambda: self.stylize_text(style=font.ITALIC),
                           x=x + 30, y=y + 22, height=25, width=25)
        view.create_button(master=settings_frame, text="U", command=lambda: self.stylize_text(underline=True),
                           x=x + 60, y=y + 22, height=25, width=25)
        # блок выравнивания
        x = 120
        y = 38
        view.create_label(master=settings_frame, text="Выравнивание:", x=x, y=y)
        view.create_button(master=settings_frame, text="L", command=lambda: self.change_align("left"),
                           x=x, y=y + 22, height=25, width=25)
        view.create_button(master=settings_frame, text="C", command=lambda: self.change_align("center"),
                           x=x + 30, y=y + 22, height=25, width=25)
        view.create_button(master=settings_frame, text="R", command=lambda: self.change_align("right"),
                           x=x + 60, y=y + 22, height=25, width=25)
        # блок undo/redo
        x = 230
        y = 38
        view.create_label(master=settings_frame, text="Отмена:", x=x, y=y)
        view.create_button(master=settings_frame, text="↺", command=lambda: self.undo(),
                           x=x, y=y + 22, height=25, width=25)
        view.create_button(master=settings_frame, text="↻", command=lambda: self.redo(),
                           x=x + 30, y=y + 22, height=25, width=25)
        # блок страниц
        x = 330
        y = 65
        view.create_label(master=settings_frame, text="Страница", x=x, y=y)
        self.page_num = view.get_spinbox(x=x + 80, y=y, width=30,
                                         master=settings_frame, from_=0, to=0,
                                         state="readonly", command=self.change_page)
        # блок шрифта
        self.font_type = view.get_combobox(master=settings_frame,
                                           values=FONTS, state="readonly",
                                           x=10, y=10, current=2)
        self.font_size = view.get_combobox(master=settings_frame, values=list(range(10, 61, 4)),
                                           x=160, y=10, width=40, current=3, state="readonly",)
        view.create_button(master=settings_frame, text="Применить",
                           command=lambda: self.text.config(font=self.get_font()),
                           x=210, y=10, height=20, width=80)
        # блок цветов
        x = 330
        y = 10
        view.create_button(master=settings_frame, text="Цвет текста", command=lambda: self.choose_text_color(),
                           x=x, y=y, height=20, width=80)
        self.text_color = view.get_frame(master=settings_frame, bg="#000000", x=x + 90, y=y, width=20, height=20)
        x = 330
        y = 35
        view.create_button(master=settings_frame, text="Цвет фона", command=lambda: self.choose_back_color(),
                           x=x, y=y, height=20, width=80)
        self.back_color = view.get_frame(master=settings_frame, bg="#ffffff", x=x + 90, y=y, width=20, height=20)

        """ Окно статистики """
        info_frame = LabelFrame(master=self.window, text="Параметры текста")
        view.place_obj(info_frame, x=width - 320, y=10, height=height / 6 + 10, width=310)
        view.create_button(master=info_frame, text="Обновить", command=lambda: self.update_stat(),
                           x=35, y=67, height=20)
        view.create_label(master=info_frame, text="Страниц:", x=10, y=5)
        self.pages_counter = view.get_entry(master=info_frame, state="readonly", x=75, y=5, width=50)
        view.create_label(master=info_frame, text="Строк:", x=10, y=25)
        self.lines_counter = view.get_entry(master=info_frame, state="readonly", x=75, y=25, width=50)
        view.create_label(master=info_frame, text="Символов:", x=10, y=45)
        self.letters_counter = view.get_entry(master=info_frame, state="readonly", x=75, y=45, width=50)
        self.finder = view.get_entry(master=info_frame, state="normal", x=160, y=10)
        view.create_button(master=info_frame, text="Найти все", command=lambda: self.find_text(),
                           x=150, y=40, height=20)
        view.create_button(master=info_frame, text="Сбросить", command=lambda: self.clean_find_text(),
                           x=230, y=40, height=20)
        view.create_label(master=info_frame, text="Нашлось слов: ", x=165, y=65)
        self.world_counter = view.get_entry(master=info_frame, x=255, y=67, state="readonly", width=25)

        """ Окно ввода текста """
        self.text = Text(master=self.window, undo=True, font=self.get_font(), wrap=WORD)
        view.place_obj(self.text, x=10, y=height / 5 + 10, height=height * 4 / 5 - 40, width=width - 35)
        scroll_text_ver = Scrollbar(master=self.window, orient="vertical", command=self.text.yview)
        view.place_obj(scroll_text_ver, x=775, y=height / 5 + 10, height=height * 4 / 5 - 40)
        self.text["yscrollcommand"] = scroll_text_ver.set

        """ Горячие клавиши """
        view.create_bind(self.text, "<Control-o>", lambda _: self.open_file())
        view.create_bind(self.text, "<Control-s>", lambda _: self.save_file())
        view.create_bind(self.text, "<Control-d>", lambda _: self.delete_file())

        """ Установка стартовых значений """
        self.change_file_name()
        self.update_stat()

    def show(self):
        self.window.mainloop()

    def open_file(self):
        file_path = filedialog.askopenfilename()
        try:
            self.pages = model.check_and_open_file(file_path)
            self.page_num.config(from_=1, to=len(self.pages))
            page_numb = int(self.page_num.get()) - 1
            self.text.delete(1.0, END)
            self.curr_file = file_path
            self.change_file_name(file_path.split("/")[-1])
            self.text.insert(INSERT, self.pages[page_numb])
            self.update_stat()
        except FileNotFoundError as e:
            if str(e) == "":
                return
            elif str(e) == "Неверный формат файла":
                messagebox.showerror("Неверный формат файла", "Откройте файл с расширением .txt")
            else:
                print("Что-то пошло не так")
                return

    def save_file(self):
        if self.curr_file is None:
            self.save_file_as()
            return
        model.save_file(self.curr_file, self.text.get(1.0, END))

    def save_file_as(self):
        file_path = filedialog.asksaveasfilename()
        if file_path == "":
            return
        self.curr_file = file_path
        self.change_file_name(file_path.split("/")[-1])
        model.save_file(self.curr_file, self.text.get(1.0, END))

    def delete_file(self):
        if self.curr_file is None:
            messagebox.showerror("Ошибка файла", "Файла не существует")
            return
        model.delete_file(self.curr_file)
        self.curr_file = None
        self.text.delete(1.0, END)
        self.change_file_name()
        self.page_num.config(from_=0, to=0)

    def change_file_name(self, new_name=None):
        if new_name is None:
            self.window.title("2M NotePad")
        else:
            self.window.title(f"2M NotePad ― {new_name}")

    def change_page(self):
        # todo здесь должно происходить сохранение тегов в список общий
        try:
            new_page_num = int(self.page_num.get()) - 1
        except ValueError:
            return
        self.text.delete(1.0, END)
        self.change_align(self.global_tags["align"])
        self.text.insert(INSERT, self.pages[new_page_num])
        self.update_stat()
        self.clean_find_text()
        # todo здесь нужен метод, который будет применять теги все

    def change_align(self, align):
        self.text.tag_configure("align", justify=align)
        self.text.insert(1.0, " ")
        self.text.tag_add("align", "1.0", "end")
        self.global_tags["align"] = align

    def update_stat(self):
        page_count = max(len(self.pages), 1)
        lines_count = self.text.count("0.0", "end", "displaylines")[0]
        letters_count = len(self.text.get(1.0, END))
        self.update_entry(self.pages_counter, page_count)
        self.update_entry(self.lines_counter, lines_count)
        self.update_entry(self.letters_counter, letters_count)

    @staticmethod
    def update_entry(entry, count, block=True):
        entry.config(state="normal")
        entry.delete(0, END)
        entry.insert(0, count)
        if block:
            entry.config(state="readonly")

    def find_text(self):
        self.clean_highlighted_text()
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
        self.update_entry(self.world_counter, counter)

    def clean_find_text(self):
        self.update_entry(self.world_counter, "")
        self.update_entry(self.finder, "", block=False)
        self.clean_highlighted_text()
        self.global_tags['finder'] = 0

    def clean_highlighted_text(self):
        self.text.tag_configure(f"search{self.global_tags['finder']}", background="#ffffff")

    def stylize_text(self, underline=False, style=NORMAL, type="", size=""):
        if type == "":
            type = self.font_type.get()
        if size == "":
            size = self.font_size.get()
        tag_name = self.global_tags["format"] + 1
        self.text.tag_config(tag_name, font=(type, size, style), underline=underline)
        self.text.tag_add(tag_name, "sel.first", "sel.last")
        self.global_tags["format"] += 1

    def get_font(self, style=NORMAL, type="", size=""):
        if type == "":
            type = self.font_type.get()
        if size == "":
            size = self.font_size.get()
        return type, size, style

    def undo(self):
        try:
            self.text.edit_undo()
        except TclError:
            pass

    def redo(self):
        try:
            self.text.edit_redo()
        except TclError:
            pass

    def choose_text_color(self):
        (rgb, hx) = colorchooser.askcolor()
        self.text_color.config(bg=hx)
        self.text.config(fg=hx)

    def choose_back_color(self):
        (rgb, hx) = colorchooser.askcolor()
        self.back_color.config(bg=hx)
        self.text.config(bg=hx)