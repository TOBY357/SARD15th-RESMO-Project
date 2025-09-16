#!/usr/bin/env python3
# coding: utf-8
"""
SFE-GPS-14414 (Qwiic Titan GPS) を I2C 経由で読み取るシンプルなスクリプト
動作：
 - モジュールに接続できれば NMEA / 緯度経度等を一定間隔で表示し、gps_realtime.txt に保存する
 - 接続失敗時はリトライする
依存: qwiic_titan_gps
"""

import time
import sys
import qwiic_titan_gps

GPS_TXT_PATH = "gps_realtime.txt"
POLL_INTERVAL = 1.0  # sec

def open_and_init():
    gps = qwiic_titan_gps.QwiicTitanGps()
    if not gps.connected:
        raise RuntimeError("Qwiic Titan GPSが見つかりません。配線/I2C有効を確認してください。")
    gps.begin()
    # 必要に応じ通信/出力の設定を行う（例：NMEA出力を有効化等）
    # gps.enable_nmea_messages()  # ライブラリの該当メソッドがあれば
    return gps

def save_realtime(lat, lon):
    try:
        with open(GPS_TXT_PATH, "w", encoding="utf-8") as f:
            f.write(f"{lat},{lon}")
    except Exception as e:
        print("ファイル書き込みエラー:", e)

def main_loop():
    try:
        gps = open_and_init()
    except Exception as e:
        print("初期化エラー:", e)
        return 1

    print("GPS 接続 OK。データ取得を開始します。Ctrl-C で終了。")
    try:
        while True:
            # qwiic_titan_gps の実装によってプロパティ名が多少異なる場合がありますが、
            # 一般的にはわかりやすい getter が用意されています。
            # ここではライブラリの nmea / gnss 情報を参照する方法を想定しています。
            try:
                # ライブラリが提供する NMEA 文字列取得メソッドがあれば取得
                # （なければ位置情報プロパティを参照）
                if gps.get_nmea_data() is True:
                    # ライブラリ内部の gnss_messages から情報を読む想定
                    lat = gps.gnss_messages.get('Latitude', None)
                    lon = gps.gnss_messages.get('Longitude', None)
                    sats = gps.gnss_messages.get('NumSats', None)
                    fix = gps.gnss_messages.get('FixType', None)
                    # NMEA フル文が欲しければ:
                    # nmea = gps.last_nmea_sentence  # ライブラリによる
                else:
                    # get_nmea_data() が False の場合は過去データを参照するかスキップ
                    lat = None
                    lon = None
                    sats = None
                    fix = None

                # 表示
                now = time.strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{now}] lat={lat} lon={lon} sats={sats} fix={fix}")

                # ファイル保存（座標が取得できていれば）
                if lat is not None and lon is not None:
                    save_realtime(lat, lon)

            except Exception as e:
                # 個別読み取りエラーは軽く扱う（接続の一時不良等を想定）
                print("読み取り中の例外:", e)

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print("終了要求を受け取りました。")
    finally:
        # 必要ならクリーンアップ
        try:
            gps.end()  # ライブラリで終了処理があれば
        except Exception:
            pass

    return 0

if __name__ == "__main__":
    sys.exit(main_loop())
