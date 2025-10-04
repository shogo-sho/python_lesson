# merge_split_pdfs_multi_folders_no_merger_recursive.py
# サブフォルダもまとめて処理したいときは RECURSIVE=True（既定がTrue）。

import re, json
from pathlib import Path
from tkinter import Tk, filedialog, messagebox
from pypdf import PdfReader, PdfWriter

HISTORY_FILE = Path("last_folders.json")
HISTORY_MAX = 10
OVERWRITE_OUTPUT = True
DELETE_PARTS = True
RECURSIVE = True  # ★ Trueでサブフォルダも全部処理
PART_PATTERN = re.compile(r"^(?P<base>.+)-(?P<start>\d+)-(?P<end>\d+)\.pdf$", re.IGNORECASE)

def load_history() -> list[str]:
    if HISTORY_FILE.exists():
        try:
            data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                lst = data.get("last_folders", [])
                if isinstance(lst, list):
                    return [p for p in lst if isinstance(p, str)]
        except Exception:
            pass
    return []

def save_history(paths: list[Path]):
    new = [str(p) for p in paths]
    old = load_history()
    merged = []
    for p in new + old:
        if p not in merged:
            merged.append(p)
    merged = merged[:HISTORY_MAX]
    HISTORY_FILE.write_text(json.dumps({"last_folders": merged}, ensure_ascii=False, indent=2), encoding="utf-8")

def choose_folders() -> list[Path]:
    chosen: list[Path] = []
    history = load_history()
    init_dir = history[0] if history else "/"
    root = Tk(); root.withdraw()
    while True:
        folder = filedialog.askdirectory(
            title="結合対象のフォルダを選んでください（キャンセルで終了）",
            initialdir=init_dir
        )
        if not folder:
            break
        p = Path(folder)
        if p not in chosen:
            chosen.append(p)
        init_dir = str(p)
        if not messagebox.askyesno("確認", "さらにフォルダを選びますか？"):
            break
    root.destroy()
    if not chosen:
        raise ValueError("フォルダが選択されませんでした")
    save_history(chosen)
    return chosen

def find_part_groups(folder: Path) -> dict[str, list[tuple[int,int,Path]]]:
    """このフォルダ直下の分割PDFを base ごとにグループ化"""
    groups: dict[str, list[tuple[int,int,Path]]] = {}
    for p in folder.glob("*.pdf"):
        m = PART_PATTERN.match(p.name)
        if not m:
            continue
        base = m.group("base")
        start = int(m.group("start")); end = int(m.group("end"))
        groups.setdefault(base, []).append((start, end, p))
    return groups

def merge_with_writer(input_paths: list[Path], output_path: Path):
    writer = PdfWriter()
    for ip in input_paths:
        r = PdfReader(str(ip))
        if getattr(r, "is_encrypted", False):
            try: r.decrypt("")
            except Exception: raise RuntimeError(f"暗号化で結合不可: {ip.name}")
        for page in r.pages:
            writer.add_page(page)
    with open(output_path, "wb") as f:
        writer.write(f)

def merge_group(base: str, parts: list[tuple[int,int,Path]], folder: Path):
    parts_sorted = sorted(parts, key=lambda t: t[0])
    for i in range(1, len(parts_sorted)):
        if parts_sorted[i][0] != parts_sorted[i-1][1] + 1:
            print(f"警告: {folder} の {base} に隙間/重複の可能性 "
                  f"({parts_sorted[i-1][1]} -> {parts_sorted[i][0]})")

    out_path = folder / f"{base}.pdf"
    if out_path.exists():
        if OVERWRITE_OUTPUT:
            try: out_path.unlink()
            except Exception as e:
                print(f"出力上書き失敗: {out_path} ({e})"); return
        else:
            print(f"スキップ（既存）: {out_path}"); return

    try:
        merge_with_writer([p for _,_,p in parts_sorted], out_path)
        print(f"[結合] {out_path}")
        if DELETE_PARTS:
            for _,_,p in parts_sorted:
                try: p.unlink(); print(f"  削除: {p.name}")
                except Exception as e: print(f"  削除失敗: {p.name} ({e})")
    except Exception as e:
        print(f"結合失敗: {folder} / {base} ({e})")
        if out_path.exists():
            try: out_path.unlink()
            except Exception: pass

def process_one_folder(folder: Path):
    groups = find_part_groups(folder)
    if not groups:
        # 分割PDFが無ければ情報表示のみ
        # print(f"[情報] 分割PDFなし: {folder}")
        return
    for base, parts in groups.items():
        merge_group(base, parts, folder)

def main():
    try:
        roots = choose_folders()
    except ValueError as e:
        print(e); return

    for ri, root in enumerate(roots, 1):
        if not root.exists():
            print(f"[警告] 存在しないフォルダ: {root}")
            continue
        print(f"\n=== ({ri}/{len(roots)}) ルート: {root} ===")
        if RECURSIVE:
            # ルート自身＋全サブフォルダを処理
            to_process = [root] + [p for p in root.rglob("*") if p.is_dir()]
        else:
            to_process = [root]
        for folder in to_process:
            process_one_folder(folder)

if __name__ == "__main__":
    main()