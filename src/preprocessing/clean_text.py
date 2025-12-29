"""
Text Preprocessing Module
Cleans and normalizes OCR text output
"""

import re
import string
from typing import Dict
from pathlib import Path
import json


class TextCleaner:
    """Text preprocessing and cleaning utilities"""
    
    def __init__(self):
        # Common OCR error mappings
        self.ocr_corrections = {
            r'\b0\b': 'O',  # Standalone 0 to O
            r'([A-Z])0([A-Z])': r'\1O\2',  # 0 between letters to O
            r'l\b': '1',  # Lowercase L at end to 1
            r'\bl\b': 'I',  # Standalone l to I
            r'rn': 'm',  # Common OCR error
        }
        
        # Keywords to preserve (case-insensitive)
        self.important_keywords = [
            'survey', 'owner', 'name', 'bank', 'loan', 'mortgage', 'encumbrance',
            'case', 'court', 'mutation', 'sale', 'deed', 'registration', 'village',
            'taluk', 'district', 'extent', 'boundaries', 'north', 'south', 'east', 'west',
            'khata', 'hissa', 'acre', 'cents', 'hectare', 'property', 'land', 'plot'
        ]
    
    def clean_text(self, raw_text: str) -> str:
        """
        Clean and normalize OCR text
        ISSUE 2 FIX: Ensure cleaned text length > 0 if OCR text exists
        
        Args:
            raw_text: Raw OCR output
            
        Returns:
            str: Cleaned text
        """
        if not raw_text or not raw_text.strip():
            return ""
        
        # Step 1: Remove extreme noise
        text = self.remove_noise(raw_text)
        
        # Step 2: Fix common OCR errors
        text = self.fix_ocr_errors(text)
        
        # Step 3: Normalize text
        text = self.normalize_text(text)
        
        # Step 4: Remove excessive whitespace
        text = self.clean_whitespace(text)
        
        # ISSUE 2 FIX: Safety check - if cleaned text is empty but raw wasn't, return minimally cleaned
        if not text.strip() and raw_text.strip():
            # Fallback: only remove control chars and normalize whitespace
            text = re.sub(r'[\x00-\x1F\x7F]', '', raw_text)
            text = re.sub(r' +', ' ', text)
            text = text.strip()
        
        return text
    
    def remove_noise(self, text: str) -> str:
        """
        Remove noise and unwanted characters
        ISSUE 2 FIX: Must preserve Unicode (Kannada), names, numbers, dates, currency (₹), slashes
        
        Args:
            text: Input text
            
        Returns:
            str: Text with noise removed
        """
        # Remove page headers/footers patterns
        text = re.sub(r'First\s+Previous\s+Next\s+Last', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Print Page[_\s]*No[:\s]*\d+', '', text, flags=re.IGNORECASE)
        
        # CRITICAL FIX: Do NOT remove Unicode characters (Kannada text)
        # Only remove control characters and excessive symbols
        # Keep: letters (all scripts), digits, spaces, punctuation, currency symbols
        # Remove only: control chars, excessive symbols
        text = re.sub(r'[\x00-\x1F\x7F]', '', text)  # Control characters only
        
        # Remove URLs and email-like patterns
        text = re.sub(r'http\S+|www\.\S+', '', text)
        
        # Remove standalone special characters (but keep when part of text)
        text = re.sub(r'\s+[.,;:!?]\s+', ' ', text)
        
        return text
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize text format
        
        Args:
            text: Input text
            
        Returns:
            str: Normalized text
        """
        # Standardize number formats
        # Preserve survey numbers like 45/2A, 123/4B
        text = re.sub(r'(\d+)\s*/\s*(\d+)', r'\1/\2', text)
        
        # Standardize date formats
        text = re.sub(r'(\d{1,2})/(\d{1,2})/(\d{4})', r'\1/\2/\3', text)
        
        # Fix spacing around punctuation
        text = re.sub(r'\s+([.,;:!?])', r'\1', text)
        text = re.sub(r'([.,;:!?])(\w)', r'\1 \2', text)
        
        # Standardize case for common abbreviations
        text = re.sub(r'\brtc\b', 'RTC', text, flags=re.IGNORECASE)
        text = re.sub(r'\bec\b', 'EC', text, flags=re.IGNORECASE)
        text = re.sub(r'\bsbi\b', 'SBI', text, flags=re.IGNORECASE)
        text = re.sub(r'\bhdfc\b', 'HDFC', text, flags=re.IGNORECASE)
        text = re.sub(r'\bicici\b', 'ICICI', text, flags=re.IGNORECASE)
        
        return text
    
    def fix_ocr_errors(self, text: str) -> str:
        """
        Fix common OCR errors (ISSUE 4: Improve loan context quality)
        
        Args:
            text: Input text
            
        Returns:
            str: Text with OCR errors corrected
        """
        for pattern, replacement in self.ocr_corrections.items():
            text = re.sub(pattern, replacement, text)
        
        # Fix common word errors
        text = re.sub(r'\bSurvey\s+N[o0]\.?\s*', 'Survey No. ', text, flags=re.IGNORECASE)
        text = re.sub(r'\bOwner\s+Name', 'Owner Name', text, flags=re.IGNORECASE)
        
        # ISSUE 4 FIX: OCR normalization for mixed Kannada-English loan context readability
        text = re.sub(r'\bans grew\b', 'has granted', text, flags=re.IGNORECASE)
        text = re.sub(r'\btoan\b', 'loan', text, flags=re.IGNORECASE)
        text = re.sub(r'\bIoan\b', 'loan', text, flags=re.IGNORECASE)
        text = re.sub(r'\b0f\b', 'of', text, flags=re.IGNORECASE)
        text = re.sub(r'\blOan\b', 'loan', text, flags=re.IGNORECASE)
        text = re.sub(r'\bthat\s+grew\b', 'has granted', text, flags=re.IGNORECASE)
        text = re.sub(r'\bManager\s+S\.B\.M\.?\b', 'Manager State Bank of Mysore', text, flags=re.IGNORECASE)
        text = re.sub(r'\bS\.?B\.?M\.?\b', 'State Bank of Mysore', text, flags=re.IGNORECASE)
        text = re.sub(r'\bPurava\s+branch\b', 'Puravara branch', text, flags=re.IGNORECASE)
        text = re.sub(r'\bRs\.?\s+', 'Rs. ', text)  # Standardize rupee notation
        text = re.sub(r'\b(\d{3,})\.\s*(\d{3})/-', r'\1,\2/-', text)  # Fix amount format: 550.000 -> 550,000
        
        return text
    
    def clean_whitespace(self, text: str) -> str:
        """
        Clean excessive whitespace
        
        Args:
            text: Input text
            
        Returns:
            str: Text with cleaned whitespace
        """
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        
        # Replace multiple newlines with double newline
        text = re.sub(r'\n\s*\n+', '\n\n', text)
        
        # Remove leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        return text.strip()
    
    def extract_key_sections(self, text: str) -> Dict[str, str]:
        """
        Extract key sections from document
        
        Args:
            text: Cleaned text
            
        Returns:
            dict: Extracted sections
        """
        sections = {}
        
        # Try to identify and extract important sections
        lines = text.split('\n')
        current_section = "general"
        sections[current_section] = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line is a section header
            lower_line = line.lower()
            if any(keyword in lower_line for keyword in ['owner', 'survey', 'extent', 'boundaries']):
                current_section = line
                sections[current_section] = []
            else:
                sections[current_section].append(line)
        
        # Convert lists to strings
        for key in sections:
            sections[key] = '\n'.join(sections[key])
        
        return sections
    
    def to_json(self, cleaned_text: str) -> Dict:
        """
        Convert cleaned text to JSON format
        
        Args:
            cleaned_text: Cleaned text
            
        Returns:
            dict: JSON output
        """
        return {
            "clean_text": cleaned_text,
            "char_count": len(cleaned_text),
            "word_count": len(cleaned_text.split()),
            "line_count": len(cleaned_text.split('\n'))
        }
    
    def process_file(self, input_file: str, output_file: str = None) -> Dict:
        """
        Process a text file and clean it
        
        Args:
            input_file: Path to input text file
            output_file: Path to save cleaned text (optional)
            
        Returns:
            dict: Processing results
        """
        input_path = Path(input_file)
        
        if not input_path.exists():
            raise FileNotFoundError(f"File not found: {input_file}")
        
        # Read input (support both .txt and .json)
        if input_path.suffix == '.json':
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Check for translated_text first (from translation), then 'text' (from OCR)
                raw_text = data.get('translated_text', data.get('text', ''))
        else:
            with open(input_path, 'r', encoding='utf-8') as f:
                raw_text = f.read()
        
        # Clean text
        cleaned_text = self.clean_text(raw_text)
        
        # Determine output file path (always use JSON for pipeline)
        if output_file is None:
            output_file = input_path.parent / f"{input_path.stem}_cleaned.json"
        
        output_path = Path(output_file)
        
        # Create JSON output
        json_output = self.to_json(cleaned_text)
        json_output['input_file'] = str(input_path)
        json_output['output_file'] = str(output_path)
        json_output['original_char_count'] = len(raw_text)
        
        # Save as JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_output, f, indent=2, ensure_ascii=False)
        
        # Also save as plain text for easy reading
        txt_path = output_path.parent / f"{output_path.stem}.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_text)
        
        return {
            "raw_text": raw_text,
            "cleaned_text": cleaned_text,
            "output_file": str(output_path),
            "txt_file": str(txt_path),
            "stats": json_output
        }
