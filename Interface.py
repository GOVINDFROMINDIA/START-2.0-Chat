import customtkinter as ctk
import subprocess

# Initialize the application
app = ctk.CTk()

# Set the theme to Light
ctk.set_appearance_mode("Light")

# Configure the window
app.title("START 2.0")
app.geometry("400x400")

# Function to toggle between dark and light theme
def toggle_theme():
    current_theme = ctk.get_appearance_mode()
    new_theme = "Dark" if current_theme == "Light" else "Light"
    ctk.set_appearance_mode(new_theme)

# Function to run Search.py
def run_search():
    subprocess.Popen(["python", "Search.py"])

# Function to run assistant.py
def run_assistant():
    subprocess.Popen(["python", "assistant.py"])

# Function to run troubleshoot.py
def run_troubleshoot():
    subprocess.Popen(["python", "troubleshoot.py"])

# Header Frame
header_frame = ctk.CTkFrame(app, height=50)
header_frame.pack(fill="x", padx=10, pady=5)

# Header Label
header_label = ctk.CTkLabel(header_frame, text="START 2.0", font=("Arial", 20))
header_label.pack(side="left", padx=10)

# Theme Toggle Button
theme_button = ctk.CTkButton(header_frame, text="Toggle Theme", command=toggle_theme)
theme_button.pack(side="right", padx=10)

# Create a frame for the boxes
box_frame = ctk.CTkFrame(app)
box_frame.pack(expand=True, fill="both", padx=10, pady=10)

# Box 1: Windows Assistant
box1 = ctk.CTkFrame(box_frame, corner_radius=10)
box1.pack(fill="x", pady=5)
box1_label = ctk.CTkLabel(box1, text="Windows Assistant 👋", font=("Arial", 16))
box1_label.pack(pady=20, padx=10)
box1_label.bind("<Button-1>", lambda e: run_assistant())

# Box 2: File/Folder Search
box2 = ctk.CTkFrame(box_frame, corner_radius=10)
box2.pack(fill="x", pady=5)
box2_label = ctk.CTkLabel(box2, text="File/Folder Search 🔍", font=("Arial", 16))
box2_label.pack(pady=20, padx=10)
box2_label.bind("<Button-1>", lambda e: run_search())

# Box 3: Trouble Shoot
box3 = ctk.CTkFrame(box_frame, corner_radius=10)
box3.pack(fill="x", pady=5)
box3_label = ctk.CTkLabel(box3, text="Trouble Shoot 🔧", font=("Arial", 16))
box3_label.pack(pady=20, padx=10)
box3_label.bind("<Button-1>", lambda e: run_troubleshoot())

# Run the application
app.mainloop()
