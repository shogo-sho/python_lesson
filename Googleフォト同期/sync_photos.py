import os
import json
import pickle
import mimetypes
import csv
import requests
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# ==========================================
# 設定エリア（ここを書き換えてください）
# ==========================================
# 同期したい親フォルダのパス
# Windowsの場合は r"C:\Users\..." のように r をつけるのが無難です
TARGET_DIR = r"/Users/shogo/画像/引越し用/圧縮後"

# 認証情報ファイルの名前
CLIENT_SECRET_FILE = 'client_secret.json'

# アップロード済み履歴ファイル（重複アップロード防止用）
HISTORY_FILE = 'uploaded_log.json'

# 生成するアルバムURLリストのファイル名
CSV_OUTPUT_FILE = 'album_urls.csv'

# スコープ設定（2025年以降の仕様に対応）
SCOPES = [
    'https://www.googleapis.com/auth/photoslibrary.appendonly',
    'https://www.googleapis.com/auth/photoslibrary.readonly.appcreateddata',
    'https://www.googleapis.com/auth/photoslibrary.edit.appcreateddata'
]

# ==========================================
# 以下、プログラム本体
# ==========================================

def get_authenticated_service():
    """OAuth認証を行い、APIサービスを取得する"""
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('photoslibrary', 'v1', credentials=creds, static_discovery=False)

def load_history():
    """アップロード済みファイルの履歴を読み込む"""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            try:
                return set(json.load(f))
            except json.JSONDecodeError:
                return set()
    return set()

def save_history(history_set):
    """アップロード済みファイルの履歴を保存する"""
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(history_set), f, indent=4, ensure_ascii=False)

def get_or_create_album(service, album_title):
    """
    指定したタイトルのアルバムを探し、IDとURLを返す。
    なければ新規作成する。
    """
    next_page_token = None
    while True:
        # このアプリが作成したアルバムのみ検索可能
        results = service.albums().list(
            pageSize=50, 
            pageToken=next_page_token, 
            excludeNonAppCreatedData=True
        ).execute()
        albums = results.get('albums', [])
        
        for album in albums:
            if album.get('title') == album_title:
                return album.get('id'), album.get('productUrl')
        
        next_page_token = results.get('nextPageToken')
        if not next_page_token:
            break
            
    # 見つからなければ作成
    print(f"  [新規作成] アルバムを作成します: {album_title}")
    new_album = service.albums().create(body={
        'album': {'title': album_title}
    }).execute()
    return new_album.get('id'), new_album.get('productUrl')

def get_album_items(service, album_id):
    """アルバム内の写真一覧（ファイル名とID）を取得する"""
    items_map = {} # {filename: mediaItemId}
    next_page_token = None
    
    while True:
        body = {
            'albumId': album_id, 
            'pageSize': 100, 
            'pageToken': next_page_token
        }
        try:
            results = service.mediaItems().search(body=body).execute()
            items = results.get('mediaItems', [])
            
            for item in items:
                filename = item.get('filename')
                item_id = item.get('id')
                if filename and item_id:
                    items_map[filename] = item_id
                    
            next_page_token = results.get('nextPageToken')
            if not next_page_token:
                break
        except Exception as e:
            print(f"    警告: アルバム内容の取得中にエラーが発生しました: {e}")
            break
            
    return items_map

def remove_items_from_album(service, album_id, item_ids):
    """指定されたアイテムIDをアルバムから削除（登録解除）する"""
    if not item_ids:
        return
        
    chunk_size = 50
    print(f"    -> ローカルにない {len(item_ids)} 枚の写真をアルバムから除外します...")
    
    for i in range(0, len(item_ids), chunk_size):
        chunk = item_ids[i:i + chunk_size]
        body = {
            'mediaItemIds': chunk
        }
        try:
            service.albums().batchRemoveMediaItems(albumId=album_id, body=body).execute()
        except Exception as e:
            print(f"    削除エラー: {e}")

def upload_image(service, file_path, filename):
    """画像をアップロードしてアップロードトークンを取得する"""
    print(f"    アップロード中: {filename} ...")
    
    try:
        with open(file_path, 'rb') as f:
            image_data = f.read()
    except IOError as e:
        print(f"    ファイル読み込みエラー: {e}")
        return None
        
    headers = {
        'Authorization': 'Bearer ' + service._http.credentials.token,
        'Content-Type': 'application/octet-stream',
        'X-Goog-Upload-File-Name': filename.encode('utf-8'), # 日本語対応
        'X-Goog-Upload-Protocol': 'raw',
    }
    
    try:
        response = requests.post(
            'https://photoslibrary.googleapis.com/v1/uploads',
            headers=headers,
            data=image_data
        )
        
        if response.status_code == 200:
            return response.content.decode('utf-8')
        else:
            print(f"    APIエラー: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"    通信エラー: {e}")
        return None

def batch_create_media(service, album_id, new_media_items):
    """アップロードトークンを使ってアルバムにメディアを追加する"""
    if not new_media_items:
        return
        
    body = {
        'albumId': album_id,
        'newMediaItems': new_media_items
    }
    
    try:
        service.mediaItems().batchCreate(body=body).execute()
        print(f"    -> {len(new_media_items)} 枚の画像をアルバムに追加しました。")
    except Exception as e:
        print(f"    -> 追加エラー: {e}")

def main():
    # 認証
    service = get_authenticated_service()
    # 履歴読み込み
    uploaded_history = load_history()
    
    # CSV出力用のリスト
    csv_rows = [['AlbumName', 'URL']]
    
    if not os.path.exists(TARGET_DIR):
        print(f"エラー: 指定されたフォルダが見つかりません: {TARGET_DIR}")
        return

    print(f"親フォルダ '{TARGET_DIR}' の同期（追加・削除・URL出力）を開始します...\n")

    # 親フォルダ内のサブフォルダを走査
    subfolders = sorted([f for f in os.listdir(TARGET_DIR) if os.path.isdir(os.path.join(TARGET_DIR, f))])
    
    for folder_name in subfolders:
        folder_path = os.path.join(TARGET_DIR, folder_name)
        
        print(f"■ フォルダ処理中: {folder_name}")
        
        # 1. アルバムIDとURLの取得
        album_id, album_url = get_or_create_album(service, folder_name)
        
        # CSVリストに追加
        csv_rows.append([folder_name, album_url])
        
        # 2. ローカルファイルのリスト作成
        local_files = set()
        files_to_upload = []
        
        # フォルダ内のファイルをチェック
        for file in sorted(os.listdir(folder_path)):
            if file.startswith('.'): continue # 隠しファイルは無視
            
            file_full_path = os.path.join(folder_path, file)
            
            if os.path.isfile(file_full_path):
                # 画像判定（簡易）
                mime_type, _ = mimetypes.guess_type(file_full_path)
                if mime_type and mime_type.startswith('image'):
                    local_files.add(file)
                    
                    # 履歴になければアップロード候補へ
                    if file_full_path not in uploaded_history:
                        files_to_upload.append((file, file_full_path))
        
        # 3. 【同期削除】アルバムにあるがローカルにないものを除外
        album_items_map = get_album_items(service, album_id)
        items_to_remove = []
        
        for album_filename, item_id in album_items_map.items():
            if album_filename not in local_files:
                items_to_remove.append(item_id)
        
        if items_to_remove:
            remove_items_from_album(service, album_id, items_to_remove)
        
        # 4. 【新規追加】アップロード処理
        if not files_to_upload:
            print("  -> 新しい追加画像はありません。")
        else:
            batch_items = []
            processed_paths = []
            
            for idx, (fname, fpath) in enumerate(files_to_upload):
                upload_token = upload_image(service, fpath, fname)
                
                if upload_token:
                    batch_items.append({
                        'simpleMediaItem': {'uploadToken': upload_token}
                    })
                    processed_paths.append(fpath)
                
                # 50枚ごと、または最後にまとめて登録
                if len(batch_items) == 50 or idx == len(files_to_upload) - 1:
                    if batch_items:
                        batch_create_media(service, album_id, batch_items)
                        
                        # 成功したら履歴を更新
                        for p in processed_paths:
                            uploaded_history.add(p)
                        save_history(uploaded_history)
                        
                        batch_items = []
                        processed_paths = []

    # 5. URLリストをCSVに出力
    try:
        with open(CSV_OUTPUT_FILE, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(csv_rows)
        print(f"\n完了: アルバムURLリストを '{CSV_OUTPUT_FILE}' に保存しました。")
    except Exception as e:
        print(f"\nエラー: CSVファイルの保存に失敗しました: {e}")

    print("\nすべての同期処理が完了しました！")

if __name__ == '__main__':
    main()