"""
Text Translation Module
Translates Kannada and other regional languages to English
"""

import json
from pathlib import Path
from deep_translator import GoogleTranslator
import re


class TextTranslator:
    """Translate regional language text to English"""
    
    def __init__(self):
        """Initialize translator"""
        self.translator = GoogleTranslator(source='kn', target='en')  # Kannada to English
        self.auto_translator = GoogleTranslator(source='auto', target='en')  # Auto-detect
    
    def translate_text(self, text: str, chunk_size: int = 4000) -> dict:
        """
        Translate text from Kannada to English
        
        Args:
            text: Input text in Kannada
            chunk_size: Maximum characters per translation request
            
        Returns:
            Dictionary with original and translated text
        """
        if not text or len(text.strip()) == 0:
            return {
                'original_text': text,
                'translated_text': '',
                'original_length': 0,
                'translated_length': 0
            }
        
        print("\n🌐 Translating Kannada to English...")
        
        # Split text into chunks (Google Translate has character limits)
        chunks = self._split_into_chunks(text, chunk_size)
        translated_chunks = []
        
        for i, chunk in enumerate(chunks):
            try:
                print(f"   Translating chunk {i+1}/{len(chunks)}...")
                # Try Kannada-specific translator first
                translated = self.translator.translate(chunk)
                translated_chunks.append(translated)
            except Exception as e:
                print(f"   ⚠️ Kannada translator failed, trying auto-detect...")
                try:
                    # Fallback to auto-detect
                    translated = self.auto_translator.translate(chunk)
                    translated_chunks.append(translated)
                except Exception as e2:
                    print(f"   ⚠️ Translation failed: {e2}")
                    translated_chunks.append(chunk)  # Use original if translation fails
        
        translated_text = ' '.join(translated_chunks)
        
        print(f"✅ Translation complete!")
        print(f"   Original: {len(text)} chars")
        print(f"   Translated: {len(translated_text)} chars")
        
        return {
            'original_text': text,
            'translated_text': translated_text,
            'original_length': len(text),
            'translated_length': len(translated_text),
            'chunks_processed': len(chunks)
        }
    
    def _split_into_chunks(self, text: str, chunk_size: int) -> list:
        """Split text into chunks for translation"""
        # Split by sentences or paragraphs to avoid breaking context
        sentences = re.split(r'([.!?\n]+)', text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= chunk_size:
                current_chunk += sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks if chunks else [text]
    
    def process_file(self, input_file: str, output_file: str = None) -> dict:
        """
        Translate text from JSON file
        
        Args:
            input_file: Path to input JSON file (with 'text' field)
            output_file: Optional output path
            
        Returns:
            Translation results
        """
        input_path = Path(input_file)
        
        if not input_path.exists():
            raise FileNotFoundError(f"File not found: {input_file}")
        
        # Read input JSON
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Get text to translate
        original_text = data.get('text', '') or data.get('cleaned_text', '')
        
        # Translate
        result = self.translate_text(original_text)
        
        # Create output
        output_data = {
            **data,  # Keep original fields
            'original_text': result['original_text'],
            'translated_text': result['translated_text'],
            'translation_stats': {
                'original_length': result['original_length'],
                'translated_length': result['translated_length'],
                'chunks_processed': result['chunks_processed']
            }
        }
        
        # Update 'text' field to translated version
        output_data['text'] = result['translated_text']
        
        # Save output
        if output_file is None:
            output_file = input_path.parent / f"{input_path.stem}_translated.json"
        
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved to: {output_path}")
        
        return output_data


if __name__ == "__main__":
    # Test translation
    translator = TextTranslator()
    
    # Test with a sample file
    result = translator.process_file(
        "data/ocr_text/178.1_ocr.json"
    )
    
    print(f"\n✅ Translation test complete!")
    print(f"Original (first 200 chars): {result['original_text'][:200]}")
    print(f"Translated (first 200 chars): {result['translated_text'][:200]}")
