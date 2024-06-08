import os
import ctypes
import shutil
import glob
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from transformers import pipeline
import tkinter as tk
from tkinter import filedialog
import screen_brightness_control as sbc
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow.keras.applications.vgg16 import VGG16
from tensorflow.keras.preprocessing import image
from sklearn.metrics.pairwise import cosine_similarity
from tkinter import messagebox

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
    # Implement VGG ImageNet model to find duplicates
    pass

def rename_file(src, dst):
    os.rename(src, dst)

def set_system_volume(volume_level):
    volume_level = volume_level / 100
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
    
    similarity_score = cosine_similarity(first_image_vector, second_image_vector).reshape(1,)
    
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
                similarity_score = cosine_similarity(target_vector, comparison_vector).reshape(1,)[0] * 100
                if similarity_score > 95:
                    duplicate_images.append((file, similarity_score))
            except Exception as e:
                print(f"Error processing file {file}: {e}")

    return duplicate_images

def upload_and_compare():
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    image_path = filedialog.askopenfilename(title="Select an Image", filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.webp;*.bmp;*.tiff")])
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
    factor = factor / 100
    initial_brightness = sbc.get_brightness(display=0)
    print(initial_brightness)
    
    # Ensure the factor is between 0 and 1
    if not (0 <= factor <= 1):
        raise ValueError("Factor must be between 0 and 100")
    
    sbc.set_brightness(factor * 100, display=0)
    
    return 1

def set_alarm(time_str):
    scheduler = BackgroundScheduler()
    alarm_time = datetime.strptime(time_str, "%H:%M:%S").time()
    scheduler.add_job(lambda: print("Alarm!"), 'cron', hour=alarm_time.hour, minute=alarm_time.minute, second=alarm_time.second)
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

# Load pre-trained model
nlp = pipeline("fill-mask", model="distilbert-base-uncased")

def select_image():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
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
    elif "find duplicate image" in user_input:
        return upload_and_compare, []
    elif "rename file" in user_input:
        src = input("Please provide the current file name with path: ")
        dst = input("Please provide the new file name with path: ")
        return rename_file, [src, dst]
    elif "volume" in user_input:
        vol = int(input("Enter percentage of volume "))
        return set_system_volume, [vol]
    elif "brightness" in user_input:
        factor = float(input("Please enter new brightness percentage "))
        return reduce_brightness, [factor]
    elif "set alarm" in user_input:
        time_str = input("Please provide the time in HH:MM:SS format: ")
        return set_alarm, [time_str]
    elif "set wallpaper" in user_input:
        return select_image, []
    elif "clear temp" in user_input:
        return clear_temp, []
    elif "clear env temp" in user_input:
        return clear_env_temp, []
    else:
        return None, []

def chatbot():
    print("Hello! I am your assistant. How can I help you today?")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
        function, args = interpret_user_input(user_input)
        if function:
            function(*args)
        else:
            print("Sorry, I didn't understand that command.")

if __name__ == "__main__":
    chatbot()
