import tkinter
import search_component_final

class UI_Zootgle:
    def __init__(self):
        self.create_UI()

    def search(self):
        ''' Returns top 5 results based off search query '''
        entered_text = self.textentry.get()
        self.output.config(state=tkinter.NORMAL)
        self.output.delete(0.0, tkinter.END)
        self.textentry.delete(0, tkinter.END)
        top_5 = search_component_final.search_results(entered_text, self.doc_len_loaded, "dev_full_index_with_tfidf.txt", self.pos_dict_loaded, self.doc_ids, len(self.doc_ids))
        if len(top_5):
            self.output.insert(tkinter.END, "Top 5 Results:\n")
            for URL in top_5:
                self.output.insert(tkinter.END, self.doc_ids[URL] + "\n")
        else:
            self.output.insert(tkinter.END, "No results found.")
        self.output.config(state=tkinter.DISABLED)

    def create_UI(self):
        self.load_dicts()
        window = tkinter.Tk()
        window.resizable(width = False, height = False)
        window.title("Zootgle Search")
        window.configure(background = "black")
        zootgle_logo = tkinter.PhotoImage(file = "zootgle.png")
        tkinter.Label(window, image = zootgle_logo, bg = "black").grid(row = 0, column = 0)
        self.textentry = tkinter.Entry(window, width = 22, bg = "white")
        self.textentry.grid(row = 2, column = 0)
        tkinter.Button(window, text = "Search", width = 6, command = self.search).grid(row = 3, column = 0)
        self.output = tkinter.Text(window, width = 75, height = 6, background = "white", state=tkinter.DISABLED, wrap = "none")
        self.output.bind("<1>", lambda event: self.output.focus_set()) #allow for highlighting of text
        self.output.grid(row = 4, column = 0, columnspan = 1)
        window.mainloop()

    def load_dicts(self):
        with open("dev_doc_len_list.txt", "r") as doc_len_list:
            self.doc_len_loaded = eval(doc_len_list.read())
        with open("dev_final_pos_dict.txt", "r") as pos_dict:
            self.pos_dict_loaded = eval(pos_dict.read())
        with open("dev_doc_ids.txt", "r") as doc_id_name:
            self.doc_ids = eval(doc_id_name.read())

UI_Zootgle()