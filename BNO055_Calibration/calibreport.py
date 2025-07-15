#calib.report
from smbus2 import SMBus
import json
import time

BNO055_ADDRESS = 0x28
CALIB_DATA_ADDR = 0x55
CALIB_DATA_LENGTH = 22
OPR_MODE_ADDR = 0x3D
CONFIG_MODE = 0x00
NDOF_MODE = 0x0C

with SMBus(1) as bus:
    # モードをCONFIGに
    bus.write_byte_data(BNO055_ADDRESS, OPR_MODE_ADDR, CONFIG_MODE)
    time.sleep(0.02)

    # キャリブレーションデータ読み取り
    calib_data = bus.read_i2c_block_data(BNO055_ADDRESS, CALIB_DATA_ADDR, CALIB_DATA_LENGTH)

    # 保存
    with open("bno055_calib.json", "w") as f:
        json.dump(calib_data, f)

    # 元のモードに戻す
    bus.write_byte_data(BNO055_ADDRESS, OPR_MODE_ADDR, NDOF_MODE)
    time.sleep(0.02)

print("キャリブレーションデータを保存しました。")
