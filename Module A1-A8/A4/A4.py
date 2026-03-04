import sys
import cv2
import numpy as np
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi

class ShowImage(QMainWindow):
    def __init__(self):
        super(ShowImage, self).__init__()
        loadUi("A4.ui", self)
        self.image = None
        self.rgb_image = None
        self.gray_image = None
        self.brightness_image = None

        self.loadbutton.clicked.connect(self.loadClicked)
        self.actionBrightness.triggered.connect(self.brightnessClicked)
        self.saveButton.clicked.connect(self.saveClicked)

    @pyqtSlot()
    def loadClicked(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Open Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*)",
        )
        if not filename:
            return
        self.loadImage(filename)

    def loadImage(self, flname):
        self.image = cv2.imread(flname)
        if self.image is None:
            QtWidgets.QMessageBox.warning(self, "Load Image", f"Gagal membuka: {flname}")
            return
        self.rgb_image = self.image.copy()
        self.gray_image = None
        self.brightness_image = None
        self.displayImage(1)

    @pyqtSlot()
    def grayClicked(self):
        if self.rgb_image is None:
            QtWidgets.QMessageBox.information(self, "Info", "Load image terlebih dahulu.")
            return

        H, W = self.rgb_image.shape[:2]
        gray = np.zeros((H, W), np.uint8)
        for i in range(H):
            for j in range(W):
                gray[i, j] = np.clip(
                    0.299 * self.rgb_image[i, j, 0]
                    + 0.587 * self.rgb_image[i, j, 1]
                    + 0.114 * self.rgb_image[i, j, 2],
                    0,
                    255,
                )
        self.gray_image = gray
        self.image = gray
        self.displayImage(2)

    @pyqtSlot()
    def brightnessClicked(self):
        if self.rgb_image is None:
            QtWidgets.QMessageBox.information(self, "Info", "Load image terlebih dahulu.")
            return

        # 1-2. Load image RGB lalu konversi ke grayscale pakai def grayClicked
        self.grayClicked()
        gray = self.gray_image.copy()

        # 3. Baca array nilai piksel setiap baris dan kolom
        brightness = 50
        h, w = gray.shape[:2]
        img = gray.copy()

        # 4-5. Terapkan persamaan brightness dan clipping
        for i in range(h):
            for j in range(w):
                a = int(gray[i, j])
                b = a + brightness
                if b > 255:
                    b = 255
                elif b < 0:
                    b = 0
                img[i, j] = b

        self.gray_image = gray
        self.brightness_image = img
        self.image = img

        # 6. Display citra
        self.displayImage(2)

    @pyqtSlot()
    def saveClicked(self):
        if self.brightness_image is not None:
            image_to_save = self.brightness_image
        elif self.gray_image is not None:
            image_to_save = self.gray_image
        else:
            image_to_save = self.image

        if image_to_save is None:
            QtWidgets.QMessageBox.information(self, "Info", "Tidak ada image untuk disimpan.")
            return

        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save Image",
            "",
            "PNG (*.png);;JPG (*.jpg *.jpeg);;BMP (*.bmp);;All Files (*)",
        )
        if not filename:
            return

        if cv2.imwrite(filename, image_to_save):
            QtWidgets.QMessageBox.information(self, "Save Image", f"Berhasil simpan: {filename}")
        else:
            QtWidgets.QMessageBox.warning(self, "Save Image", f"Gagal simpan: {filename}")

    def displayImage(self, windows=1):
        if self.image is None:
            return

        qformat = QImage.Format_Indexed8
        if len(self.image.shape) == 3:
            if self.image.shape[2] == 4:
                qformat = QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888

        img = QImage(
            self.image.data,
            self.image.shape[1],
            self.image.shape[0],
            self.image.strides[0],
            qformat,
        )
        if qformat in (QImage.Format_RGB888, QImage.Format_RGBA8888):
            img = img.rgbSwapped()

        if windows == 1:
            label = getattr(self, "inputwindow", None)
            if label is not None:
                label.setPixmap(QPixmap.fromImage(img))
                label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                label.setScaledContents(True)

        if windows == 2:
            label = getattr(self, "outputwindow", None)
            if label is not None:
                label.setPixmap(QPixmap.fromImage(img))
                label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                label.setScaledContents(True)


app = QtWidgets.QApplication(sys.argv)
window = ShowImage()
window.setWindowTitle("Show Image GUI")
window.show()
sys.exit(app.exec_())
