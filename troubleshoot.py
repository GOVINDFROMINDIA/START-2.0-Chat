import openai
import customtkinter as ctk
from tkinter import *

# Set your OpenAI API key
openai.api_key = "*****************************"

# Set up the main window
ctk.set_appearance_mode("dark")  
ctk.set_default_color_theme("blue")

class ChatbotApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Windows Assistant")
        self.geometry("400x400")

        self.wm_attributes("-alpha", 0.95)

        self.chat_frame = ctk.CTkFrame(self)
        self.chat_frame.pack(expand=True, fill=BOTH, padx=10, pady=10)

        self.text_widget = Text(self.chat_frame, bg="#2c2c2c", fg="white", wrap=WORD, state=DISABLED)
        self.text_widget.pack(expand=True, fill=BOTH, padx=10, pady=10)

        self.entry_frame = ctk.CTkFrame(self)
        self.entry_frame.pack(fill=X, padx=10, pady=10)

        self.entry = ctk.CTkEntry(self.entry_frame, width=300, placeholder_text="Type your message here...")
        self.entry.pack(side=LEFT, padx=10)
        self.entry.bind("<Return>", self.on_enter)

        self.send_button = ctk.CTkButton(self.entry_frame, text="Send", command=self.on_enter)
        self.send_button.pack(side=RIGHT, padx=10)

        self.insert_bot_message("Hi There, how can I help you?")

        self.messages = [
            {"role": "system", "content": "Hi ChatGPT, you are a troubleshooting and fixing expert assistant."},
        ]

    def on_enter(self, event=None):
        user_input = self.entry.get()
        if user_input.strip():
            self.insert_user_message(user_input)
            self.entry.delete(0, END)
            self.messages.append({"role": "user", "content": user_input})
            self.get_bot_response()

    def get_bot_response(self):
        try:
            chat_completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=self.messages
            )
            bot_reply = chat_completion["choices"][0]["message"]["content"]
            self.messages.append({"role": "assistant", "content": bot_reply})
            self.insert_bot_message(bot_reply)
        except Exception as e:
            self.insert_bot_message(f"Error: {e}")

    def insert_user_message(self, message):
        self.text_widget.configure(state=NORMAL)
        self.text_widget.insert(END, f"\n{' ' * 70 + message}\n", "user")
        self.text_widget.tag_configure("user", foreground="#00FF00", justify='right')  
        self.text_widget.configure(state=DISABLED)
        self.text_widget.yview(END)

    def insert_bot_message(self, message):
        self.text_widget.configure(state=NORMAL)
        self.text_widget.insert(END, f"\n{message}\n", "bot")
        self.text_widget.tag_configure("bot", foreground="#00BFFF") 
        self.text_widget.configure(state=DISABLED)
        self.text_widget.yview(END)

if __name__ == "__main__":
    app = ChatbotApp()
    app.mainloop()
