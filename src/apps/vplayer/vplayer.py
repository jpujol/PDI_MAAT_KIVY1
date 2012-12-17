import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout

class VPlayer(BoxLayout):
    pass

class VPlayerApp(App):
    def build(self):
        return VPlayer()

if __name__ == '__main__':
    VPlayerApp().run()
