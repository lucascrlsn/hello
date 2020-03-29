# AUTHOR: Erik Sandberg
# SOURCE: https://www.youtube.com/watch?v=UyuyaykVurM&list=PLy5hjmUzdc0mSl1d8dHBtk1730deh7rKX

from kivy.app import App
from kivy.uix.button import ButtonBehavior
from kivy.uix.label import  Label
from kivy.uix.image import Image


class ImageButton(ButtonBehavior, Image):
    pass


class LabelButton(ButtonBehavior, Label):
    pass


class MainApp(App):
    pass


MainApp().run()
