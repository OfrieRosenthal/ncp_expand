import os

def remove_files_in_target(target_folder):
    for root, dirs, files in os.walk(target_folder):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Failed to remove {file_path}: {e}")

if __name__ == "__main__":
    target_folder = "../target"  # Change this to your target folder path if needed
    remove_files_in_target(target_folder)