import streamlit as st
import pandas as pd
import os
from datetime import datetime
from dotenv import load_dotenv
from typing import Dict, Optional

# Import custom modules
from utils.data_processor import DataProcessor
from utils.gemini_client import GeminiClient
from utils.excel_generator import ExcelReportGenerator
from utils.streamlit_cache import StreamlitCache
from utils.sidebar import render_sidebar

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="Autobot - Automate Your Workflow",
    page_icon="static/logo.png",
    layout="wide"
)

def load_css():
    """Loads modern, beautiful CSS styling."""
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            
            /* Global styles */
            .stApp {
                /*background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);*/
                font-family: 'Inter', sans-serif;
            }
            
            .main .block-container {
                padding-top: 1rem;
                padding-bottom: 2rem;
                max-width: 1200px;
            }
            
            /* Hide default streamlit elements */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            [data-testid="stSidebarNav"] {display: none;}
            
            /* Custom header */
            .app-header {
                background: linear-gradient(135deg, #667eea, #764ba2);
                backdrop-filter: blur(20px);
                border-radius: 20px;
                padding: 1rem;
                margin-bottom: 0rem;
                border: 1px solid rgba(255, 255, 255, 0.2);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            }
            
            .app-title {
                font-size: 3.5rem;
                font-weight: 700;
                background: linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                text-align: center;
                margin: 0;
                letter-spacing: -0.02em;
            }
            
            .app-subtitle {
                text-align: center;
                color: rgba(255, 255, 255, 0.8);
                font-size: 1.2rem;
                font-weight: 400;
                margin-top: 0.5rem;
                margin-bottom: 1;
            }
                
            /* Divider line after header */
            .header-divider {
                height: 2px;
                background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.3) 20%, rgba(255,255,255,0.8) 50%, rgba(255,255,255,0.3) 80%, transparent 100%);
                margin: 1.5rem 0;
                border-radius: 2px;
            }
            
            /* Mode selection cards */
            .mode-container {
                display: flex;
                gap: 1.5rem;
                justify-content: center;
                margin: 3rem 0;
            }
            
            .mode-card {
                /*background: rgba(255, 255, 255, 0.95);*/
                backdrop-filter: blur(20px);
                border-radius: 24px;
                padding: 1rem;
                width: 580px;
                text-align: center;
                cursor: pointer;
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                border: 2px solid transparent;
                position: relative;
                overflow: hidden;
            }
            
            .mode-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: linear-gradient(135deg, #667eea, #764ba2);
                opacity: 0;
                transition: opacity 0.3s ease;
                z-index: -1;
            }
            
            .mode-card:hover {
                transform: translateY(-8px) scale(1.02);
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
                border-color: rgba(255, 255, 255, 0.3);
            }
            
            .mode-card:hover::before {
                opacity: 0.1;
            }
            
            .mode-card.active {
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                transform: translateY(-4px);
                box-shadow: 0 15px 30px rgba(102, 126, 234, 0.4);
            }
            
            .mode-card.active::before {
                opacity: 0;
            }
            
            .mode-icon {
                font-size: 3rem;
                margin-bottom: 1rem;
                display: block;
            }
            
            .mode-title {
                font-size: 1.5rem;
                font-weight: 600;
                margin-bottom: 0.5rem;
                color: inherit;
            }
            
            .mode-description {
                font-size: 0.95rem;
                opacity: 0.8;
                line-height: 1.5;
                color: inherit;
            }
            
            /* Content area */
            .content-area {
                background: linear-gradient(135deg, #667eea, #764ba2);
                backdrop-filter: blur(20px);
                border-radius: 24px;
                padding: 2rem;
                margin-top: 1rem;
                margin-bottom: 1rem;
                border: 1px solid rgba(255, 255, 255, 0.2);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            }
            
            .content-title {
                font-size: 2rem;
                font-weight: 600;
                color: #2d3748;
                margin-bottom: 1.5rem;
                text-align: center;
            }
            
            /* Chat interface */
            .chat-container {
                max-width: 800px;
                margin: 0 auto;
            }
            
            .stTextInput > div > div > input {
                border: 2px solid rgba(102, 126, 234, 0.2);
                border-radius: 16px;
                padding: 1rem 1.5rem;
                font-size: 1rem;
                transition: all 0.3s ease;
                background: rgba(255, 255, 255, 0.8);
            }
            
            .stTextInput > div > div > input:focus {
                border-color: #667eea;
                box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
                outline: none;
            }
            
            /* Custom buttons */
            .modern-button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 16px;
                padding: 0.75rem 2rem;
                font-size: 1rem;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
                text-decoration: none;
                margin: 0.5rem 0;
            }
            
            .modern-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
            }
            
            .modern-button:active {
                transform: translateY(0);
            }
            
            /* File upload area */
            .upload-area {
                border: 3px dashed rgba(102, 126, 234, 0.3);
                border-radius: 20px;
                padding: 3rem 2rem;
                text-align: center;
                background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
                transition: all 0.3s ease;
                margin: 2rem 0;
            }
            
            .upload-area:hover {
                border-color: #667eea;
                background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
            }
            
            .upload-icon {
                font-size: 4rem;
                color: #667eea;
                margin-bottom: 1rem;
            }
            
            .upload-text {
                font-size: 1.2rem;
                color: #4a5568;
                font-weight: 500;
                margin-bottom: 0.5rem;
            }
            
            .upload-subtext {
                color: #718096;
                font-size: 0.9rem;
            }
            
            /* Sidebar styling */
            .css-1d391kg {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(20px);
            }
            
            /* Metrics and data display */
            .metric-card {
                background: linear-gradient(135deg, #667eea, #764ba2);
                backdrop-filter: blur(10px);
                border-radius: 16px;
                padding: 1rem;
                margin-bottom: 2rem;
                border: 2px solid rgba(255, 255, 255, 0.2);
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
            }
            
            /* Response styling */
            .ai-response {
                background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
                border-left: 4px solid #667eea;
                border-radius: 0 16px 16px 0;
                padding: 1.5rem;
                margin: 1rem 0;
                backdrop-filter: blur(10px);
            }
            
            /* Success/Error messages */
            .stSuccess, .stError, .stWarning, .stInfo {
                border-radius: 12px;
                border: none;
                backdrop-filter: blur(10px);
            }
            
            /* Tabs styling */
            .stTabs [data-baseweb="tab-list"] {
                gap: 1rem;
                background: transparent;
            }
            
            .stTabs [data-baseweb="tab"] {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 0.75rem 1.5rem;
                border: 1px solid rgba(255, 255, 255, 0.2);
                color: #4a5568;
                font-weight: 500;
            }
            
            .stTabs [data-baseweb="tab"]:hover {
                background: rgba(102, 126, 234, 0.1);
                color: #667eea;
            }
            
            .stTabs [aria-selected="true"] {
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
            }
            
            /* DataFrame styling */
            .stDataFrame {
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
            }
        </style>
    """, unsafe_allow_html=True)

class AutobotApp:
    def __init__(self):
        """Initialize the application components."""
        self.data_processor = DataProcessor()
        self.cache = StreamlitCache()
        self.excel_generator = ExcelReportGenerator()
        
        # Initialize Gemini client from .env
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if gemini_api_key:
            self.gemini_client = GeminiClient(gemini_api_key)
        else:
            self.gemini_client = None
            st.error("🔑 GEMINI_API_KEY not found in .env file. Please add it to continue.")


    def render_header(self):
        """Render the modern header."""
        st.markdown("""
            <div class="app-header">
                <h1 class="app-title">Autobot</h1>
                <p class="app-subtitle">Automate your workflow with AI-powered intelligence</p>
            </div>
            <div class="header-divider"></div>
        """, unsafe_allow_html=True)

    def render_mode_selection(self):
        """Render modern mode selection cards."""
        # Initialize mode in session state if not present
        if 'mode' not in st.session_state:
            st.session_state.mode = "Personal"
        
        st.markdown("""
            <div class="mode-container">
                <div class="mode-card {}" onclick="selectMode('Personal')">
                    <div class="mode-icon">📨</div>
                    <div class="mode-title">Personal Mode</div>
                    <div class="mode-description">Chat with AI assistant for quick questions and everyday tasks</div>
                </div>
                <div class="mode-card {}" onclick="selectMode('Business')">
                    <div class="mode-icon">📝</div>
                    <div class="mode-title">Business Mode</div>
                    <div class="mode-description">Upload files and generate comprehensive AI-powered reports</div>
                </div>
            </div>
        """.format(
            "active" if st.session_state.mode == "Personal" else "",
            "active" if st.session_state.mode == "Business" else ""
        ), unsafe_allow_html=True)
        
        # Mode selection buttons under the cards
        st.markdown("""
            <div class="mode-buttons">
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Personal Mode", key="personal_mode", use_container_width=True):
                st.session_state.mode = "Personal"
                st.rerun()
        with col2:
            if st.button("Business Mode", key="business_mode", use_container_width=True):
                st.session_state.mode = "Business"
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="header-divider"></div>
        """, unsafe_allow_html=True)

    def render_personal_mode(self):
        """Render the Personal Mode interface."""
        st.markdown("""
            <div class="content-area">
                <h2 class="content-title">💬 What can I help you with today?</h2>
                <div class="chat-container">
        """, unsafe_allow_html=True)
        
        # Chat interface
        user_input = st.text_input(
            "Ask me anything... How can I help you today?",
            key="personal_input",
            placeholder="Ask me anything... How can I help you today?",
            label_visibility="collapsed"
        )
        
        # Center the submit button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            submit_pressed = st.button("✨ Submit", key="personal_submit", use_container_width=True)
        
        if submit_pressed and user_input:
            if not self.gemini_client:
                st.error("🔑 Gemini client is not initialized. Check your API key.")
                return
            
            with st.spinner("🤔 Thinking..."):
                try:
                    response = self.gemini_client.chat(user_input)
                    st.markdown(f"""
                        <div class="ai-response">
                            <strong>🤖 Autobot:</strong><br>
                            {response}
                        </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"❌ An error occurred: {str(e)}")
        
        st.markdown("</div></div>", unsafe_allow_html=True)

    def render_business_mode(self):
        # File upload area
        st.markdown("""
            <div class="upload-area">
                <div class="upload-icon">📁</div>
                <div class="upload-text">Upload Your Data Files</div>
                <div class="upload-subtext">Support for Excel (.xlsx, .xls) and CSV files</div>
            </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Upload your data files. Support for Excel (.xlsx, .xls) and CSV files.",
            type=['xlsx', 'xls', 'csv'],
            label_visibility="collapsed"
        )
        
        if uploaded_file:
            self._process_uploaded_file(uploaded_file)
        
        st.markdown("</div>", unsafe_allow_html=True)

    def _process_uploaded_file(self, uploaded_file):
        """Process the uploaded file with enhanced UI feedback."""
        try:
            with st.spinner("🔄 Processing your file..."):
                raw_data = self.data_processor.load_file(uploaded_file)
                cleaned_data = self.data_processor.clean_and_format(raw_data)
                self.cache.store_raw_data(cleaned_data)
                st.success("✅ File processed successfully!")

            self._display_data_preview(cleaned_data)

            # Generate report button with modern styling
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🚀 Generate AI Report Analysis", key="generate_report", use_container_width=True):
                    if not self.gemini_client:
                        st.error("🔑 Gemini client not available for analysis.")
                        return
                    self._generate_ai_analysis(cleaned_data)
        
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")

    def _display_data_preview(self, data: pd.DataFrame):
        """Display enhanced data preview."""
        st.markdown("### 📋 Data Preview")
        
        # Metrics in cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
                <div class="metric-card">
                    <h3>📊 Total Records</h3>
                    <h2 style="color: white; margin: 0;">{len(data):,}</h2>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="metric-card">
                    <h3>📅 Date Range</h3>
                    <h2 style="color: white; margin: 0; font-size: 1.7rem;">{data['workdate'].min():%b %Y} - {data['workdate'].max():%b %Y}</h2>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
                <div class="metric-card">
                    <h3>📈 Columns</h3>
                    <h2 style="color: white; margin: 0;">{len(data.columns)}</h2>
                </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
                <div class="metric-card">
                    <h3>💾 Size</h3>
                    <h2 style="color: white; margin: 0;">{data.memory_usage(deep=True).sum() / 1024 / 1024:.1f}MB</h2>
                </div>
            """, unsafe_allow_html=True)
        
        # Data table
        st.dataframe(data, use_container_width=True)

    def _generate_ai_analysis(self, data: pd.DataFrame):
        """Generate AI analysis with beautiful progress indicators."""
        with st.spinner("🧠 AI is analyzing your data... This may take a moment."):
            try:
                report_template = self.cache.get_report_template()
                data_summary = self.data_processor.prepare_for_ai(data)
                analysis = self.gemini_client.analyze_report_data(data_summary, report_template)
                
                validated_result = self._validate_ai_response(analysis)
                if validated_result:
                    self.cache.store_processed_data(validated_result)
                    self._display_ai_results(validated_result)
                    self._generate_excel_report(validated_result)
                else:
                    st.error("❌ AI response validation failed. The structure might be incorrect.")
            
            except Exception as e:
                st.error(f"❌ Error during AI analysis: {str(e)}")

    def _validate_ai_response(self, ai_response: Dict) -> Optional[Dict]:
        """Validate the AI response structure."""
        required_keys = ['monthly_summaries', 'weekly_summaries', 'user_summaries']
        if all(key in ai_response for key in required_keys):
            return ai_response
        st.warning("⚠️ AI response is missing one or more required keys.")
        return None

    def _display_ai_results(self, results: Dict):
        """Display AI results with beautiful tabs."""
        st.markdown("### 🎯 AI Analysis Results")
        
        tab1, tab2, tab3 = st.tabs(["📅 Monthly Summary", "📊 Weekly Breakdown", "👥 User Analysis"])
        
        with tab1:
            if results.get('monthly_summaries'):
                st.dataframe(pd.DataFrame(results['monthly_summaries']), use_container_width=True)
            else:
                st.info("No monthly summary data available.")
        
        with tab2:
            if results.get('weekly_summaries'):
                st.dataframe(pd.DataFrame(results['weekly_summaries']), use_container_width=True)
            else:
                st.info("No weekly breakdown data available.")
        
        with tab3:
            if results.get('user_summaries'):
                st.dataframe(pd.DataFrame(results['user_summaries']), use_container_width=True)
            else:
                st.info("No user analysis data available.")

    def _generate_excel_report(self, processed_data: Dict):
        """Generate Excel report with modern download button."""
        try:
            excel_buffer = self.excel_generator.create_report(processed_data)
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                st.download_button(
                    label="📥 Download Excel Report",
                    data=excel_buffer.getvalue(),
                    file_name=f"AI_Report_{datetime.now():%Y%m%d_%H%M%S}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        except Exception as e:
            st.error(f"❌ Failed to generate Excel report: {str(e)}")

    def run(self):
        """Main application runner."""
        load_css()
        render_sidebar()
        self.render_header()
        self.render_mode_selection()

        # Render content based on selected mode
        if st.session_state.get('mode') == "Personal":
            self.render_personal_mode()
        else:
            self.render_business_mode()

if __name__ == "__main__":
    app = AutobotApp()
    app.run()
