import sys
from PySide6.QtWidgets import QApplication, QMainWindow

from components.lexica import PropLogicLexer
from components.parser import PropLogicParser
from components.ui import Ui_MainWindow


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Bind buttons
        self.ui.button_t.clicked.connect(lambda: self.push("t"))
        self.ui.button_f.clicked.connect(lambda: self.push("f"))
        self.ui.button_and.clicked.connect(lambda: self.push("and"))
        self.ui.button_imply.clicked.connect(lambda: self.push("->"))
        self.ui.button_or.clicked.connect(lambda: self.push("∨"))
        self.ui.button_clear.clicked.connect(self.clear)
        self.ui.button_equal.clicked.connect(self.evaluate)

        # Also evaluate on Enter key
        self.ui.input_text.returnPressed.connect(self.evaluate)

    def push(self, char: str) -> None:
        current = self.ui.input_text.text()
        self.ui.input_text.setText(current + char)

    def clear(self) -> None:
        self.ui.input_text.clear()
        self.ui.truth_label.setText("—")
        self.ui.prefix_label.setText("—")

    def evaluate(self) -> None:
        text = self.ui.input_text.text().strip()
        if not text:
            return
        try:
            lexer  = PropLogicLexer()
            parser = PropLogicParser()
            result = parser.parse(lexer.tokenize(text))
            if result is None:
                self.ui.truth_label.setText("Error")
                self.ui.prefix_label.setText("Parse error — check your input")
                return
            self.ui.truth_label.setText("t" if result.run() else "f")
            self.ui.prefix_label.setText(result.prefix())
        except Exception as e:
            self.ui.truth_label.setText("Error")
            self.ui.prefix_label.setText(str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
