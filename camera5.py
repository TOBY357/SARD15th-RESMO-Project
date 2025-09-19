import subprocess
import cv2
import numpy as np
import time

def take_picture(output_path):
    """
    libcamera-jpeg コマンドを使って写真を撮影します。
    """
    try:
        print("写真を撮影中...")
        subprocess.run(
            ['libcamera-jpeg', '-t', '2000', '-o', output_path],
            check=True
        )
        print(f"写真が {output_path} に保存されました。")
    except subprocess.CalledProcessError as e:
        print(f"写真撮影コマンドの実行に失敗しました: {e}")
        return False
    return True

def find_red_cone(image_path):
    """
    画像から赤いコーン（物体）を検知し、その中心座標を返します。
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            print(f"エラー: 画像ファイル {image_path} を読み込めません。")
            return (-1, -1)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_red1 = np.array([0, 50, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([160, 50, 50])
        upper_red2 = np.array([179, 255, 255])
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        red_mask = mask1 + mask2
        contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            if cv2.contourArea(largest_contour) > 100:
                M = cv2.moments(largest_contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    return (cx, cy)
    except Exception as e:
        print(f"画像処理中にエラーが発生しました: {e}")
        return (-1, -1)
    return (-1, -1)

def main():
    image_file = f"detected_image.jpg"
    
    if not take_picture(image_file):
        return

    x, y = find_red_cone(image_file)
    coords = list((x, y))

    if x != -1 and y != -1:
        print(f"赤いコーンの座標: ({x}, {y})")
        return coords
    else:
        print("赤いコーンが見つかりませんでした。")
        


if __name__ == "__main__":
    coords = main()
    print("座標",coords)
    time.sleep(1)