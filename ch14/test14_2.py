import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.image import imread

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
    QWidget, QFileDialog, QMessageBox, QMenuBar, QStatusBar
)

class InteractivePlot(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Interactive Image Editor")
        self.resize(800, 600)

        # 상태 표시줄 설정
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        # 메뉴 바 설정
        self.menuBar = QMenuBar(self)
        self.setMenuBar(self.menuBar)
        file_menu = self.menuBar.addMenu("File")
        load_action = file_menu.addAction("Load Image")
        load_action.triggered.connect(self.load_image_from_menu)

        # 메인 레이아웃 설정
        main_layout = QVBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # 그래프 영역 설정
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.axis('off')  # 축을 초기에 비활성화하여 이미지만 표시

        main_layout.addWidget(self.canvas)

        # 마우스 드래그 상태 및 사각형 선택을 위한 변수 초기화
        self.dragging = False
        self.rect = None
        self.start_point = (0, 0)
        self.click_count = 0  # 클릭 횟수 카운트를 위한 변수
        self.image = None

        # 마우스 클릭 및 더블클릭 이벤트 연결
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.mpl_connect('motion_notify_event', self.on_drag)
        self.canvas.mpl_connect('button_release_event', self.on_release)

    def load_image_from_menu(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 
                                                   "Open Image", 
                                                   "", 
                                                   "Image Files (*.png *.jpg *.bmp)")
        if file_name:
            self.load_image(file_name)

    def load_image(self, file_name):
        if not file_name.lower().endswith(('.png', '.jpg', '.bmp')):
            QMessageBox.warning(self, "Invalid File", "Please select a valid image file.")
            return
        self.image = imread(file_name)
        self.ax.clear()
        self.ax.imshow(self.image)
        self.ax.axis('on')
        self.canvas.draw()
        self.statusBar.showMessage(f"Loaded image: {file_name}")

    def on_click(self, event):
        if self.image is None:
            return
        if event.button == 3:
            self.on_right_click(event)
        else:
            if event.inaxes != self.ax:
                return
            self.dragging = True
            self.start_point = (event.xdata, event.ydata)
            self.rect = self.ax.add_patch(
                plt.Rectangle(self.start_point, 0, 0, fill=False, color='red')
            )
            self.canvas.draw()

    def on_right_click(self, event):
        if self.image is None:
            return
        if event.dblclick:
            self.ax.add_patch(
                plt.Circle((event.xdata, event.ydata), 10, color='blue', fill=True)
            )
            self.canvas.draw()

    def on_drag(self, event):
        if self.image is None:
            return
        if not self.dragging or not event.inaxes:
            return
        if event.dblclick:
            return 
        x0, y0 = self.start_point
        x1, y1 = event.xdata, event.ydata
        self.rect.set_width(x1 - x0)
        self.rect.set_height(y1 - y0)
        self.rect.set_xy((min(x0, x1), min(y0, y1)))
        self.canvas.draw()

    def on_release(self, event):
        if self.image is None:
            return
        if event.button == 3:
            return
        if self.dragging:
            self.dragging = False
            response = QMessageBox.question(self, 
                                            "Confirm", 
                                            "Keep the rectangle?", 
                                            QMessageBox.Yes | QMessageBox.No)
            if response == QMessageBox.No:
                self.rect.remove()
            self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mwd = InteractivePlot()
    mwd.show()
    sys.exit(app.exec())
