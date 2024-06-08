import os
import ctypes
import shutil
import glob
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from transformers import pipeline

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

def file_search(query):
    for root, dirs, files in os.walk("C:\\"):
        for file in files:
            if query in file:
                print(os.path.join(root, file))

def rename_file(src, dst):
    os.rename(src, dst)

def reduce_volume():
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        volume = session._ctl.QueryInterface(ISimpleAudioVolume)
        volume.SetMasterVolume(0.5, None)  # Reduce to 50%

def reduce_brightness(factor):
    """
    Reduce the brightness by the given factor.

    Parameters:
    factor (float): The factor by which to reduce the brightness.
                    It should be a value between 0 and 1.
    
    Returns:
    float: The new brightness level.
    """
    # Assuming initial brightness is 100
    initial_brightness = 100
    
    # Ensure the factor is between 0 and 1
    if not (0 <= factor <= 1):
        raise ValueError("Factor must be between 0 and 1")
    
    new_brightness = initial_brightness * (1 - factor)
    return new_brightness

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
        # You might want to extract the image path from the user input
        image_path = input("Please provide the image path: ")
        return find_duplicate_image, [image_path]
    elif "search file" in user_input:
        query = input("Please provide the file name to search: ")
        return file_search, [query]
    elif "rename file" in user_input:
        src = input("Please provide the current file name with path: ")
        dst = input("Please provide the new file name with path: ")
        return rename_file, [src, dst]
    elif "reduce volume" in user_input:
        return reduce_volume, []
    elif "reduce brightness" in user_input:
        return reduce_brightness, []
    elif "set alarm" in user_input:
        time_str = input("Please provide the time in HH:MM:SS format: ")
        return set_alarm, [time_str]
    elif "set wallpaper" in user_input:
        #image_path = input("Please provide the image path: ")
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
