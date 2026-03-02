import os

# Force OpenCV's Qt backend to use X11/XWayland plugin (xcb) on Linux.
os.environ["QT_QPA_PLATFORM"] = "xcb"

import cv2

# Command Soal 1: Import library computer vision (OpenCV).
# Command Soal 2: Baca file gambar yang akan di-load ke sistem.
img = cv2.imread("../image/cat.jpeg")
if img is None:
    raise FileNotFoundError("Gambar tidak ditemukan: ../image/cat.jpeg")

# Command Soal 3: Tampilkan gambar pada window bernama "Image".
cv2.imshow("Image", img)

# Command Soal 4: Tunggu input keyboard agar window tetap terbuka.
cv2.waitKey(0)

# Command Soal 5: Tutup semua window OpenCV.
cv2.destroyAllWindows()
