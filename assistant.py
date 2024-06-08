import os
import ctypes
import shutil
from pycaw.pycaw import AudioUtilities
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from transformers import pipeline
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import screen_brightness_control as sbc
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import IAudioEndpointVolume
import numpy as np
from PIL import Image
from tensorflow.keras.applications.vgg16 import VGG16
from tensorflow.keras.preprocessing import image
from sklearn.metrics.pairwise import cosine_similarity
import customtkinter as ctk

# Set up the main window
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class ChatbotApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Windows Assistant")
        self.geometry("600x500")

        self.wm_attributes("-alpha", 0.95)

        self.chat_frame = ctk.CTkFrame(self)
        self.chat_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        self.text_widget = tk.Text(self.chat_frame, bg="#2c2c2c", fg="white", wrap=tk.WORD, state=tk.DISABLED)
        self.text_widget.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        self.entry_frame = ctk.CTkFrame(self)
        self.entry_frame.pack(fill=tk.X, padx=10, pady=10)

        self.entry = ctk.CTkEntry(self.entry_frame, width=300, placeholder_text="Type your message here...")
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        self.entry.bind("<Return>", self.on_enter)

        self.send_button = ctk.CTkButton(self.entry_frame, text="Send", command=self.on_enter)
        self.send_button.pack(side=tk.RIGHT, padx=10)

        self.insert_bot_message("Hi There, how can I help you?")

        self.pending_function = None

    def on_enter(self, event=None):
        user_input = self.entry.get()
        if user_input.strip():
            self.insert_user_message(user_input)
            self.entry.delete(0, tk.END)
            self.process_user_input(user_input)

    def insert_user_message(self, message):
        self.text_widget.configure(state=tk.NORMAL)
        self.text_widget.insert(tk.END, f"\n{' ' * 70}{message}\n", "user")
        self.text_widget.tag_configure("user", foreground="#00FF00", justify='right')
        self.text_widget.configure(state=tk.DISABLED)
        self.text_widget.yview(tk.END)

    def insert_bot_message(self, message):
        self.text_widget.configure(state=tk.NORMAL)
        self.text_widget.insert(tk.END, f"\nBot: {message}\n", "bot")
        self.text_widget.tag_configure("bot", foreground="#00BFFF")
        self.text_widget.configure(state=tk.DISABLED)
        self.text_widget.yview(tk.END)

    def process_user_input(self, user_input):
        if self.pending_function:
            function, args = self.pending_function
            args.append(user_input)
            self.pending_function = None
            function(*args)
        else:
            function, args = interpret_user_input(user_input)
            if function:
                if args:
                    self.pending_function = (function, args)
                    self.insert_bot_message(args[0])
                else:
                    function()

    def prompt_for_input(self, prompt):
        self.insert_bot_message(prompt)




# Define the functions
def shutdown_system():
    os.system("shutdown /s /f /t 0")


def restart_system():
    os.system("shutdown /r /f /t 0")


def sleep_system():
    os.system("rundll32.exe powrprof.dll,SetSuspendState Sleep")


def empty_recycle_bin():
    from win32com.shell import shell
    shell.SHEmptyRecycleBin(None, None, 3)


def find_duplicate_image(image_path):
    pass


def rename_file(src, dst):
    os.rename(src, dst)


def set_system_volume(volume_level):
    volume_level = int(volume_level) / 100
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volume.SetMasterVolumeLevelScalar(volume_level, None)


def initialize_model():
    vgg16 = VGG16(weights='imagenet', include_top=False, pooling='max', input_shape=(224, 224, 3))
    for model_layer in vgg16.layers:
        model_layer.trainable = False
    return vgg16


def load_image(image_path):
    input_image = Image.open(image_path)
    resized_image = input_image.resize((224, 224))
    return resized_image


def get_image_embeddings(model, object_image):
    image_array = np.expand_dims(image.img_to_array(object_image), axis=0)
    image_embedding = model.predict(image_array)
    return image_embedding


def get_similarity_score(model, first_image_path, second_image_path):
    first_image = load_image(first_image_path)
    second_image = load_image(second_image_path)

    first_image_vector = get_image_embeddings(model, first_image)
    second_image_vector = get_image_embeddings(model, second_image)

    similarity_score = cosine_similarity(first_image_vector, second_image_vector).reshape(1, )

    return similarity_score


def compare_images(model, image_path, directory_path):
    target_image = load_image(image_path)
    target_vector = get_image_embeddings(model, target_image)

    duplicate_images = []

    for file in os.listdir(directory_path):
        if file.lower().endswith(('png', 'jpg', 'jpeg', 'webp', 'bmp', 'tiff')):
            file_path = os.path.join(directory_path, file)
            try:
                comparison_image = load_image(file_path)
                comparison_vector = get_image_embeddings(model, comparison_image)
                similarity_score = cosine_similarity(target_vector, comparison_vector).reshape(1, )[0] * 100
                if similarity_score > 95:
                    duplicate_images.append((file, similarity_score))
            except Exception as e:
                print(f"Error processing file {file}: {e}")

    return duplicate_images


def upload_and_compare():
    root = tk.Tk()
    root.withdraw()

    image_path = filedialog.askopenfilename(title="Select an Image",
                                            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.webp;*.bmp;*.tiff")])
    if not image_path:
        messagebox.showinfo("Information", "No image selected.")
        return

    directory_path = filedialog.askdirectory(title="Select a Directory")
    if not directory_path:
        messagebox.showinfo("Information", "No directory selected.")
        return

    model = initialize_model()
    duplicates = compare_images(model, image_path, directory_path)

    if duplicates:
        result_text = "Found duplicates:\n\n" + "\n".join([f"{file}: {score:.2f}%" for file, score in duplicates])
    else:
        result_text = "No duplicates found."

    messagebox.showinfo("Result", result_text)


def reduce_brightness(factor):
    factor = int(factor) / 100
    initial_brightness = sbc.get_brightness(display=0)

    if not (0 <= factor <= 1):
        raise ValueError("Factor must be between 0 and 100")

    sbc.set_brightness(factor * 100, display=0)

    return 1


def set_alarm(time_str):
    scheduler = BackgroundScheduler()
    alarm_time = datetime.strptime(time_str, "%H:%M:%S").time()
    scheduler.add_job(lambda: print("Alarm!"), 'cron', hour=alarm_time.hour, minute=alarm_time.minute,
                      second=alarm_time.second)
    scheduler.start()


def set_wallpaper(image_path):
    ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 0)


def clear_temp():
    temp_path = os.getenv('TEMP')
    shutil.rmtree(temp_path)
    os.makedirs(temp_path)


def clear_env_temp():
    temp_path = os.getenv('TEMP')
    shutil.rmtree(temp_path)
    os.makedirs(temp_path)


nlp = pipeline("fill-mask", model="distilbert-base-uncased")


def select_image():
    root = tk.Tk()
    root.withdraw()
    image_path = filedialog.askopenfilename(
        title="Select an Image",
        filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp;*.gif")]
    )
    if image_path:
        set_wallpaper(image_path)
        print(f"Wallpaper set to: {image_path}")
    else:
        print("No image selected.")




def interpret_user_input(user_input):
    if "shutdown" in user_input:
        return shutdown_system, []
    elif "restart" in user_input:
        return restart_system, []
    elif "sleep" in user_input:
        return sleep_system, []
    elif "empty recycle bin" in user_input:
        return empty_recycle_bin, []
    elif "duplicate image" in user_input:
        return upload_and_compare, []
    elif "rename file" in user_input:
        return rename_file_gui, []
    elif "volume" in user_input:
        return set_volume_gui, ["Please enter the volume level (0-100):"]
    elif "brightness" in user_input:
        return set_brightness_gui, ["Please enter the brightness level (0-100):"]
    elif "alarm" in user_input:
        return set_alarm_gui, ["Please enter the time (HH:MM:SS):"]
    elif "wallpaper" in user_input:
        return select_image, []
    elif "clear temp" in user_input:
        return clear_temp, []
    elif "clear env temp" in user_input:
        return clear_env_temp, []
    else:
        return None, []


def rename_file_gui(app, src):
    app.prompt_for_input("Please provide the new file name with path:")
    app.pending_function = (rename_file, [src])


def set_volume_gui(app, volume_level):
    set_system_volume(volume_level)



def set_brightness_gui(app, brightness_level):
    reduce_brightness(brightness_level)


def set_alarm_gui(app, time_str):
    set_alarm(time_str)


if __name__ == "__main__":
    app = ChatbotApp()
    app.mainloop()
