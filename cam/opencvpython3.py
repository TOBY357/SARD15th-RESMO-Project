#python3 - <<'EOF'
import cv2, sys
print("OpenCV:", cv2.__version__)
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
print("V4L2 enabled? ", cap.isOpened())