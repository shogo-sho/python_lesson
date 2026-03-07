import os
from rembg import remove
from PIL import Image

def remove_bg_folder(input_folder, output_folder="no_bg"):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for file_name in os.listdir(input_folder):
        if file_name.lower().endswith(('.png', '.webp', '.avif', '.jpg', '.jpeg')):
            input_path = os.path.join(input_folder, file_name)
            output_path = os.path.join(output_folder, f"trimmed_{file_name}")

            print(f"処理中: {file_name}")
            try:
                input_image = Image.open(input_path)
                # 背景を削除（透過PNGとして出力）
                output_image = remove(input_image)
                output_image.save(output_path, "PNG")
            except Exception as e:
                print(f"エラー: {file_name} - {e}")

if __name__ == "__main__":
    # 先ほどダウンロードした画像が入っているフォルダを指定
    remove_bg_folder("/Users/shogo/Documents/python_lesson/ドラクエ/ドラクエ7_Switch2")