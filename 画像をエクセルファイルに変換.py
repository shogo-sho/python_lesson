from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage
import os

def image_to_excel(image_path, output_excel_path="output.xlsx", anchor_cell="A1"):
    """
    指定された画像をExcelファイル（.xlsx）に貼り付けて保存します。
    
    Parameters:
        image_path (str): 入力画像ファイルのパス（jpg, png など）
        output_excel_path (str): 出力するExcelファイルのパス
        anchor_cell (str): 画像を貼り付けるセル（例: "A1"）
    """
    # ファイルの存在確認
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"画像ファイルが見つかりません: {image_path}")
    
    # Excelブックとワークシート作成
    wb = Workbook()
    ws = wb.active
    ws.title = "画像付きシート"

    # 画像読み込みと貼り付け
    img = XLImage(image_path)
    ws.add_image(img, anchor_cell)

    # Excelファイル保存
    wb.save(output_excel_path)
    print(f"Excelファイルを保存しました: {output_excel_path}")
