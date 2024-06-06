import customtkinter as ctk
import os
import threading
from tkinter import StringVar, Listbox, END

class StartMenuApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Start Menu Search")
        self.geometry("600x400")

        self.search_var = StringVar()
        self.search_var.trace("w", self.on_search_query_change)

        self.create_widgets()

    def create_widgets(self):
        self.search_entry = ctk.CTkEntry(self, textvariable=self.search_var)
        self.search_entry.pack(pady=10, padx=10)

        self.results_listbox = Listbox(self)
        self.results_listbox.pack(fill="both", expand=True, pady=10, padx=10)

    def on_search_query_change(self, *args):
        search_query = self.search_var.get()
        if search_query:
            threading.Thread(target=self.update_search_results, args=(search_query,)).start()

    def update_search_results(self, search_query):
        results = []
        for root, dirs, files in os.walk("C:/"):  # Change this to the desired search directory
            for name in files + dirs:
                if search_query.lower() in name.lower():
                    results.append(os.path.join(root, name))
                    if len(results) > 100:  # Limit results for performance
                        break
            if len(results) > 100:
                break

        self.display_results(results)

    def display_results(self, results):
        self.results_listbox.delete(0, END)
        for result in results:
            self.results_listbox.insert(END, result)

if __name__ == "__main__":
    app = StartMenuApp()
    app.mainloop()
