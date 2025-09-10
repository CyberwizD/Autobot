import streamlit as st
from utils.streamlit_cache import StreamlitCache

def render_sidebar():
    """Render the modern sidebar."""
    with st.sidebar:
        # Logo and navigation
        st.markdown("""
            <div style="text-align: center; padding: 1rem 0 2rem 0;">
                <div style="font-size: 3rem;">🤖</div>
                <div style="color: white; font-weight: 600; margin-top: 0.5rem;">Autobot</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Navigation
        st.page_link("Dashboard.py", label="🏠 Dashboard")
        st.page_link("pages/Reports.py", label="📊 Reports")

        st.divider()
        
        # Cache status with modern styling
        st.markdown("### 💾 Cache Status")
        cache = StreamlitCache()
        cache_info = cache.get_cache_info()
        
        # Display cache info in a more visual way
        for key, value in cache_info.get("cache_status", {}).items():
            status_icon = "✅" if value else "❌"
            st.markdown(f"**{key.replace('_', ' ').title()}**: {status_icon}")
        
        if st.button("🗑️ Clear Cache", use_container_width=True):
            cache.clear_all()
            st.success("Cache cleared!")
            st.rerun()
