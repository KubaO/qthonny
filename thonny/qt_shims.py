from PyQt6.QtCore import Qt
from PyQt6 import QtCore as qtc, QtGui as qtg, QtWidgets as qtw
import weakref


class Variable(qtc.QObject):
    def __init__(self, value, *, parent):
        super().__init__(parent)
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value
        self.changed.emit(value)
        return value

    def trace(self, what, callable):
        if what == 'w':
            self.changed.connect(callable)
        else:
            raise NotImplementedError


class IntVar(Variable):
    changed = qtc.pyqtSignal(int, name="changed")

    def __init__(self, value = 0, *, parent = None):
        super().__init__(value, parent=parent)


class StringVar(Variable):
    changed = qtc.pyqtSignal(str, name="changed")

    def __init__(self, value = "", *, parent = None):
        super().__init__(value, parent=parent)


class PhotoImage(qtg.QImage):
    def __init__(self, **kwargs):
        initialized = False
        for key, val in kwargs.items():
            if key == 'file':
                super().__init__(val)
                initialized = True
            else:
                raise NotImplementedError
        if not initialized:
            super().__init__()


class TTkMixin:
    def grid(self, *, row: int = -1, column: int = 0, rowspan: int = 1, columnspan: int = 1, sticky: str = "", padx: tuple[int,int] = (0,0), pady: tuple[int,int] = (0,0)):
        layout = self.parent().layout()
        if layout is None:
            layout = qtw.QGridLayout(self.parent())
        assert(isinstance(layout, qtw.QGridLayout))
        if row == -1:
            row = layout.rowCount()
        layout.addWidget(self, row, column, rowspan, columnspan)

    def geometry(self, geom: str):
        pass # TODO

    def config(self, **kwargs):
        for key, val in kwargs.items():
            if key == 'state':
                if val == 'disabled':
                    self.setDisabled(True)
                elif val == 'normal':
                    self.setEnabled(True)
            else:
                raise NotImplementedError

    def focus_set(self):
        widget = self
        while widget:
            widget.show()
            widget = widget.parent()
        self.setFocus(Qt.FocusReason.OtherFocusReason)

    def destroy(self):
        self.deleteLater()

    def get(self):
        prop = self.metaObject().userProperty()
        if prop:
            return prop.read(self)
        else:
            raise NotImplementedError

    def set(self, value):
        prop = self.metaObject().userProperty()
        if prop:
            prop.write(self, value)
        else:
            raise NotImplementedError

    def title(self, title: str):
        self.setWindowTitle(title)

    def bind(self, event, callable, *args):
        # TODO: bind(..., True)
        qkey, qevent = (None, None)
        if event == '<Escape>':
            qkey = qtg.QKeySequence('Esc')
        elif event == '<F3>':
            qkey = qtg.QKeySequence('F3')
        elif event == '<Return>' or event == '<KP_Enter>':
            qkey = qtg.QKeySequence('Enter')
        #elif event == '<Button-1>':
        #    qevent = (qtc.QEvent.Type.MouseButtonPress, Qt.LeftButton)
        if qkey:
            short = qtg.QShortcut(qkey, self, context=Qt.ShortcutContext.WidgetShortcut)
            short.activated.connect(callable)
        elif qevent:
            self._add_event_handler(qevent, callable)
            pass
        else:
            raise NotImplementedError

    def _add_event_handler(self, qevent, callable):
        if not hasattr(self, '_event_handlers'):
            self._event_handlers = {}
        handlers = self._event_handlers.setdefault(qevent, [])
        handlers.append(weakref.ref(callable))

    def protocol(self, msg: str, callable):
        if msg == 'WM_DELETE_WINDOW':
            self._add_event_handler(qtc.QEvent.Type.Close, callable)
        else:
            raise NotImplementedError

    def _event(self, event: qtc.QEvent):
        handlers = getattr(self, '_event_handlers', None)
        if handlers:
            ev_handlers = handlers.get(event.type(), None)
            if ev_handlers:
                to_remove = None
                for i, handler in enumerate(ev_handlers):
                    callback = handler()
                    if callback:
                        callback()
                    else:
                        if not to_remove:
                            to_remove = [i]
                        else:
                            to_remove.append(i)
                if to_remove:
                    to_remove.reverse()
                    for i in to_remove:
                        ev_handlers.pop(i)

    def eval(self, cmd: str):
        items = cmd.split()
        if not items:
            return
        if items[0] == 'tk::PlaceWindow':
            if items[2] == 'center':
                pass
            else:
                raise NotImplementedError
        else:
            raise NotImplementedError

    def get_large_padding(self):
        return 0

    def get_medium_padding(self):
        return 0

    def get_small_padding(self):
        return 0

    def columnconfigure(self, col: int, *, weight:int = 0):
        pass

    def rowconfigure(self, col: int, *, weight:int = 0):
        pass


class Frame(qtw.QWidget, TTkMixin):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)
        for key, val in kwargs.items():
            if key == 'className':
                self.setObjectName(val)
            else:
                raise NotImplementedError

    def grid(self, **kwargs):
        TTkMixin.grid(self, **kwargs)
        layout = self.parent().layout()
        if layout:
            layout.setContentsMargins(0, 0, 0, 0)


class CommonDialog(qtw.QDialog, TTkMixin):
    def __init__(self, parent = None, **kwargs):
        if isinstance(parent, qtw.QWidget):
            super().__init__(parent)
        else:
            super().__init__()

        for key, val in kwargs.items():
            if key == 'skip_tk_dialog_attributes':
                pass # TODO
            elif key == 'takefocus':
                pass # TODO
            elif key == 'className':
                self.setObjectName(val)
            else:
                raise NotImplementedError

        app = qtw.QApplication.instance()
        self.setWindowIcon(app.windowIcon())

    def event(self, event: qtc.QEvent) -> bool:
        TTkMixin._event(self, event)
        return super().event(event)

    def geometry(self, *args):
        if len(args) == 1:
            TTkMixin.geometry(self, *args)
        else:
            return qtw.QDialog.geometry(self)

    def resizable(self, *, height: int, width: int):
        if not height and not width:
            if self.layout() is None:
                qtw.QGridLayout(self)
            self.layout().setSizeConstraint(qtw.QLayout.SizeConstraint.SetFixedSize)
        else:
            raise NotImplementedError

    def transient(self, parent):
        pass

    def mainloop(self):
        return self.exec()

    def destroy(self):
        self.accept()
        self.deleteLater()


class CommonDialogEx(CommonDialog):
    def __init__(self, *args):
        super().__init__(*args);
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.main_frame = self

        self.bind("<Escape>", self.on_close, True)

    def on_close(self, event=None):
        self.reject()


class Tk(CommonDialog):
    pass


class Label(qtw.QLabel, TTkMixin):
    def __init__(self, parent, **kwargs):
        super().__init__(parent)
        stylesheet = ""
        for key, val in kwargs.items():
            if key == 'text':
                self.setText(val)
            elif key == 'textvariable':
                if not val.parent():
                    val.setParent(parent)
                self.setText(val.get())
                val.changed.connect(self.setText)
            elif key == 'foreground':
                stylesheet += f"color : {val};"
            elif key == 'font':
                self.setFont(val.qfont)
            elif key == 'justify':
                if val == CENTER:
                    self.setAlignment(Qt.AlignmentFlag.AlignCenter)
                else:
                    raise NotImplementedError
            elif key == 'image':
                assert(isinstance(val, PhotoImage))
                self.setPixmap(qtg.QPixmap.fromImage(val))
            else:
                raise NotImplementedError
        if stylesheet:
            self.setStyleSheet(stylesheet)


class Entry(qtw.QLineEdit, TTkMixin):
    def __init__(self, parent, **kwargs):
        super().__init__(parent)
        for key, val in kwargs.items():
            if key == 'textvariable':
                if not val.parent():
                    val.setParent(parent)
                self.setText(val.get())
                self.textChanged.connect(val.set)
            else:
                raise NotImplementedError

    def insert(self, index: int, text: str):
        assert(index == 0)
        self.setText(text)

    def selection_range(self, start, end):
        if start == 0 and end == 'end':
            self.selectAll()
        else:
            raise NotImplementedError

class Combobox(qtw.QComboBox, TTkMixin):
    def __init__(self, parent, **kwargs):
        super().__init__(parent)
        self._textvariable = None
        for key, val in kwargs.items():
            if key == 'exportselection':
                pass
            elif key == 'state':
                pass
            elif key == 'height' or key == 'width':
                pass
            elif key == 'values':
                self.addItems(val)
            elif key == 'textvariable':
                self._textvariable = val
            else:
                raise NotImplementedError

        if self._textvariable:
            index = self.findText(self._textvariable.get())
            if index >= 0:
                self.setCurrentIndex(index)
            self.currentTextChanged.connect(self._textvariable.set)


class Checkbutton(qtw.QCheckBox, TTkMixin):
    def __init__(self, parent, **kwargs):
        super().__init__(parent)
        for key, val in kwargs.items():
            if key == 'text':
                self.setText(val)
            elif key == 'variable':
                if not val.parent():
                    val.setParent(parent)
                self.var = val
                self.checkStateChanged.connect(self._new_state)
            else:
                raise NotImplementedError

    def _new_state(self, state: Qt.CheckState):
        self.var.set(1 if state == Qt.CheckState.Checked else 0)


class Button(qtw.QPushButton, TTkMixin):
    def __init__(self, parent, **kwargs):
        super().__init__(parent)
        for key, val in kwargs.items():
            if key == 'text':
                self.setText(val)
            elif key == 'width':
                pass
            elif key == 'default':
                pass
            elif key == 'command':
                self.clicked.connect(val)
            else:
                raise NotImplementedError


class Radiobutton(qtw.QRadioButton, TTkMixin):
    def __init__(self, parent, **kwargs):
        super().__init__(parent)
        for key, val in kwargs.items():
            if key == 'text':
                self.setText(val)
            elif key == 'variable':
                var = val
                button_value = kwargs['value']
                if not var.parent():
                    var.setParent(self.parent())
                group = var.findChild(qtw.QButtonGroup)
                if not group:
                    group = qtw.QButtonGroup(var)
                    group.idClicked.connect(var.set)
                group.addButton(self, button_value)
            elif key == 'value':
                # handled with variable above
                pass
            else:
                raise NotImplementedError

    def invoke(self):
        self.click()


class Font:
    def __init__(self, *args, **kwargs):
        self.qfont = qtg.QFont(*args)

    def copy(self):
        return Font(self.qfont)

    def configure(self, **kwargs):
        for key, val in kwargs.items():
            if key == 'size':
                self.qfont.setPointSizeF(val)
            elif key == 'weight':
                if val == 'bold':
                    self.qfont.setBold(True)
                else:
                    raise NotImplementedError
            else:
                raise KeyError

    def __getitem__(self, key):
        if key == 'size':
            return self.qfont.pointSizeF()
        elif key == 'weight':
            if self.qfont.bold():
                return 'bold'
            else:
                raise NotImplementedError
        else:
            raise KeyError

    def measure(self, text: str):
        metrics = qtg.QFontMetricsF(self.qfont)
        size = metrics.size(Qt.TextFlag.TextSingleLine, text)
        return size.width()

    @staticmethod
    def nametofont(name: str):
        if name == 'TkDefaultFont':
            return Font()
        elif name == 'TkHeadingFont':
            font = Font()
            font.configure(size=9)
            return font
        else:
            raise NotImplementedError


class Style:
    def theme_use(self, theme):
        # this may do something in the future
        pass


def create_url_label(master, url, text=None, **kw):
    text = text.replace("\n", "<br/>") if text else url
    url_label = Label(master, text=f'<a href="{url}">{text}</a>', **kw)
    # QLabel handles the hyperlink cursor automatically
    url_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
    url_label.setOpenExternalLinks(True)
    return url_label


def create_string_var(value: str, callable):
    var = StringVar(value = value)
    var.changed.connect(callable)
    return var


def ems_to_pixels(x: float) -> int:
    global EM_WIDTH
    if EM_WIDTH is None:
        EM_WIDTH = font.nametofont("TkDefaultFont").measure("m")
    return int(EM_WIDTH * x)


def pixels_to_ems(x: int) -> float:
    global EM_WIDTH
    if EM_WIDTH is None:
        EM_WIDTH = font.nametofont("TkDefaultFont").measure("m")
    return x / EM_WIDTH


font = Font

EM_WIDTH = None

END = 'end'
FALSE = 0
TRUE = 1
W = 'w'
E = 'e'

import tkinter as tk

#END = tk.END
#FALSE = tk.FALSE
#TRUE = tk.TRUE
#W = tk.W
#E = tk.E
CENTER = tk.CENTER
Text = tk.Text

import sys
ttk = sys.modules[__name__]
