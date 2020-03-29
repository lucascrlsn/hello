
# AUTHOR: Erik Sandberg
# SOURCE: https://www.youtube.com/watch?v=nI9mjajX4TI&t=37s

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout

import requests

from kivy.network.urlrequest import UrlRequest
from functools import partial


class MainApp(App):
    def build(self):
        grid = GridLayout(cols=1)
        button1 = Button(text='Normal Requests', on_release=self.run_requests)
        button2 = Button(text='Kivy Url Requests', on_release=self.run_UrlRequests)
        blank_button = Button(text='Click Me!')
        grid.add_widget(button1)
        grid.add_widget(button2)
        grid.add_widget(blank_button)
        return grid

    def run_requests(self, *args):
        for i in range(10):
            r = requests.get('https://wwww.google.com')
            print(i)

    def run_UrlRequests(self, *args):
        for i in range(10):
            self.r = UrlRequest('https://wwww.google.com', on_success=partial(self.update_label, i))

    def update_label(self, i, *args):
        print(i)
        print(self.r.result)


MainApp().run()




