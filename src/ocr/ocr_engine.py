"""
OCR Engine Module
Handles document OCR processing using Tesseract and EasyOCR
"""

import pytesseract
import easyocr
import fitz  # PyMuPDF
import cv2
import os
import numpy as np
from pathlib import Path
import json
from datetime import datetime
from PIL import Image


class OCREngine:
    """OCR processing engine for document text extraction"""
    
    def __init__(self, use_easyocr=True):
        """
        Initialize OCR Engine
        
        Args:
            use_easyocr: Whether to use EasyOCR (slower but better for Indian documents)
        """
        self.use_easyocr = use_easyocr
        self.reader = None
        
        if use_easyocr:
            print("Initializing EasyOCR reader with Kannada + English support...")
            self.reader = easyocr.Reader(['kn', 'en'], gpu=False)
    
    def process_document(self, file_path: str, output_dir: str = None) -> dict:
        """
        Process document and extract text
        
        Args:
            file_path: Path to PDF/JPG/PNG file
            output_dir: Directory to save intermediate files
            
        Returns:
            dict: Extracted text and metadata
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Set output directories
        if output_dir is None:
            output_dir = file_path.parent.parent
        
        images_dir = Path(output_dir) / "images"
        ocr_dir = Path(output_dir) / "ocr_text"
        images_dir.mkdir(parents=True, exist_ok=True)
        ocr_dir.mkdir(parents=True, exist_ok=True)
        
        # Extract images from PDF or load image
        image_paths = []
        if file_path.suffix.lower() == '.pdf':
            print(f"Converting PDF to images: {file_path.name}")
            image_paths = self.pdf_to_images(str(file_path), str(images_dir))
        else:
            # Copy image to images folder
            image_paths = [str(file_path)]
        
        # Process each image
        all_text = []
        for img_path in image_paths:
            print(f"Processing image: {Path(img_path).name}")
            
            # Load and enhance image
            image = cv2.imread(img_path)
            enhanced = self.enhance_image(image)
            
            # Extract text
            text = self.extract_text_from_array(enhanced)
            all_text.append(text)
        
        # Combine all text
        combined_text = "\n\n--- PAGE BREAK ---\n\n".join(all_text)
        
        # Create result object
        result = {
            "property_id": f"PRT-{file_path.stem}",
            "file_path": str(file_path),
            "file_name": file_path.name,
            "page_count": len(image_paths),
            "text": combined_text,
            "processed_at": datetime.now().isoformat()
        }
        
        # Save as JSON (for pipeline compatibility)
        json_file = ocr_dir / f"{file_path.stem}_ocr.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        # Also save plain text for easy reading
        txt_file = ocr_dir / f"{file_path.stem}_ocr.txt"
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(combined_text)
        
        print(f"\n✅ OCR completed!")
        print(f"   JSON saved to: {json_file}")
        print(f"   Text saved to: {txt_file}")
        
        return result
    
    def pdf_to_images(self, pdf_path: str, output_folder: str) -> list:
        """
        Convert PDF to images using PyMuPDF
        
        Args:
            pdf_path: Path to PDF file
            output_folder: Folder to save images
            
        Returns:
            list: List of image file paths
        """
        output_folder = Path(output_folder)
        output_folder.mkdir(parents=True, exist_ok=True)
        
        # Open PDF
        pdf_document = fitz.open(pdf_path)
        
        image_paths = []
        pdf_name = Path(pdf_path).stem
        
        # Convert each page to image
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            
            # Render page to image (300 DPI)
            mat = fitz.Matrix(300/72, 300/72)  # 300 DPI scaling
            pix = page.get_pixmap(matrix=mat)
            
            # Save as PNG
            image_path = output_folder / f"{pdf_name}_page_{page_num+1}.png"
            pix.save(str(image_path))
            
            image_paths.append(str(image_path))
            print(f"   Saved page {page_num+1}: {image_path.name}")
        
        pdf_document.close()
        return image_paths
    
    def enhance_image(self, image):
        """
        Enhance image quality for better OCR
        
        Args:
            image: OpenCV image array
            
        Returns:
            Enhanced image
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            denoised, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Dilation and erosion to remove noise
        kernel = np.ones((1, 1), np.uint8)
        processed = cv2.dilate(thresh, kernel, iterations=1)
        processed = cv2.erode(processed, kernel, iterations=1)
        
        return processed
    
    def extract_text_from_array(self, image_array) -> str:
        """
        Extract text from image array using OCR
        
        Args:
            image_array: numpy array of image
            
        Returns:
            str: Extracted text
        """
        if self.use_easyocr and self.reader:
            # Use EasyOCR
            results = self.reader.readtext(image_array)
            text = "\n".join([result[1] for result in results])
        else:
            # Use Tesseract
            text = pytesseract.image_to_string(image_array)
        
        return text
    
    def extract_text(self, image_path: str) -> str:
        """
        Extract text from image file using OCR
        
        Args:
            image_path: Path to image file
            
        Returns:
            str: Extracted text
        """
        image = cv2.imread(image_path)
        enhanced = self.enhance_image(image)
        return self.extract_text_from_array(enhanced)
