#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ldr_adc.py -- Photo‑resistor (LDR) + MCP3208 demo
Raspberry Pi Zero W  /  SPI bus 0 CE0

目的:
* CH0 に接続した CdS フォトレジスタ分圧の **電圧 (V)** をそのまま表示
* オプションで簡易換算した **照度 (lx)** も併記

使い方:
$ python3 ldr_adc.py          # 電圧 + lx を 0.5 s ごとに表示

必要配線 / 10 kΩ 分圧などは README 参照。

Author : ChatGPT (OpenAI)
Licence: MIT
"""
from __future__ import annotations

import math
import time
import spidev
from typing import Final

# --------------------- ユーザー調整パラメータ ---------------------
V_REF:   Final[float] = 3.29476   # [V] 3V3 実測値
ADC_MAX: Final[int]   = 4095      # 12‑bit
FIXED_R: Final[int]   = 10_000    # [Ω] 分圧用抵抗 (→GND)
CHANNEL: Final[int]   = 0         # MCP3208 CH0
# 照度モデル R = A * lux^-B  → lux = (R/A)^(-1/B)
A_CAL:   Final[float] = 500
B_CAL:   Final[float] = 1.4
INTERVAL:Final[float] = 0.5       # [s] 表示間隔
# -----------------------------------------------------------------

spi = spidev.SpiDev()


# ───────────────── SPI ヘルパ ──────────────────

def open_spi(bus: int = 0, dev: int = 0, speed_hz: int = 1_000_000) -> None:
    spi.open(bus, dev)
    spi.max_speed_hz = speed_hz
    spi.mode = 0b00  # MCP3208 datasheet: CPOL=0 CPHA=0


def close_spi() -> None:
    spi.close()


def _adc_raw(ch: int = CHANNEL) -> int:
    if not 0 <= ch <= 7:
        raise ValueError("channel must be 0‑7")
    cmd = 0b11000 | ch              # start(1) + single‑ended(1) + ch
    tx  = [(cmd >> 2) & 0xFF,       # 先頭 5bit + 3bit ダミー
           (cmd & 0x03) << 6,
           0x00]
    rx = spi.xfer2(tx)
    return ((rx[1] & 0x0F) << 8) | rx[2]  # 12‑bit


# ────────────────── 計算関数 ────────────────────

def read_voltage(ch: int = CHANNEL) -> float:
    """入力電圧 [V] を返す"""
    return _adc_raw(ch) * V_REF / ADC_MAX


def read_lux(ch: int = CHANNEL) -> float:
    """簡易照度推定 [lx] (キャリブレーション必須)"""
    v = read_voltage(ch)
    if v <= 0.001 or v >= V_REF * 0.999:
        # 極端に暗い / 明るいときは発散 → 無限大扱い
        return math.inf if v <= 0.001 else 0.0
    r_ldr = FIXED_R * (V_REF / v - 1)
    return (r_ldr / A_CAL) ** (-1.0 / B_CAL)


# ────────────────── メインループ ─────────────────

def main() -> None:
    open_spi()
    try:
        print("Voltage [V]   |   Est. Lux [lx]")
        print("─" * 30)
        while True:
            v   = read_voltage()
            lux = read_lux()
            lux_str = f"{lux:8.1f}" if math.isfinite(lux) else ("  0.0" if lux == 0 else "  inf")
            print(f"{v:6.3f} V     |{lux_str} lx")
            time.sleep(INTERVAL)
    finally:
        close_spi()


if __name__ == "__main__":
    main()
