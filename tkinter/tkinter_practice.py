from tkinter import *
#from tkinter import ttk

# https://makeapppie.com/2014/05/04/from-apple-to-raspberry-pi-a-gentle-introduction-to-themed-widgets-with-ttk/
 

root = Tk()
root.title('TTK Power Panel #1')
 
# Frame
frame = Frame(root)
frame.grid(row=0, column=0)

# Variables
status = StringVar()
 
# Styles
 
# controller


def onButtonPressed():
    status.set('On')


def offButtonPressed():
    status.set('Off')


# label
status.set('System Off')
status_label = Label(frame, textvariable=status)
status_label.configure(font=('Sans', '14', 'bold'), background='blue', foreground='#eeeeff')
status_label.grid(row=0, column=0, columnspan=3, sticky=EW)

# on Button
on_button = Button(frame, command=onButtonPressed, text='On')
on_button.configure(font=('Sans', '14', 'bold'),background='blue', foreground='#eeeeff')
on_button.grid(row=2, column=0)
 
# off Button
off_button = Button(frame, command=offButtonPressed, text='Off')
 
off_button.configure(font=('Sans', '14', 'bold'), background='blue', foreground='#eeeeff')
off_button.grid(row=2, column=1)
 
quit_button = Button(frame, command=quit, text='Quit')
 
quit_button.configure(font=('Sans', '14', 'bold'), background='blue', foreground='#eeeeff')
quit_button.grid(row=2, column=2)

 
mainloop()
