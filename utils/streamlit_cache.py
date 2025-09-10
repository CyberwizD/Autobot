# utils/streamlit_cache.py
import streamlit as st
import pandas as pd
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

class StreamlitCache:
    def __init__(self):
        self.cache_keys = {
            'raw_data': 'autobot_raw_data',
            'processed_data': 'autobot_processed_data',
            'report_template': 'autobot_report_template',
            'analysis_history': 'autobot_analysis_history',
            'user_preferences': 'autobot_user_preferences'
        }
        
        # Initialize cache with default template
        self._init_report_template()
    
    def _init_report_template(self):
        """Initialize the report template structure"""
        if self.cache_keys['report_template'] not in st.session_state:
            template = {
                "structure": {
                    "monthly_summaries": {
                        "required_fields": [
                            "month", "month_name", "start_date", "end_date",
                            "total_done", "total_reviewed", "total_edited",
                            "good_count", "bad_count", "rejected_count",
                            "unique_users", "working_days"
                        ],
                        "format": "list_of_objects"
                    },
                    "weekly_summaries": {
                        "required_fields": [
                            "week_id", "week_period", "start_date", "end_date",
                            "month", "total_done", "total_reviewed", "total_edited",
                            "daily_breakdown"
                        ],
                        "format": "list_of_objects"
                    },
                    "user_summaries": {
                        "required_fields": [
                            "user", "total_done", "total_reviewed", "total_edited",
                            "good_count", "bad_count", "rejected_count",
                            "days_active", "avg_per_day"
                        ],
                        "format": "list_of_objects"
                    },
                    "daily_summaries": {
                        "required_fields": [
                            "date", "weekday", "user_records", "daily_totals"
                        ],
                        "format": "list_of_objects"
                    }
                },
                "validation_rules": {
                    "date_format": "DD/MM/YYYY",
                    "numeric_fields": [
                        "total_done", "total_reviewed", "total_edited",
                        "good_count", "bad_count", "rejected_count"
                    ],
                    "required_totals": [
                        "monthly_totals_match",
                        "weekly_totals_match", 
                        "user_totals_match"
                    ]
                },
                "excel_format": {
                    "sheets": ["Week1", "Week2", "Week3", "Week4", "Month"],
                    "headers": {
                        "reviewer": ["Good", "Good Original", "Good Enhanced", 
                                   "For Editing", "Bad", "Rejected", "Total Reviewed"],
                        "editor": ["Downloaded", "Uploaded", "Total Edited"]
                    },
                    "formatting": {
                        "merge_dates": True,
                        "bold_totals": True,
                        "borders": "all_cells",
                        "column_widths": {
                            "work_date": 12,
                            "user": 35,
                            "numeric": 10
                        }
                    }
                }
            }
            
            st.session_state[self.cache_keys['report_template']] = template
    
    def store_raw_data(self, df: pd.DataFrame):
        """Store raw processed data in cache"""
        st.session_state[self.cache_keys['raw_data']] = {
            'dataframe': df,
            'timestamp': datetime.now().isoformat(),
            'shape': df.shape,
            'columns': list(df.columns),
            'date_range': {
                'start': df['workdate'].min().isoformat() if 'workdate' in df.columns else None,
                'end': df['workdate'].max().isoformat() if 'workdate' in df.columns else None
            }
        }
    
    def store_processed_data(self, processed_data: Dict):
        """Store AI-processed analysis results"""
        st.session_state[self.cache_keys['processed_data']] = {
            'data': processed_data,
            'timestamp': datetime.now().isoformat(),
            'validation_status': 'validated'
        }
        
        # Also store in analysis history
        self._add_to_history(processed_data)
    
    def _add_to_history(self, analysis_data: Dict):
        """Add analysis to history for future reference"""
        history_key = self.cache_keys['analysis_history']
        
        if history_key not in st.session_state:
            st.session_state[history_key] = []
        
        # Keep only last 10 analyses
        history = st.session_state[history_key]
        history.append({
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_records': len(analysis_data.get('daily_summaries', [])),
                'months': len(analysis_data.get('monthly_summaries', [])),
                'weeks': len(analysis_data.get('weekly_summaries', [])),
                'users': len(analysis_data.get('user_summaries', []))
            }
        })
        
        # Keep only recent history
        st.session_state[history_key] = history[-10:]
    
    def get_raw_data(self) -> Optional[pd.DataFrame]:
        """Retrieve raw data from cache"""
        raw_data_info = st.session_state.get(self.cache_keys['raw_data'])
        if raw_data_info:
            return raw_data_info['dataframe']
        return None
    
    def get_processed_data(self) -> Optional[Dict]:
        """Retrieve processed data from cache"""
        if self.cache_keys['processed_data'] in st.session_state:
            return st.session_state[self.cache_keys['processed_data']]['data']
        return None
    
    def get_report_template(self) -> Dict:
        """Retrieve report template"""
        return st.session_state[self.cache_keys['report_template']]
    
    def get_cache_info(self) -> Dict:
        """Get information about current cache state"""
        info = {
            'cache_status': {},
            'data_summary': {},
            'last_updated': None
        }
        
        # Check what's in cache
        for key_name, cache_key in self.cache_keys.items():
            info['cache_status'][key_name] = cache_key in st.session_state
        
        # Get raw data summary
        if self.cache_keys['raw_data'] in st.session_state:
            raw_data_info = st.session_state[self.cache_keys['raw_data']]
            info['data_summary'] = {
                'shape': raw_data_info['shape'],
                'columns': len(raw_data_info['columns']),
                'date_range': raw_data_info['date_range']
            }
            info['last_updated'] = raw_data_info['timestamp']
        
        # Get processed data summary
        if self.cache_keys['processed_data'] in st.session_state:
            processed_info = st.session_state[self.cache_keys['processed_data']]
            info['last_analysis'] = processed_info['timestamp']
            info['validation_status'] = processed_info['validation_status']
        
        return info
    
    def validate_against_template(self, ai_response: Dict) -> Dict[str, Any]:
        """Validate AI response against template structure"""
        template = self.get_report_template()
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'corrections_applied': []
        }
        
        try:
            # Check required top-level keys
            required_keys = list(template['structure'].keys())
            for key in required_keys:
                if key not in ai_response:
                    validation_result['errors'].append(f"Missing required section: {key}")
                    validation_result['is_valid'] = False
            
            # Validate each section
            for section_name, section_config in template['structure'].items():
                if section_name in ai_response:
                    section_data = ai_response[section_name]
                    
                    # Check if it's a list
                    if section_config['format'] == 'list_of_objects':
                        if not isinstance(section_data, list):
                            validation_result['errors'].append(f"{section_name} should be a list")
                            validation_result['is_valid'] = False
                            continue
                        
                        # Check required fields in each object
                        for i, item in enumerate(section_data):
                            for required_field in section_config['required_fields']:
                                if required_field not in item:
                                    validation_result['warnings'].append(
                                        f"Missing field '{required_field}' in {section_name}[{i}]"
                                    )
            
            # Validate numeric fields
            numeric_fields = template['validation_rules']['numeric_fields']
            for section_name, section_data in ai_response.items():
                if isinstance(section_data, list):
                    for i, item in enumerate(section_data):
                        for field in numeric_fields:
                            if field in item and not isinstance(item[field], (int, float)):
                                try:
                                    item[field] = int(float(item[field]))
                                    validation_result['corrections_applied'].append(
                                        f"Converted {section_name}[{i}][{field}] to integer"
                                    )
                                except (ValueError, TypeError):
                                    validation_result['errors'].append(
                                        f"Invalid numeric value in {section_name}[{i}][{field}]"
                                    )
                                    validation_result['is_valid'] = False
            
            # Validate date formats
            date_format = template['validation_rules']['date_format']
            self._validate_date_formats(ai_response, date_format, validation_result)
            
            return validation_result
            
        except Exception as e:
            validation_result['errors'].append(f"Validation error: {str(e)}")
            validation_result['is_valid'] = False
            return validation_result
    
    def _validate_date_formats(self, data: Dict, expected_format: str, validation_result: Dict):
        """Validate date formats in the data"""
        date_fields = ['start_date', 'end_date', 'date']
        
        for section_name, section_data in data.items():
            if isinstance(section_data, list):
                for i, item in enumerate(section_data):
                    for field in date_fields:
                        if field in item:
                            date_value = item[field]
                            if not self._is_valid_date_format(date_value, expected_format):
                                validation_result['warnings'].append(
                                    f"Date format issue in {section_name}[{i}][{field}]: {date_value}"
                                )
    
    def _is_valid_date_format(self, date_str: str, expected_format: str) -> bool:
        """Check if date string matches expected format"""
        try:
            if expected_format == "DD/MM/YYYY":
                datetime.strptime(date_str, '%d/%m/%Y')
                return True
            return False
        except ValueError:
            return False
    
    def clear_all(self):
        """Clear all cached data"""
        for cache_key in self.cache_keys.values():
            if cache_key in st.session_state:
                del st.session_state[cache_key]
        
        # Reinitialize template
        self._init_report_template()
    
    def clear_processed_data(self):
        """Clear only processed data, keep raw data"""
        if self.cache_keys['processed_data'] in st.session_state:
            del st.session_state[self.cache_keys['processed_data']]
    
    def export_cache_state(self) -> Dict:
        """Export current cache state for debugging"""
        export_data = {}
        
        for key_name, cache_key in self.cache_keys.items():
            if cache_key in st.session_state:
                if key_name == 'raw_data':
                    # Don't export the actual dataframe, just metadata
                    raw_data = st.session_state[cache_key]
                    export_data[key_name] = {
                        'timestamp': raw_data['timestamp'],
                        'shape': raw_data['shape'],
                        'columns': raw_data['columns'],
                        'date_range': raw_data['date_range']
                    }
                else:
                    export_data[key_name] = st.session_state[cache_key]
        
        return export_data
