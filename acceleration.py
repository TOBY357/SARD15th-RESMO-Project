import time
import board
import busio
import adafruit_bno055

# I2Cバスの初期化
i2c = busio.I2C(board.SCL, board.SDA)

# BNO055の初期化
sensor = adafruit_bno055.BNO055_I2C(i2c)

# 取得関数
def print_sensor_data():
    print("温度： {} ° C".format(sensor.temperature))
    print("加速度: {}".format(sensor.acceleration))  # 単位: m/s^2
    print("磁力: {}".format(sensor.magnetic))        # 単位: uT
    print("ジャイロ: {}".format(sensor.gyro))        # 単位: rad/s
    print("オイラー角: {}".format(sensor.euler))     # 単位: degrees
    print("クォータニオン: {}".format(sensor.quaternion))
    print("線形加速度: {}".format(sensor.linear_acceleration))
    print("重力ベクトル: {}".format(sensor.gravity))
    print("="*40)

# メインループ
while True:
    print_sensor_data()
    time.sleep(1)
    