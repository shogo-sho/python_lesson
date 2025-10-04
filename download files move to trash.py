import os
import shutil

#ダウンロードフォルダ
downloads = os.path.expanduser("/Users/shogo/Downloads")

#ゴミ箱フォルダ
trash = os.path.expanduser("/Users/shogo/.Trash")

#ダウンロード内のファイルをゴミ箱に移動
for f in os.listdir(downloads):
    src = os.path.join(downloads, f)
    dst = os.path.join(trash, f)
    try:
        shutil.move(src, dst)
        print(f"移動: {src} → {dst}")
    except Exception as e:
        print(f"移動失敗: {src} ({e})")

print("✅ ダウンロード内のファイルをゴミ箱に移動しました")
