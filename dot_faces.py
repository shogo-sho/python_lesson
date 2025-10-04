from PIL import Image

def draw_face(pattern, pixel_size, filename):
    h, w = len(pattern), len(pattern[0])
    img = Image.new("RGB", (w * pixel_size, h * pixel_size), "white")

    # 色コード（RGB）
    color_map = {
        0: (255, 255, 255),  # 白（背景）
        1: (0, 0, 0),        # 黒（目・口）
        2: (255, 192, 203),  # ピンク（頬）
        3: (200, 200, 200),  # 髪（妖精ちゃん）
        4: (255, 0, 0),      # 赤（凛）
        5: (138, 43, 226),   # 紫（哀ちゃん）
        6: (255, 255, 0),    # 黄色（リボン）
    }

    for y in range(h):
        for x in range(w):
            color = color_map.get(pattern[y][x], (255, 255, 255))
            for i in range(pixel_size):
                for j in range(pixel_size):
                    img.putpixel((x*pixel_size + i, y*pixel_size + j), color)

    img.save(filename)
    print(f"{filename} を保存しました。")


# 👼 妖精ちゃん
fairy_face = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,3,3,3,3,3,3,3,3,0,0,0,0],
    [0,0,0,3,3,3,3,3,3,3,3,3,3,0,0,0],
    [0,0,3,3,3,3,3,3,3,3,3,3,3,3,0,0],
    [0,3,3,3,1,0,3,3,3,3,0,1,3,3,3,0],
    [0,3,3,3,0,0,3,3,3,3,0,0,3,3,3,0],
    [0,3,3,3,0,0,3,3,3,3,0,0,3,3,3,0],
    [0,3,3,3,1,0,0,0,0,0,0,1,3,3,3,0],
    [0,3,3,3,0,2,0,0,0,0,2,0,3,3,3,0],
    [0,3,3,3,0,0,0,1,1,0,0,0,3,3,3,0],
    [0,3,3,3,3,3,3,3,3,3,3,3,3,3,3,0],
    [0,0,3,3,3,3,3,3,3,3,3,3,3,3,0,0],
    [0,0,0,0,3,3,3,3,3,3,3,3,0,0,0,0],
    [0,0,0,0,0,0,3,3,3,3,0,0,0,0,0,0],
    [0,0,0,0,0,0,3,3,3,3,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
]

# 🔴 凛（赤いリボン）
rin_face = [row.copy() for row in fairy_face]
for y in range(2, 4):
    for x in range(5, 11):
        rin_face[y][x] = 4  # 赤

# 🟣 哀ちゃん（紫髪）
ai_face = [row.copy() for row in fairy_face]
for y in range(len(ai_face)):
    for x in range(len(ai_face[0])):
        if ai_face[y][x] == 3:
            ai_face[y][x] = 5  # 紫


# 保存
draw_face(fairy_face, 8, "fairy_face.png")
draw_face(rin_face, 8, "rin_face.png")
draw_face(ai_face, 8, "ai_face.png")