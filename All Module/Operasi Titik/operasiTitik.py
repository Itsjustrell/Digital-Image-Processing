import sys
import os
import cv2
import numpy as np
import math
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi


class ShowImage(QMainWindow):
    def __init__(self):
        super(ShowImage, self).__init__()
        ui_path = os.path.join(os.path.dirname(__file__), "operasiTitik.ui")
        loadUi(ui_path, self)
        self.image = None
        self.gray_image = None
        self.brightness_image = None
        self.contrast_image = None
        self.contrast_stretching_image = None
        self.negative_image = None
        self.binary_image = None

        # Operasi Titik
        self.loadbutton.clicked.connect(self.loadClicked)
        self.GrayScaleButton.triggered.connect(self.grayClicked)
        self.saveButton.clicked.connect(self.saveClicked)
        brightness_action = getattr(self, "actionBrightness", None) or getattr(
            self, "actionBrightness_2", None
        )
        if brightness_action is not None:
            brightness_action.triggered.connect(self.brightnessClicked)
        self.actionSimpleContrast.triggered.connect(self.contrastClicked)
        self.actionContrastStretching.triggered.connect(self.contrastStretchingClicked)
        self.actionNegative.triggered.connect(self.negativeClicked)
        biner_action = getattr(self, "actionBinerImage", None) or getattr(
            self, "actionBiner_Image", None
        )
        if biner_action is not None:
            biner_action.triggered.connect(self.binaryClicked)

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
        self.gray_image = None
        self.brightness_image = None
        self.contrast_image = None
        self.contrast_stretching_image = None
        self.negative_image = None
        self.binary_image = None
        self.displayImage(self.image, window=1)

    @pyqtSlot()
    def grayClicked(self):
        if self.image is None:
            QtWidgets.QMessageBox.information(self, "Info", "Load image terlebih dahulu.")
            return

        H, W = self.image.shape[:2]
        gray = np.zeros((H, W), np.uint8)
        for i in range(H):
            for j in range(W):
                gray[i, j] = np.clip(
                    0.299 * self.image[i, j, 2]
                    + 0.587 * self.image[i, j, 1]
                    + 0.114 * self.image[i, j, 0],
                    0,
                    255,
                )

        self.gray_image = gray
        self.displayImage(self.gray_image, window=2)

    @pyqtSlot()
    def brightnessClicked(self):
        if self.image is None:
            QtWidgets.QMessageBox.information(
                self,
                "Info",
                "Load image terlebih dahulu.",
            )
            return

        img = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        # tentukan konstanta nilai bright
        brightness = 50
        # Baca Nilai piksel citra
        h, w = img.shape[:2]
        # untuk masing-masing array piksel dilakukan penjumlahan dengan konstanta
        for i in np.arange(h):
            for j in np.arange(w):
                a = img.item(i, j)
                b = a + brightness
                # terapkan proses clipping
                if b > 255:
                    b = 255
                elif b < 0:
                    b = 0
                else:
                    b = b
                img.itemset((i, j), b)

        self.brightness_image = img
        self.displayImage(self.brightness_image, window=3)

    @pyqtSlot()
    def contrastClicked(self):
        if self.image is None:
            QtWidgets.QMessageBox.information(
                self,
                "Info",
                "Load image terlebih dahulu.",
            )
            return

        img = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        # tentukan konstanta nilai kontras
        contrast = 1.6
        # Baca Nilai piksel citra
        h, w = img.shape[:2]
        # untuk masing-masing array piksel dilakukan pengali denga konstanta kontras
        for i in np.arange(h):
            for j in np.arange(w):
                a = img.item(i, j)
                b = math.ceil(a * contrast)

                # Clipping ke rentang 0..255
                if b > 255:
                    b = 255
                elif b < 0:
                    b = 0

                img.itemset((i, j), b)

        self.contrast_image = img
        self.displayImage(self.contrast_image, window=4)

    @pyqtSlot()
    def contrastStretchingClicked(self):
        if self.image is None:
            QtWidgets.QMessageBox.information(
                self,
                "Info",
                "Load image terlebih dahulu.",
            )
            return

        img = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

        # 1. Tentukan nilai konstanta maksimum dan minimum piksel (citra 8-bit).
        max_pixel = 255
        min_pixel = 0

        # rmin dan rmax dari citra semula.
        rmin = int(np.min(img))
        rmax = int(np.max(img))

        h, w = img.shape[:2]
        for i in np.arange(h):
            for j in np.arange(w):
                # 2. Baca nilai array piksel.
                a = int(img.item(i, j))

                # 3. Jika nilai piksel > nilai maksimum, set ke maksimum.
                if a > max_pixel:
                    a = max_pixel
                # 4. Jika nilai piksel < nilai minimum, set ke minimum.
                elif a < min_pixel:
                    a = min_pixel

                # 5. Terapkan Persamaan (6): S = (R-rmin)/(rmax-rmin) * (max-min) + min
                if rmax == rmin:
                    b = a
                else:
                    b = ((a - rmin) / (rmax - rmin)) * (max_pixel - min_pixel) + min_pixel
                img.itemset((i, j), int(np.clip(round(b), min_pixel, max_pixel)))

        self.contrast_stretching_image = img
        self.displayImage(self.contrast_stretching_image, window=5)

    @pyqtSlot()
    def negativeClicked(self):
        if self.image is None:
            QtWidgets.QMessageBox.information(
                self,
                "Info",
                "Load image terlebih dahulu.",
            )
            return

        img = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

        # 1. Tentukan nilai konstanta maximum_intensity = 255
        maximum_intensity = 255

        h, w = img.shape[:2]
        for i in np.arange(h):
            for j in np.arange(w):
                # 2. Baca nilai array piksel
                pixel_value = int(img.item(i, j))
                # 3. Terapkan Persamaan (7): f'(x,y) = 255 - f(x,y)
                new_value = maximum_intensity - pixel_value
                img.itemset((i, j), new_value)

        self.negative_image = img
        self.displayImage(self.negative_image, window=6)

    @pyqtSlot()
    def binaryClicked(self):
        if self.image is None and self.gray_image is None:
            QtWidgets.QMessageBox.information(
                self,
                "Info",
                "Load image terlebih dahulu.",
            )
            return

        # Prerequisite: gunakan citra grayscale dari praktek sebelumnya jika ada.
        # Jika belum ada, konversi dari citra input.
        img_gray = (
            self.gray_image
            if self.gray_image is not None
            else cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        )
        self.gray_image = img_gray

        # 1. Implementasi konversi grayscale -> biner.
        threshold_value = 128
        h, w = img_gray.shape
        binary_img = np.zeros((h, w), dtype=np.uint8)

        for i in np.arange(h):
            for j in np.arange(w):
                pixel_value = int(img_gray.item(i, j))
                binary_img[i, j] = 255 if pixel_value >= threshold_value else 0

        # Display hasil citra biner.
        self.binary_image = binary_img
        self.displayImage(self.binary_image, window=7)

        # 2. Analisis threshold dengan nilai yang berbeda signifikan.
        self.analyzeBinaryThresholds([64, 128, 192])

    def analyzeBinaryThresholds(self, thresholds):
        total = int(self.gray_image.size)
        avg_before = float(np.mean(self.gray_image))
        print("\n=== ANALISIS GRAYSCALE -> BINER ===")
        print(f"Total piksel: {total}")
        print(f"Rata-rata grayscale (sebelum): {avg_before:.2f}")

        for t in thresholds:
            white = int(np.sum(self.gray_image >= t))
            black = total - white
            pct_white = (white / total) * 100.0
            pct_black = (black / total) * 100.0
            print(
                f"Threshold {t:3d}: putih={white} ({pct_white:.2f}%), "
                f"hitam={black} ({pct_black:.2f}%)"
            )

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

        # operasiTitik.ui menggunakan 2 label: inputwindow dan outputwindow.
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
