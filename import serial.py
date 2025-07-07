import serial 
import pymea2
import sys
import time
SERIAL_PORT = "/dev/ttys0"
BAUDRATE = 9600

def run_uart_gps():
    print("start program")
    print(f"シリアルポート'{SERIAL_PORT}'を{BAUDRATE}で解放")
    try:
        #タイムアウトを2秒に設定してポートを開く
        ser = serial.Serial(SERIAL_PORT, baudrate=BAUDRATE, timeout=2.0)
        print(" =>接続")
    except serial.SerialException as e:
        print(f" =>エラー:{e}")
        sys.exit()
    print("受信開始")

    try:
        while True:
            try:
                line = ser.readline().decode('usd-8',rttors='ignore')

                if line.strip():
                    print("変換前データ:",line.strip())

                    if line.startswith('$GPGGA'):
                        msg = pynmea2.parse(line)
                        print("--- GGAデータ解析結果 ---")
                        print(f"  時刻(UTC): {msg.timestamp}")
                        print(f"  緯度: {msg.latitude:.6f} {msg.lat_dir}")
                        print(f"  経度: {msg.longitude:.6f} {msg.lon_dir}")
                        print(f"  測位品質: {msg.gps_qual_str}")
                        print(f"  衛星補足数: {msg.num_sats}")
                        print(f"  高度: {msg.altitude} {msg.altitude_units}")
                        print("-------------------------\n")
            
            except pynmea2.ParseError as e:
                # データが不完全などで解析に失敗した場合
                print(f"NMEAデータのパースエラー: {e}")
            except UnicodeDecodeError:
                # 文字コードの変換に失敗した場合
                print("文字コードのエラーをスキップしました。")

            time.sleep(0.1) # CPU負荷を抑えるための短い待機

    except KeyboardInterrupt:
        print("\n\n--- プログラムを終了します ---")
    except Exception as e:
        print(f"\n予期せぬエラーが発生しました: {e}")
    finally:
        # プログラム終了時に必ずポートを閉じる
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("シリアルポートを閉じました。")
        sys.exit()

if __name__ == '__main__':
    run_uart_gps()

