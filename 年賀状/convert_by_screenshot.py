from html2image import Html2Image
import os

# 変換したいSVGファイル名
input_svg = "/Users/shogo/Desktop/年賀状.svg"
output_png = "年賀状.png"

# SVGファイルがある場所の絶対パスを取得（ブラウザに渡すため）
cwd = os.getcwd()
svg_path = os.path.join(cwd, input_svg)

# html2imageの初期化（Chromeを使ってスクショを撮る準備）
hti = Html2Image()

# ブラウザのサイズをSVGに合わせて調整（SVGが1000x1480なのでそれに合わせる）
# 少し大きめにしておくと切れにくいです
hti.browser_executable = 'chrome' # Mac/Linuxで動かない場合はここを調整（後述）
# Windowsなら自動で見つけてくれることが多いです

print("ブラウザエンジンを使って変換中...")

# 画像化実行
# size引数で画像の解像度を指定できます
hti.screenshot(
    other_file=svg_path,
    save_as=output_png,
    size=(1000, 1480)
)

print(f"完了！ '{output_png}' を確認してください。グラデーションも完璧なはずです。")