#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#モーター操作用プログラム
#Unix系OS (Linux, macOS, Raspberry Piなど) 専用
#
# [操作キー説明]
#  W: 前進         S: 後進
#  A: 左信地旋回   D: 右信地旋回
#  Q: 左カーブ旋回 E: 右カーブ旋回
#  K: モーターパワー増加
#  L: モーターパワー減少
#  ,: モーター左右差調節（左にずらす）
#  .: モーター左右差調節（右にずらす）
#  SPACE: モーター停止
#  B: ブレーキ
#  X: プログラム終了

# --- 標準ライブラリ・外部ライブラリのインポート ---
import sys
import time
import os
import pigpio
import tty
import termios

# --- キー入力処理 ---
class _Getch:
    """
    標準入力から1文字を取得します。画面にはエコーされません。
    Unix系OS (Linux, macOS, Raspberry Piなど) 専用の実装です。
    """
    def __call__(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            char = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return char.encode('utf-8')


# --- 定数定義 ---
# GPIOピン番号 (BCMモード)
LEFT_MOTOR_PIN1 = 12
LEFT_MOTOR_PIN2 = 13
RIGHT_MOTOR_PIN1 = 18
RIGHT_MOTOR_PIN2 = 19

# PWM設定
PWM_FREQUENCY = 50  # 50Hz
PWM_RANGE = 100     # Duty Cycleの範囲を 0-100 に設定

# 動作設定
POWER_ADJUST_STEP = 5       # K,Lキーでのパワー増減量
BALANCE_ADJUST_STEP = 0.025 # ,.キーでのバランス増減量
CURVE_TURN_POWER_RATIO = 0.75 # カーブ旋回時のパワー比率
CURVE_TURN_RATE = 0.3       # カーブ旋回時の内輪の速度比率
SPIN_TURN_POWER_RATIO = 0.75  # 信地旋回時のパワー比率
SPIN_TURN_RATE = -1.0       # 信地旋回時の内輪の速度比率 (-1.0で逆回転)

class motor_pawer_control: #10期リスペクト
    """
    モーター制御や状態をまとめたクラス
    """
    def __init__(self, pi):
        self.pi = pi
        self.power = 80  # モーターの基本パワー (0-100)
        self.left_balance = 1.0  # 左モーターのバランス補正値
        self.right_balance = 1.0 # 右モーターのバランス補正値

        # GPIOピンのセットアップ
        pins = [LEFT_MOTOR_PIN1, LEFT_MOTOR_PIN2, RIGHT_MOTOR_PIN1, RIGHT_MOTOR_PIN2]
        for pin in pins:
            self.pi.set_mode(pin, pigpio.OUTPUT)
            self.pi.set_PWM_frequency(pin, PWM_FREQUENCY)
            self.pi.set_PWM_range(pin, PWM_RANGE)

        self.stop()

    def stop(self):
        """モーターを停止（ブレーキではない）"""
        self.pi.set_PWM_dutycycle(LEFT_MOTOR_PIN1, 0)
        self.pi.set_PWM_dutycycle(LEFT_MOTOR_PIN2, 0)
        self.pi.set_PWM_dutycycle(RIGHT_MOTOR_PIN1, 0)
        self.pi.set_PWM_dutycycle(RIGHT_MOTOR_PIN2, 0)

    def brake(self):
        """モーターにブレーキをかける"""
        self.pi.set_PWM_dutycycle(LEFT_MOTOR_PIN1, self.power)
        self.pi.set_PWM_dutycycle(LEFT_MOTOR_PIN2, self.power)
        self.pi.set_PWM_dutycycle(RIGHT_MOTOR_PIN1, self.power)
        self.pi.set_PWM_dutycycle(RIGHT_MOTOR_PIN2, self.power)

    def forward(self):
        """前進"""
        self.pi.set_PWM_dutycycle(LEFT_MOTOR_PIN2, 0)
        self.pi.set_PWM_dutycycle(RIGHT_MOTOR_PIN2, 0)
        self.pi.set_PWM_dutycycle(LEFT_MOTOR_PIN1, self.power * self.left_balance)
        self.pi.set_PWM_dutycycle(RIGHT_MOTOR_PIN1, self.power * self.right_balance)

    def backward(self):
        """後進"""
        self.pi.set_PWM_dutycycle(LEFT_MOTOR_PIN1, 0)
        self.pi.set_PWM_dutycycle(RIGHT_MOTOR_PIN1, 0)
        self.pi.set_PWM_dutycycle(LEFT_MOTOR_PIN2, self.power * self.left_balance)
        self.pi.set_PWM_dutycycle(RIGHT_MOTOR_PIN2, self.power * self.right_balance)

    def turn(self, direction, power_ratio, turn_rate):
        """
        旋回（信地旋回、カーブ旋回を統合）
        :param direction: 'left' or 'right'
        :param power_ratio: 全体のパワーをどれくらい使うか (0.0 - 1.0)
        :param turn_rate: 内側のモーターの速度比率 (-1.0 - 1.0)
                        -1: 逆回転（信地旋回）
                         0: 停止（片輪旋回）
                         0.3: 正回転（カーブ旋回）
        """
        turn_power = self.power * power_ratio

        # 方向によって左右のパワーを決定
        if direction == 'left':
            outer_power = turn_power
            inner_power = turn_power * turn_rate
            outer_pin1, outer_pin2 = RIGHT_MOTOR_PIN1, RIGHT_MOTOR_PIN2
            inner_pin1, inner_pin2 = LEFT_MOTOR_PIN1, LEFT_MOTOR_PIN2
            outer_balance, inner_balance = self.right_balance, self.left_balance
        else: 
            outer_power = turn_power
            inner_power = turn_power * turn_rate
            outer_pin1, outer_pin2 = LEFT_MOTOR_PIN1, LEFT_MOTOR_PIN2
            inner_pin1, inner_pin2 = RIGHT_MOTOR_PIN1, RIGHT_MOTOR_PIN2
            outer_balance, inner_balance = self.left_balance, self.right_balance

        # 外側のモーターをセット
        self.pi.set_PWM_dutycycle(outer_pin2, 0)
        self.pi.set_PWM_dutycycle(outer_pin1, outer_power * outer_balance)

        # 内側のモーターをセット (turn_rateが負なら逆回転)
        if turn_rate >= 0:
            self.pi.set_PWM_dutycycle(inner_pin2, 0)
            self.pi.set_PWM_dutycycle(inner_pin1, inner_power * inner_balance)
        else:
            self.pi.set_PWM_dutycycle(inner_pin1, 0)
            self.pi.set_PWM_dutycycle(inner_pin2, -inner_power * inner_balance)

    def adjust_power(self, amount):
        """モーターパワーを調整"""
        self.power += amount
        # 0から100の範囲に収める
        self.power = max(0, min(100, self.power))
        print(f"モーターパワー: {self.power}")

    def adjust_balance(self, direction):
        """左右のバランスを調整"""
        if direction == 'left': # 左を弱く、右を強く
            self.left_balance -= BALANCE_ADJUST_STEP
            self.right_balance += BALANCE_ADJUST_STEP
        else: # 左を強く、右を弱く
            self.left_balance += BALANCE_ADJUST_STEP
            self.right_balance -= BALANCE_ADJUST_STEP

        # 0.0から1.0の範囲に収める
        self.left_balance = max(0.0, min(1.0, self.left_balance))
        self.right_balance = max(0.0, min(1.0, self.right_balance))
        print(f"左右バランス: L={self.left_balance:.3f}, R={self.right_balance:.3f}")


# --- メイン処理 ---
def main():
    """メインの処理ループ"""
    pi_instance = pigpio.pi()
    if not pi_instance.connected:
        print("pigpioデーモンに接続できません。sudo pigpiod を実行してください。")
        return

    kansei = motor_pawer_control(pi_instance)
    getch = _Getch()

    current_action = "停止中" # 初期状態

    try:
        while True:
            # 画面クリア
            os.system('cls' if os.name == 'nt' else 'clear')

            # 操作説明と現在の状態を表示
            print("--- CanSat ラジコン操作プログラム ---")
            print("[操作キー]")
            print("  W: 前進         S: 後進")
            print("  A: 左信地旋回   D: 右信地旋回")
            print("  Q: 左カーブ旋回 E: 右カーブ旋回")
            print("  K: モーターパワー増加")
            print("  L: モーターパワー減少")
            print("  ,: モーター左右差調節（左にずらす）")
            print("  .: モーター左右差調節（右にずらす）")
            print("  SPACE: モーター停止")
            print("  B: ブレーキ")
            print("  X: プログラム終了")
            print(f"[現在の状態]")
            print(f"  アクション: {current_action}")
            print(f"  モーターパワー: {kansei.power}")
            print(f"  左右バランス: L={kansei.left_balance:.3f}, R={kansei.right_balance:.3f}")
            print("キー入力待ち...")

            key = getch()

            if key == b'w':
                kansei.forward()
                current_action = "前進中"
            elif key == b's':
                kansei.backward()
                current_action = "後進中"
            elif key == b'q':
                kansei.turn('left', CURVE_TURN_POWER_RATIO, CURVE_TURN_RATE)
                current_action = "左カーブ旋回中"
            elif key == b'e':
                kansei.turn('right', CURVE_TURN_POWER_RATIO, CURVE_TURN_RATE)
                current_action = "右カーブ旋回中"
            elif key == b'a':
                kansei.turn('left', SPIN_TURN_POWER_RATIO, SPIN_TURN_RATE)
                current_action = "左信地旋回中"
            elif key == b'd':
                kansei.turn('right', SPIN_TURN_POWER_RATIO, SPIN_TURN_RATE)
                current_action = "右信地旋回中"
            elif key == b'k':
                kansei.stop()
                kansei.adjust_power(POWER_ADJUST_STEP)
                current_action = "パワー増加"
            elif key == b'l':
                kansei.stop()
                kansei.adjust_power(-POWER_ADJUST_STEP)
                current_action = "パワー減少"
            elif key == b',':
                kansei.stop()
                kansei.adjust_balance('left')
                current_action = "バランス調整（左）"
            elif key == b'.':
                kansei.stop()
                kansei.adjust_balance('right')
                current_action = "バランス調整（右）"
            elif key == b' ':
                kansei.stop()
                current_action = "停止中"
            elif key == b'b':
                kansei.brake()
                current_action = "ブレーキ中"
            elif key == b'x':
                print("プログラムを終了します。")
                break
            else:
                # 未知のキーが押された場合、アクションは変更しない
                pass
            
            # CPU負荷軽減
            time.sleep(0.01)

    finally:
        # プログラム終了時に必ずモーターを停止
        if 'kansei' in locals():
            kansei.stop()
        if 'pi_instance' in locals() and pi_instance.connected:
            pi_instance.stop()
        print("クリーンアップ完了")


if __name__ == '__main__':
    main()
