"""
Named Entity Recognition Module
Extracts entities like owner names, survey numbers, bank names, etc.
"""

import spacy
import re
from typing import Dict, List
from pathlib import Path
import json
from datetime import datetime


class NERExtractor:
    """Entity extraction using spaCy NER and custom patterns"""
    
    def __init__(self, model_path: str = None):
        """
        Initialize NER model
        
        Args:
            model_path: Path to trained spaCy model (optional)
        """
        # Load spaCy model
        if model_path:
            self.nlp = spacy.load(model_path)
        else:
            # Use default English model
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except:
                print("Downloading en_core_web_sm model...")
                import subprocess
                subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
                self.nlp = spacy.load("en_core_web_sm")
        
        # Define custom patterns for property documents
        self.patterns = self._define_patterns()
    
    def _define_patterns(self) -> Dict:
        """Define regex patterns for entity extraction"""
        # Bank name mappings (full names, abbreviations, legacy names)
        self.bank_mappings = {
            'SBM': 'State Bank of Mysore (now SBI)',
            'S.B.M': 'State Bank of Mysore (now SBI)',
            'State Bank of Mysore': 'State Bank of Mysore (now SBI)',
            'SBI': 'State Bank of India',
            'State Bank of India': 'State Bank of India',
            'HDFC': 'HDFC Bank',
            'ICICI': 'ICICI Bank',
            'Axis': 'Axis Bank',
            'BOB': 'Bank of Baroda',
            'PNB': 'Punjab National Bank',
            'Canara': 'Canara Bank',
            'Union': 'Union Bank'
        }
        
        return {
            'survey_no': [
                r'Survey\s*(?:No|Number)\.?\s*[:\-]?\s*(\d+[/\-]?\d*[A-Za-z]?)',
                r'(?:Sy\.?\s*No\.?\s*|S\.?\s*No\.?\s*)(\d+[/\-]?\d*[A-Za-z]?)',
                r'\b(\d{1,4}[/\-]\d{1,3}[A-Za-z]?)\b',
                r'Sno[:\s]*(\d+[/\-]?\d*)',
            ],
            'owner_name': [
                r'(?:Owner|Holder|Name)[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})',
                r'Name[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'Cultivator[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'Pattadar[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            ],
            'khata_no': [
                r'Khata\s*(?:No|Number)\.?\s*[:\-]?\s*(\d+)',
                r'Account\s*(?:No|Number)\.?\s*[:\-]?\s*(\d+)',
                r'Hissa\s*(?:No|Number)\.?\s*[:\-]?\s*(\d+)',
            ],
            'extent': [
                r'Extent[:\s]*([\d.]+)\s*(?:Acres?|Guntas?|Hectares?)',
                r'Area[:\s]*([\d.]+)\s*(?:Acres?|Guntas?|Hectares?)',
                r'([\d.]+)\s*(?:Ac|Gnt|Ha)\b',
            ],
            'loan_bank': [
                r'\b(SBI|State Bank|HDFC|ICICI|Axis Bank|Bank of Baroda|Canara Bank|PNB|Union Bank)\b',
                r'(?:Loan|Mortgage|Charge)\s+(?:from|by|with)\s+([A-Z][a-z]+\s+Bank)',
                r'\b([A-Z][a-z]+\s+Bank(?:\s+of\s+[A-Z][a-z]+)?)\b',
            ],
            'loan_amount': [
                r'(?:Loan|Amount|Rs\.?)[:\s]*(?:Rs\.?\s*)?(\d+(?:,\d{3})*(?:\.\d{2})?)',
                r'₹\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
                r'(\d{3,},?\d{3,}\.?[\d\-/]*)',  # Pattern like 2000001- or 385606
            ],
            'date': [
                r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{4})\b',  # DD/MM/YYYY or DD-MM-YYYY
                r'\b(\d{4}[/-]\d{1,2}[/-]\d{1,2})\b',  # YYYY/MM/DD
            ],
            'bank': [
                r'\b(State\s+Bank\s+of\s+Mysore|S\.?B\.?M\.?)\b',
                r'\b(State\s+Bank\s+of\s+India|SBI)\b',
                r'\b(HDFC\s+Bank|HDFC)\b',
                r'\b(ICICI\s+Bank|ICICI)\b',
                r'\b(Axis\s+Bank|Axis)\b',
                r'\b(Bank\s+of\s+Baroda|BOB)\b',
                r'\b(Punjab\s+National\s+Bank|PNB)\b',
                r'\b(Canara\s+Bank)\b',
                r'\b(Union\s+Bank)\b',
                r'([A-Z][a-z]+\s+Bank(?:\s+of\s+[A-Z][a-z]+)?)\b',
                r'\b([A-Z\.]+)\s+(?:Bank|branch)\b'
            ],
            'extent': [
                r'(\d+\.?\d*)\s*(?:Acre|Acres|acre|acres)',
                r'(\d+\.?\d*)\s*(?:Hectare|Hectares|hectare|hectares|Ha|ha)',
                r'(\d+\.?\d*)\s*(?:Cent|Cents|cent|cents)',
                r'(\d+\.?\d*)\s*(?:Sq\.?\s*(?:ft|feet|meter|metre|m))'
            ],
            'case_no': [
                r'(?:Civil\s+Suit|C\.S\.|CS)\s*No\.?\s*(\d+[/\-]?\d*)',
                r'(?:Case\s+No|Case)\s*[:\-]?\s*(\d+[/\-]?\d*)',
                r'(?:Criminal\s+Case|Cr\.C\.|CC)\s*No\.?\s*(\d+[/\-]?\d*)'
            ],
            'village': [
                r'Village[:\s]+([A-Z][a-zA-Z\s]+)',
                r'Gramam[:\s]+([A-Z][a-zA-Z\s]+)'
            ],
            'taluk': [
                r'Taluk[:\s]+([A-Z][a-zA-Z\s]+)',
                r'Taluka[:\s]+([A-Z][a-zA-Z\s]+)'
            ],
            'district': [
                r'District[:\s]+([A-Z][a-zA-Z\s]+)'
            ]
        }
    
    def extract_entities(self, text: str) -> Dict:
        """
        Extract entities from text
        
        Args:
            text: Cleaned text
            
        Returns:
            dict: Extracted entities
        """
        entities = {
            "owner_names": [],
            "survey_numbers": [],
            "dates": [],
            "banks": [],
            "loan_indicators": [],
            "case_numbers": [],
            "extents": [],
            "locations": {
                "village": None,
                "taluk": None,
                "district": None
            },
            "raw_persons": [],
            "raw_organizations": [],
            "raw_locations": []
        }
        
        # Use spaCy NER for general entities
        doc = self.nlp(text)
        
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                entities["raw_persons"].append(ent.text)
            elif ent.label_ == "ORG":
                entities["raw_organizations"].append(ent.text)
            elif ent.label_ in ["GPE", "LOC"]:
                entities["raw_locations"].append(ent.text)
        
        # Extract using custom patterns
        survey_candidates = self._extract_pattern(text, 'survey_no')
        date_candidates = self._extract_pattern(text, 'date')
        
        # Validate survey numbers vs dates
        entities["survey_numbers"] = self._validate_survey_numbers(survey_candidates, date_candidates)
        entities["dates"] = self._validate_dates(date_candidates, survey_candidates)
        
        # Extract and normalize bank names
        bank_raw = self._extract_pattern(text, 'bank')
        entities["banks"] = self._normalize_bank_names(bank_raw)
        entities["case_numbers"] = self._extract_pattern(text, 'case_no')
        entities["extents"] = self._extract_pattern(text, 'extent')
        
        # Extract loan amounts
        loan_amounts = self._extract_pattern(text, 'loan_amount')
        entities["loan_amounts"] = loan_amounts
        
        # Extract location details
        villages = self._extract_pattern(text, 'village')
        if villages:
            entities["locations"]["village"] = villages[0]
        
        taluks = self._extract_pattern(text, 'taluk')
        if taluks:
            entities["locations"]["taluk"] = taluks[0]
        
        districts = self._extract_pattern(text, 'district')
        if districts:
            entities["locations"]["district"] = districts[0]
        
        # Check for loan/mortgage indicators
        loan_keywords = ['loan', 'mortgage', 'encumbrance', 'charge', 'hypothecation']
        entities["loan_indicators"] = [kw for kw in loan_keywords if kw in text.lower()]
        
        # Determine if loan is present (check amounts too!)
        entities["loan_present"] = (
            len(entities["banks"]) > 0 or 
            len(entities["loan_indicators"]) > 0 or
            len(loan_amounts) > 0
        )
        
        # Clean and deduplicate
        entities = self._clean_entities(entities)
        
        return entities
    
    def _extract_pattern(self, text: str, pattern_type: str) -> List[str]:
        """
        Extract entities using regex patterns
        
        Args:
            text: Input text
            pattern_type: Type of pattern to use
            
        Returns:
            list: Extracted values
        """
        results = []
        patterns = self.patterns.get(pattern_type, [])
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if match.groups():
                    results.append(match.group(1).strip())
                else:
                    results.append(match.group(0).strip())
        
        return results
    
    def _validate_survey_numbers(self, survey_candidates: List[str], date_candidates: List[str]) -> List[str]:
        """Validate survey numbers against land-record formats (PROMPT 1)"""
        valid_surveys = []
        
        for sn in survey_candidates:
            # Reject if it looks like a date (DD/MM or MM/DD format)
            if re.match(r'^\d{1,2}/\d{1,2}$', sn):
                parts = sn.split('/')
                if len(parts) == 2:
                    n1, n2 = int(parts[0]), int(parts[1])
                    # If both <= 12 or one > 12 (day), likely a date
                    if (n1 <= 12 and n2 <= 12) or n1 > 12 or n2 > 12:
                        continue
            
            # Valid: 178/1, 45/2A, 123-4B, 16/3
            if re.match(r'^\d{1,4}[/\-]\d{1,3}[A-Za-z]?$', sn) or re.match(r'^\d{1,5}$', sn):
                if len(sn) <= 20:
                    valid_surveys.append(sn)
        
        return list(dict.fromkeys(valid_surveys))
    
    def _validate_dates(self, date_candidates: List[str], survey_candidates: List[str]) -> List[str]:
        """Validate dates and remove survey numbers"""
        valid_dates = []
        
        for date in date_candidates:
            # Only accept with year (YYYY)
            if re.match(r'^\d{1,2}[/-]\d{1,2}[/-]\d{4}$', date) or re.match(r'^\d{4}[/-]\d{1,2}[/-]\d{1,2}$', date):
                valid_dates.append(date)
        
        return list(dict.fromkeys(valid_dates))
    
    def _normalize_bank_names(self, bank_raw: List[str]) -> List[str]:
        """Normalize bank names using dictionary mapping (PROMPT 2)"""
        # Bank name mappings
        bank_mappings = {
            'SBM': 'State Bank of Mysore (now SBI)',
            'S.B.M': 'State Bank of Mysore (now SBI)',
            'State Bank of Mysore': 'State Bank of Mysore (now SBI)',
            'SBI': 'State Bank of India',
            'State Bank of India': 'State Bank of India',
            'HDFC': 'HDFC Bank',
            'ICICI': 'ICICI Bank',
            'Axis': 'Axis Bank',
            'BOB': 'Bank of Baroda',
            'PNB': 'Punjab National Bank',
            'Canara': 'Canara Bank',
            'Union': 'Union Bank'
        }
        
        normalized_banks = set()
        
        for bank in bank_raw:
            bank_clean = bank.strip().replace('.', '').replace('  ', ' ')
            
            # Check against mappings
            matched = False
            for key, normalized_name in bank_mappings.items():
                if key.replace('.', '').upper() in bank_clean.upper():
                    normalized_banks.add(normalized_name)
                    matched = True
                    break
            
            # If no mapping but looks like a bank, keep it
            if not matched and ('bank' in bank_clean.lower() or 'branch' in bank_clean.lower()):
                normalized_banks.add(bank)
        
        return list(normalized_banks)
    
    def _clean_entities(self, entities: Dict) -> Dict:
        """
        Clean and deduplicate extracted entities
        ENHANCED: Comprehensive removal of filename artifacts
        
        Args:
            entities: Raw extracted entities
            
        Returns:
            dict: Cleaned entities
        """
        # Remove duplicates while preserving order
        for key in entities:
            if isinstance(entities[key], list):
                entities[key] = list(dict.fromkeys(entities[key]))
        
        # COMPREHENSIVE CLEANUP: Remove ALL filename artifacts from survey numbers
        cleaned_surveys = []
        for sn in entities["survey_numbers"]:
            # Remove page markers: _page_1, -page-2, .page.3
            cleaned = re.sub(r'[._-]page[_-]?\d+', '', sn, flags=re.IGNORECASE)
            # Remove file extensions
            cleaned = re.sub(r'\.(jpg|jpeg|png|pdf|tiff?)$', '', cleaned, flags=re.IGNORECASE)
            # Remove underscore/dot/dash at boundaries
            cleaned = cleaned.strip('_.-')
            # Validate format (survey or survey/hissa)
            if cleaned and len(cleaned) <= 20 and re.match(r'^\d+([/\-]\d+[A-Za-z]?)?$', cleaned):
                cleaned_surveys.append(cleaned)
        entities["survey_numbers"] = cleaned_surveys
        
        # Clean dates (basic validation)
        entities["dates"] = [
            d for d in entities["dates"]
            if len(d) >= 8  # Minimum date length
        ]
        
        return entities
    
    def process_file(self, input_file: str, output_file: str = None) -> Dict:
        """
        Process a text file and extract entities
        
        Args:
            input_file: Path to input text file
            output_file: Path to save extracted entities (optional)
            
        Returns:
            dict: Processing results
        """
        input_path = Path(input_file)
        
        if not input_path.exists():
            raise FileNotFoundError(f"File not found: {input_file}")
        
        # Read text
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            text = data.get('cleaned_text', '')
        
        # Extract entities
        entities = self.extract_entities(text)
        
        # CRITICAL: Override survey_numbers with FILENAME-based values (PRIMARY SOURCE)
        # This ensures consistency and overrides any OCR extraction errors
        rtc_fields_file = input_path.parent / f"{input_path.stem.replace('_ocr_cleaned', '')}_rtc_fields.json"
        if rtc_fields_file.exists():
            try:
                with open(rtc_fields_file, 'r', encoding='utf-8') as f:
                    rtc_fields = json.load(f)
                    
                # PRIMARY SOURCE: Use filename-based survey/hissa (authoritative)
                survey = rtc_fields.get('survey_number')
                hissa = rtc_fields.get('hissa_number')
                
                if survey:
                    # Clear any OCR-extracted survey numbers
                    entities['survey_numbers'] = []
                    
                    # Add pure survey number (e.g., "178")
                    entities['survey_numbers'].append(survey)
                    
                    # Add combined format ONLY if hissa exists (e.g., "178*1")
                    if hissa:
                        # Use asterisk (*) as separator per user requirement
                        entities['survey_numbers'].append(f"{survey}*{hissa}")
                    
                    print(f"   [OVERRIDE] Survey: {survey}, Hissa: {hissa or 'None'}, Combined: {entities['survey_numbers']}")
                
                # CRITICAL FIX: Populate loan/bank data from RTC fields for risk scoring
                loan_details = rtc_fields.get('loan_details', [])
                if loan_details and len(loan_details) > 0:
                    # Mark loan as present
                    entities['loan_present'] = True
                    
                    # Extract loan amounts
                    for loan in loan_details:
                        amount = loan.get('amount', '')
                        if amount and amount not in entities['loan_amounts']:
                            entities['loan_amounts'].append(amount)
                    
                    # Extract bank names from loan context
                    if not entities['banks']:
                        for loan in loan_details:
                            context = loan.get('context', '')
                            # Look for bank names in context
                            bank_patterns = [
                                r'(State Bank of Mysore|S\.?B\.?M\.?)',
                                r'(State Bank of India|SBI)',
                                r'(HDFC Bank|HDFC)',
                                r'(ICICI Bank|ICICI)',
                                r'(Axis Bank)',
                                r'(Canara Bank)',
                                r'(Bank of Baroda|BOB)',
                            ]
                            for pattern in bank_patterns:
                                match = re.search(pattern, context, re.IGNORECASE)
                                if match:
                                    bank_name = match.group(1)
                                    # Normalize bank name
                                    if 'mysore' in bank_name.lower() or 'sbm' in bank_name.lower():
                                        bank_name = 'State Bank of Mysore (now SBI)'
                                    if bank_name not in entities['banks']:
                                        entities['banks'].append(bank_name)
                                        break
            except Exception as e:
                print(f"   [WARNING] Could not load RTC fields: {e}")
                pass  # Continue if RTC fields can't be loaded
        
        # Determine output file path
        if output_file is None:
            output_file = input_path.parent / f"{input_path.stem}_entities.json"
        
        output_path = Path(output_file)
        
        # Create result
        result = {
            "input_file": str(input_path),
            "processed_at": datetime.now().isoformat(),
            "entities": entities,
            "summary": {
                "survey_numbers_found": len(entities["survey_numbers"]),
                "dates_found": len(entities["dates"]),
                "banks_found": len(entities["banks"]),
                "loan_present": entities["loan_present"],
                "case_numbers_found": len(entities["case_numbers"]),
                "persons_found": len(entities["raw_persons"]),
                "organizations_found": len(entities["raw_organizations"])
            }
        }
        
        # Save to JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        result["output_file"] = str(output_path)
        return result
    
    def load_model(self, model_path: str):
        """Load trained spaCy model"""
        self.nlp = spacy.load(model_path)
    
    def train_model(self, training_data: List, output_dir: str):
        """
        Train custom NER model
        
        Args:
            training_data: List of (text, entities) tuples
            output_dir: Directory to save trained model
        """
        # This is a placeholder for future model training
        # For now, we use pattern-based extraction
        pass
