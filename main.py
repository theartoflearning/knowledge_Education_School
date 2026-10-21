from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.utils import platform
import os
from cleaner import clean_pdf


class Root(BoxLayout):
    def __init__(self, **kw):
        super().__init__(orientation="vertical", padding=20, spacing=12, **kw)
        self.path = None
        self.pick_btn = Button(text="PDF বাছাই করুন", size_hint_y=None, height=120)
        self.pick_btn.bind(on_release=self.pick)
        self.text = TextInput(hint_text="Watermark লেখা (যেমন DRAFT)",
                              multiline=False, size_hint_y=None, height=120)
        row = BoxLayout(size_hint_y=None, height=100)
        self.img = CheckBox(size_hint_x=None, width=100)
        row.add_widget(self.img)
        row.add_widget(Label(text="ছবি watermark সরান"))
        go = Button(text="Watermark সরান", size_hint_y=None, height=120)
        go.bind(on_release=self.run)
        self.status = Label(text="")
        for w in (self.pick_btn, self.text, row, go, self.status):
            self.add_widget(w)

    def pick(self, *_):
        start = "/storage/emulated/0" if platform == "android" else os.path.expanduser("~")
        fc = FileChooserListView(path=start, filters=["*.pdf"])
        pop = Popup(title="PDF বাছাই", content=fc, size_hint=(1, 0.9))

        def chosen(_, sel, *a):
            if sel:
                self.path = sel[0]
                self.pick_btn.text = os.path.basename(self.path)
                pop.dismiss()
        fc.bind(on_submit=chosen)
        pop.open()

    def run(self, *_):
        if not self.path:
            self.status.text = "আগে PDF বাছাই করুন"
            return
        if not self.img.active and not self.text.text.strip():
            self.status.text = "watermark লেখা দিন"
            return
        out = self.path[:-4] + "_cleaned.pdf"
        try:
            clean_pdf(self.path, out, self.text.text.strip(), self.img.active)
            self.status.text = "সেভ হয়েছে:\n" + out
        except Exception as e:
            self.status.text = "ত্রুটি: %s" % e


class PdfApp(App):
    def build(self):
        if platform == "android":
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.READ_EXTERNAL_STORAGE,
                                 Permission.WRITE_EXTERNAL_STORAGE])
        return Root()


PdfApp().run()
