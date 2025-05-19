from customtkinter import *
from tkinter import filedialog
from PIL import Image


import socket, threading, io, base64


class MainWindow(CTk): # Клас для головного вікна програми
    def __init__(self): # Ініціалізація вікна (конструктор класу)
        super().__init__() # Виклик конструктора батьківського класу
       
        self.title('LogiTalk') # Назва вікна
        self.geometry('800x600') # Розміри вікна
       
        self.frame = CTkFrame(self, width=0, height=self.winfo_height()) # Створення фрейму
        self.frame.pack_propagate(False)
        self.frame.place(x=0,y=0) # Розміщення фрейму в координатах (0,0)
       
        self.btn = CTkButton(self, text='▶️', width=30, command=self.toggle_menu) # ◀️
        self.btn.place(x=0, y=0) # Кнопка для відкриття меню
       
        self.label = CTkLabel(self.frame, text="Ваше ім'я") # Створення лейблу
        self.label.pack(pady=30)
        self.entry = CTkEntry(self.frame, placeholder_text="Введіть ваше ім'я")
        self.entry.pack()
        self.entry_btn = CTkButton(self.frame, text='Змінити', command=self.change_name)
        self.entry_btn.pack(pady=10)
       
        self.change_theme_list = CTkOptionMenu(self.frame, values=["System", "Light", "Dark"], command=self.set_theme)
        self.change_theme_list.pack(side='bottom', pady=10)
       
        self.user_name = 'Dance' # Ім'я користувача
        self.is_open = False # Змінна для перевірки чи відкрите меню
        self.online = None # Змінна для виводу користувачів онлайн
       
        self.chat_online = CTkLabel(self, text="Онлайн:", height=self.btn.winfo_height())
        self.chat_online.place(x=0, y=0)
       
        self.chat_field = CTkScrollableFrame(self)
        self.chat_field.place(x=0, y=0)
       
        self.chat_entry = CTkEntry(self, placeholder_text="Введіть повідомлення", height=40)
        self.chat_entry.place(x=0, y=0)
       
        self.chat_btn = CTkButton(self, text='>', height=40, width=50, command=self.send_message)
        self.chat_btn.place(x=0, y=0)
       
        self.chat_btn_img = CTkButton(self, text='📂', height=40, width=50, command=self.open_img)
        self.chat_btn_img.place(x=0, y=0)
       
        self.file_name = None
        self.raw = None
        self.image_to_send = CTkLabel(self, text="")
        self.image_to_send.bind("<Button-1>", self.remove_image)
       
        self.adaptation_ui()


        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect(('6.tcp.eu.ngrok.io', 14258))
            hello = f'TEXT@{self.user_name}@[SYSTEM] {self.user_name} підключився(лась) до чату!\n'
            self.socket.sendall(hello.encode('utf-8'))
           
            threading.Thread(target=self.receive_message, daemon=True).start()
        except Exception as e:
            self.add_message(f'Не вдалося підключитися до сервера: {e}')
   
    def remove_image(self, e=None):
        self.image_to_send.place_forget()
        self.raw = None
        self.file_name = None
   
    def adaptation_ui(self):
        w_width = self.winfo_width()
        w_height = self.winfo_height()
        # place - ставимо об'єкт на якісь координати
        # configure - змінюємо розміри
        # winfo_height - висота віджета або екрану
        # winfo_width - ширина віджета або екрану
        # winfo_x - координати віджета або екрану
        # winfo_y - координати віджета або екрану
        self.frame.configure(height=w_height)
       
        self.chat_field.place(x=self.frame.winfo_width(), y=self.btn.winfo_height())
        self.chat_field.configure(width=w_width - self.frame.winfo_width() - 20, height = w_height - self.btn.winfo_height() - 45)
       
        self.chat_btn.place(x=w_width - 50, y = w_height - 40)
        self.chat_btn_img.place(x=w_width - 105, y = w_height - 40)
       
        self.chat_entry.place(x= self.frame.winfo_width(), y=w_height - 40)
        self.chat_entry.configure(width=self.chat_btn_img.winfo_x() - self.frame.winfo_width() - 5)
       
        self.chat_online.place(x=self.btn.winfo_width() + 20)
       
        if self.raw:
            self.image_to_send.configure(image=CTkImage(Image.open(self.file_name), size=(100, 100)))
            self.image_to_send.place(x=self.frame.winfo_width()+20, y=self.chat_entry.winfo_y()-100)
       
        self.after(100, self.adaptation_ui) # Виклик функції адаптації інтерфейсу
   
    def toggle_menu(self):
        if self.is_open:
            self.is_open = False
            self.frame.configure(width=0, height=self.winfo_height())
            self.btn.configure(text='▶️', width=30)
        else:
            self.is_open = True
            self.frame.configure(width=200, height=self.winfo_height())
            self.btn.configure(text='◀️', width=200)
           
    def set_theme(self, value):
        if value == 'System':
            set_appearance_mode('system')
        elif value == 'Light':
            set_appearance_mode('light')
        elif value == 'Dark':
            set_appearance_mode('dark')
           
    def change_name(self):
        self.user_name = self.entry.get()
        self.label.configure(text=self.user_name)
        self.entry.delete(0, 'end')
   
    def open_img(self):
        self.file_name = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        if not self.file_name:
            return
        try:
            # 'rb' - read binary, 'r' - read text, 'wb' - write binary, 'w' - write text, 'a' - append text, 'ab' - append binary,
            with open(self.file_name, "rb") as f:
                self.raw = f.read()
                print(self.raw)
            return self.raw
        except Exception as e:
            print(f"Error opening file: {e}")


    def add_message(self, message, img=None):
        message_frame = CTkFrame(self.chat_field, fg_color='#636363')
        message_frame.pack(pady=5,padx=5, anchor='w')


        w_size = self.winfo_width() - self.frame.winfo_width() - 20


        if not img: # якщо немає картинки
            CTkLabel(message_frame, text=message, justify='left', wraplength=w_size, text_color='white').pack(pady=5,padx=10)
        else: # інакше коли є картинка
            CTkLabel(message_frame, text=message, justify='left', wraplength=w_size, text_color='white', compound='top', image=img).pack(pady=5,padx=10)


    def resize_image(self, image):
        width, height = image.size


        new_width = 300


        if width <= new_width:
            if height < 300:
                return CTkImage(image, size=(width, height))
            else:
                new_height = 300
                new_width = int(width*new_height / height)
        else:
            new_height = int(height*new_width / width)


        return CTkImage(image, size=(new_width, new_height))


    def send_message(self):
        message = self.chat_entry.get()
        if message and not self.raw:
            self.add_message(f'{self.user_name}: {message}')
            data = f'TEXT@{self.user_name}@{message}\n'
            try:
                self.socket.sendall(data.encode())
            except:
                pass
        elif self.raw:
            b64_data = base64.b64encode(self.raw).decode() # base64 encode - кодування даних в base64
            data = f'IMAGE@{self.user_name}@{message}@{b64_data}\n'
            try:
                self.socket.sendall(data.encode())
            except:
                pass
            self.add_message(message, img=self.resize_image(Image.open(self.file_name)))
            self.remove_image()
        self.chat_entry.delete(0, 'end')
   
    def handle_line(self, line):
        if not line:
            return
        parts = line.split('@')
        message_type = parts[0]
        if message_type == 'TEXT':
            self.add_message(f'{parts[1]}: {parts[2]}')
        elif message_type == 'IMAGE':
            try:
                img_data = base64.b64decode(parts[3]) # перетворюємо картинку в байти
                img_data = io.BytesIO(img_data) # збираємо до купи байти щоб отримати картинку
                img = Image.open(img_data) # відкриваємо картинку перетворену з байтів
                img = self.resize_image(img)
                self.add_message(f'{parts[1]}: {parts[2]}', img=img)
            except Exception as e:
                self.add_message(f'Помилка отримання зображення: {e}')
    def receive_message(self):
        buffer = ''
        while True:
            try:
                message = self.socket.recv(16384) #1024
                buffer += message.decode('utf-8', errors='ignore') # тип кодування, errors
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    self.handle_line(line.strip())
            except:
                break
        self.socket.close()


       
           
window = MainWindow() # Створення об'єкту класу MainWindow
window.mainloop() # Запуск головного циклу програми