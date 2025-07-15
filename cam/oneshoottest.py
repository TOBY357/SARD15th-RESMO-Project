#oneshoottest.py
#!/usr/bin/env python3
import cv2, time, sys
DEV = '/dev/video10'

cap = cv2.VideoCapture(DEV, cv2.CAP_V4L2)
if not cap.isOpened():
    sys.exit(f'open failed: {DEV}')

time.sleep(0.5)          # バッファが貯まるまで待機
ret, frame = cap.read()
cap.release()

if not ret:
    sys.exit('grab failed')

cv2.imwrite('shot.jpg', frame)
print('saved: shot.jpg')
