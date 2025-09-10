import streamlit as st
import pandas as pd
from utils.streamlit_cache import StreamlitCache
from utils.sidebar import render_sidebar

def load_css():
    """Loads modern, beautiful CSS styling for reports page."""
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            
            /* Global styles */
            .stApp {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                font-family: 'Inter', sans-serif;
            }
            
            .main .block-container {
                padding-top: 1rem;
                padding-bottom: 2rem;
                max-width: 1400px;
            }
            
            /* Hide default streamlit elements */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            [data-testid="stSidebarNav"] {display: none;}
            
            /* Page header */
            .reports-header {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(20px);
                border-radius: 20px;
                padding: 2rem;
                margin-bottom: 2rem;
                border: 1px solid rgba(255, 255, 255, 0.2);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                text-align: center;
            }
            
            .reports-title {
                font-size: 3rem;
                font-weight: 700;
                background: linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin: 0;
                letter-spacing: -0.02em;
            }
            
            .reports-subtitle {
                color: rgba(255, 255, 255, 0.8);
                font-size: 1.1rem;
                font-weight: 400;
                margin-top: 0.5rem;
                margin-bottom: 0;
            }
            
            /* Content sections */
            .report-section {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                border-radius: 20px;
                padding: 2rem;
                margin-bottom: 2rem;
                border: 1px solid rgba(255, 255, 255, 0.2);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            }
            
            .section-title {
                font-size: 1.8rem;
                font-weight: 600;
                color: #2d3748;
                margin-bottom: 1.5rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            
            .section-title::before {
                content: '';
                width: 4px;
                height: 2rem;
                background: linear-gradient(135deg, #667eea, #764ba2);
                border-radius: 2px;
            }
            
            /* No data state */
            .no-data-container {
                text-align: center;
                padding: 4rem 2rem;
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            }
            
            .no-data-icon {
                font-size: 5rem;
                margin-bottom: 1.5rem;
                opacity: 0.6;
            }
            
            .no-data-title {
                font-size: 1.8rem;
                font-weight: 600;
                color: #2d3748;
                margin-bottom: 1rem;
            }
            
            .no-data-message {
                font-size: 1.1rem;
                color: #718096;
                margin-bottom: 2rem;
                line-height: 1.6;
            }
            
            .action-button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 16px;
                padding: 1rem 2rem;
                font-size: 1.1rem;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                text-decoration: none;
                display: inline-block;
            }
            
            .action-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
            }
            
            /* Weekly breakdown cards */
            .week-card {
                background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
                border-radius: 16px;
                padding: 1.5rem;
                margin-bottom: 1.5rem;
                border: 1px solid rgba(102, 126, 234, 0.2);
                transition: all 0.3s ease;
            }
            
            .week-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
            }
            
            .week-header {
                font-size: 1.2rem;
                font-weight: 600;
                color: #2d3748;
                margin-bottom: 1rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            
            .metrics-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 1rem;
                margin-bottom: 1rem;
            }
            
            .metric-item {
                background: rgba(255, 255, 255, 0.8);
                border-radius: 12px;
                padding: 1rem;
                text-align: center;
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
            
            .metric-value {
                font-size: 1.5rem;
                font-weight: 700;
                color: #667eea;
                margin: 0;
            }
            
            .metric-label {
                font-size: 0.9rem;
                color: #718096;
                margin-top: 0.25rem;
            }
            
            /* DataFrame styling */
            .stDataFrame {
                border-radius: 16px;
                overflow: hidden;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            
            /* Success message */
            .success-message {
                background: linear-gradient(135deg, rgba(72, 187, 120, 0.1) 0%, rgba(56, 178, 172, 0.1) 100%);
                border-left: 4px solid #48bb78;
                border-radius: 0 12px 12px 0;
                padding: 1rem 1.5rem;
                margin: 1rem 0;
                color: #2f855a;
                font-weight: 500;
            }
            
            /* Expandable sections */
            .stExpander {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                margin: 0.5rem 0;
            }
            
            .stExpander > div > div > div > div {
                background: transparent;
            }
            
            /* Sidebar styling */
            .css-1d391kg {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(20px);
            }
        </style>
    """, unsafe_allow_html=True)

def display_reports():
    """Renders the modern reports page with enhanced UI."""
    cache = StreamlitCache()
    
    # Modern header
    st.markdown("""
        <div class="reports-header">
            <h1 class="reports-title">📊 Generated Reports</h1>
            <p class="reports-subtitle">Comprehensive AI-generated analysis and insights</p>
        </div>
    """, unsafe_allow_html=True)
    
    processed_data = cache.get_processed_data()
    
    if processed_data:
        st.markdown("""
            <div class="success-message">
                ✅ Report data loaded successfully from cache
            </div>
        """, unsafe_allow_html=True)
        
        _display_monthly_summary(processed_data)
        _display_weekly_breakdown(processed_data)
        _display_user_analysis(processed_data)
        
        # Raw data expander with modern styling
        with st.expander("🔍 Show Raw JSON Data", expanded=False):
            st.json(processed_data)
    else:
        st.markdown("""
            <div class="no-data-container">
                <div class="no-data-icon">📈</div>
                <div class="no-data-title">No Reports Available</div>
                <div class="no-data-message">
                    You haven't generated any reports yet. Head to the dashboard to upload your data files and create AI-powered analysis reports.
                </div>
                <a href="Dashboard.py" class="action-button">
                    🚀 Generate Your First Report
                </a>
            </div>
        """, unsafe_allow_html=True)

def _display_monthly_summary(data: dict):
    """Displays the monthly performance summary with modern styling."""
    if 'monthly_summaries' in data and data['monthly_summaries']:
        st.markdown("""
            <div class="report-section">
                <h2 class="section-title">📅 Monthly Performance Summary</h2>
        """, unsafe_allow_html=True)
        
        try:
            df = pd.DataFrame(data['monthly_summaries'])
            st.dataframe(df, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"❌ Error displaying monthly summary: {e}")
        
        st.markdown("</div>", unsafe_allow_html=True)

def _display_weekly_breakdown(data: dict):
    """Displays the weekly performance breakdown with enhanced cards."""
    if 'weekly_summaries' in data and data['weekly_summaries']:
        st.markdown("""
            <div class="report-section">
                <h2 class="section-title">🗓️ Weekly Performance Breakdown</h2>
        """, unsafe_allow_html=True)
        
        try:
            for i, week in enumerate(data['weekly_summaries']):
                st.markdown(f"""
                    <div class="week-card">
                        <div class="week-header">
                            📊 Week {week.get('week_id', i+1)}: {week.get('start_date', 'N/A')} to {week.get('end_date', 'N/A')}
                        </div>
                        <div class="metrics-grid">
                            <div class="metric-item">
                                <div class="metric-value">{week.get('total_done', 0):,}</div>
                                <div class="metric-label">Total Done</div>
                            </div>
                            <div class="metric-item">
                                <div class="metric-value">{week.get('total_reviewed', 0):,}</div>
                                <div class="metric-label">Total Reviewed</div>
                            </div>
                            <div class="metric-item">
                                <div class="metric-value">{week.get('total_edited', 0):,}</div>
                                <div class="metric-label">Total Edited</div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Daily breakdown in expandable section
                if week.get('daily_breakdown'):
                    with st.expander(f"📋 Daily Breakdown - Week {week.get('week_id', i+1)}", expanded=False):
                        daily_df = pd.DataFrame(week.get('daily_breakdown', []))
                        if not daily_df.empty:
                            st.dataframe(daily_df, use_container_width=True, hide_index=True)
                        else:
                            st.info("No daily breakdown data available for this week.")
        except Exception as e:
            st.error(f"❌ Error displaying weekly breakdown: {e}")
        
        st.markdown("</div>", unsafe_allow_html=True)

def _display_user_analysis(data: dict):
    """Displays the user performance analysis with modern styling."""
    if 'user_summaries' in data and data['user_summaries']:
        st.markdown("""
            <div class="report-section">
                <h2 class="section-title">👥 User Performance Analysis</h2>
        """, unsafe_allow_html=True)
        
        try:
            df = pd.DataFrame(data['user_summaries'])
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Add some insights if data is available
            if not df.empty and 'total_done' in df.columns:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    top_performer = df.loc[df['total_done'].idxmax()] if 'total_done' in df.columns else None
                    if top_performer is not None:
                        st.markdown(f"""
                            <div class="metric-item">
                                <div class="metric-value">🏆</div>
                                <div class="metric-label">Top Performer</div>
                                <div style="font-weight: 600; color: #2d3748; margin-top: 0.5rem;">
                                    {top_performer.get('user_name', 'Unknown')}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                
                with col2:
                    total_users = len(df)
                    st.markdown(f"""
                        <div class="metric-item">
                            <div class="metric-value">{total_users}</div>
                            <div class="metric-label">Total Users</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    avg_performance = df['total_done'].mean() if 'total_done' in df.columns else 0
                    st.markdown(f"""
                        <div class="metric-item">
                            <div class="metric-value">{avg_performance:.0f}</div>
                            <div class="metric-label">Avg Tasks/User</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
        except Exception as e:
            st.error(f"❌ Error displaying user analysis: {e}")
        
        st.markdown("</div>", unsafe_allow_html=True)

st.set_page_config(
    page_title="Generated Reports - Autobot",
    page_icon="📊",
    layout="wide"
)
    
load_css()
render_sidebar()
display_reports()
