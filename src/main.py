from pathlib import Path
import sys
import os

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import (
    ObjectProperty, DictProperty, StringProperty,
    NumericProperty, ReferenceListProperty)
from kivy.resources import resource_add_path, resource_find
from kivy.extras.highlight import KivyLexer
from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.clock import Clock
from kivy.config import ConfigParser
from pygments import lexers

__file__ = sys.argv[0]
resource_add_path(str(Path(__file__).parent / "resources"))

LabelBase.register(DEFAULT_FONT, "fonts/NotoSansCJKjp-Regular.otf")
LabelBase.register("code_input", "fonts/NotoSansMonoCJKjp-Regular.otf")


class IconBase:
    icon = StringProperty("")
    padding_left = NumericProperty(0)
    padding_top = NumericProperty(0)
    padding_right = NumericProperty(0)
    padding_bottom = NumericProperty(0)
    padding = ReferenceListProperty(
        padding_left, padding_top, padding_right, padding_bottom)


class IconWidget(IconBase, Widget):
    pass


class IconButton(IconBase, Button):
    pass


class IconToggleButton(IconBase, ToggleButton):
    pass


class ClosablePopup(Popup):
    def __init__(self, content, close_function=None, **kwargs):
        super().__init__(**kwargs)
        self.content = content
        self.content.close = self.dismiss
        self.close_function = close_function

        def close():
            self.dismiss()
            if self.close_function:
                self.close_function()


class SaveFilePopupLayout(RelativeLayout):
    close = ObjectProperty(None)
    save_file = ObjectProperty(None)


class SaveFilePopup(Popup):
    def __init__(self, save_function, close_function=None, **kwargs):
        super().__init__(**kwargs)
        self.content = SaveFilePopupLayout()
        self.content.close = self.dismiss
        self.content.save_file = save_function
        self.close_function = close_function

        def close():
            self.dismiss()
            if self.close_function:
                self.close_function()


class OpenFilePopupLayout(RelativeLayout):
    close = ObjectProperty(None)
    open_file = ObjectProperty(None)

    def on_close_now(self, instance, close_now):
        if close_now:
            instance.close()


class OpenFilePopup(Popup):
    def __init__(self, open_function, close_function=None, **kwargs):
        super().__init__(**kwargs)
        self.content = OpenFilePopupLayout()
        self.content.open_file = open_function
        self.close_function = close_function

        def close():
            self.dismiss()
            if self.close_function:
                self.close_function()
        self.content.close = close


LICENSE_SHOWING = """
(C) 2018 Eleven-junichi2:
https://eleven-junichi2.github.io/

This app's repository
https://github.com/Eleven-junichi2/tsukushi

The copyright of the following libraries and resources belongs to their
respective rights holders:

Kivy:
https://github.com/kivy/kivy/blob/master/LICENSE

Noto:
https://scripts.sil.org/cms/scripts/page.php?site_id=nrsi&id=OFL

Pygments:
https://bitbucket.org/birkenfeld/pygments-main/src/tip/LICENSE

SDL:
https://www.libsdl.org/license.php

GLEW:
http://glew.sourceforge.net/glew.txt
"""


class LicensePopupLayout(RelativeLayout):
    close = ObjectProperty(None)
    license_showing = StringProperty(LICENSE_SHOWING)


class LicensePopup(Popup):
    def __init__(self, close_function=None, **kwargs):
        super().__init__(**kwargs)
        self.content = LicensePopupLayout()
        self.close_function = close_function

        def close():
            self.dismiss()
            if self.close_function:
                self.close_function()
        self.content.close = close


class ProgressPopupLayout(RelativeLayout):
    progress_bar = ObjectProperty(None)


class ProgressPopup(Popup):
    def __init__(self, init_value=0, max_value=0, **kwargs):
        super().__init__(**kwargs)
        self.content = ProgressPopupLayout()
        self.content.progress_bar.value = init_value
        self.content.progress_bar.max = max_value
        self.content.progress_bar.bind(value=self.on_progress_value)
        self.auto_dismiss = False
        self.open()

    def on_progress_value(self, instance, value):
        if value == instance.max:
            self.dismiss()

    def set_progress_value(self, value):
        self.content.progress_bar.value = value

    def set_progress_max(self, max_value):
        self.content.progress_bar.max = max_value


class DashBoardFileChooserView(RelativeLayout):
    file_chooser = ObjectProperty(None)
    file_chooser_user = ObjectProperty(None)
    file_name_input = ObjectProperty(None)
    cwd_path_input = ObjectProperty(None)

    def __init__(self, file_chooser_user, **kwargs):
        super().__init__(**kwargs)
        self.file_chooser_user = file_chooser_user

    def set_cwd_path(self, text):
        if Path(text).is_dir():
            self.file_chooser.path = text
        self.cwd_path_input.text = self.file_chooser.path

    def add_file(self, file_location, file_name):
        if not file_name:
            return False
        file_location = Path(file_location)
        if file_location.is_dir():
            file_path = file_location / file_name
            if not file_path.is_file():
                self.file_chooser_user.save_file(str(file_path))
                return True
            else:
                return False
        else:
            return False

    def add_dir(self, dir_location, dir_name):
        if not dir_name:
            return False
        file_location = Path(dir_location)
        if file_location.is_dir():
            file_path = file_location / dir_name
            if not file_path.is_dir():
                file_path.mkdir()
                return True
            else:
                return False
        else:
            return False


class EditorScreen(Screen):
    row_num = ObjectProperty(None)
    col_num = ObjectProperty(None)
    text_input_area = ObjectProperty(None)
    file_name_input = ObjectProperty(None)
    language_mode_chooser = ObjectProperty(None)
    dashboard = ObjectProperty(None)
    toggle_btn_file_chooser = ObjectProperty(None)
    lexer_dict = DictProperty({
        "Plain text": lexers.get_lexer_by_name("text"),
        "C": lexers.CLexer(),
        "C++": lexers.CppLexer(),
        "CSS": lexers.CssLexer(),
        "HTML": lexers.HtmlLexer(),
        "JavaScript": lexers.JavascriptLexer(),
        "Kivy": KivyLexer(),
        "Rust": lexers.RustLexer(),
        "Python": lexers.PythonLexer(),
        "Python3": lexers.Python3Lexer(),
        "SASS": lexers.SassLexer(),
        "SCSS": lexers.ScssLexer(),
    })

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_syntax_highlight(tuple(self.lexer_dict.keys())[0])
        self.text_input_area.bind(cursor=self.on_cursor)
        self.language_mode_chooser.bind(text=self.on_lang_mode_chooser)
        self.file_path = ""
        self.progress_popup = None
        self.gen_to_progress = None

    def launch_external_terminal(self):
        from kivy.uix.label import Label
        LAUNCH_SUCESS = 0
        if True:
            popup = Popup(title="Required",
                          content=Label(text="You have not set an external program. See the setting."))
            popup.open()

    def on_cursor(self, instance, cursor):
        # cursor[0]: current cursor postition(col)
        # cursor[1]: current cursor postition(row)
        self.col_num.text = str(cursor[0])
        self.row_num.text = str(cursor[1])

    def on_lang_mode_chooser(self, instance, text):
        self.set_syntax_highlight(text)

    def set_syntax_highlight(self, language):
        self.text_input_area.lexer = self.lexer_dict[language]

    def toggle_file_chooser_show(self):
        if self.toggle_btn_file_chooser.state == "normal":
            # self.dashboard_file_chooser = None
            self.dashboard.clear_widgets()
            self.dashboard.size_hint_x = None
            self.dashboard.width = 0
        elif self.toggle_btn_file_chooser.state == "down":
            self.dashboard.add_widget(DashBoardFileChooserView(
                file_chooser_user=self))
            self.dashboard.size_hint_x = 0.4

    def clear_text(self):
        self.text_input_area.text = ""

    def save_file(self, file_path):
        with open(file_path, "w") as f:
            f.write(self.text_input_area.text)
        self.file_path = file_path
        return True

    def show_save(self):
        def close():
            if self.toggle_btn_file_chooser.state == "down":
                self.toggle_btn_file_chooser.state = "normal"
                self.toggle_file_chooser_show()
                # self.toggle_btn_file_chooser.state = "down"
                # self.toggle_file_chooser_show()
        popup = SaveFilePopup(self.save_file, close)
        popup.open()

    def open_file_yield_progress(self, file_path, *args):
        progress_max = 0
        progress_count = 0
        try:
            with open(file_path, "r") as f:
                progress_max = sum(1 for line in open(file_path, "r")) + 1
                yield progress_count, progress_max
                text = ""
                for line in f:
                    text += line
                    progress_count += 1
                    yield progress_count, progress_max
                self.text_input_area.text = text
                self.file_name_input.text = Path(file_path).parts[-1]
                self.file_path = file_path
                progress_count += 1
                yield progress_count, progress_max
        except PermissionError:
            self.text_input_area.text = (
                ":( Permisson denined: {}".format(
                    Path(file_path).parts[-1]))
            yield progress_max, progress_max
        except UnicodeDecodeError:
            self.text_input_area.text = (
                ":( Unicode decode error: {}".format(
                    Path(file_path).parts[-1]))
            yield progress_max, progress_max

    def open_file(self, file_path):
        try:
            with open(file_path, "r") as f:
                text = ""
                for line in f:
                    text += line
                self.text_input_area.text = text
                self.file_name_input.text = Path(file_path).parts[-1]
                self.file_path = file_path
        except PermissionError:
            self.text_input_area.text = (
                ":( Permisson denined: {}".format(
                    Path(file_path).parts[-1]))
        except UnicodeDecodeError:
            self.text_input_area.text = (
                ":( Unicode decode error: {}".format(
                    Path(file_path).parts[-1]))
        else:
            return True

    def update_progress_popup(self, dt):
        try:
            value, max_value = next(self.gen_to_progress)
            self.progress_popup.set_progress_max(max_value)
            self.progress_popup.set_progress_value(value)
            # --- This code For speeding up to opening file.
            if dt == 0:
                dt = -1
            else:
                dt = 0
            # ---
            Clock.schedule_once(self.update_progress_popup, dt)
        except StopIteration:
            Clock.unschedule(self.show_progress_schedule)
            self.progress_popup.dismiss()

    def open_file_with_progress(self, file_path):
        self.progress_popup = ProgressPopup()
        self.gen_to_progress = self.open_file_yield_progress(file_path)
        self.show_progress_schedule = Clock.schedule_interval(
            self.update_progress_popup, 0)

    def show_open(self):
        open_file_popup = OpenFilePopup(self.open_file_with_progress)
        open_file_popup.open()

    def show_license(self):
        save_file_popup = LicensePopup()
        save_file_popup.open()


class LicenseScreen(Screen):
    pass


class TsukushiScreenManager(ScreenManager):
    pass


class TsukushiApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.icon = "images/icon.png"
        self.title = "Tsukushi"

    # def build_config(self, config):
    #     config.read(resource_find("config.ini"))

    # def build_settings(self, settings):
    #     settings.add_json_panel("App settings", self.config, filename=resource_find("settings.json"))

    def build(self):
        root_widget = TsukushiScreenManager()
        root_widget.add_widget(EditorScreen(name="editor"))
        root_widget.add_widget(LicenseScreen(name="license"))
        return root_widget


def main():
    TsukushiApp().run()


if __name__ == "__main__":
    main()
