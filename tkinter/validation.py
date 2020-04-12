
import tkinter as tk  # python 3.x

'''THIS PROJECT WAS FORKED FROM THE FIRST SOURCE LISTED BELOW AND MODIFIED'''

'''RESOURCES'''
# https://stackoverflow.com/questions/6548837/how-do-i-get-an-event-callback-when-a-tkinter-entry-widget-is-modified
# https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/entry-validation.html
# http://stupidpythonideas.blogspot.com/2013/12/tkinter-validation.html?view=classic


class Example(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        # valid percent substitutions (from the Tk entry man page)
        # note: you only have to register the ones you need; this
        # example registers them all for illustrative purposes
        #
        # %d = Type of action (1=insert, 0=delete, -1 for others)
        # %i = index of char string to be inserted/deleted, or -1
        # %P = value of the entry if the edit is allowed
        # %s = value of entry prior to editing
        # %S = the text string being inserted or deleted, if any
        # %v = the type of validation that is currently set
        # %V = the type of validation that triggered the callback
        #      (key, focusin, focusout, forced)
        # %W = the tk name of the widget

        vcmd = (self.register(self.onValidate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.entry = tk.Entry(self, validate="key", validatecommand=vcmd)
        self.entry.config(bg='light grey', highlightbackground='red', highlightthickness=2)
        self.text = tk.Text(self, fg='white', height=10, width=40)
        self.text.config(bg='#384048')
        self.entry.pack(side="top", fill="x")
        self.text.pack(side="bottom", fill="both", expand=True)

    def onValidate(self, d, i, P, s, S, v, V, W):
        self.text.delete("1.0", "end")
        self.text.insert("end", "OnValidate:\n")
        self.text.insert("end", "Type of Action='%s'\n" % d)
        self.text.insert("end", "Index of Character String Affected='%s'\n" % i)
        self.text.insert("end", "Value of Entry if Edit Allowed='%s'\n" % P)
        self.text.insert("end", "Value of Entry Prior to Editing='%s'\n" % s)
        self.text.insert("end", "The Text String Being Inserted or Deleted (if any)='%s'\n" % S)
        self.text.insert("end", "Type of Validation Currently Set='%s'\n" % v)
        self.text.insert("end", "The Type of Validation That Triggered the Callback (key, focusin, "
                                "focusout, forced)='%s'\n" % V)
        self.text.insert("end", "The tk Name of the Widget='%s'\n" % W)

        # Disallow anything but lowercase letters
        if S == S.lower():
            return True
        else:
            self.bell()
            return False


if __name__ == "__main__":
    root = tk.Tk()
    root.title('tk Validation Tool')
    root.config(padx=7, pady=7)
    root.geometry('700x300')
    root.resizable(0, 0)
    Example(root).pack(fill="both", expand=True)
    root.mainloop()