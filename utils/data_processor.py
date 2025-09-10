# utils/data_processor.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import io

class DataProcessor:
    def __init__(self):
        self.expected_columns = [
            'workdate', 'useremail', 'TotalDone', 'Good', 'GoodOriginal', 
            'GoodEnhanced', 'ForDownload', 'Bad', 'Rejected', 'Downloaded', 'Uploaded'
        ]
        
        self.calculated_columns = [
            'ForEditing', 'TotalReviewed', 'TotalEdited'
        ]
    
    def load_file(self, uploaded_file) -> pd.DataFrame:
        """Load and parse uploaded file"""
        try:
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            if file_extension == 'csv':
                # Try different encodings for CSV
                try:
                    df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
                except UnicodeDecodeError:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, encoding='latin-1')
            
            elif file_extension in ['xlsx', 'xls']:
                df = pd.read_excel(uploaded_file)
            
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
            
            return df
        
        except Exception as e:
            raise Exception(f"Error loading file: {str(e)}")
    
    def clean_and_format(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and format the raw data"""
        # Make a copy to avoid modifying original
        clean_df = df.copy()
        
        # Clean column names
        clean_df.columns = clean_df.columns.str.strip()
        
        # Remove unnamed columns
        clean_df = clean_df.loc[:, ~clean_df.columns.str.contains('^Unnamed')]
        
        # Handle missing columns by adding them with default values
        for col in self.expected_columns:
            if col not in clean_df.columns:
                clean_df[col] = 0
        
        # Convert workdate to datetime
        if 'workdate' in clean_df.columns:
            clean_df['workdate'] = pd.to_datetime(clean_df['workdate'], 
                                                format='%d/%m/%Y', 
                                                errors='coerce')
        
        # Fill NaN values with 0 for numeric columns
        numeric_columns = ['TotalDone', 'Good', 'GoodOriginal', 'GoodEnhanced', 
                          'ForDownload', 'Bad', 'Rejected', 'Downloaded', 'Uploaded']
        
        for col in numeric_columns:
            if col in clean_df.columns:
                clean_df[col] = pd.to_numeric(clean_df[col], errors='coerce').fillna(0)
        
        # Add calculated columns
        clean_df['ForEditing'] = clean_df['GoodEnhanced'] + clean_df['ForDownload']
        clean_df['TotalReviewed'] = clean_df['Good'] + clean_df['Bad'] + clean_df['Rejected']
        clean_df['TotalEdited'] = clean_df['Downloaded'] + clean_df['Uploaded']
        
        # Sort by date and user
        clean_df = clean_df.sort_values(['workdate', 'useremail']).reset_index(drop=True)
        
        return clean_df
    
    def prepare_for_ai(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Prepare data summary for AI analysis"""
        # Get basic statistics
        date_range = {
            'start_date': df['workdate'].min().strftime('%d/%m/%Y'),
            'end_date': df['workdate'].max().strftime('%d/%m/%Y')
        }
        
        # Get months and weeks
        months = sorted(df['workdate'].dt.to_period('M').unique())
        month_summaries = []
        
        for month in months:
            month_data = df[df['workdate'].dt.to_period('M') == month]
            month_summaries.append({
                'month': str(month),
                'total_records': len(month_data),
                'unique_users': month_data['useremail'].nunique(),
                'total_done': int(month_data['TotalDone'].sum()),
                'total_reviewed': int(month_data['TotalReviewed'].sum()),
                'total_edited': int(month_data['TotalEdited'].sum()),
                'good_count': int(month_data['Good'].sum()),
                'bad_count': int(month_data['Bad'].sum()),
                'rejected_count': int(month_data['Rejected'].sum())
            })
        
        # Get weekly summaries
        df['week_period'] = df['workdate'].dt.to_period('W')
        weeks = sorted(df['week_period'].unique())
        weekly_summaries = []
        
        for week in weeks:
            week_data = df[df['week_period'] == week]
            # Only include weekdays (Monday to Friday)
            weekday_data = week_data[week_data['workdate'].dt.dayofweek < 5]
            
            if not weekday_data.empty:
                weekly_summaries.append({
                    'week': str(week),
                    'start_date': week.start_time.strftime('%d/%m/%Y'),
                    'end_date': (week.start_time + timedelta(days=4)).strftime('%d/%m/%Y'),
                    'total_records': len(weekday_data),
                    'unique_users': weekday_data['useremail'].nunique(),
                    'total_done': int(weekday_data['TotalDone'].sum()),
                    'total_reviewed': int(weekday_data['TotalReviewed'].sum()),
                    'total_edited': int(weekday_data['TotalEdited'].sum())
                })
        
        # Get user summaries
        user_summaries = []
        for user in sorted(df['useremail'].unique()):
            user_data = df[df['useremail'] == user]
            user_summaries.append({
                'user': user,
                'total_done': int(user_data['TotalDone'].sum()),
                'total_reviewed': int(user_data['TotalReviewed'].sum()),
                'total_edited': int(user_data['TotalEdited'].sum()),
                'good_count': int(user_data['Good'].sum()),
                'bad_count': int(user_data['Bad'].sum()),
                'rejected_count': int(user_data['Rejected'].sum()),
                'days_active': len(user_data['workdate'].unique())
            })
        
        # Sample data for AI context (first 20 rows)
        sample_data = df.head(20).to_dict('records')
        
        return {
            'date_range': date_range,
            'total_records': len(df),
            'unique_users': df['useremail'].nunique(),
            'months': [str(m) for m in months],
            'month_summaries': month_summaries,
            'weekly_summaries': weekly_summaries,
            'user_summaries': user_summaries,
            'sample_data': sample_data,
            'columns': list(df.columns)
        }
    
    def separate_by_months(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Separate data by months"""
        months_data = {}
        
        for month_period in df['workdate'].dt.to_period('M').unique():
            month_data = df[df['workdate'].dt.to_period('M') == month_period].copy()
            months_data[str(month_period)] = month_data
        
        return months_data
    
    def separate_by_weeks(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Separate data by weeks (Monday to Friday only)"""
        weeks_data = {}
        
        # Add week period column
        df_temp = df.copy()
        df_temp['week_period'] = df_temp['workdate'].dt.to_period('W')
        
        for week_period in df_temp['week_period'].unique():
            week_data = df_temp[df_temp['week_period'] == week_period].copy()
            
            # Filter to weekdays only (Monday=0 to Friday=4)
            weekday_data = week_data[week_data['workdate'].dt.dayofweek < 5]
            
            if not weekday_data.empty:
                weeks_data[str(week_period)] = weekday_data.drop('week_period', axis=1)
        
        return weeks_data
    
    def generate_daily_summary(self, df: pd.DataFrame, period_type: str = 'week') -> List[Dict]:
        """Generate daily summary with totals"""
        daily_summary = []
        
        # Group by date
        for date, day_data in df.groupby('workdate'):
            weekday = date.strftime('%A')
            date_str = date.strftime('%d/%m/%Y')
            
            # Add individual user records for this day
            for _, row in day_data.iterrows():
                daily_summary.append({
                    'WorkDate': date_str,
                    'Weekday': weekday,
                    'User': row['useremail'],
                    'TotalDone': int(row['TotalDone']),
                    'Good': int(row['Good']),
                    'GoodOriginal': int(row['GoodOriginal']),
                    'GoodEnhanced': int(row['GoodEnhanced']),
                    'ForEditing': int(row['ForEditing']),
                    'Bad': int(row['Bad']),
                    'Rejected': int(row['Rejected']),
                    'TotalReviewed': int(row['TotalReviewed']),
                    'Downloaded': int(row['Downloaded']),
                    'Uploaded': int(row['Uploaded']),
                    'TotalEdited': int(row['TotalEdited'])
                })
            
            # Add daily total
            daily_total = {
                'WorkDate': f'TOTAL {weekday.upper()}',
                'Weekday': '',
                'User': '',
                'TotalDone': int(day_data['TotalDone'].sum()),
                'Good': int(day_data['Good'].sum()),
                'GoodOriginal': int(day_data['GoodOriginal'].sum()),
                'GoodEnhanced': int(day_data['GoodEnhanced'].sum()),
                'ForEditing': int(day_data['ForEditing'].sum()),
                'Bad': int(day_data['Bad'].sum()),
                'Rejected': int(day_data['Rejected'].sum()),
                'TotalReviewed': int(day_data['TotalReviewed'].sum()),
                'Downloaded': int(day_data['Downloaded'].sum()),
                'Uploaded': int(day_data['Uploaded'].sum()),
                'TotalEdited': int(day_data['TotalEdited'].sum())
            }
            daily_summary.append(daily_total)
        
        # Add period total
        if not df.empty:
            period_name = 'WEEKLY TOTAL' if period_type == 'week' else 'MONTHLY TOTAL'
            period_total = {
                'WorkDate': period_name,
                'Weekday': '',
                'User': '',
                'TotalDone': int(df['TotalDone'].sum()),
                'Good': int(df['Good'].sum()),
                'GoodOriginal': int(df['GoodOriginal'].sum()),
                'GoodEnhanced': int(df['GoodEnhanced'].sum()),
                'ForEditing': int(df['ForEditing'].sum()),
                'Bad': int(df['Bad'].sum()),
                'Rejected': int(df['Rejected'].sum()),
                'TotalReviewed': int(df['TotalReviewed'].sum()),
                'Downloaded': int(df['Downloaded'].sum()),
                'Uploaded': int(df['Uploaded'].sum()),
                'TotalEdited': int(df['TotalEdited'].sum())
            }
            daily_summary.append(period_total)
        
        return daily_summary
    
    def generate_user_summary(self, df: pd.DataFrame, period_name: str) -> List[Dict]:
        """Generate summary by user"""
        user_summary = []
        
        for user in sorted(df['useremail'].unique()):
            user_data = df[df['useremail'] == user]
            summary = {
                'User': user,
                'TotalDone': int(user_data['TotalDone'].sum()),
                'Good': int(user_data['Good'].sum()),
                'GoodOriginal': int(user_data['GoodOriginal'].sum()),
                'GoodEnhanced': int(user_data['GoodEnhanced'].sum()),
                'ForEditing': int(user_data['ForEditing'].sum()),
                'Bad': int(user_data['Bad'].sum()),
                'Rejected': int(user_data['Rejected'].sum()),
                'TotalReviewed': int(user_data['TotalReviewed'].sum()),
                'Downloaded': int(user_data['Downloaded'].sum()),
                'Uploaded': int(user_data['Uploaded'].sum()),
                'TotalEdited': int(user_data['TotalEdited'].sum())
            }
            user_summary.append(summary)
        
        # Add period total
        period_total = {
            'User': f'{period_name.upper()} TOTAL',
            'TotalDone': int(df['TotalDone'].sum()),
            'Good': int(df['Good'].sum()),
            'GoodOriginal': int(df['GoodOriginal'].sum()),
            'GoodEnhanced': int(df['GoodEnhanced'].sum()),
            'ForEditing': int(df['ForEditing'].sum()),
            'Bad': int(df['Bad'].sum()),
            'Rejected': int(df['Rejected'].sum()),
            'TotalReviewed': int(df['TotalReviewed'].sum()),
            'Downloaded': int(df['Downloaded'].sum()),
            'Uploaded': int(df['Uploaded'].sum()),
            'TotalEdited': int(df['TotalEdited'].sum())
        }
        user_summary.append(period_total)
        
        return user_summary
    