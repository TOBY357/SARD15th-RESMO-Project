#!/usr/bin/env python3
# coding: utf-8
"""
I2C 接続の Qwiic Titan GPS を使って NMEA / GNSS 情報を表示するスクリプト
 - できれば仮想環境内で実行してください（pynmea2, qwiic_titan_gps が必要）
 - NMEA 生文が取れれば pynmea2 でパースして GGA/RMC 等を出力
 - 生文が無ければ gnss_messages を参照して主要フィールドを出力
"""

import time
import sys

try:
    import qwiic_titan_gps
except Exception as e:
    print("qwiic_titan_gps が import できません:", e)
    raise

try:
    import pynmea2
    HAVE_PYNMEA2 = True
except Exception:
    HAVE_PYNMEA2 = False

POLL_INTERVAL = 0.5  # 秒

def open_gps():
    gps = qwiic_titan_gps.QwiicTitanGps()
    if not gps.connected:
        raise RuntimeError("Qwiic Titan GPS が見つかりません。配線 / I2C の有効化を確認してください。")
    gps.begin()
    # ライブラリにより get_nmea_data() を呼ぶことで内部バッファが更新される想定
    return gps

def try_get_last_nmea(gps):
    """ライブラリ内の生NMEAを得られるか色々試す（属性名はバージョン差があるため保険）"""
    # まず get_nmea_data() を呼ぶ（内部で NMEA を取得してくれる場合あり）
    try:
        _ = gps.get_nmea_data()
    except Exception:
        pass

    candidates = [
        "last_nmea_sentence",
        "lastNMEA",
        "lastNmeaSentence",
        "last_nmea",
        "last_nmea_str",
        "nmea_sentence",
        "nmea",
    ]
    for attr in candidates:
        val = getattr(gps, attr, None)
        if isinstance(val, str) and val.strip():
            return val.strip()

    # もしかしてライブラリが複数文を貯めている container を持つケース
    for attr in ("nmea_sentences", "nmea_buffer", "nmea_list"):
        val = getattr(gps, attr, None)
        if val:
            # try last element if it's a list
            if isinstance(val, (list, tuple)) and len(val) > 0:
                last = val[-1]
                if isinstance(last, str) and last.strip():
                    return last.strip()
            # if it's a string
            if isinstance(val, str) and val.strip():
                return val.strip()

    return None

def print_from_gnss_messages(gps):
    """gnss_messages 辞書から主要フィールドを取り出して表示"""
    gm = getattr(gps, "gnss_messages", None)
    if not gm:
        print("gnss_messages が利用できません")
        return

    # ライブラリによってキー名が違うことがあるので安全に取り出す
    lat = gm.get("Latitude") if isinstance(gm, dict) else None
    lon = gm.get("Longitude") if isinstance(gm, dict) else None
    sats = gm.get("NumSats") if isinstance(gm, dict) else None
    fix = gm.get("FixType") if isinstance(gm, dict) else None
    hdop = gm.get("HDOP") if isinstance(gm, dict) else None

    print(f"GNSS - lat={lat} lon={lon} sats={sats} fix={fix} hdop={hdop}")

def main():
    try:
        gps = open_gps()
    except Exception as e:
        print("GPS 初期化エラー:", e)
        sys.exit(1)

    print("I2C GPS 接続 OK。データ受信開始。Ctrl-C で停止。")
    last_print = time.monotonic()
    try:
        while True:
            # まず生NMEAを試す
            nmea = try_get_last_nmea(gps)

            if nmea:
                # 取得できた生NMEAを逐次パースして、GGA/RMC を検出する（pynmea2 があるなら使う）
                if HAVE_PYNMEA2:
                    # NMEA 文は複数来る場合があるので $ で分割してパース（最後の完全文のみ取り出す）
                    lines = [s for s in (nmea.split('\n') if '\n' in nmea else [nmea]) if s.strip()]
                    for line in lines:
                        try:
                            msg = pynmea2.parse(line)
                        except pynmea2.ParseError:
                            continue
                        if isinstance(msg, pynmea2.types.talker.GGA) or msg.sentence_type == "GGA":
                            lat = getattr(msg, "latitude", None)
                            lon = getattr(msg, "longitude", None)
                            fix = getattr(msg, "gps_qual", None)
                            sat = getattr(msg, "num_sats", None)
                            print(f"GGA - 緯度:{lat} 経度:{lon} 測位品質:{fix} 衛星数:{sat}")
                        elif isinstance(msg, pynmea2.types.talker.RMC) or msg.sentence_type == "RMC":
                            speed = getattr(msg, "spd_over_grnd", None)
                            true_course = getattr(msg, "true_course", None)
                            print(f"RMC - 速度:{speed}ノット, 真方位:{true_course}度")
                else:
                    # pynmea2 がない場合は生NMEA文字列をそのまま出力
                    print("生NMEA:", nmea)

            else:
                # 生NMEAが取れなければ gnss_messages を参照して代替出力
                # get_nmea_data() をもう一度投げてみる（ライブラリ依存で内部バッファが更新される場合あり）
                try:
                    gps.get_nmea_data()
                except Exception:
                    pass
                print_from_gnss_messages(gps)

            # 1秒に1回くらい行いたければ以下の制御（元スクリプトは毎ループで標準出力）
            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print("受信停止")
    finally:
        # Qwiic ライブラリに close/end があれば呼ぶ
        try:
            gps.end()
        except Exception:
            pass
        print("終了")

if __name__ == "__main__":
    main()
