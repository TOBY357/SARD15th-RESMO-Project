#!/usr/bin/env python3
import time, re, sys
from smbus2 import SMBus, i2c_msg
import pynmea2

# ===== 設定 =====
I2C_BUS = 1
XA1110_ADDR = 0x10
READ_CHUNK = 128
AGGREGATE_PERIOD = 1.0
POLL_INTERVAL = 0.05
RAW_DEBUG = False
NO_MSG_RESET_SEC = 10  # 何秒メッセージ無しならバッファをクリアして再試行
# ==================

NMEA_SENTENCE_RE = re.compile(r'(\$[^$]*\*[0-9A-Fa-f]{2}\r?\n?)')  # 完全なセンテンス抽出

def read_i2c_bytes(bus, addr, length):
    """i2c_msg を使って length バイトを読み取る。例外は上位で処理する。"""
    msg = i2c_msg.read(addr, length)
    bus.i2c_rdwr(msg)
    return bytes(list(msg))

def process_sentence(sentence):
    """1つの完全な NMEA 文（文字列）を受け取り parseして処理する"""
    s = sentence.strip()
    if not s:
        return
    try:
        msg = pynmea2.parse(s)
    except Exception as e:
        if RAW_DEBUG:
            print("parse failed:", repr(s), "->", e, file=sys.stderr)
        return

    if isinstance(msg, pynmea2.GGA):
        try:
            lat = msg.latitude; lon = msg.longitude
        except Exception as e:
            if RAW_DEBUG:
                print("Invalid GGA fields:", msg.__dict__, file=sys.stderr)
            return
        fix = getattr(msg, "gps_qual", None)
        sats = getattr(msg, "num_sats", None)
        print(f"GGA - 緯度:{lat:.6f}, 経度:{lon:.6f}, 測位品質:{fix}, 衛星数:{sats}")
    elif isinstance(msg, pynmea2.RMC):
        try:
            speed = msg.spd_over_grnd
            course = msg.true_course
        except Exception:
            speed = course = None
        print(f"RMC - 速度:{speed}ノット, 真方位:{course}度")
    else:
        # 他のセンテンスは今は無視（必要ならここで処理）
        if RAW_DEBUG:
            print("Other sentence:", type(msg), msg.__dict__, file=sys.stderr)

def main():
    print(f"I2C XA1110 安全版（集約 {AGGREGATE_PERIOD}s）開始")
    buffer = ""           # 文字列バッファ
    last_msg_time = time.monotonic()
    with SMBus(I2C_BUS) as bus:
        try:
            while True:
                # 1秒分（AGGREGATE_PERIOD）を小刻みに読み取って集める
                start = time.monotonic()
                collected = []
                while time.monotonic() - start < AGGREGATE_PERIOD:
                    try:
                        chunk = read_i2c_bytes(bus, XA1110_ADDR, READ_CHUNK)
                    except OSError as e:
                        # I2C の一時エラーはログして短く休んで再試行
                        print("I2C読み取りエラー:", e, file=sys.stderr)
                        time.sleep(0.2)
                        continue

                    if chunk:
                        if RAW_DEBUG:
                            print("RAW CHUNK:", repr(chunk), file=sys.stderr)
                        collected.append(chunk)
                    time.sleep(POLL_INTERVAL)

                if collected:
                    # まとめてデコードしてバッファへ追加
                    try:
                        text = b"".join(collected).decode('ascii', errors='ignore')
                    except Exception as e:
                        print("デコード失敗:", e, file=sys.stderr)
                        text = ""
                    if text:
                        buffer += text

                # 正規表現で"完全な"センテンスをすべて抜き出して処理
                if buffer:
                    matches = list(NMEA_SENTENCE_RE.finditer(buffer))
                    if matches:
                        last_end = 0
                        for m in matches:
                            sent = m.group(1)
                            process_sentence(sent)
                            last_end = m.end()
                            last_msg_time = time.monotonic()
                        # matches の最後までを削除して残り（断片）を buffer に保持
                        buffer = buffer[last_end:]
                    else:
                        # 完全な文が無ければ buffer はそのまま残す（断片を待つ）
                        # でも長大化しすぎる場合は保護
                        if len(buffer) > 4096:
                            # バッファ異常に大きくなったら切り捨て
                            if RAW_DEBUG:
                                print("buffer too large, trimming", file=sys.stderr)
                            buffer = buffer[-1024:]

                # ウォッチドッグ: 一定時間メッセージが来なければバッファをクリアして再試行
                if time.monotonic() - last_msg_time > NO_MSG_RESET_SEC:
                    if RAW_DEBUG:
                        print("No messages for", NO_MSG_RESET_SEC, "s -> clearing buffer", file=sys.stderr)
                    buffer = ""
                    last_msg_time = time.monotonic()

        except KeyboardInterrupt:
            print("停止 (Ctrl-C)")

if __name__ == "__main__":
    main()
