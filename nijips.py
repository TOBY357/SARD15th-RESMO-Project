import time
import serial
import pynmea2

ser = serial.Serial('/dev/ttyS0', baudrate=9600, timeout=1)

print("URAT GPS データ受信開始")

try:
    last_print = time.monotonic()
    while True:
        line = ser.readline().decode('ascii', errors='ignore').strip()
        if not line:
            continue
    
        try:
            msg = pynmea2.parse(line)
        except pynmea2.ParseError:
            continue

        if isinstance(msg, pynmea2.GGA):
            lat = msg.latitude
            lon = msg.longitude
            fix = msg.gps_qual
            sat = msg.num_sats
            print(f"GGA - 緯度:{lat:.6f}, 経度:{lon:.6f}, 測位品質:{fix}, 衛星数:{sat}")
        elif isinstance(msg, pynmea2.RMC):
            speed = msg.spd_over_grnd
            true_course = msg.true_course
            print(f"RMC - 速度:{speed:}ノット, 真方位:{true_course}度")

        if time.monotonic() - last_print > 1:
            last_print = time.monotonic()
    
except KeyboardInterrupt:
    print("受信停止")
finally:
    ser.close()
    print("シリアルポートを閉じました。")