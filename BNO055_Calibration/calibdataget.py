#calib data get
import time
import board
import busio
import adafruit_bno055

# I2C初期化
i2c = busio.I2C(board.SCL, board.SDA)
bno = adafruit_bno055.BNO055_I2C(i2c)

print("=== BNO055 キャリブレーション支援ツール ===")
print("センサーを動かしながら各軸の値とキャリブレーション状態を確認してください。\n")

try:
    while True:
        # キャリブレーション状態
        sys_cal, gyro_cal, accel_cal, mag_cal = bno.calibration_status

        # センサーデータ取得
        euler = bno.euler
        accel = bno.acceleration
        mag = bno.magnetic
        gyro = bno.gyro

        print("========== 現在のセンサーデータ ==========")
        print(f"[キャリブレーション] System: {sys_cal} | Gyro: {gyro_cal} | Accel: {accel_cal} | Mag: {mag_cal}")

        if euler:
            print(f"[オイラー角] Heading: {euler[0]:.1f}°, Roll: {euler[1]:.1f}°, Pitch: {euler[2]:.1f}°")
        if accel:
            print(f"[加速度] X: {accel[0]:.2f}, Y: {accel[1]:.2f}, Z: {accel[2]:.2f} m/s²")
        if mag:
            print(f"[地磁気] X: {mag[0]:.2f}, Y: {mag[1]:.2f}, Z: {mag[2]:.2f} µT")
        if gyro:
            print(f"[ジャイロ] X: {gyro[0]:.2f}, Y: {gyro[1]:.2f}, Z: {gyro[2]:.2f} °/s")

        # 全項目がキャリブレーション完了したら通知
        if sys_cal == 3 and gyro_cal == 3 and accel_cal == 3 and mag_cal == 3:
            print("🎉 全センサーキャリブレーション完了！")
            break

        print("-------------------------------------------")
        time.sleep(1)

except KeyboardInterrupt:
    print("\n終了しました。")
