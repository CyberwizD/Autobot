# utils/gemini_client.py
import google.generativeai as genai
import json
from typing import Dict, List, Any, Optional
import pandas as pd

class GeminiClient:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.chat_session = self.model.start_chat(history=[])
    
    def chat(self, message: str) -> str:
        """Simple chat functionality for personal mode"""
        try:
            response = self.chat_session.send_message(message)
            return response.text
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def analyze_report_data(self, data_summary: Dict, template: Dict) -> Dict:
        """Analyze report data and generate structured summaries"""
        
        # Create the prompt for data analysis
        prompt = self._create_analysis_prompt(data_summary, template)
        
        try:
            response = self.model.generate_content(prompt)
            
            # Parse the JSON response
            result = self._parse_ai_response(response.text)
            
            return result
            
        except Exception as e:
            raise Exception(f"Error in AI analysis: {str(e)}")
    
    def _create_analysis_prompt(self, data_summary: Dict, template: Dict) -> str:
        """Create detailed prompt for AI analysis"""
        
        prompt = f"""
You are an expert data analyst specializing in image enhancement workflow reports. 
Analyze the following data and generate structured summaries following the exact template format.

**DATA TO ANALYZE:**
```json
{json.dumps(data_summary, indent=2, default=str)}
```

**EXPECTED TEMPLATE FORMAT:**
```json
{json.dumps(template, indent=2)}
```

**ANALYSIS REQUIREMENTS:**

1. **Monthly Summaries**: For each month in the data, calculate:
   - Total records processed
   - Total images done, reviewed, and edited
   - Breakdown by Good, Bad, Rejected categories
   - User participation statistics

2. **Weekly Summaries**: For each week (Monday-Friday only), calculate:
   - Weekly totals for all metrics
   - Daily breakdowns with totals per day
   - User performance per week
   - Progress tracking

3. **User Summaries**: For each user, calculate:
   - Individual performance metrics
   - Total contribution across all periods
   - Quality metrics (Good/Bad/Rejected ratios)
   - Activity patterns

4. **Daily Summaries**: For each working day, provide:
   - Individual user records
   - Daily totals per weekday
   - Weekly and monthly aggregations

**CALCULATIONS TO PERFORM:**
- TotalDone = Sum of all images processed
- TotalReviewed = Good + Bad + Rejected
- TotalEdited = Downloaded + Uploaded  
- ForEditing = GoodEnhanced + ForDownload

**OUTPUT FORMAT:**
Return ONLY a valid JSON object with this exact structure:
```json
{{
  "monthly_summaries": [
    {{
      "month": "2025-07",
      "month_name": "July 2025",
      "start_date": "01/07/2025",
      "end_date": "31/07/2025",
      "total_done": 0,
      "total_reviewed": 0,
      "total_edited": 0,
      "good_count": 0,
      "bad_count": 0,
      "rejected_count": 0,
      "unique_users": 0,
      "working_days": 0
    }}
  ],
  "weekly_summaries": [
    {{
      "week_id": "Week1",
      "week_period": "2025-W30",
      "start_date": "21/07/2025",
      "end_date": "25/07/2025",
      "month": "July 2025",
      "total_done": 0,
      "total_reviewed": 0,
      "total_edited": 0,
      "daily_breakdown": [
        {{
          "date": "21/07/2025",
          "weekday": "Monday",
          "total_done": 0,
          "users_active": 0
        }}
      ]
    }}
  ],
  "user_summaries": [
    {{
      "user": "user@example.com",
      "total_done": 0,
      "total_reviewed": 0,
      "total_edited": 0,
      "good_count": 0,
      "bad_count": 0,
      "rejected_count": 0,
      "days_active": 0,
      "avg_per_day": 0
    }}
  ],
  "daily_summaries": [
    {{
      "date": "21/07/2025",
      "weekday": "Monday",
      "user_records": [
        {{
          "user": "user@example.com",
          "total_done": 0,
          "good": 0,
          "bad": 0,
          "rejected": 0,
          "downloaded": 0,
          "uploaded": 0
        }}
      ],
      "daily_totals": {{
        "total_done": 0,
        "total_reviewed": 0,
        "total_edited": 0
      }}
    }}
  ],
  "overall_statistics": {{
    "total_records": 0,
    "date_range": {{
      "start": "21/07/2025",
      "end": "01/08/2025"
    }},
    "total_users": 0
  }}
}}
```
"""
        return prompt

    def _parse_ai_response(self, response_text: str) -> Dict:
        """Parse the AI's JSON response, cleaning it if necessary."""
        try:
            # The response might contain markdown code fences
            if response_text.strip().startswith("```json"):
                response_text = response_text.strip()[7:-4].strip()
            elif response_text.strip().startswith("```"):
                response_text = response_text.strip()[3:-3].strip()
            
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to decode AI response JSON: {{e}}\\nResponse: {{response_text}}")
