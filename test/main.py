from LoginUi import *
from InterfaceUi import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QSizePolicy, QPushButton, QFrame
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
import sys
import requests
import os
import folium


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_LoginWindow()
        self.ui.setupUi(self)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        self.shadow.setOffset(3, 4)
        self.shadow.setBlurRadius(10)
        self.shadow.setColor(QtCore.Qt.black)
        self.ui.frame.setGraphicsEffect(self.shadow)
        self.ui.pushButton_Login.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(0))
        self.ui.pushButton_Register.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(1))
        self.ui.pushButton_L_sure.clicked.connect(self.login_in)
        self.ui.pushButton_R_register.clicked.connect(self.register)

        self.dragPosition = QtCore.QPoint()                 # 鼠标点击

        self.show()

    def login_in(self):
        username = self.ui.lineEdit_L_username.text()
        password = self.ui.lineEdit_L_password.text()

        response = requests.post(
            "http://123.57.236.111:801/api/login_in",
            json={"username": username, "password": password}
        )
        if response.status_code == 200:
            if response.json().get("message") == "Logged in successfully":
                self.window = MainWindow()
                self.close()
            else:
                QMessageBox.critical(self, "Error", response.json().get("message"))
        else:
            QMessageBox.critical(self, "Error", "Failed to send JSON data")

    def register(self):
        username = self.ui.lineEdit_R_username.text()
        password = self.ui.lineEdit_R_password.text()
        repassword = self.ui.lineEdit_R_password_re.text()

        if password != repassword:
            QMessageBox.critical(self, "Error", "Passwords do not match")
            return

        response = requests.post(
            "http://123.57.236.111:801/api/register",
            json={"username": username, "password": password}
        )
        if response.status_code == 200:
            QMessageBox.information(self, "Success", "Registration successful")
        else:
            QMessageBox.critical(self, "Error", "Failed to send JSON data")

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            self.move(event.globalPos() - self.dragPosition)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.dragPosition = QtCore.QPoint()

    def keyPressEvent(self, event):
        # 在登录页面按下回车键
        if self.ui.stackedWidget_2.currentIndex() == 0 and event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter:
            self.login_in()

        # 在注册页面按下回车键
        elif self.ui.stackedWidget_2.currentIndex() == 1 and event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter:
            self.register()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        # self.ui.pushButton_Login.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(0))

        # self.ui.pushButton_track.clicked.connect(self.load_track)
        self.ui.pushButton_adding.clicked.connect(self.addButton)

        self.dragPosition = QtCore.QPoint()                 # 鼠标点击
        self.load_map()
        # 获取scrollAreaWidgetContents的布局
        self.content_layout = QtWidgets.QVBoxLayout(self.ui.scrollAreaWidgetContents)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        self.frames = []  # 保存frame的引用

        self.show()

    def load_map(self):
        # 创建地图
        Map = folium.Map(
            location=[39.059960224517766, 117.13505134076973],
            control_scale=True,
            zoom_start=15,
            tiles='https://webrd02.is.autonavi.com/appmaptile?lang=zh_en&size=1&scale=1&style=8&x={x}&y={y}&z={z}',
            attr="gaodeditu"
        )
        Map.add_child(folium.LatLngPopup())
        Map.add_child(folium.ClickForMarker(popup='Waypoint'))

        # 创建新的图层并将其添加到地图上
        feature_group = folium.FeatureGroup(name="Track")
        response = requests.get("http://123.57.236.111:801/api/track")
        data = response.json()
        for point in data:
            lon, lat = point["lon"], point["lat"]
            marker = folium.Marker([lat, lon])
            feature_group.add_child(marker)
        Map.add_child(feature_group)

        # 保存地图为HTML文件
        map_path = "save_map.html"
        Map.save(map_path)

        # 加载地图到QWebEngineView
        self.map = QWebEngineView(self.ui.frame_13)
        self.map.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.map.setGeometry(QtCore.QRect(0, 0, self.ui.frame_13.width(), self.ui.frame_13.height()))
        self.ui.frame_13.layout().addWidget(self.map)

        def set_map_size():
            self.map.resize(self.ui.frame_13.size())

        self.map.loadFinished.connect(set_map_size)

        path = QtCore.QUrl.fromLocalFile(os.path.abspath(map_path))
        self.map.load(path)
        self.map.show()

    def addButton(self):
        # 创建一个新的 QFrame，并设置样式和背景颜色
        frame = QtWidgets.QFrame()
        frame.setStyleSheet("background-color: gray")
        frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        frame.setFrameShadow(QtWidgets.QFrame.Raised)

        # 创建内部垂直布局
        verticalLayout = QtWidgets.QVBoxLayout(frame)
        verticalLayout.setContentsMargins(0, 0, 0, 0)
        verticalLayout.setSpacing(0)

        # 创建编号按钮，并设置编号随着frame的增减而调整
        button = QtWidgets.QPushButton()
        # button.setText(str(self.ui.scrollAreaWidgetContents.count() + 1))
        button.setStyleSheet("border: none;")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setVerticalStretch(4)
        button.setSizePolicy(sizePolicy)

        # 创建进度条，并设置样式和大小策略
        progressBar = QtWidgets.QProgressBar()
        progressBar.setAlignment(QtCore.Qt.AlignCenter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setVerticalStretch(1)
        progressBar.setSizePolicy(sizePolicy)

        # 将按钮和进度条添加到垂直布局中
        verticalLayout.addWidget(button)
        verticalLayout.addWidget(progressBar)

        # 设置frame的布局为垂直布局
        frame.setLayout(verticalLayout)

        # 设置frame的最大高度为200
        frame.setMaximumHeight(70)
        frame.setMinimumHeight(70)

        # 在顶部插入新的frame
        self.content_layout.insertWidget(0, frame)
        # 将frame的引用保存到列表中
        self.frames.append(frame)
        
    def updateFrameInfo(self, frame_index, new_text):
        if 0 <= frame_index < len(self.frames):
            button = self.frames[frame_index].findChild(QtWidgets.QPushButton)
            if button:
                button.setText(new_text)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            self.move(event.globalPos() - self.dragPosition)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.dragPosition = QtCore.QPoint()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LoginWindow()
    # window = MainWindow()
    sys.exit(app.exec_())

