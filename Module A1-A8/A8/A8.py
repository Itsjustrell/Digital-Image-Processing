import sys
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
        loadUi("A8.ui", self)
        self.image = None
        self.gray_image = None
        self.brightness_image = None
        self.contrast_image = None
        self.contrast_stretching_image = None
        self.negative_image = None
        self.binary_image = None

        self.loadbutton.clicked.connect(self.loadClicked)
        self.GrayScaleButton.clicked.connect(self.grayClicked)
        self.saveButton.clicked.connect(self.saveClicked)
        self.actionBrightness.triggered.connect(self.brightnessClicked)
        self.actionSimpleContrast.triggered.connect(self.contrastClicked)
        self.actionContrastStretching.triggered.connect(self.contrastStretchingClicked)
        self.actionNegative.triggered.connect(self.negativeClicked)
        self.actionBinerImage.triggered.connect(self.binaryClicked)

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

        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.gray_image = gray
        self.displayImage(self.gray_image, window=2)

    @pyqtSlot()
    def brightnessClicked(self):
        if self.gray_image is None:
            QtWidgets.QMessageBox.information(
                self,
                "Info",
                "Klik Grayscale dulu untuk menghasilkan image grayscale.",
            )
            return

        brightness = 50
        bright = np.clip(self.gray_image.astype(np.int16) + brightness, 0, 255).astype(np.uint8)
        self.brightness_image = bright
        self.displayImage(self.brightness_image, window=3)

    @pyqtSlot()
    def contrastClicked(self):
        if self.gray_image is None:
            QtWidgets.QMessageBox.information(
                self,
                "Info",
                "Klik Grayscale dulu untuk menghasilkan image grayscale.",
            )
            return

        # Persamaan contrast: b = ceil(a * c)
        c = 1.6
        h, w = self.gray_image.shape
        contrast_img = np.zeros((h, w), dtype=np.uint8)

        for i in range(h):
            for j in range(w):
                a = int(self.gray_image[i, j])
                b = math.ceil(a * c)

                # Clipping ke rentang 0..255
                if b > 255:
                    b = 255
                elif b < 0:
                    b = 0

                contrast_img[i, j] = b

        self.contrast_image = contrast_img
        self.displayImage(self.contrast_image, window=4)

    @pyqtSlot()
    def contrastStretchingClicked(self):
        if self.gray_image is None:
            QtWidgets.QMessageBox.information(
                self,
                "Info",
                "Klik Grayscale dulu untuk menghasilkan image grayscale.",
            )
            return

        # Soal 1: Tentukan konstanta nilai minimum dan maksimum piksel untuk citra 8-bit.
        PIXEL_MIN = 0
        PIXEL_MAX = 255

        h, w = self.gray_image.shape
        stretched_img = np.zeros((h, w), dtype=np.uint8)

        # Gunakan rmin/rmax aktual citra untuk Persamaan (6).
        min_val = int(np.min(self.gray_image))
        max_val = int(np.max(self.gray_image))
        denom = max_val - min_val

        for i in range(h):
            for j in range(w):
                # Soal 2: Baca nilai array piksel pada koordinat (i, j).
                a = int(self.gray_image[i, j])

                # Soal 3: Jika nilai piksel > maksimum, set ke nilai maksimum.
                if a > PIXEL_MAX:
                    a = PIXEL_MAX

                # Soal 4: Jika nilai piksel < minimum, set ke nilai minimum.
                if a < PIXEL_MIN:
                    a = PIXEL_MIN

                # Soal 5: Terapkan Persamaan (6) untuk contrast stretching.
                # b = (a - min) / (max - min) * (L - 1), dengan L = 256.
                if denom == 0:
                    b = a
                else:
                    b = ((a - min_val) / denom) * (PIXEL_MAX - PIXEL_MIN) + PIXEL_MIN

                stretched_img[i, j] = np.uint8(np.clip(round(b), PIXEL_MIN, PIXEL_MAX))

        self.contrast_stretching_image = stretched_img

        print("\n=== ANALISIS CONTRAST STRETCHING (A8) ===")
        print(f"rmin: {min_val}, rmax: {max_val}")

        # Soal 6: Tampilkan hasil image.
        self.displayImage(self.contrast_stretching_image, window=5)

    @pyqtSlot()
    def negativeClicked(self):
        if self.gray_image is None:
            QtWidgets.QMessageBox.information(
                self,
                "Info",
                "Klik Grayscale dulu untuk menghasilkan image grayscale.",
            )
            return

        # Soal 1
        # Command Soal 1: maximum_intensity = 255
        maximum_intensity = 255

        h, w = self.gray_image.shape
        negative_img = np.zeros((h, w), dtype=np.uint8)

        for i in range(h):
            for j in range(w):
                # Soal 2
                # Command Soal 2: pixel_value = self.gray_image[i, j]
                pixel_value = int(self.gray_image[i, j])

                # Soal 3
                # Command Soal 3: new_value = maximum_intensity - pixel_value
                new_value = maximum_intensity - pixel_value
                negative_img[i, j] = np.uint8(new_value)

        self.negative_image = negative_img

        # Soal 4
        # Command Soal 4: self.displayImage(self.negative_image, window=6)
        self.displayImage(self.negative_image, window=6)

    @pyqtSlot()
    def binaryClicked(self):
        if self.gray_image is None:
            QtWidgets.QMessageBox.information(
                self,
                "Info",
                "Klik Grayscale dulu untuk menghasilkan image grayscale.",
            )
            return

        # Command Soal 1: Konversi grayscale ke biner dengan threshold utama.
        threshold_value = 128
        h, w = self.gray_image.shape
        binary_img = np.zeros((h, w), dtype=np.uint8)

        for i in range(h):
            for j in range(w):
                # Command Soal 2: Baca piksel grayscale dan bandingkan dengan threshold.
                pixel_value = int(self.gray_image[i, j])
                binary_img[i, j] = 255 if pixel_value >= threshold_value else 0

        # Command Soal 3: Display hasil citra biner.
        self.binary_image = binary_img
        self.displayImage(self.binary_image, window=7)

        # Command Soal 4: Analisis threshold signifikan.
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

        if window == 1:
            target_label = self.imglabel
        elif window == 2:
            target_label = self.imglabel_2
        elif window == 3:
            target_label = getattr(self, "imglabel3", None) or getattr(self, "imglabel_3", None)
            if target_label is None:
                QtWidgets.QMessageBox.warning(
                    self,
                    "UI Error",
                    "Label brightness (imglabel3/imglabel_3) tidak ditemukan di A8.ui.",
                )
                return
        elif window == 4:
            target_label = getattr(self, "imglabel4", None) or getattr(self, "imglabel_4", None)
            if target_label is None:
                QtWidgets.QMessageBox.warning(
                    self,
                    "UI Error",
                    "Label contrast (imglabel4/imglabel_4) tidak ditemukan di A8.ui.",
                )
                return
        elif window == 5:
            target_label = getattr(self, "imglabel5", None) or getattr(self, "imglabel_5", None)
            if target_label is None:
                QtWidgets.QMessageBox.warning(
                    self,
                    "UI Error",
                    "Label contrast stretching (imglabel5/imglabel_5) tidak ditemukan di A8.ui.",
                )
                return
        elif window == 6:
            target_label = getattr(self, "imglabel6", None) or getattr(self, "imglabel_6", None)
            if target_label is None:
                QtWidgets.QMessageBox.warning(
                    self,
                    "UI Error",
                    "Label negative image (imglabel6/imglabel_6) tidak ditemukan di A8.ui.",
                )
                return
        else:
            target_label = getattr(self, "imglabel7", None) or getattr(self, "imglabel_7", None)
            if target_label is None:
                QtWidgets.QMessageBox.warning(
                    self,
                    "UI Error",
                    "Label biner image (imglabel7/imglabel_7) tidak ditemukan di A8.ui.",
                )
                return

        target_label.setPixmap(QPixmap.fromImage(qimg))
        target_label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        target_label.setScaledContents(True)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ShowImage()
    window.setWindowTitle("Show Image GUI")
    window.show()
    sys.exit(app.exec_())
