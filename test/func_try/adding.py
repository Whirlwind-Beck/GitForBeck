import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QHBoxLayout


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.frame_count = 0

        self.setWindowTitle("生成Frame")
        self.setGeometry(100, 100, 400, 500)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.button = QPushButton("生成Frame")
        self.button.clicked.connect(self.generate_frame)
        self.layout.addWidget(self.button)

        self.bottom_frame = QWidget()
        self.bottom_layout = QVBoxLayout()
        self.bottom_frame.setLayout(self.bottom_layout)
        self.bottom_frame.setFixedHeight(300)
        self.layout.addWidget(self.bottom_frame)

    def generate_frame(self):
        self.frame_count += 1
        new_frame = QWidget()
        new_frame.setStyleSheet(
            f"background-color: rgb({255 - self.frame_count * 20}, {255 - self.frame_count * 20}, 255)")

        # 设置新生成的frame紧贴着上方排布
        self.bottom_layout.addLayout(QHBoxLayout())
        self.bottom_layout.addSpacing(10)
        self.bottom_layout.addWidget(new_frame)

        new_frame.setMaximumHeight(70)
        new_frame.setMinimumHeight(70)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
