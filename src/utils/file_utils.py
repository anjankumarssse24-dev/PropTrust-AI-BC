"""
File Utilities Module
Helper functions for file handling and storage
"""

import os
import json
from pathlib import Path
from typing import Union


class FileUtils:
    """File handling utilities"""
    
    @staticmethod
    def save_json(data: dict, filepath: str):
        """Save data as JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def load_json(filepath: str) -> dict:
        """Load JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def ensure_dir(directory: Union[str, Path]):
        """Create directory if it doesn't exist"""
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def get_file_extension(filepath: str) -> str:
        """Get file extension"""
        return os.path.splitext(filepath)[1].lower()
    
    @staticmethod
    def is_pdf(filepath: str) -> bool:
        """Check if file is PDF"""
        return FileUtils.get_file_extension(filepath) == '.pdf'
    
    @staticmethod
    def is_image(filepath: str) -> bool:
        """Check if file is image (JPG/PNG)"""
        ext = FileUtils.get_file_extension(filepath)
        return ext in ['.jpg', '.jpeg', '.png']
