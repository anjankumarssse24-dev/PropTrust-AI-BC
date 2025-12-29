"""
Phase 6: Verification Report Generator
Generates comprehensive HTML/PDF reports from all pipeline outputs
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import os


class ReportGenerator:
    """Generate comprehensive verification reports"""
    
    def __init__(self):
        """Initialize report generator"""
        self.template = self._load_template()
    
    def generate_report(
        self,
        document_id: str,
        ocr_file: str,
        cleaned_file: str,
        entities_file: str,
        classification_file: str,
        risk_file: str,
        rtc_fields_file: str = None,
        output_path: str = None
    ) -> str:
        """
        Generate comprehensive HTML report from all pipeline outputs
        
        Args:
            document_id: Document identifier
            ocr_file: Path to OCR output JSON
            cleaned_file: Path to cleaned text JSON
            entities_file: Path to entities JSON
            classification_file: Path to classification JSON
            risk_file: Path to risk assessment JSON
            output_path: Optional custom output path
            
        Returns:
            Path to generated HTML report
        """
        print("\n" + "="*70)
        print("PHASE 6: VERIFICATION REPORT GENERATION")
        print("="*70)
        
        # Load all data
        print("\n📂 Loading pipeline outputs...")
        data = self._load_all_data(
            ocr_file, cleaned_file, entities_file, 
            classification_file, risk_file, rtc_fields_file
        )
        
        # Generate HTML content
        print("📝 Generating report...")
        html_content = self._generate_html(document_id, data)
        
        # Save report
        if output_path is None:
            output_path = f"data/reports/{document_id}_verification_report.html"
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Clean invalid surrogates from HTML content
        html_content = html_content.encode('utf-8', errors='ignore').decode('utf-8')
        
        output_file.write_text(html_content, encoding='utf-8')
        
        print(f"\n✅ Report generated: {output_file.absolute()}")
        return str(output_file.absolute())
    
    def _load_all_data(
        self,
        ocr_file: str,
        cleaned_file: str,
        entities_file: str,
        classification_file: str,
        risk_file: str,
        rtc_fields_file: str = None
    ) -> Dict[str, Any]:
        """Load all pipeline output files"""
        
        data = {}
        
        # OCR data
        if os.path.exists(ocr_file):
            with open(ocr_file, 'r', encoding='utf-8') as f:
                data['ocr'] = json.load(f)
        else:
            data['ocr'] = {'text': 'N/A', 'page_count': 0}
        
        # Cleaned text
        if os.path.exists(cleaned_file):
            with open(cleaned_file, 'r', encoding='utf-8') as f:
                data['cleaned'] = json.load(f)
        else:
            data['cleaned'] = {'cleaned_text': 'N/A'}
        
        # Entities
        if os.path.exists(entities_file):
            with open(entities_file, 'r', encoding='utf-8') as f:
                data['entities'] = json.load(f)
        else:
            data['entities'] = {'entities': {}}
        
        # Classification
        if os.path.exists(classification_file):
            with open(classification_file, 'r', encoding='utf-8') as f:
                data['classification'] = json.load(f)
        else:
            data['classification'] = {'label': 'Unknown', 'confidence': 0}
        
        # Risk assessment
        if os.path.exists(risk_file):
            with open(risk_file, 'r', encoding='utf-8') as f:
                data['risk'] = json.load(f)
        else:
            data['risk'] = {'risk_assessment': {'risk_score': 0, 'risk_level': 'Unknown'}}
        
        # RTC fields
        if rtc_fields_file and os.path.exists(rtc_fields_file):
            with open(rtc_fields_file, 'r', encoding='utf-8') as f:
                data['rtc_fields'] = json.load(f)
        else:
            data['rtc_fields'] = {}
        
        return data
    
    def _extract_survey_hissa(self, document_id: str) -> Dict[str, str]:
        """Extract survey number and hissa from document ID"""
        # Document ID format: 178.1 (survey.hissa)
        parts = document_id.split('.')
        if len(parts) == 2:
            return {
                'survey': parts[0],
                'hissa': parts[1],
                'combined': f"{parts[0]}*{parts[1]}",
                'display': f"Survey No: {parts[0]} | Hissa: {parts[1]}"
            }
        return {
            'survey': document_id,
            'hissa': '',
            'combined': document_id,
            'display': f"Survey No: {document_id}"
        }
    
    def _generate_html(self, document_id: str, data: Dict[str, Any]) -> str:
        """Generate HTML report content"""
        
        # Extract survey and hissa information
        survey_info = self._extract_survey_hissa(document_id)
        
        # Extract data
        ocr_data = data.get('ocr', {})
        cleaned_data = data.get('cleaned', {})
        entities_data = data.get('entities', {})
        classification_data = data.get('classification', {})
        risk_data = data.get('risk', {})
        rtc_fields = data.get('rtc_fields', {})
        
        # Risk assessment details
        risk_assessment = risk_data.get('risk_assessment', {})
        risk_score = risk_assessment.get('risk_score', 0)
        risk_level = risk_assessment.get('risk_level', 'Unknown')
        risk_percentage = risk_assessment.get('risk_percentage', '0%')
        
        # Determine risk color
        if risk_score <= 30:
            risk_color = '#28a745'  # Green
            risk_icon = '✅'
        elif risk_score <= 60:
            risk_color = '#ffc107'  # Yellow
            risk_icon = '⚠️'
        else:
            risk_color = '#dc3545'  # Red
            risk_icon = '🚨'
        
        # Entity summary
        entities = entities_data.get('entities', {})
        entity_summary = data.get('risk', {}).get('entity_summary', {})
        
        # HTML template
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Property Verification Report - {document_id}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .survey-banner {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 15px 30px;
            font-size: 1.5em;
            font-weight: bold;
            text-align: center;
            border-bottom: 3px solid #d14765;
        }}
        
        .owner-banner {{
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
            padding: 20px 30px;
            font-size: 1.8em;
            font-weight: bold;
            text-align: center;
            border-bottom: 3px solid #0f7c6f;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .section {{
            margin-bottom: 40px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            overflow: hidden;
        }}
        
        .section-header {{
            background: #f8f9fa;
            padding: 15px 20px;
            border-bottom: 2px solid #667eea;
            font-size: 1.4em;
            font-weight: bold;
            color: #333;
        }}
        
        .section-content {{
            padding: 20px;
        }}
        
        .risk-score {{
            text-align: center;
            padding: 30px;
            background: linear-gradient(135deg, {risk_color}22 0%, {risk_color}11 100%);
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        
        .risk-score-value {{
            font-size: 4em;
            font-weight: bold;
            color: {risk_color};
            margin: 10px 0;
        }}
        
        .risk-level {{
            font-size: 1.8em;
            color: {risk_color};
            font-weight: bold;
            margin: 10px 0;
        }}
        
        .risk-meter {{
            width: 100%;
            height: 40px;
            background: #e0e0e0;
            border-radius: 20px;
            overflow: hidden;
            margin: 20px 0;
        }}
        
        .risk-meter-fill {{
            height: 100%;
            background: {risk_color};
            width: {risk_percentage};
            transition: width 1s ease;
        }}
        
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        
        .info-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        
        .info-card h3 {{
            color: #667eea;
            margin-bottom: 10px;
            font-size: 1.1em;
        }}
        
        .info-card p {{
            color: #333;
            font-size: 1.3em;
            font-weight: bold;
        }}
        
        .entity-list {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
        }}
        
        .entity-list h4 {{
            color: #667eea;
            margin-bottom: 10px;
        }}
        
        .entity-list ul {{
            list-style: none;
            padding-left: 0;
        }}
        
        .entity-list li {{
            padding: 8px 0;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        .entity-list li:last-child {{
            border-bottom: none;
        }}
        
        .recommendation {{
            background: #e7f3ff;
            border-left: 4px solid #2196F3;
            padding: 15px;
            margin: 10px 0;
            border-radius: 4px;
        }}
        
        .recommendation.low {{
            background: #e8f5e9;
            border-left-color: #28a745;
        }}
        
        .recommendation.medium {{
            background: #fff8e1;
            border-left-color: #ffc107;
        }}
        
        .recommendation.high {{
            background: #ffebee;
            border-left-color: #dc3545;
        }}
        
        .text-preview {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            max-height: 300px;
            overflow-y: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            border-top: 2px solid #e0e0e0;
        }}
        
        .badge {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
            margin: 5px;
        }}
        
        .badge-success {{
            background: #28a745;
            color: white;
        }}
        
        .badge-warning {{
            background: #ffc107;
            color: #333;
        }}
        
        .badge-danger {{
            background: #dc3545;
            color: white;
        }}
        
        .badge-info {{
            background: #17a2b8;
            color: white;
        }}
        
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            
            .container {{
                box-shadow: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>🏠 Property Verification Report</h1>
            <p>Document ID: {document_id}</p>
            <p>Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
        
        <!-- Survey and Hissa Banner -->
        <div class="survey-banner">
            📍 {survey_info['display']} | Combined: {survey_info['combined']}
        </div>
        
        <!-- Owner Name Banner (if available) -->
        {self._generate_owner_banner(rtc_fields)}
        
        <!-- Content -->
        <div class="content">
            
            <!-- RTC Document Fields Section (NEW - TOP PRIORITY) -->
            <div class="section">
                <div class="section-header">
                    \ud83d\udcdc RTC Document Fields
                </div>
                <div class="section-content">
                    {self._generate_rtc_fields_section(rtc_fields, survey_info)}
                </div>
            </div>
            
            <!-- Risk Assessment Section -->
            <div class="section">
                <div class="section-header">
                    {risk_icon} Risk Assessment
                </div>
                <div class="section-content">
                    <div class="risk-score">
                        <div class="risk-score-value">{risk_score}/100</div>
                        <div class="risk-level">{risk_level} RISK</div>
                        <div class="risk-meter">
                            <div class="risk-meter-fill"></div>
                        </div>
                        <p style="color: #666; margin-top: 10px;">
                            {risk_assessment.get('summary', 'Assessment complete')}
                        </p>
                    </div>
                    
                    <h3 style="margin: 20px 0 10px 0;">📋 Recommendations:</h3>
                    {''.join([f'<div class="recommendation {risk_level.lower()}">{rec}</div>' 
                              for rec in risk_assessment.get('recommendations', [])])}
                    
                    <h3 style="margin: 30px 0 10px 0;">⚖️ Risk Breakdown:</h3>
                    <div class="info-grid">
                        {self._generate_risk_breakdown_cards(risk_assessment.get('breakdown', {}))}
                    </div>
                </div>
            </div>
            
            <!-- Document Classification -->
            <div class="section">
                <div class="section-header">
                    📄 Document Classification
                </div>
                <div class="section-content">
                    <div class="info-grid">
                        <div class="info-card">
                            <h3>Classification</h3>
                            <p>{classification_data.get('label', 'Unknown')}</p>
                        </div>
                        <div class="info-card">
                            <h3>Confidence</h3>
                            <p>{classification_data.get('confidence', 0) * 100:.1f}%</p>
                        </div>
                    </div>
                    
                    <h4 style="margin: 20px 0 10px 0;">Classification Explanation:</h4>
                    <div class="text-preview">
{classification_data.get('explanation', 'No explanation available')}
                    </div>
                </div>
            </div>
            
            <!-- Extracted Entities -->
            <div class="section">
                <div class="section-header">
                    🔍 Extracted Entities
                </div>
                <div class="section-content">
                    <div class="info-grid">
                        <div class="info-card">
                            <h3>Survey Numbers</h3>
                            <p>{entity_summary.get('survey_numbers_found', 0)}</p>
                        </div>
                        <div class="info-card">
                            <h3>Banks Mentioned</h3>
                            <p>{entity_summary.get('banks_found', 0)}</p>
                        </div>
                        <div class="info-card">
                            <h3>Dates Found</h3>
                            <p>{entity_summary.get('dates_found', 0)}</p>
                        </div>
                        <div class="info-card">
                            <h3>Legal Cases</h3>
                            <p>{entity_summary.get('case_numbers_found', 0)}</p>
                        </div>
                    </div>
                    
                    {self._generate_entity_lists(entities)}
                </div>
            </div>
            
            <!-- OCR Extraction -->
            <div class="section">
                <div class="section-header">
                    📝 OCR Extraction
                </div>
                <div class="section-content">
                    <div class="info-grid">
                        <div class="info-card">
                            <h3>Pages Processed</h3>
                            <p>{ocr_data.get('page_count', 0)}</p>
                        </div>
                        <div class="info-card">
                            <h3>Characters Extracted</h3>
                            <p>{len(ocr_data.get('text', ''))}</p>
                        </div>
                        <div class="info-card">
                            <h3>Characters (Cleaned)</h3>
                            <p>{len(cleaned_data.get('cleaned_text', ''))}</p>
                        </div>
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-top: 20px;">
                        <h4 style="margin: 0 0 15px 0; color: #2c3e50;">Text Quality Metrics (ISSUE 2 FIX):</h4>
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px;">
                            <div style="background: white; padding: 15px; border-radius: 6px; border-left: 4px solid #3498db;">
                                <strong style="color: #7f8c8d;">Original OCR:</strong>
                                <p style="font-size: 1.5em; margin: 5px 0 0 0; color: #2c3e50;">{len(ocr_data.get('text', ''))} chars</p>
                            </div>
                            <div style="background: white; padding: 15px; border-radius: 6px; border-left: 4px solid #9b59b6;">
                                <strong style="color: #7f8c8d;">Cleaned Text:</strong>
                                <p style="font-size: 1.5em; margin: 5px 0 0 0; color: #2c3e50;">{len(cleaned_data.get('cleaned_text', ''))} chars</p>
                            </div>
                            <div style="background: {'#d4edda' if len(cleaned_data.get('cleaned_text', '')) > 0 else '#f8d7da'}; padding: 15px; border-radius: 6px; border-left: 4px solid {'#28a745' if len(cleaned_data.get('cleaned_text', '')) > 0 else '#dc3545'};">
                                <strong style="color: #7f8c8d;">Validation:</strong>
                                <p style="font-size: 1.5em; margin: 5px 0 0 0; color: {'#155724' if len(cleaned_data.get('cleaned_text', '')) > 0 else '#721c24'};">{'✅ Valid' if len(cleaned_data.get('cleaned_text', '')) > 0 else '❌ Empty'}</p>
                            </div>
                        </div>
                    </div>
                    
                    <h4 style="margin: 20px 0 10px 0;">Cleaned Text Preview (First 500 characters):</h4>
                    <div class="text-preview" style="max-height: 250px; overflow-y: auto; background: #f5f5f5; padding: 15px; border-radius: 6px; border-left: 3px solid #3498db; font-family: monospace; font-size: 0.9em; line-height: 1.6;">
{cleaned_data.get('cleaned_text', 'N/A')[:500]}{'...' if len(cleaned_data.get('cleaned_text', '')) > 500 else ''}
                    </div>
                </div>
            </div>
            
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <p><strong>Property Document Verification System</strong></p>
            <p>Automated AI-powered document verification using OCR, NER, Classification & Risk Scoring</p>
            <p style="margin-top: 10px; font-size: 0.9em;">
                This is an automated assessment. Please consult legal professionals for final decisions.
            </p>
        </div>
    </div>
</body>
</html>"""
        
        return html
    
    def _generate_risk_breakdown_cards(self, breakdown: Dict[str, int]) -> str:
        """Generate HTML for risk breakdown cards"""
        cards = []
        
        risk_categories = {
            'loan_risk': 'Loan Risk',
            'legal_risk': 'Legal Risk',
            'mutation_risk': 'Mutation Risk',
            'data_quality_risk': 'Data Quality',
            'other_risks': 'Other Risks'
        }
        
        for key, label in risk_categories.items():
            value = breakdown.get(key, 0)
            cards.append(f"""
                <div class="info-card">
                    <h3>{label}</h3>
                    <p>{value} points</p>
                </div>
            """)
        
        return ''.join(cards)
    
    def _generate_entity_lists(self, entities: Dict[str, list]) -> str:
        """Generate HTML for entity lists"""
        html_parts = []
        
        entity_labels = {
            'survey_numbers': '📍 Survey Numbers',
            'dates': '📅 Dates',
            'banks': '🏦 Banks',
            'case_numbers': '⚖️ Case Numbers',
            'persons': '👤 Persons',
            'organizations': '🏢 Organizations'
        }
        
        for key, label in entity_labels.items():
            entity_list = entities.get(key, [])
            if entity_list:
                items = ''.join([f'<li>{item}</li>' for item in entity_list[:10]])  # Limit to 10
                count_note = f' (Showing 10 of {len(entity_list)})' if len(entity_list) > 10 else ''
                
                html_parts.append(f"""
                    <div class="entity-list">
                        <h4>{label}{count_note}</h4>
                        <ul>{items}</ul>
                    </div>
                """)
        
        return ''.join(html_parts) if html_parts else '<p>No entities extracted</p>'
    
    def _generate_rtc_fields_section(self, rtc_fields: Dict, survey_info: Dict = None) -> str:
        """Generate HTML for RTC-specific fields"""
        
        if not rtc_fields:
            return '<p>No RTC fields extracted</p>'
        
        html_parts = []
        
        # Basic Info Grid
        basic_info = []
        
        # Add Survey and Hissa Information from document ID
        if survey_info:
            basic_info.append(f'<div class="info-card" style="border-left: 4px solid #f5576c;"><h3>📍 Survey Number</h3><p style="font-size: 1.3em; font-weight: bold;">{survey_info["survey"]}</p></div>')
            if survey_info['hissa']:
                basic_info.append(f'<div class="info-card" style="border-left: 4px solid #f5576c;"><h3>📍 Hissa Number</h3><p style="font-size: 1.3em; font-weight: bold;">{survey_info["hissa"]}</p></div>')
            basic_info.append(f'<div class="info-card" style="border-left: 4px solid #f5576c;"><h3>📍 Survey*Hissa</h3><p style="font-size: 1.3em; font-weight: bold;">{survey_info["combined"]}</p></div>')
        
        if rtc_fields.get('form_number'):
            form_num = rtc_fields['form_number']
            basic_info.append(f'<div class="info-card"><h3>Form Number</h3><p>Village Account Form No. {form_num}</p></div>')
        if rtc_fields.get('survey_number'):
            survey_num = rtc_fields['survey_number']
            basic_info.append(f'<div class="info-card"><h3>Survey Number (Extracted)</h3><p>{survey_num}</p></div>')
        if rtc_fields.get('extent_acres') or rtc_fields.get('extent_guntas'):
            extent_text = f"{rtc_fields.get('extent_acres', '0')} Acres {rtc_fields.get('extent_guntas', '0')} Guntas"
            basic_info.append(f'<div class="info-card"><h3>Land Extent</h3><p>{extent_text}</p></div>')
        if rtc_fields.get('owner_name'):
            owner = rtc_fields['owner_name']
            basic_info.append(f'<div class="info-card"><h3>Owner Name</h3><p>{owner}</p></div>')
        
        if basic_info:
            html_parts.append('<h3 style="margin: 0 0 15px 0;">🏛️ Basic Information</h3>')
            html_parts.append('<div class="info-grid">')
            html_parts.append(''.join(basic_info))
            html_parts.append('</div>')
        
        # Validity Info
        if rtc_fields.get('valid_from') or rtc_fields.get('valid_to'):
            html_parts.append('<h3 style="margin: 30px 0 15px 0;">📅 Validity Period</h3>')
            html_parts.append('<div class="info-grid">')
            if rtc_fields.get('valid_from'):
                valid_from = rtc_fields['valid_from']
                html_parts.append(f'<div class="info-card"><h3>Valid From</h3><p>{valid_from}</p></div>')
            if rtc_fields.get('valid_to'):
                valid_to = rtc_fields['valid_to']
                html_parts.append(f'<div class="info-card"><h3>Valid To</h3><p>{valid_to}</p></div>')
            if rtc_fields.get('digitally_signed_date'):
                signed_date = rtc_fields['digitally_signed_date']
                html_parts.append(f'<div class="info-card"><h3>Digitally Signed</h3><p>{signed_date}</p></div>')
            html_parts.append('</div>')
        
        # Loan Details - CRITICAL SECTION
        loan_details = rtc_fields.get('loan_details', [])
        if loan_details and len(loan_details) > 0:
            html_parts.append('<h3 style="margin: 30px 0 15px 0; color: #dc3545;">🚨 LOAN DETAILS DETECTED</h3>')
            for idx, loan in enumerate(loan_details):
                amount = loan.get('amount', 'Unknown')
                context = loan.get('context', '')[:100]
                loan_html = f'''
                    <div class="recommendation high">
                        <strong>💰 Loan Entry #{idx+1}</strong><br>
                        <strong>Amount:</strong> ₹ {amount}<br>
                        <strong>Context:</strong> {context}...
                    </div>
                '''
                html_parts.append(loan_html)
        
        # Mutation Details
        mutation_details = rtc_fields.get('mutation_details', [])
        if mutation_details and len(mutation_details) > 0:
            html_parts.append('<h3 style="margin: 30px 0 15px 0;">🔄 Mutation Records</h3>')
            for mutation in mutation_details:
                ref = mutation.get('reference', 'N/A')
                mut_type = mutation.get('type', 'Unknown')
                mut_html = f'''
                    <div class="recommendation">
                        <strong>{ref}</strong> - {mut_type}
                    </div>
                '''
                html_parts.append(mut_html)
        
        return ''.join(html_parts)
    
    def _generate_owner_banner(self, rtc_fields: Dict) -> str:
        """Generate owner name banner if available"""
        owner_name = rtc_fields.get('owner_name')
        if owner_name:
            return f'''
        <div class="owner-banner">
            👤 Property Owner: {owner_name}
        </div>
            '''
        return ''
    
    def _load_template(self) -> str:
        """Load HTML template (placeholder for future customization)"""
        return ""


if __name__ == "__main__":
    # Test report generation
    generator = ReportGenerator()
    
    document_id = "178.1"
    base_path = f"data/ocr_text/{document_id}"
    
    report_path = generator.generate_report(
        document_id=document_id,
        ocr_file=f"{base_path}_ocr.json",
        cleaned_file=f"{base_path}_ocr_cleaned.json",
        entities_file=f"{base_path}_ocr_cleaned_entities.json",
        classification_file=f"{base_path}_ocr_cleaned_classification.json",
        risk_file=f"{base_path}_risk_assessment.json"
    )
    
    print(f"\n✅ Report ready: {report_path}")
