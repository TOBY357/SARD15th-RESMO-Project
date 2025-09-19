import time
import pigpio

# pigpio初期化
pi = pigpio.pi()

# 使用するGPIO番号 (例: 17番)
CAREER_CUT = 16  

# 出力ピンを設定
pi.set_mode(CAREER_CUT, pigpio.OUTPUT)

def career_cat(t=3):
    career_time = t
    
    # 1回目点火
    print("点火")
    pi.write(CAREER_CUT, 1)
    time.sleep(career_time)
    pi.write(CAREER_CUT, 0)
    time.sleep(1)

    # 2回目点火
    print("点火")
    pi.write(CAREER_CUT, 1)
    time.sleep(career_time)
    pi.write(CAREER_CUT, 0)
    time.sleep(1)

# 実行例
career_cat(3)

# 終了時はリソース解放
pi.stop()