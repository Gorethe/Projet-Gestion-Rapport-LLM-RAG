import os
import shutil

def prepare_processed_folder(processed_path):
    if not os.path.exists(processed_path):
        os.makedirs(processed_path)

def move_processed_documents(data_path, processed_path):
    """Déplace les fichiers de data_path vers processed_path"""
    prepare_processed_folder(processed_path)
    
    for filename in os.listdir(data_path):
        file_path = os.path.join(data_path, filename)
        if os.path.isfile(file_path):
            shutil.move(file_path, os.path.join(processed_path, filename))
            print(f"Fichier déplacé : {filename}")
