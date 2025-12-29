"""
Complete Property Verification Pipeline
Run all 6 phases with a single command:
1. OCR Extraction
2. Text Cleaning  
3. Entity Extraction (NER)
4. Document Classification
5. Risk Scoring
6. Report Generation

Usage:
    python run_verification.py <pdf_file_path>
    
Example:
    python run_verification.py data/raw_docs/178.1.pdf
"""

import sys
import os
from pathlib import Path
import time
from datetime import datetime
import json

# Import all pipeline modules
from src.ocr.ocr_engine import OCREngine
from src.translation.translator import TextTranslator
from src.preprocessing.clean_text import TextCleaner
from src.ner.ner_extractor import NERExtractor
from src.classifier.doc_classifier import DocumentClassifier
from src.risk.risk_engine import RiskEngine
from src.reports.report_generator import ReportGenerator
from extract_rtc_fields import extract_rtc_fields


class VerificationPipeline:
    """Complete end-to-end property verification pipeline"""
    
    def __init__(self):
        """Initialize all pipeline components"""
        print("\n" + "="*70)
        print("PROPERTY DOCUMENT VERIFICATION SYSTEM")
        print("="*70)
        print("Initializing pipeline components...")
        
        self.ocr = OCREngine()
        self.translator = TextTranslator()
        self.cleaner = TextCleaner()
        self.ner = NERExtractor()
        self.classifier = DocumentClassifier()
        self.risk_engine = RiskEngine()
        self.report_gen = ReportGenerator()
        
        print("✅ All components initialized")
    
    def run(self, pdf_path: str, open_report: bool = True) -> dict:
        """
        Run complete verification pipeline
        
        Args:
            pdf_path: Path to PDF document
            open_report: Whether to open HTML report after generation
            
        Returns:
            Dictionary with all output file paths
        """
        start_time = time.time()
        
        # Validate input
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Extract document ID from filename
        document_id = Path(pdf_path).stem
        
        print(f"\n📄 Processing Document: {document_id}")
        print(f"📂 Input File: {pdf_path}")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        results = {
            'document_id': document_id,
            'input_file': pdf_path,
            'outputs': {}
        }
        
        try:
            # Phase 1: OCR Extraction
            print("\n" + "="*70)
            print("PHASE 1/6: OCR EXTRACTION")
            print("="*70)
            ocr_output = self.ocr.process_document(pdf_path)
            results['outputs']['ocr'] = ocr_output
            print(f"✅ OCR Complete: {len(ocr_output.get('text', ''))} characters extracted")
            
            # Phase 1.5: Translation (Kannada to English)
            print("\n" + "="*70)
            print("PHASE 1.5/6: KANNADA TO ENGLISH TRANSLATION")
            print("="*70)
            ocr_file = f"data/ocr_text/{document_id}_ocr.json"
            translated_output = self.translator.process_file(ocr_file)
            results['outputs']['translated'] = translated_output
            print(f"✅ Translation Complete: {len(translated_output.get('translated_text', ''))} characters")
            
            # Phase 1.75: RTC Field Extraction
            print("\n" + "="*70)
            print("PHASE 1.75/6: RTC FIELD EXTRACTION")
            print("="*70)
            translated_file = f"data/ocr_text/{document_id}_ocr_translated.json"
            translated_text = translated_output.get('translated_text', '')
            # CRITICAL: Pass document_id for correct hissa extraction (e.g., 178.1 -> hissa 1)
            rtc_fields = extract_rtc_fields(translated_text, document_id=document_id)
            
            # Save RTC fields
            rtc_output_path = Path(f"data/ocr_text/{document_id}_rtc_fields.json")
            with open(rtc_output_path, 'w', encoding='utf-8') as f:
                json.dump(rtc_fields, f, indent=2, ensure_ascii=False)
            
            results['outputs']['rtc_fields'] = rtc_fields
            
            # Print key findings
            print("📋 Extracted RTC Fields:")
            if rtc_fields.get('survey_number'):
                print(f"   • Survey Number: {rtc_fields['survey_number']}")
            if rtc_fields.get('extent_acres'):
                print(f"   • Extent: {rtc_fields['extent_acres']} Acres {rtc_fields.get('extent_guntas', '')} Guntas")
            if rtc_fields.get('owner_name'):
                print(f"   • Owner: {rtc_fields['owner_name']}")
            if rtc_fields.get('loan_details'):
                print(f"   • Loans Found: {len(rtc_fields['loan_details'])} entries")
                for loan in rtc_fields['loan_details']:
                    print(f"     - Amount: {loan.get('amount', 'N/A')}")
            if rtc_fields.get('mutation_details'):
                print(f"   • Mutations: {len(rtc_fields['mutation_details'])} records")
            
            print(f"✅ RTC Extraction Complete: {len([v for v in rtc_fields.values() if v])} fields extracted")
            
            # Phase 2: Text Cleaning (on translated text)
            print("\n" + "="*70)
            print("PHASE 2/6: TEXT CLEANING")
            print("="*70)
            translated_file = f"data/ocr_text/{document_id}_ocr_translated.json"
            # Specify output file name to avoid _translated_cleaned naming
            cleaned_file = f"data/ocr_text/{document_id}_ocr_cleaned.json"
            cleaned_output = self.cleaner.process_file(translated_file, output_file=cleaned_file)
            results['outputs']['cleaned'] = cleaned_output
            print(f"✅ Text Cleaned: {len(cleaned_output.get('cleaned_text', ''))} characters")
            
            # Phase 3: Entity Extraction (NER)
            print("\n" + "="*70)
            print("PHASE 3/6: ENTITY EXTRACTION (NER)")
            print("="*70)
            entities_output = self.ner.process_file(cleaned_file)
            results['outputs']['entities'] = entities_output
            
            # Count entities (handle both list and boolean values)
            entities_dict = entities_output.get('entities', {})
            entity_counts = {}
            for k, v in entities_dict.items():
                if isinstance(v, list):
                    entity_counts[k] = len(v)
                elif isinstance(v, bool):
                    entity_counts[k] = 1 if v else 0
                else:
                    entity_counts[k] = 0
            
            print(f"✅ Entities Extracted:")
            for entity_type, count in entity_counts.items():
                print(f"   • {entity_type}: {count}")
            
            # Phase 4: Document Classification
            print("\n" + "="*70)
            print("PHASE 4/6: DOCUMENT CLASSIFICATION")
            print("="*70)
            entities_file = f"data/ocr_text/{document_id}_ocr_cleaned_entities.json"
            classification_output = self.classifier.classify_from_entity_file(entities_file)
            results['outputs']['classification'] = classification_output
            
            # Extract classification from nested structure
            classification = classification_output.get('classification', {})
            confidence = classification.get('confidence', 0) or 0
            print(f"✅ Classification: {classification.get('label')} "
                  f"({confidence*100:.1f}% confidence)")
            
            # Phase 5: Risk Scoring
            print("\n" + "="*70)
            print("PHASE 5/6: RISK SCORING")
            print("="*70)
            classification_file = f"data/ocr_text/{document_id}_ocr_cleaned_classification.json"
            risk_output = self.risk_engine.calculate_from_files(entities_file, classification_file)
            results['outputs']['risk'] = risk_output
            
            risk_assessment = risk_output.get('risk_assessment', {})
            risk_score = risk_assessment.get('risk_score', 0)
            risk_level = risk_assessment.get('risk_level', 'Unknown')
            print(f"✅ Risk Score: {risk_score}/100 ({risk_level} RISK)")
            
            # Phase 6: Report Generation
            print("\n" + "="*70)
            print("PHASE 6/6: REPORT GENERATION")
            print("="*70)
            risk_file = f"data/ocr_text/{document_id}_risk_assessment.json"
            
            rtc_fields_file = f"data/ocr_text/{document_id}_rtc_fields.json"
            report_path = self.report_gen.generate_report(
                document_id=document_id,
                ocr_file=ocr_file,
                cleaned_file=cleaned_file,
                entities_file=entities_file,
                classification_file=classification_file,
                risk_file=risk_file,
                rtc_fields_file=rtc_fields_file
            )
            results['outputs']['report'] = report_path
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Final Summary
            print("\n" + "="*70)
            print("✅ VERIFICATION COMPLETE!")
            print("="*70)
            print(f"\n📊 FINAL RESULTS:")
            print(f"   Document ID: {document_id}")
            print(f"   Classification: {classification_output.get('classification', {}).get('label')}")
            print(f"   Risk Score: {risk_score}/100 ({risk_level})")
            print(f"   Execution Time: {execution_time:.2f} seconds")
            
            print(f"\n📁 OUTPUT FILES:")
            print(f"   1. OCR Text: {ocr_file}")
            print(f"   2. Cleaned Text: {cleaned_file}")
            print(f"   3. Entities: {entities_file}")
            print(f"   4. Classification: {classification_file}")
            print(f"   5. Risk Assessment: {risk_file}")
            print(f"   6. HTML Report: {report_path}")
            
            print(f"\n🌐 VIEW REPORT:")
            print(f"   Open in browser: file:///{report_path}")
            
            # Open report in browser
            if open_report:
                try:
                    import webbrowser
                    webbrowser.open(f"file:///{report_path}")
                    print(f"\n✅ Report opened in browser")
                except Exception as e:
                    print(f"\n⚠️ Could not auto-open report: {e}")
            
            print("\n" + "="*70)
            
            return results
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            raise


def main():
    """Main entry point"""
    
    # Check command line arguments
    if len(sys.argv) < 2:
        print("\n❌ Error: PDF file path required")
        print("\nUsage:")
        print("   python run_verification.py <pdf_file_path>")
        print("\nExample:")
        print("   python run_verification.py data/raw_docs/178.1.pdf")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    # Run pipeline
    pipeline = VerificationPipeline()
    results = pipeline.run(pdf_path)
    
    # Exit successfully
    sys.exit(0)


if __name__ == "__main__":
    main()
