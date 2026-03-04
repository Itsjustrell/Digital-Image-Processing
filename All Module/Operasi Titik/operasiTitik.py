import os
import sys
import math
import cv2
import numpy as np
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi

class ShowImage(QMainWindow):
    def __init__(self):
        super().__init__()
        ui_path = os.path.join(os.path.dirname(__file__), "operasiTitik.ui")
        loadUi(ui_path, self)

        self.image = None
        self.rgb_image = None
        self.gray_image = None
        self.brightness_image = None
        self.contrast_image = None
        self.contrast_stretching_image = None
        self.negative_image = None
        self.binary_image = None

        self.loadbutton.clicked.connect(self.loadClicked)
        self.GrayScaleButton.triggered.connect(self.grayClicked)

        brightness_action = getattr(self, "actionBrightness", None) or getattr(
            self, "actionBrightness_2", None
        )
        if brightness_action is not None:
            brightness_action.triggered.connect(self.brightnessClicked)

        self.actionSimpleContrast.triggered.connect(self.contrastClicked)
        self.actionContrastStretching.triggered.connect(self.contrastStretchingClicked)
        self.actionNegative.triggered.connect(self.negativeClicked)
        self.actionBinerImage.triggered.connect(self.binaryClicked)
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

    def loadImage(self, filename):
        self.image = cv2.imread(filename)
        if self.image is None:
            QtWidgets.QMessageBox.warning(self, "Load Image", f"Gagal membuka: {filename}")
            return

        self.rgb_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        self.gray_image = None
        self.brightness_image = None
        self.contrast_image = None
        self.contrast_stretching_image = None
        self.negative_image = None
        self.binary_image = None

        self.displayImage(self.image, window=1)

    def createGray(self):
        if self.rgb_image is None:
            return None

        h, w = self.rgb_image.shape[:2]
        gray = np.zeros((h, w), np.uint8)
        for i in range(h):
            for j in range(w):
                gray[i, j] = np.clip(
                    0.299 * self.rgb_image[i, j, 0]
                    + 0.587 * self.rgb_image[i, j, 1]
                    + 0.114 * self.rgb_image[i, j, 2],
                    0,
                    255,
                )

        self.gray_image = gray
        return gray

    @pyqtSlot()
    def grayClicked(self):
        if self.rgb_image is None:
            QtWidgets.QMessageBox.information(self, "Info", "Load image terlebih dahulu.")
            return

        gray = self.createGray()
        self.displayImage(gray, window=2)

    @pyqtSlot()
    def brightnessClicked(self):
        if self.rgb_image is None:
            QtWidgets.QMessageBox.information(self, "Info", "Load image terlebih dahulu.")
            return

        gray = self.createGray()
        if gray is None:
            return

        brightness = 50
        h, w = gray.shape[:2]
        img = gray.copy()

        for i in range(h):
            for j in range(w):
                a = int(gray[i, j])
                b = a + brightness
                if b > 255:
                    b = 255
                elif b < 0:
                    b = 0
                img[i, j] = b

        self.brightness_image = img
        self.displayImage(self.brightness_image, window=2)

    @pyqtSlot()
    def contrastClicked(self):
        if self.rgb_image is None:
            QtWidgets.QMessageBox.information(self, "Info", "Load image terlebih dahulu.")
            return

        gray = self.createGray()
        if gray is None:
            return

        contrast = 1.6
        h, w = gray.shape[:2]
        img = gray.copy()

        for i in range(h):
            for j in range(w):
                a = int(gray[i, j])
                b = math.ceil(a * contrast)
                if b > 255:
                    b = 255
                elif b < 0:
                    b = 0
                img[i, j] = b

        self.contrast_image = img
        self.displayImage(self.contrast_image, window=2)

    @pyqtSlot()
    def contrastStretchingClicked(self):
        if self.image is None:
            QtWidgets.QMessageBox.information(self, "Info", "Load image terlebih dahulu.")
            return

        img = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

        max_pixel = 255
        min_pixel = 0

        rmin = int(np.min(img))
        rmax = int(np.max(img))

        h, w = img.shape[:2]
        for i in range(h):
            for j in range(w):
                a = int(img[i, j])

                if a > max_pixel:
                    a = max_pixel
                elif a < min_pixel:
                    a = min_pixel

                if rmax == rmin:
                    b = a
                else:
                    b = ((a - rmin) / (rmax - rmin)) * (max_pixel - min_pixel) + min_pixel

                img[i, j] = int(np.clip(round(b), min_pixel, max_pixel))

        self.contrast_stretching_image = img
        self.displayImage(self.contrast_stretching_image, window=2)

    @pyqtSlot()
    def negativeClicked(self):
        if self.image is None:
            QtWidgets.QMessageBox.information(self, "Info", "Load image terlebih dahulu.")
            return

        img = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        maximum_intensity = 255

        h, w = img.shape[:2]
        for i in range(h):
            for j in range(w):
                a = int(img[i, j])
                b = maximum_intensity - a
                img[i, j] = b

        self.negative_image = img
        self.displayImage(self.negative_image, window=2)

    @pyqtSlot()
    def binaryClicked(self):
        if self.image is None:
            QtWidgets.QMessageBox.information(self, "Info", "Load image terlebih dahulu.")
            return

        gray = self.createGray()
        if gray is None:
            return

        h, w = gray.shape
        binary_img = gray.copy()

        for i in range(h):
            for j in range(w):
                pixel_value = int(binary_img[i, j])
                if pixel_value <= 180:
                    new_value = 0
                else:
                    new_value = 255
                binary_img[i, j] = new_value

        self.binary_image = binary_img
        self.displayImage(self.binary_image, window=2)

    @pyqtSlot()
    def saveClicked(self):
        if self.binary_image is not None:
            image_to_save = self.binary_image
        elif self.negative_image is not None:
            image_to_save = self.negative_image
        elif self.contrast_stretching_image is not None:
            image_to_save = self.contrast_stretching_image
        elif self.contrast_image is not None:
            image_to_save = self.contrast_image
        elif self.brightness_image is not None:
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

    def displayImage(self, image, window=1):
        if image is None:
            return

        if len(image.shape) == 2:
            qformat = QImage.Format_Grayscale8
        elif image.shape[2] == 4:
            qformat = QImage.Format_RGBA8888
        else:
            qformat = QImage.Format_RGB888

        qimg = QImage(
            image.data,
            image.shape[1],
            image.shape[0],
            image.strides[0],
            qformat,
        )
        if qformat in (QImage.Format_RGB888, QImage.Format_RGBA8888):
            qimg = qimg.rgbSwapped()

        target_label = self.inputwindow if window == 1 else self.outputwindow
        target_label.setPixmap(QPixmap.fromImage(qimg))
        target_label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        target_label.setScaledContents(True)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ShowImage()
    window.setWindowTitle("Show Image GUI")
    window.show()
    sys.exit(app.exec_())
