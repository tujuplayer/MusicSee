from kivy.app import App
from kivy.uix.popup import Popup
from gui.main_window import MainWindow

class MusicAnalyzerApp(App):
    def build(self):
        return MainWindow()

if __name__ == '__main__':
    MusicAnalyzerApp().run()