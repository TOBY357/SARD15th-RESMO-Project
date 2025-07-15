import cv2, time
cap = cv2.VideoCapture('/dev/video10', cv2.CAP_V4L2)
time.sleep(0.5)
ret, frame = cap.read()
cv2.imwrite("frame.jpg", frame)
cap.release()
