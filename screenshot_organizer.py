import os
import time
import shutil
import argparse
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pygetwindow as gw

# デフォルト設定
DEFAULT_WATCH_FOLDER = os.path.join(os.path.expanduser("~"), "Pictures", "Screenshots")
DEFAULT_DEST_BASE_FOLDER = os.path.join(os.path.expanduser("~"), "Desktop", "OrganizedScreenshots")
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp', '.gif'}

class ScreenshotHandler(FileSystemEventHandler):
    def __init__(self, dest_base_folder):
        self.dest_base_folder = dest_base_folder

    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path
            print(f"File created: {file_path}")
            if os.path.splitext(file_path)[1].lower() in IMAGE_EXTENSIONS:
                self.process_new_screenshot(file_path)

    def on_modified(self, event):
        if not event.is_directory:
            file_path = event.src_path
            print(f"File modified: {file_path}")
            if os.path.splitext(file_path)[1].lower() in IMAGE_EXTENSIONS:
                self.process_new_screenshot(file_path)

    def process_new_screenshot(self, file_path):
        # 保存中のファイルが安定するまで少し待つ
        time.sleep(0.2)
        if not os.path.exists(file_path):
            print(f"File no longer exists: {file_path}")
            return
        window_title = get_active_window_title()
        if not window_title:
            window_title = "Unknown"
            print(f"Active window could not be detected for: {file_path}")
        self.move_to_folder(file_path, window_title)

    def move_to_folder(self, file_path, window_title):
        # ウィンドウ名をフォルダ名に（無効な文字を置換）
        safe_title = "".join(c for c in window_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        if not safe_title:
            safe_title = "Unknown"
        dest_folder = os.path.join(self.dest_base_folder, safe_title)
        os.makedirs(dest_folder, exist_ok=True)
        dest_path = os.path.join(dest_folder, os.path.basename(file_path))
        shutil.move(file_path, dest_path)
        print(f"Moved {file_path} to {dest_path}")

def get_active_window_title():
    try:
        active_window = gw.getActiveWindow()
        if active_window and active_window.title:
            return active_window.title
    except Exception as e:
        print(f"Error getting active window: {e}")
    return None

def main():
    parser = argparse.ArgumentParser(description="Organize screenshots by active window name.")
    parser.add_argument('--watch', help='Folder to watch for new screenshots')
    parser.add_argument('--dest', help='Base folder for organized screenshots')
    args = parser.parse_args()

    watch_folder = args.watch
    dest_base_folder = args.dest

    # 引数が指定されていない場合、ユーザーに質問
    if not watch_folder:
        watch_folder = input(f"監視するフォルダを入力してください（省略すると {DEFAULT_WATCH_FOLDER}）：").strip()
        if not watch_folder:
            watch_folder = DEFAULT_WATCH_FOLDER

    if not dest_base_folder:
        dest_base_folder = input(f"分類先のベースフォルダを入力してください（省略すると {DEFAULT_DEST_BASE_FOLDER}）：").strip()
        if not dest_base_folder:
            dest_base_folder = DEFAULT_DEST_BASE_FOLDER

    # フォルダが存在するかチェック
    if not os.path.exists(watch_folder):
        print(f"Watch folder does not exist: {watch_folder}")
        print("Creating it...")
        os.makedirs(watch_folder, exist_ok=True)

    if not os.path.exists(dest_base_folder):
        print(f"Destination base folder does not exist: {dest_base_folder}")
        print("Creating it...")
        os.makedirs(dest_base_folder, exist_ok=True)

    # 監視を開始
    event_handler = ScreenshotHandler(dest_base_folder)
    observer = Observer()
    observer.schedule(event_handler, watch_folder, recursive=False)
    observer.start()

    print(f"Watching folder: {watch_folder}")
    print(f"Destination base: {dest_base_folder}")
    print("フォルダへの画像保存を監視しています。Ctrl+C で停止します。")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()