import RPi.GPIO as GPIO
import time

# GPIOピンの設定（AE-DRV8835をIN/INモードで制御）
# ------------------------------------------------
# モーターA (左側のモーター)
MOTOR_A_IN1 = 22  # GPIO22
MOTOR_A_IN2 = 23  # GPIO23

# モーターB (右側のモーター)
MOTOR_B_IN1 = 24  # GPIO24
MOTOR_B_IN2 = 25  # GPIO25

# GPIOモードの設定
GPIO.setmode(GPIO.BCM)
GPIO.setup(MOTOR_A_IN1, GPIO.OUT)
GPIO.setup(MOTOR_A_IN2, GPIO.OUT)
GPIO.setup(MOTOR_B_IN1, GPIO.OUT)
GPIO.setup(MOTOR_B_IN2, GPIO.OUT)

# モーター制御関数
# ------------------------------------------------
def stop():
    """すべてのモーターを停止させます。"""
    GPIO.output(MOTOR_A_IN1, GPIO.LOW)
    GPIO.output(MOTOR_A_IN2, GPIO.LOW)
    GPIO.output(MOTOR_B_IN1, GPIO.LOW)
    GPIO.output(MOTOR_B_IN2, GPIO.LOW)
    print("停止")

def forward():
    """前進します。"""
    GPIO.output(MOTOR_A_IN1, GPIO.HIGH)
    GPIO.output(MOTOR_A_IN2, GPIO.LOW)
    GPIO.output(MOTOR_B_IN1, GPIO.HIGH)
    GPIO.output(MOTOR_B_IN2, GPIO.LOW)
    print("前進")

def backward():
    """後退します。"""
    GPIO.output(MOTOR_A_IN1, GPIO.LOW)
    GPIO.output(MOTOR_A_IN2, GPIO.HIGH)
    GPIO.output(MOTOR_B_IN1, GPIO.LOW)
    GPIO.output(MOTOR_B_IN2, GPIO.HIGH)
    print("後退")

def turn_left():
    """その場で左に回転します。"""
    # 左モーターを後退、右モーターを前進
    GPIO.output(MOTOR_A_IN1, GPIO.LOW)
    GPIO.output(MOTOR_A_IN2, GPIO.HIGH)
    GPIO.output(MOTOR_B_IN1, GPIO.HIGH)
    GPIO.output(MOTOR_B_IN2, GPIO.LOW)
    print("左回転")

def turn_right():
    """その場で右に回転します。"""
    # 左モーターを前進、右モーターを後退
    GPIO.output(MOTOR_A_IN1, GPIO.HIGH)
    GPIO.output(MOTOR_A_IN2, GPIO.LOW)
    GPIO.output(MOTOR_B_IN1, GPIO.LOW)
    GPIO.output(MOTOR_B_IN2, GPIO.HIGH)
    print("右回転")

# メインの実行部分
# ------------------------------------------------
try:
    print("モーターの動作テストを開始します。")

    # 前進
    forward()
    time.sleep(2)  # 2秒間動作

    # 停止
    stop()
    time.sleep(1)  # 1秒間停止

    # 後退
    backward()
    time.sleep(2)  # 2秒間動作

    # 停止
    stop()
    time.sleep(1)

    # 左回転
    turn_left()
    time.sleep(2)

    # 停止
    stop()
    time.sleep(1)

    # 右回転
    turn_right()
    time.sleep(2)

    # 停止
    stop()
    time.sleep(1)
    
finally:
    # 終了処理: GPIO設定をリセット
    GPIO.cleanup()
    print("プログラムを終了し、GPIOをクリーンアップしました。")