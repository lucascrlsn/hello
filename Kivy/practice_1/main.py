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
