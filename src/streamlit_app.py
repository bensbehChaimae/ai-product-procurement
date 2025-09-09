import streamlit as st
import os
import json
import time
from datetime import datetime
from crew_manager import CrewManager
import threading
from concurrent.futures import ThreadPoolExecutor

# Configure Streamlit page
st.set_page_config(
    page_title="RankX Product Research",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "crew_manager" not in st.session_state:
    st.session_state.crew_manager = CrewManager()
if "job_status" not in st.session_state:
    st.session_state.job_status = None
if "job_results" not in st.session_state:
    st.session_state.job_results = None
if "job_running" not in st.session_state:
    st.session_state.job_running = False

def run_research_job(inputs):
    """Run the research job in background"""
    st.session_state.job_running = True
    st.session_state.job_status = "Starting research..."
    
    try:
        results = st.session_state.crew_manager.execute_crew(inputs)
        st.session_state.job_results = results
        st.session_state.job_status = "Research completed successfully!"
    except Exception as e:
        st.session_state.job_results = {"success": False, "error": str(e)}
        st.session_state.job_status = f"Research failed: {str(e)}"
    finally:
        st.session_state.job_running = False

def main():
    st.title("🔍 RankX Product Research System")
    st.markdown("---")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Keys section
        st.subheader("API Keys")
        openai_key = st.text_input("OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", ""))
        agentops_key = st.text_input("AgentOps API Key", type="password", value=os.getenv("AGENTOPS_API_KEY", ""))
        tavily_key = st.text_input("Tavily API Key", type="password", value=os.getenv("TAVILY_API_KEY", ""))
        scrapegraph_key = st.text_input("ScrapGraph API Key", type="password", value=os.getenv("SCRAPEGRAPH_API_KEY", ""))
        
        # Update environment variables
        if openai_key:
            os.environ["OPENAI_API_KEY"] = openai_key
        if agentops_key:
            os.environ["AGENTOPS_API_KEY"] = agentops_key
        if tavily_key:
            os.environ["TAVILY_API_KEY"] = tavily_key
        if scrapegraph_key:
            os.environ["SCRAPEGRAPH_API_KEY"] = scrapegraph_key
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📝 Research Parameters")
        
        # Product information
        product_name = st.text_input(
            "Product Name",
            value="Office air conditioners",
            placeholder="Enter the product you want to research"
        )
        
        # Website list
        websites_text = st.text_area(
            "Target Websites (one per line)",
            value="www.amazon.com\nwww.electroplanet.ma\nwww.ikea.com",
            height=100,
            placeholder="Enter website URLs, one per line"
        )
        
        # Parse websites list
        websites_list = [site.strip() for site in websites_text.split('\n') if site.strip()]
        
        # Location and language
        col1_1, col1_2 = st.columns(2)
        with col1_1:
            country_name = st.text_input("Country", value="Morocco")
        with col1_2:
            language = st.text_input("Language", value="English")
        
        # Advanced parameters
        st.subheader("🎯 Advanced Parameters")
        col1_3, col1_4, col1_5 = st.columns(3)
        
        with col1_3:
            no_keywords = st.number_input(
                "Max Keywords",
                min_value=1,
                max_value=50,
                value=10,
                help="Maximum number of search keywords to generate"
            )
        
        with col1_4:
            score_th = st.number_input(
                "Score Threshold",
                min_value=0.0,
                max_value=1.0,
                value=0.10,
                step=0.01,
                help="Minimum score threshold for filtering results"
            )
        
        with col1_5:
            top_recommendations_no = st.number_input(
                "Top Recommendations",
                min_value=1,
                max_value=50,
                value=10,
                help="Number of top product recommendations to generate"
            )
        
        # Start research button
        if st.button("🚀 Start Research", type="primary", disabled=st.session_state.job_running):
            if not all([openai_key, tavily_key, scrapegraph_key]):
                st.error("Please provide all required API keys in the sidebar!")
            elif not product_name:
                st.error("Please enter a product name!")
            elif not websites_list:
                st.error("Please provide at least one website!")
            else:
                # Prepare inputs
                inputs = {
                    "product_name": product_name,
                    "websites_list": websites_list,
                    "country_name": country_name,
                    "no_keywords": no_keywords,
                    "language": language,
                    "score_th": score_th,
                    "top_recommendations_no": top_recommendations_no
                }
                
                # Validate inputs
                validation = st.session_state.crew_manager.validate_inputs(inputs)
                if not validation["valid"]:
                    st.error("Input validation failed:")
                    for error in validation["errors"]:
                        st.error(f"• {error}")
                else:
                    # Start the research job
                    thread = threading.Thread(target=run_research_job, args=(inputs,))
                    thread.start()
                    st.success("Research job started! Check the status panel for updates.")
    
    with col2:
        st.header("📊 Status & Results")
        
        # Job status display
        if st.session_state.job_running:
            st.info("🔄 Research in progress...")
            st.write(f"Status: {st.session_state.job_status}")
            
            # Progress bar (indeterminate)
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
            
            # Auto-refresh
            time.sleep(2)
            st.rerun()
            
        elif st.session_state.job_results:
            if st.session_state.job_results["success"]:
                st.success("✅ Research completed successfully!")
                
                # Display output directory
                output_dir = st.session_state.job_results.get("output_directory", "./ai_agent_output")
                st.info(f"📁 Output directory: {output_dir}")
                
                # List available files
                if os.path.exists(output_dir):
                    files = [f for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f))]
                    
                    if files:
                        st.subheader("📄 Generated Files")
                        for file in files:
                            file_path = os.path.join(output_dir, file)
                            file_size = os.path.getsize(file_path)
                            
                            col_file, col_download = st.columns([3, 1])
                            with col_file:
                                st.write(f"📄 {file} ({file_size} bytes)")
                            with col_download:
                                with open(file_path, "rb") as f:
                                    st.download_button(
                                        label="⬇️",
                                        data=f.read(),
                                        file_name=file,
                                        key=f"download_{file}"
                                    )
                        
                        # Special handling for HTML report
                        html_files = [f for f in files if f.endswith('.html')]
                        if html_files:
                            st.subheader("📋 Report Preview")
                            selected_html = st.selectbox("Select HTML file to preview:", html_files)
                            if selected_html:
                                html_path = os.path.join(output_dir, selected_html)
                                with open(html_path, "r", encoding="utf-8") as f:
                                    html_content = f.read()
                                    st.components.v1.html(html_content, height=600, scrolling=True)
                
            else:
                st.error("❌ Research failed!")
                error_msg = st.session_state.job_results.get("error", "Unknown error")
                st.error(f"Error: {error_msg}")
        
        else:
            st.info("👋 Welcome! Enter your research parameters and click 'Start Research' to begin.")
        
        # Clear results button
        if st.session_state.job_results and not st.session_state.job_running:
            if st.button("🗑️ Clear Results"):
                st.session_state.job_results = None
                st.session_state.job_status = None
                st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center'>
            <p>🤖 Powered by RankX AI Research System | 
            Built with CrewAI, FastAPI & Streamlit</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()