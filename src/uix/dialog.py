from pathlib import Path

from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty, StringProperty
from kivy.lang import Builder
from kivy.resources import resource_add_path

resource_add_path(Path(__file__).parent)
Builder.load_file("dialog.kv")


class SuccessDialogLayout(RelativeLayout):
    close = ObjectProperty(None)
    message = StringProperty("")

    def __init__(self, layout_user, message="Succeed.", **kwargs):
        super().__init__(**kwargs)
        self.close = layout_user.close
        self.message = message


class ErrorDialogLayout(RelativeLayout):
    close = ObjectProperty(None)
    message = StringProperty("")

    def __init__(self, layout_user, message="Error.", **kwargs):
        super().__init__(**kwargs)
        self.close = layout_user.close
        self.message = message


class SuccessDialog(Popup):
    def __init__(self, message=None, **kwargs):
        if message:
            dialog_layout = SuccessDialogLayout(self, message=message)
        else:
            dialog_layout = SuccessDialogLayout(self)
        self.content = dialog_layout

    def close(self):
        self.dismiss()


class ErrorDialog(Popup):
    def __init__(self, message=None, **kwargs):
        if message:
            dialog_layout = ErrorDialogLayout(self, message=message)
        else:
            dialog_layout = ErrorDialogLayout(self)
        self.content = dialog_layout

    def close(self):
        self.dismiss()


class SaveAsFileDialog(Popup):
    def __init__(self, save_file_function, success_dialog,
                 error_dialog, **kwargs):
        super().__init__(**kwargs)
        self.content = SaveAsFileLayout(save_file_function, self)
        self.content.close = self.dismiss
        # self.success_dialog = success_dialog
        # self.error_dialog = error_dialog

    def close(self):
        self.dismiss()

    # def show_success_popup(self):
        # self.success_dialog.open()

    # def show_error_popup(self):
        # self.error_dialog.open()


class SaveAsFileLayout(RelativeLayout):
    save_file = ObjectProperty(None)
    close = ObjectProperty(None)
    show_success = ObjectProperty(None)
    show_alert = ObjectProperty(None)

    def __init__(self, save_file, layout_user,
                 **kwargs):
        super().__init__(**kwargs)
        self.save_file = save_file
        self.close = layout_user.close
        # self.show_success = layout_user.show_success_popup
        # self.show_error = layout_user.show_error_popup

    def save(self, file_location, file_name, to_close=False,
             close_after_success=False, close_after_alert=False):
        if self.save_file(file_location, file_name):
            succeed = True
            self.show_success()
        else:
            succeed = False
            self.show_alert()
        if ((close_after_success and succeed) or
            (close_after_alert and not succeed) or
                to_close):
            self.close()


class OpenFileLayout(RelativeLayout):
    open_file = ObjectProperty(None)
    show_success = ObjectProperty(None)
    show_alert = ObjectProperty(None)
    close = ObjectProperty(None)

    def __init__(self, open_file, close, show_success=None, show_alert=None,
                 **kwargs):
        super().__init__(**kwargs)
        self.open_file = open_file
        self.close = close
        self.show_success = show_success
        self.show_alert = show_alert

    def open(self, file_selection, to_close=False,
             close_after_success=False, close_after_alert=False):
        if file_selection:
            self.open_file(str(file_selection[0]))
            succeed = True
            self.show_success()
        else:
            succeed = False
            self.show_alert()
        if ((close_after_success and succeed) or
            (close_after_alert and not succeed) or
                to_close):
            self.close()
