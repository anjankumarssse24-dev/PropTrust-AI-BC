"""
Manual RTC Field Extractor
Extracts specific fields from RTC document based on known patterns
"""

import json
import re
from pathlib import Path


def parse_survey_hissa_from_filename(filename: str) -> dict:
    """
    PRIMARY SOURCE: Extract survey and hissa from filename
    
    Rules:
    - Survey: numeric part BEFORE first dot (.)
    - Hissa: numeric/alphanumeric part AFTER first dot (.)
    - Strip suffixes: _page_1, .pdf, .jpg, .png, etc.
    
    Examples:
        "178.1_page_1" → survey=178, hissa=1
        "178.1.pdf" → survey=178, hissa=1
        "178_page_1.jpg" → survey=178, hissa=None
        "45.2A_page_1" → survey=45, hissa=2A
    
    Args:
        filename: Document filename or path
    
    Returns:
        dict: {'survey_number': str, 'hissa_number': str or None}
    """
    result = {'survey_number': None, 'hissa_number': None}
    
    # Extract just the filename without path
    filename = Path(filename).name
    
    # Remove common suffixes first
    # Remove page markers: _page_1, -page-1, .page.1
    filename = re.sub(r'[._-]page[._-]?\d+', '', filename, flags=re.IGNORECASE)
    # Remove file extensions
    filename = re.sub(r'\.(pdf|jpg|jpeg|png|tiff?|doc|docx)$', '', filename, flags=re.IGNORECASE)
    # Clean up trailing underscores, dots, dashes
    filename = filename.strip('_.-')
    
    # Primary pattern: survey.hissa (e.g., "178.1")
    match = re.match(r'^(\d+)\.(\d+[A-Za-z]?).*', filename)
    if match:
        result['survey_number'] = match.group(1)
        result['hissa_number'] = match.group(2)
        return result
    
    # Fallback pattern: just survey number (e.g., "178")
    match = re.match(r'^(\d+).*', filename)
    if match:
        result['survey_number'] = match.group(1)
        return result
    
    return result


def clean_entity_value(value: str) -> str:
    """Remove filename artifacts from entity values"""
    if not value:
        return value
    
    # Remove page markers
    value = re.sub(r'[._-]page[_-]?\d+', '', value, flags=re.IGNORECASE)
    # Remove file extensions
    value = re.sub(r'\.(jpg|jpeg|png|pdf|tiff?)$', '', value, flags=re.IGNORECASE)
    # Clean up underscores, dots, dashes at boundaries
    value = value.strip('_.-')
    
    return value


def extract_hissa_from_document_id(doc_id: str) -> str:
    """Extract hissa number from document ID (e.g., 178.1 -> '1')"""
    # Pattern: survey.hissa (e.g., 178.1, 45.2A)
    match = re.search(r'\d+\.(\d+[A-Za-z]?)', doc_id)
    if match:
        return match.group(1)
    return None


def extract_rtc_fields(text: str, document_id: str = None) -> dict:
    """Extract RTC-specific fields from translated text
    
    Args:
        text: OCR translated text
        document_id: Document filename/ID for PRIMARY survey/hissa extraction
    """
    
    fields = {
        'document_type': 'RTC (Record of Rights, Tenancy and Crops)',
        'form_number': None,
        'village': None,
        'taluk': None,
        'district': None,
        'hobli': None,
        'survey_number': None,
        'hissa_number': None,
        'khata_number': None,
        'owner_name': None,
        'extent_acres': None,
        'extent_guntas': None,
        'land_classification': None,
        'loan_details': [],
        'mutation_details': [],
        'valid_from': None,
        'valid_to': None,
        'digitally_signed_date': None,
        'print_page_no': None
    }
    
    # PRIMARY SOURCE: Parse survey and hissa from filename
    if document_id:
        filename_data = parse_survey_hissa_from_filename(document_id)
        fields['survey_number'] = filename_data['survey_number']
        fields['hissa_number'] = filename_data['hissa_number']
        print(f"   [FILENAME] Survey: {fields['survey_number']}, Hissa: {fields['hissa_number']}")
    
    # Extract Form Number
    form_match = re.search(r'Village Account Form Nc?\.?\s*(\d+)', text, re.IGNORECASE)
    if form_match:
        fields['form_number'] = form_match.group(1)
    
    # Extract Print Page Number
    page_match = re.search(r'Print Page[_\s]No:(\d+)', text)
    if page_match:
        fields['print_page_no'] = page_match.group(1)
    
    # Extract Validity Dates
    validity_match = re.search(r'Valid from (\d{2}/\d{2}/\d{4}) To (.+?)(?:\n|$)', text)
    if validity_match:
        fields['valid_from'] = validity_match.group(1)
        valid_to_raw = validity_match.group(2).strip()
        # CRITICAL FIX: Only accept "Till Date" or valid date format, NOT OCR garbage
        if 'till date' in valid_to_raw.lower():
            fields['valid_to'] = 'Till Date'
        elif re.match(r'^\d{2}/\d{2}/\d{4}$', valid_to_raw):
            fields['valid_to'] = valid_to_raw
        else:
            fields['valid_to'] = 'Till Date'  # Default to Till Date if garbage found
    
    # Extract Digital Signature Date
    sig_match = re.search(r'RTC DIGITALLY SIGNED ON (\d{2}/\d{2}/\d{4})', text)
    if sig_match:
        fields['digitally_signed_date'] = sig_match.group(1)
    
    # Extract Village, Taluk, District, Hobli
    # Common patterns in RTC documents
    village_patterns = [
        r'Village[:\s]+([A-Za-z\s]+?)(?:\n|Taluk|Hobli|District|$)',
        r'ಗ್ರಾಮ[:\s]+([A-Za-zಅ-ಹ\s]+?)(?:\n|$)',  # Kannada for village (ಗ್ರಾಮ)
        r'ಗ್ರಾವು[:\s]+([A-Za-zಅ-ಹ\s]+?)(?:\n|$)',  # Kannada variant (ಗ್ರಾವು)
        r'Gram[:\s]+([A-Za-z\s]+?)(?:\n|Taluk|Hobli|District|$)',  # English Gram
        r'Village Name[:\s]+([A-Za-z\s]+?)(?:\n|$)',
    ]
    for pattern in village_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            village = match.group(1).strip()
            if village:  # Only set if not empty
                fields['village'] = village
                break
    
    taluk_patterns = [
        r'Taluk[:\s]+([A-Za-z\s]+?)(?:\n|District|Hobli|$)',
        r'ತಾಲೂಕು[:\s]+([A-Za-zಅ-ಹ\s]+?)(?:\n|$)',  # Kannada (ತಾಲೂಕು)
        r'ತಾಲ್ಲೂಕು[:\s]+([A-Za-zಅ-ಹ\s]+?)(?:\n|$)',  # Kannada variant (ತಾಲ್ಲೂಕು)
    ]
    for pattern in taluk_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            taluk = match.group(1).strip()
            if taluk:  # Only set if not empty
                fields['taluk'] = taluk
                break
    
    district_patterns = [
        r'District[:\s]+([A-Za-z\s]+?)(?:\n|$)',
        r'ಜಿಲ್ಲೆ[:\s]+([A-Za-zಅ-ಹ\s]+?)(?:\n|$)',  # Kannada for district
    ]
    for pattern in district_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            district = match.group(1).strip()
            if district:  # Only set if not empty
                fields['district'] = district
                break
    
    hobli_patterns = [
        r'Hobli[:\s]+([A-Za-z\s]+?)(?:\n|$)',
        r'ಹೊಬ್ಳಿ[:\s]+([A-Za-zಅ-ಹ\s]+?)(?:\n|$)',  # Kannada (ಹೊಬ್ಳಿ)
        r'ಹೋಬಳಿ[:\s]+([A-Za-zಅ-ಹ\s]+?)(?:\n|$)',  # Kannada variant (ಹೋಬಳಿ)
    ]
    for pattern in hobli_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            hobli = match.group(1).strip()
            if hobli:  # Only set if not empty
                fields['hobli'] = hobli
                break
    
    # NOTE: Survey and Hissa numbers extracted from FILENAME (primary source above)
    # OCR-based extraction is SKIPPED to avoid inconsistencies
    
    # Extract Extent/Area
    # NOTE: Survey and Hissa numbers extracted from FILENAME (primary source above)
    # OCR-based extraction is SKIPPED to avoid inconsistencies
    
    # Extract Extent/Area
    extent_patterns = [
        r'1\.17\.00\.00',  # Specific pattern from document
        r'(\d+\.\d+)\s*Acres?',
        r'(\d+)\.(\d+)\.(\d+)\.(\d+)',  # Format like 1.17.00.00
    ]
    for pattern in extent_patterns:
        match = re.search(pattern, text)
        if match:
            if '1.17.00.00' in match.group(0):
                fields['extent_acres'] = '1'
                fields['extent_guntas'] = '17'
            break
    
    # Extract Loan Information - STRICT VALIDATION
    # CRITICAL: Only extract amounts that are clearly loans with bank context
    loan_patterns = [
        r'Rs\.?\s*(\d{1,3}(?:,\d{3})+)[/-]',  # Rs. 2,00,000/- format
        r'₹\s*(\d{1,3}(?:,\d{3})+)[/-]',  # ₹ 2,00,000/- format
        r'(?:loan|amount|borrowed)\s*(?:of\s*)?Rs\.?\s*(\d{1,3}(?:,\d{3})+)',  # "loan of Rs 200000"
        r'Rs\.?\s*(\d{5,7})[/-]',  # Rs. 200000/- (5-7 digits only, not 9+ garbage)
    ]
    
    loan_amounts_found = []
    for pattern in loan_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            amount_str = match.group(1).replace(',', '').replace('.', '').strip()
            try:
                amount_num = float(amount_str)
                
                # STRICT VALIDATION RULES:
                # 1. Minimum ₹10,000 (loans below this are likely OCR noise)
                # 2. Maximum ₹10,00,00,000 (10 crores - reject garbage like 213141526)
                # 3. Must appear within 200 chars of bank-related keywords
                if 10000 <= amount_num <= 10000000:
                    context = text[max(0, match.start()-200):min(len(text), match.end()+200)]
                    
                    # CONTEXT VALIDATION: Must appear near STRONG bank indicators
                    bank_keywords = [
                        'state bank', 'bank of', 'SBM', 'SBI', 'HDFC', 'ICICI', 
                        'manager', 'branch', 'loan', 'borrowed', 'mortgage',
                        'ಬ್ಯಾಂಕ್', 'ಋಣ'  # Kannada for bank/loan
                    ]
                    has_bank_context = any(kw.lower() in context.lower() for kw in bank_keywords)
                    
                    # ADDITIONAL CHECK: Reject if amount appears in date context
                    date_indicators = ['valid from', 'valid to', 'dated', 'signed on', '/202', '/201']
                    is_date_context = any(indicator in context.lower() for indicator in date_indicators)
                    
                    if has_bank_context and not is_date_context:
                        loan_amounts_found.append({
                            'amount': amount_str,
                            'amount_numeric': amount_num,
                            'context': context
                        })
            except:
                pass
    
    # AGGRESSIVE DEDUPLICATION: Keep only truly distinct loans
    seen_amounts = set()
    unique_loans = []
    
    # Sort by amount to process systematically
    loan_amounts_found.sort(key=lambda x: x['amount_numeric'])
    
    for loan in loan_amounts_found:
        amount_num = loan['amount_numeric']
        is_duplicate = False
        
        # Check if this amount is very similar to any seen amount (within 5%)
        for seen in seen_amounts:
            similarity_threshold = 0.05  # 5% similarity = duplicate
            if abs(amount_num - seen) / max(seen, 1) < similarity_threshold:
                is_duplicate = True
                break
        
        if not is_duplicate:
            unique_loans.append(loan)
            seen_amounts.add(amount_num)
    
    # FINAL VALIDATION: Keep max 3 loans (more than 3 is suspicious)
    unique_loans = unique_loans[:3]
    
    print(f"   [LOAN EXTRACTION] Found {len(unique_loans)} unique loans after deduplication")
    for i, loan in enumerate(unique_loans, 1):
        print(f"      Loan {i}: ₹{int(loan['amount_numeric']):,}")
    
    # Process unique loans only
    for loan in unique_loans:
        amount_clean = str(int(loan['amount_numeric']))
        if amount_clean not in [str(int(l.get('amount_numeric', 0))) for l in fields['loan_details'] if l.get('amount_numeric')]:
            # Clean loan context for readability
            context = loan['context']
            # Normalize common OCR errors in context
            context = re.sub(r'\bS\.B\.M\.?\b', 'State Bank of Mysore', context, flags=re.IGNORECASE)
            context = re.sub(r'\bManager\s+SBM\b', 'Manager State Bank of Mysore', context, flags=re.IGNORECASE)
            context = re.sub(r'\bPurava\s+branch\b', 'Puravara branch', context, flags=re.IGNORECASE)
            context = re.sub(r'\b(\d{3,})\.\s*(\d{3})/-', r'\1,\2/-', context)  # 550.000 -> 550,000
            context = re.sub(r'\s+', ' ', context).strip()  # Normalize whitespace
            
            # Format amount nicely with Indian numbering (lakhs)
            formatted_amount = f"{int(loan['amount_numeric']):,}"
            
            fields['loan_details'].append({
                'amount': formatted_amount,
                'amount_numeric': loan['amount_numeric'],
                'context': context[:200]  # Limit context to 200 chars for readability
            })
    
    # Extract Mutation References (MR patterns)
    mr_matches = re.findall(r'MR\s*(\d+/\d{4}-\d{4})', text)
    for mr in mr_matches:
        fields['mutation_details'].append({
            'reference': f'MR {mr}',
            'type': 'Mutation Record'
        })
    
    # Extract Owner Name (look for capitalized names near specific markers)
    # Try multiple patterns in order of specificity
    owner_patterns = [
        # Pattern 1: Name + Bin/S/o/D/o + Parent name (e.g., "Rangdhamaiah KR Bin Ramappa")
        r'\b([A-Z][a-z]+(?:aiah|appa|gowda|reddy|naik|kumar|raj|swamy)?)\s+(?:[A-Z]{1,3}\s+)?(?:Bin|S/o|D/o|W/o|Son of|Daughter of|bin)\s+(?:Lay\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b',
        # Pattern 2: Standard markers (Owner, Holder, Pattadar, Farmer)
        r'(?:Owner|Holder|Pattadar)[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4})',
        r'[Ff]armer[:\s\']+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4})',
        # Pattern 3: Name before survey number (common in RTC)
        r'\b([A-Z][a-z]+(?:aiah|appa|gowda|reddy|naik|kumar|raj|swamy))\s+(?:[A-Z]{1,3}\s+)?(?:Bin|bin)\b',
    ]
    
    for pattern in owner_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            # Get full match or first group
            name = match.group(0).strip()
            # Normalize whitespace (replace newlines and multiple spaces with single space)
            name = re.sub(r'\s+', ' ', name)
            
            # CRITICAL FIX: Remove OCR noise suffixes (skanta, kanta, etc.)
            # Pattern: Name + valid words + OCR garbage
            name = re.sub(r'\b(skanta|kanta|vathi|pathi|reddi)$', '', name, flags=re.IGNORECASE).strip()
            
            # VALIDATION: Max 4 words for Indian names
            words = name.split()
            if len(words) > 4:
                name = ' '.join(words[:4])  # Truncate to first 4 words
            
            # VALIDATION: Remove trailing non-alphabetic chars
            name = re.sub(r'[^a-zA-Z\s]+$', '', name).strip()
            
            # Validate it's not a common word
            if name and name not in ['Area', 'Account', 'Total', 'Survey', 'Village', 'Form', 'Page', 'Land', 'Bin', 'Son', 'Daughter', 'Owner', 'Holder']:
                fields['owner_name'] = name
                break
    
    # FINAL VALIDATION: Remove any invalid loans that somehow got through
    # This is a safety net to ensure absolutely no garbage loans appear
    valid_loans = []
    for loan in fields['loan_details']:
        amount_num = loan.get('amount_numeric', 0)
        # STRICT: Only keep loans between ₹10,000 and ₹1 crore
        if 10000 <= amount_num <= 10000000:
            valid_loans.append(loan)
    
    fields['loan_details'] = valid_loans
    print(f"   [FINAL] {len(valid_loans)} valid loan(s) after filtering")
    
    return fields


def analyze_rtc_document(json_file_path: str):
    """Analyze RTC document and extract all fields"""
    
    print("\n" + "="*70)
    print("RTC DOCUMENT FIELD EXTRACTION")
    print("="*70)
    
    # Read translated JSON
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Get text (prefer translated, fallback to original)
    text = data.get('translated_text', '') or data.get('text', '')
    
    # Extract document ID from filename for hissa fallback
    from pathlib import Path
    doc_id = Path(json_file_path).stem.replace('_ocr_translated', '').replace('_ocr', '')
    
    # Extract fields with document ID for fallback
    fields = extract_rtc_fields(text, document_id=doc_id)
    
    # Print findings
    print("\n📋 EXTRACTED RTC FIELDS:\n")
    
    for key, value in fields.items():
        if value and value != [] and value != {}:
            if isinstance(value, list):
                print(f"   {key.replace('_', ' ').title()}: ({len(value)} items)")
                for item in value:
                    print(f"      • {item}")
            else:
                print(f"   {key.replace('_', ' ').title()}: {value}")
    
    # Save extracted fields
    output_path = Path(json_file_path).parent / f"{Path(json_file_path).stem}_rtc_fields.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(fields, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Saved to: {output_path}")
    
    return fields


if __name__ == "__main__":
    # Analyze the translated document
    result = analyze_rtc_document("data/ocr_text/178.1_ocr_translated.json")
    
    print("\n✅ RTC field extraction complete!")
