import tkinter
import search_component_final

class UI_Zootgle:
    def __init__(self):
        self.create_UI()

    def search(self):
        entered_text = self.textentry.get()
        self.output.delete(0.0, tkinter.END)
        top_5 = search_component_final.search_results(entered_text, self.doc_len_loaded, "dev_full_index_with_tfidf.txt", self.pos_dict_loaded, self.doc_ids, len(self.doc_ids))
        if len(top_5):
            for URL in top_5:
                self.output.insert(tkinter.END, self.doc_ids[URL])
        else:
            self.output.insert(tkinter.END, "No results found.")

    def create_UI(self):
        self.load_dicts()
        window = tkinter.Tk()
        window.title("Zootgle Search")
        window.configure(background = "black")
        zootgle_logo = tkinter.PhotoImage(file = "zootgle.png")
        tkinter.Label(window, image = zootgle_logo, bg = "black").grid(row = 0, column = 0)
        self.textentry = tkinter.Entry(window, width = 20, bg = "white")
        self.textentry.grid(row = 2, column = 0)
        tkinter.Button(window, text = "Search", width = 6, command = self.search).grid(row = 3, column = 0)
        self.output = tkinter.Text(window, width = 75, height = 6, background = "white")
        self.output.grid(row = 5, column = 0, columnspan = 2)
        window.mainloop()

    def load_dicts(self):
        with open("dev_doc_len_list.txt", "r") as doc_len_list:
            self.doc_len_loaded = eval(doc_len_list.read())
        with open("dev_final_pos_dict.txt", "r") as pos_dict:
            self.pos_dict_loaded = eval(pos_dict.read())
        with open("dev_doc_ids.txt", "r") as doc_id_name:
            self.doc_ids = eval(doc_id_name.read())

    def exit(self):
        window.destroy()
        exit()

UI_Zootgle()
