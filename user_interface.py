import tkinter

def create_UI():
    window = tkinter.Tk()
    window.title("Zootgle Search")
    label = tkinter.Label(window, text = "Welcome to Zootgle!").pack()
    window.mainloop()
    #test

create_UI()