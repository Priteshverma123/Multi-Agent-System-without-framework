# app.py

import streamlit as st
from agents import AgentManager
from utils.logger import logger
import os
from dotenv import load_dotenv
import json
import re

# Load environment variables from .env if present
load_dotenv()

def extract_content(response):
    """
    Extract clean content from agent response, handling various formats
    """
    if isinstance(response, str):
        # Try to parse as JSON if it looks like JSON
        if response.strip().startswith('{') and response.strip().endswith('}'):
            try:
                parsed = json.loads(response)
                if 'content' in parsed:
                    return parsed['content']
                else:
                    return response
            except json.JSONDecodeError:
                return response
        else:
            return response
    elif isinstance(response, dict):
        # If it's already a dict, extract content
        if 'content' in response:
            return response['content']
        else:
            return str(response)
    else:
        return str(response)

def main():
    st.set_page_config(
        page_title="Multi-Agent AI System", 
        layout="wide",
        initial_sidebar_state="expanded",
        page_icon="🤖"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main > div {
        padding-top: 2rem;
    }
    
    .stTitle {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem !important;
        font-weight: 700 !important;
        text-align: center;
        margin-bottom: 2rem !important;
    }
    
    .task-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
    }
    
    .task-card h2 {
        color: white !important;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    .success-box {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    
    .info-box {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    .stSelectbox > div > div {
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        transition: border-color 0.3s ease;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
    }
    
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        transition: border-color 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        margin: 0.5rem 0;
        border-left: 5px solid #667eea;
    }
    
    .step-indicator {
        display: flex;
        align-items: center;
        margin: 1rem 0;
        padding: 0.5rem;
        background: rgba(102, 126, 234, 0.1);
        border-radius: 10px;
        border-left: 4px solid #667eea;
    }
    
    .result-section {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        border-top: 4px solid #667eea;
    }
    </style>
    """, unsafe_allow_html=True)

    # Header with icon and title
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 class="stTitle">🤖 Multi-Agent AI System</h1>
        <p style="font-size: 1.2rem; color: #666; margin-top: -1rem;">
            Intelligent Collaboration • Automated Validation • Enhanced Productivity
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Enhanced sidebar
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 10px; margin-bottom: 1rem; color: white;">
            <h2 style="color: white; margin: 0;">🎯 Task Selection</h2>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Choose your AI-powered task</p>
        </div>
        """, unsafe_allow_html=True)
        
        task = st.selectbox("", [
            "📄 Summarize Medical Text",
            "✍️ Write and Refine Research Article",
            "🔒 Sanitize Medical Data (PHI)"
        ], label_visibility="collapsed")
        
        st.markdown("---")
        st.markdown("""
        <div style="background: rgba(102, 126, 234, 0.1); padding: 1rem; border-radius: 10px; margin-top: 1rem;">
            <h4 style="color: #667eea; margin-top: 0;">✨ Features</h4>
            <ul style="color: #666; font-size: 0.9rem;">
                <li>Multi-agent collaboration</li>
                <li>Automated validation</li>
                <li>Real-time processing</li>
                <li>Error handling & logging</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    agent_manager = AgentManager(max_retries=2, verbose=True)

    if "📄 Summarize Medical Text" in task:
        summarize_section(agent_manager)
    elif "✍️ Write and Refine Research Article" in task:
        write_and_refine_article_section(agent_manager)
    elif "🔒 Sanitize Medical Data (PHI)" in task:
        sanitize_data_section(agent_manager)

def summarize_section(agent_manager):
    st.markdown("""
    <div class="task-card">
        <h2>📄 Medical Text Summarization</h2>
        <p style="margin: 0; opacity: 0.9;">Transform lengthy medical texts into concise, accurate summaries with AI-powered analysis and validation.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📝 Input Medical Text")
        text = st.text_area(
            "Enter the medical text you want to summarize:",
            height=200,
            placeholder="Paste your medical text here...",
            help="Enter any medical document, research paper, or clinical text that needs summarization."
        )
    
    with col2:
        st.markdown("### 📊 Process Overview")
        st.markdown("""
        <div class="step-indicator">
            <span style="margin-right: 10px;">1️⃣</span>
            <span>AI Analysis & Summarization</span>
        </div>
        <div class="step-indicator">
            <span style="margin-right: 10px;">2️⃣</span>
            <span>Validation & Quality Check</span>
        </div>
        <div class="step-indicator">
            <span style="margin-right: 10px;">3️⃣</span>
            <span>Final Summary Delivery</span>
        </div>
        """, unsafe_allow_html=True)
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    with col_btn2:
        summarize_btn = st.button("🚀 Generate Summary", use_container_width=True)
    
    if summarize_btn:
        if text:
            main_agent = agent_manager.get_agent("summarize")
            validator_agent = agent_manager.get_agent("summarize_validator")
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            with st.spinner("🔍 Analyzing and summarizing your text..."):
                progress_bar.progress(30)
                status_text.text("Processing with AI summarization agent...")
                try:
                    summary = main_agent.execute(text)
                    progress_bar.progress(70)
                    
                    st.markdown("""
                    <div class="result-section">
                        <h3 style="color: #667eea; margin-top: 0;">📋 Generated Summary</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Extract content if it's in JSON format
                    display_content = extract_content(summary)
                    st.text_area(
                        "Summary Result:",
                        value=display_content,
                        height=300,
                        help="You can copy this content by selecting all text (Ctrl+A) and copying (Ctrl+C)",
                        key="summary_result"
                    )
                    
                except Exception as e:
                    st.error(f"❌ Error during summarization: {e}")
                    logger.error(f"SummarizeAgent Error: {e}")
                    return

            with st.spinner("✅ Validating summary quality..."):
                progress_bar.progress(90)
                status_text.text("Running validation checks...")
                try:
                    validation = validator_agent.execute(original_text=text, summary=summary)
                    progress_bar.progress(100)
                    status_text.text("✅ Process completed successfully!")
                    
                    st.markdown("""
                    <div class="result-section">
                        <h3 style="color: #11998e; margin-top: 0;">🔍 Quality Validation</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Extract content if it's in JSON format
                    display_validation = extract_content(validation)
                    st.text_area(
                        "Validation Result:",
                        value=display_validation,
                        height=200,
                        help="You can copy this content by selecting all text (Ctrl+A) and copying (Ctrl+C)",
                        key="summary_validation"
                    )
                    
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ Validation Error: {e}")
                    logger.error(f"SummarizeValidatorAgent Error: {e}")
        else:
            st.markdown("""
            <div class="warning-box">
                <strong>⚠️ Input Required</strong><br>
                Please enter some medical text to summarize before proceeding.
            </div>
            """, unsafe_allow_html=True)

def write_and_refine_article_section(agent_manager):
    st.markdown("""
    <div class="task-card">
        <h2>✍️ Research Article Writing & Refinement</h2>
        <p style="margin: 0; opacity: 0.9;">Create comprehensive research articles with AI-powered writing, refinement, and validation processes.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 🎯 Article Configuration")
        topic = st.text_input(
            "Research Topic:",
            placeholder="Enter your research topic here...",
            help="Be specific about your research focus for better results."
        )
        outline = st.text_area(
            "Article Outline (Optional):",
            height=150,
            placeholder="1. Introduction\n2. Literature Review\n3. Methodology\n4. Results\n5. Discussion\n6. Conclusion",
            help="Provide a structured outline to guide the article writing process."
        )
    
    with col2:
        st.markdown("### 🔄 Workflow Steps")
        st.markdown("""
        <div class="step-indicator">
            <span style="margin-right: 10px;">✏️</span>
            <span>Draft Creation</span>
        </div>
        <div class="step-indicator">
            <span style="margin-right: 10px;">🔧</span>
            <span>Content Refinement</span>
        </div>
        <div class="step-indicator">
            <span style="margin-right: 10px;">✅</span>
            <span>Quality Validation</span>
        </div>
        """, unsafe_allow_html=True)
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    with col_btn2:
        write_btn = st.button("📝 Create Article", use_container_width=True)
    
    if write_btn:
        if topic:
            writer_agent = agent_manager.get_agent("write_article")
            refiner_agent = agent_manager.get_agent("refiner")
            validator_agent = agent_manager.get_agent("validator")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            with st.spinner("✏️ Creating initial draft..."):
                progress_bar.progress(25)
                status_text.text("AI writer is crafting your article...")
                try:
                    draft = writer_agent.execute(topic, outline)
                    progress_bar.progress(50)
                    
                    st.markdown("""
                    <div class="result-section">
                        <h3 style="color: #667eea; margin-top: 0;">📝 Initial Draft</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Extract content if it's in JSON format
                    display_draft = extract_content(draft)
                    st.text_area(
                        "Article Draft:",
                        value=display_draft,
                        height=400,
                        help="You can copy this content by selecting all text (Ctrl+A) and copying (Ctrl+C)",
                        key="article_draft"
                    )
                    
                except Exception as e:
                    st.error(f"❌ Writing Error: {e}")
                    logger.error(f"WriteArticleAgent Error: {e}")
                    return

            with st.spinner("🔧 Refining and improving content..."):
                progress_bar.progress(75)
                status_text.text("Enhancing article quality and structure...")
                try:
                    refined_article = refiner_agent.execute(draft)
                    progress_bar.progress(90)
                    
                    st.markdown("""
                    <div class="result-section">
                        <h3 style="color: #f093fb; margin-top: 0;">🔧 Refined Article</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Extract content if it's in JSON format
                    display_refined = extract_content(refined_article)
                    st.text_area(
                        "Refined Article:",
                        value=display_refined,
                        height=500,
                        help="You can copy this content by selecting all text (Ctrl+A) and copying (Ctrl+C)",
                        key="refined_article"
                    )
                    
                except Exception as e:
                    st.error(f"❌ Refinement Error: {e}")
                    logger.error(f"RefinerAgent Error: {e}")
                    return

            with st.spinner("✅ Final validation and quality check..."):
                progress_bar.progress(95)
                status_text.text("Performing final quality assessment...")
                try:
                    validation = validator_agent.execute(topic=topic, article=refined_article)
                    progress_bar.progress(100)
                    status_text.text("🎉 Article creation completed successfully!")
                    
                    st.markdown("""
                    <div class="result-section">
                        <h3 style="color: #11998e; margin-top: 0;">✅ Quality Assessment</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Extract content if it's in JSON format
                    display_article_validation = extract_content(validation)
                    st.text_area(
                        "Validation Result:",
                        value=display_article_validation,
                        height=200,
                        help="You can copy this content by selecting all text (Ctrl+A) and copying (Ctrl+C)",
                        key="article_validation"
                    )
                    
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ Validation Error: {e}")
                    logger.error(f"ValidatorAgent Error: {e}")
        else:
            st.markdown("""
            <div class="warning-box">
                <strong>⚠️ Topic Required</strong><br>
                Please enter a research topic to begin the article creation process.
            </div>
            """, unsafe_allow_html=True)

def sanitize_data_section(agent_manager):
    st.markdown("""
    <div class="task-card">
        <h2>🔒 Medical Data Sanitization (PHI Protection)</h2>
        <p style="margin: 0; opacity: 0.9;">Protect patient privacy by automatically identifying and sanitizing Personal Health Information (PHI) from medical data.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🏥 Input Medical Data")
        medical_data = st.text_area(
            "Enter medical data containing PHI to sanitize:",
            height=200,
            placeholder="Patient records, clinical notes, or any medical data with PHI...",
            help="Input any medical data that may contain patient identifiable information."
        )
    
    with col2:
        st.markdown("### 🛡️ Privacy Protection")
        st.markdown("""
        <div class="info-box">
            <h4 style="color: white; margin-top: 0;">Protected Information:</h4>
            <ul style="margin: 0;">
                <li>Patient Names</li>
                <li>Social Security Numbers</li>
                <li>Medical Record Numbers</li>
                <li>Addresses & Phone Numbers</li>
                <li>Email Addresses</li>
                <li>Dates of Birth</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    with col_btn2:
        sanitize_btn = st.button("🛡️ Sanitize Data", use_container_width=True)
    
    if sanitize_btn:
        if medical_data:
            main_agent = agent_manager.get_agent("sanitize_data")
            validator_agent = agent_manager.get_agent("sanitize_data_validator")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            with st.spinner("🔍 Scanning and sanitizing PHI..."):
                progress_bar.progress(40)
                status_text.text("Identifying and removing sensitive information...")
                try:
                    sanitized_data = main_agent.execute(medical_data)
                    progress_bar.progress(70)
                    
                    st.markdown("""
                    <div class="result-section">
                        <h3 style="color: #667eea; margin-top: 0;">🛡️ Sanitized Data</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Extract content if it's in JSON format
                    display_sanitized = extract_content(sanitized_data)
                    st.text_area(
                        "Sanitized Data Result:",
                        value=display_sanitized,
                        height=300,
                        help="You can copy this content by selecting all text (Ctrl+A) and copying (Ctrl+C)",
                        key="sanitized_data"
                    )
                    
                except Exception as e:
                    st.error(f"❌ Sanitization Error: {e}")
                    logger.error(f"SanitizeDataAgent Error: {e}")
                    return

            with st.spinner("🔍 Validating sanitization completeness..."):
                progress_bar.progress(90)
                status_text.text("Verifying all PHI has been properly sanitized...")
                try:
                    validation = validator_agent.execute(original_data=medical_data, sanitized_data=sanitized_data)
                    progress_bar.progress(100)
                    status_text.text("✅ Data sanitization completed successfully!")
                    
                    st.markdown("""
                    <div class="result-section">
                        <h3 style="color: #11998e; margin-top: 0;">🔍 Sanitization Validation</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Extract content if it's in JSON format
                    display_sanitize_validation = extract_content(validation)
                    st.text_area(
                        "Validation Result:",
                        value=display_sanitize_validation,
                        height=200,
                        help="You can copy this content by selecting all text (Ctrl+A) and copying (Ctrl+C)",
                        key="sanitize_validation"
                    )
                    
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ Validation Error: {e}")
                    logger.error(f"SanitizeDataValidatorAgent Error: {e}")
        else:
            st.markdown("""
            <div class="warning-box">
                <strong>⚠️ Data Input Required</strong><br>
                Please enter medical data to sanitize before proceeding.
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()