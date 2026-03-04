import sys
import cv2
import numpy as np
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi
from matplotlib import pyplot as plt


class ShowImage(QMainWindow):
    def __init__(self):
        super(ShowImage, self).__init__()
        loadUi("A11.ui", self)
        self.image = None
        self.gray_image = None

        self.loadbutton.clicked.connect(self.loadClicked)
        self.saveButton.clicked.connect(self.saveClicked)
        action_hist_eq = getattr(self, "actionHistogramEq", None) or getattr(self, "actionRGBHistogram", None)
        if action_hist_eq is not None:
            action_hist_eq.triggered.connect(self.HistogramEq)

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
        self.displayImage(self.image, window=1)

    @pyqtSlot()
    def HistogramEq(self):
        if self.image is None:
            QtWidgets.QMessageBox.information(self, "Info", "Load image terlebih dahulu.")
            return

        hist, bins = np.histogram(self.image.flatten(), 256, [0, 256])
        cdf = hist.cumsum()
        cdf_normalized = cdf * hist.max() / cdf.max()
        cdf_m = np.ma.masked_equal(cdf, 0)
        cdf_m = (cdf_m - cdf_m.min()) * 255 / (cdf_m.max() - cdf_m.min())
        cdf = np.ma.filled(cdf_m, 0).astype("uint8")
        self.image = cdf[self.image]
        self.displayImage(self.image, window=2)
        plt.figure("Histogram Equalization")
        plt.clf()
        plt.plot(cdf_normalized, color="b")
        plt.hist(self.image.flatten(), 256, [0, 256], color="r")
        plt.xlim([0, 256])
        plt.legend(("cdf", "histogram"), loc="upper left")
        plt.show()

    @pyqtSlot()
    def saveClicked(self):
        image_to_save = self.gray_image if self.gray_image is not None else self.image
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

        target_label = self.imglabel if window == 1 else self.imglabel_2
        target_label.setPixmap(QPixmap.fromImage(qimg))
        target_label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        target_label.setScaledContents(True)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ShowImage()
    window.setWindowTitle("Show Image GUI")
    window.show()
    sys.exit(app.exec_())
