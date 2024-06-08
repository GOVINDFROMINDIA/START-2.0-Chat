import customtkinter as ctk
import os
import fnmatch
import threading
import time
import tkinter as tk
from tkinter import StringVar, Listbox, END
from tkinter import filedialog, Listbox, ttk

class StartMenuApp(ctk.CTk):

    rootdir="C:\\"
    mode="All"
    currentthread=0
    results=[]

    def __init__(self):
        super().__init__()

        self.title("Start Menu Search")
        self.geometry("600x400")

        self.search_var = StringVar()
        self.search_var.trace("w", self.on_search_query_change)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.create_widgets()
        threading.Thread(target=self.display_results, daemon=True).start()

    def create_widgets(self):
        choices = ["All", "Directory", "Files", "File Extensions"]
        self.choice_vars = []
        
        ctk.set_appearance_mode("System")  # Modes: "System" (default), "Light", "Dark"
        ctk.set_default_color_theme("blue")

        self.frame = ctk.CTkFrame(self, corner_radius=10)
        self.frame.grid(column=0, row=0, sticky=(ctk.W, ctk.E, ctk.N, ctk.S), padx=20, pady=20)
        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(3, weight=1)

        def select_folder():
            folder_selected = filedialog.askdirectory()
            if folder_selected:
                self.rootdir=folder_selected

        def checkbox_clicked(i):
            self.mode=choices[i]
            self.results.clear()
            for n, boolval in enumerate(self.choice_vars):
                if n!=i:boolval.set(False)
            self.on_search_query_change()

        self.folder_button = ctk.CTkButton(self.frame, text="📁", command=select_folder, width=2)
        self.folder_button.grid(column=0, row=0, sticky=(tk.W, tk.E))

        self.text_field = ctk.CTkEntry(self.frame, textvariable=self.search_var)
        self.text_field.grid(column=1, row=0, sticky=(tk.W, tk.E), pady=5)
        self.frame.columnconfigure(1, weight=1)

        self.choice_frame = ctk.CTkFrame(self.frame, corner_radius=10)
        self.choice_frame.grid(column=0, row=2, columnspan=3, sticky=(tk.W, tk.E))

        for n, choice in enumerate(choices):
            var = ctk.BooleanVar(value=False)
            if choice=="All":
                var.set(value=True)
            choice_chip = ctk.CTkCheckBox(self.choice_frame, text=choice, variable=var, text_color='black', command=lambda i=n: checkbox_clicked(i))
            choice_chip.pack(side=tk.LEFT, padx=5)
            self.choice_vars.append(var)

        self.textbox = ctk.CTkTextbox(self.frame)
        self.textbox.grid(column=0, row=3, columnspan=2, sticky=(ctk.W, ctk.E, ctk.N, ctk.S), pady=10)

    def on_search_query_change(self, *args):
        search_query = self.search_var.get()
        if search_query:
            self.currentthread+=1
            threading.Thread(
                target=self.executesearch,
                args=(search_query, self.currentthread),
                kwargs={"mode": self.mode},
                daemon=True
            ).start()
            
    def update_search_results(self, search_query, threadcounter):
        exitthread=False
        self.results.clear()
        for root, dirs, files in os.walk(self.rootdir):  # Change this to the desired search directory
                
            for name in files + dirs:
                if threadcounter==self.currentthread:
                    if search_query.lower() in name.lower():
                        self.results.append(os.path.join(root, name))
                        if len(self.results) > 20:  # Limit results for performance
                            break
                else:exitthread=True
            if len(self.results) > 100 or exitthread:
                break
            

    def executesearch(self, search_query, threadcounter, mode='All',limit=50, samplesize=20):
        exitthread=False
        self.results.clear()
        for root, dirnames, filenames in os.walk(self.rootdir):
            if mode=='All' or mode=='Directory':
                for dirname in fnmatch.filter(dirnames, search_query):
                    self.results.append(os.path.join(root, dirname))
                    if len(self.results) > limit:break

            if mode=='All' or mode=='Files':
                print(filenames)
                for filename in filenames: #fnmatch.filter(filenames, search_query):
                    if fnmatch.fnmatch(filename, search_query):
                        self.results.append(os.path.join(root, filename))
                    if len(self.results) > limit:break

            if mode=="File Extensions":
                for file in filenames:
                    if file.endswith(search_query):
                        self.results.append(file)
            if exitthread:break

                

    def display_results(self):
        #prev=[]
        while True:

            #if self.results!=prev:
            self.textbox.delete("1.0", tk.END)
            #for result in self.results:
            text = "\n".join(self.results)
            self.textbox.insert(tk.END, text)
            #prev=self.results
            time.sleep(1)

if __name__ == "__main__":
    app = StartMenuApp()
    app.mainloop()
