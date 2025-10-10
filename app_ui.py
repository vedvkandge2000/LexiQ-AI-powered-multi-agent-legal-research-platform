#!/usr/bin/env python3
"""
LexiQ Streamlit UI
Multi-agent legal analysis interface with authentication and chat.
"""

import streamlit as st
from utils.case_similarity import CaseSimilarityAnalyzer
from agents.news_relevance_agent import NewsRelevanceAgent
from agents.statute_reference_agent import StatuteReferenceAgent
from agents.bench_bias_agent import BenchBiasAgent
from auth.user_manager import UserManager
from chat.chat_manager import ChatManager
from security.security_enforcer import SecurityEnforcer
from security.hallucination_detector import HallucinationDetector
from utils.retriever import LegalDocumentRetriever
from aws.bedrock_client import BedrockClient


# Page config
st.set_page_config(
    page_title="LexiQ - AI Legal Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .agent-header {
        font-size: 1.8rem;
        color: #2c3e50;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 1rem 2rem;
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
    st.session_state.case_analyzer = None
    st.session_state.results = None
    st.session_state.logged_in = False
    st.session_state.user_info = None
    st.session_state.current_chat_session = None
    st.session_state.chat_messages = []
    st.session_state.user_manager = UserManager()
    st.session_state.security_enforcer = SecurityEnforcer()
    st.session_state.case_text_for_chat = None


def show_auth_page():
    """Show login/register page."""
    st.markdown('<div class="main-header">⚖️ LexiQ - AI Legal Assistant</div>', 
                unsafe_allow_html=True)
    st.markdown("### Welcome! Please log in or create an account")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if not username or not password:
                    st.error("Please enter both username and password")
                else:
                    user = st.session_state.user_manager.authenticate(username, password)
                    
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user_info = user
                        st.success(f"Welcome back, {user['full_name']}!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
    
    with tab2:
        st.subheader("Create Account")
        with st.form("register_form"):
            new_username = st.text_input("Username", key="reg_username")
            new_email = st.text_input("Email", key="reg_email")
            new_full_name = st.text_input("Full Name", key="reg_name")
            new_password = st.text_input("Password", type="password", key="reg_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")
            role = st.selectbox("I am a:", ["user", "lawyer", "student"], key="reg_role")
            
            submit_reg = st.form_submit_button("Register")
            
            if submit_reg:
                if not all([new_username, new_email, new_password, confirm_password]):
                    st.error("Please fill all fields")
                elif new_password != confirm_password:
                    st.error("Passwords don't match")
                elif len(new_password) < 8:
                    st.error("Password must be at least 8 characters")
                else:
                    result = st.session_state.user_manager.register(
                        username=new_username,
                        password=new_password,
                        email=new_email,
                        full_name=new_full_name,
                        role=role
                    )
                    
                    if result['success']:
                        st.success("Account created successfully! Please log in.")
                    else:
                        st.error(result.get('error', 'Registration failed'))


def initialize_agents():
    """Initialize all agents."""
    if not st.session_state.initialized:
        with st.spinner("🔧 Initializing AI agents..."):
            try:
                st.session_state.case_analyzer = CaseSimilarityAnalyzer(
                    vector_store_dir="data/vector_store"
                )
                st.session_state.case_analyzer.initialize()
                st.session_state.news_agent = NewsRelevanceAgent(max_results=5, period='7d')
                st.session_state.statute_agent = StatuteReferenceAgent()
                st.session_state.bench_agent = BenchBiasAgent()
                
                # Initialize chat manager
                bedrock = BedrockClient()
                retriever = LegalDocumentRetriever(vector_store_dir="data/vector_store")
                retriever.load_vector_store()
                st.session_state.chat_manager = ChatManager(
                    bedrock_client=bedrock,
                    retriever=retriever
                )
                st.session_state.hallucination_detector = HallucinationDetector(retriever=retriever)
                
                st.session_state.initialized = True
                st.success("✅ All agents ready!")
            except Exception as e:
                st.error(f"❌ Error initializing agents: {e}")
                return False
    return True


def show_chat_tab():
    """Show chat interface tab."""
    st.markdown('<div class="agent-header">💬 Conversational Case Discussion</div>', 
               unsafe_allow_html=True)
    
    # Check if chat session exists
    if not st.session_state.current_chat_session:
        st.info("👆 Click 'Start Chat' button after analyzing your case to begin a conversation")
        return
    
    # Display chat
    session_id = st.session_state.current_chat_session
    session = st.session_state.chat_manager.storage.get_session(session_id)
    
    if not session:
        st.error("Chat session not found")
        return
    
    st.caption(f"Session started: {session['created_at']}")
    
    # Load messages if not in session state
    if not st.session_state.chat_messages:
        messages = st.session_state.chat_manager.get_chat_history(session_id)
        st.session_state.chat_messages = messages
    
    # Display messages
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg['role']):
            st.markdown(msg['content'])
            
            # Show precedents used
            if msg['role'] == 'assistant' and msg.get('metadata', {}).get('citations'):
                with st.expander("📚 Precedents Referenced"):
                    for cite in msg['metadata']['citations']:
                        st.write(f"• {cite}")
    
    # Chat input
    user_input = st.chat_input("Ask a question about the case...")
    
    if user_input:
        # Add user message
        st.session_state.chat_messages.append({
            'role': 'user',
            'content': user_input
        })
        
        # Get response
        with st.spinner("Thinking..."):
            result = st.session_state.chat_manager.send_message(
                session_id=session_id,
                user_message=user_input
            )
            
            if result['success']:
                # Add assistant response
                st.session_state.chat_messages.append({
                    'role': 'assistant',
                    'content': result['response'],
                    'metadata': {'citations': result['precedent_citations']}
                })
                st.rerun()


def main():
    """Main Streamlit application."""
    
    # Check authentication
    if not st.session_state.logged_in:
        show_auth_page()
        return
    
    # Header
    st.markdown('<div class="main-header">⚖️ LexiQ - AI-Powered Legal Assistant</div>', 
                unsafe_allow_html=True)
    st.markdown("---")
    
    # Initialize agents
    if not initialize_agents():
        st.stop()
    
    # Sidebar - Input
    with st.sidebar:
        # User info
        if st.session_state.user_info:
            st.markdown("---")
            st.markdown(f"**👤 {st.session_state.user_info['full_name']}**")
            st.caption(f"Role: {st.session_state.user_info['role']}")
            
            if st.button("Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.user_info = None
                st.session_state.initialized = False
                st.rerun()
            
            st.markdown("---")
        st.header("📝 Case Input")
        
        input_method = st.radio(
            "Input Method:",
            ["Text Input", "File Upload (Coming Soon)"],
            index=0
        )
        
        if input_method == "Text Input":
            case_text = st.text_area(
                "Enter your case description:",
                height=300,
                placeholder="Describe the case facts, legal issues, parties involved, etc..."
            )
        else:
            st.info("File upload feature coming soon!")
            case_text = ""
        
        st.markdown("---")
        
        # Agent Configuration
        st.header("🤖 Enable Agents")
        
        enable_precedents = st.checkbox("Precedent Analysis (Main)", value=True, disabled=True)
        enable_statutes = st.checkbox("Statute Reference", value=True)
        enable_news = st.checkbox("News Relevance", value=True)
        enable_bench = st.checkbox("Bench Bias", value=True)
        
        st.markdown("---")
        
        # Parameters
        st.header("⚙️ Parameters")
        k_precedents = st.slider("Number of precedents:", 1, 10, 5)
        
        st.markdown("---")
        
        # Analyze button
        analyze_btn = st.button("🔍 Analyze Case", type="primary", use_container_width=True)
    
    # Main content - Tabs
    if analyze_btn:
        if not case_text.strip():
            st.warning("⚠️ Please enter case text first!")
            return
        
        # Security check
        with st.spinner("🔒 Running security checks..."):
            security_result = st.session_state.security_enforcer.process_case_input(
                case_text=case_text,
                user_id=st.session_state.user_info['username']
            )
            
            if not security_result['success']:
                st.error(f"Security check failed: {security_result['error']}")
                return
            
            # PII warning
            if security_result['security_metadata']['pii_detected']:
                st.warning(f"⚠️ {security_result['security_metadata']['num_redactions']} PII items were redacted for privacy")
            
            safe_case_text = security_result['processed_text']
            st.session_state.case_text_for_chat = safe_case_text
        
        # Run analysis
        with st.spinner("🤖 Analyzing your case with AI agents..."):
            try:
                results = {}
                
                # 1. Precedent Analysis
                with st.spinner("Analyzing precedents..."):
                    precedent_result = st.session_state.case_analyzer.analyze_case_from_text(
                        safe_case_text, k=k_precedents, max_tokens=2000
                    )
                    results['precedents'] = precedent_result
                    
                    # Check for hallucinations in analysis
                    hallucination_check = st.session_state.hallucination_detector.detect_hallucinations(
                        input_query=case_text,
                        output_text=precedent_result['analysis'],
                        user_id=st.session_state.user_info['username']
                    )
                    results['hallucination_check'] = hallucination_check
                
                # 2. Statute Analysis
                if enable_statutes:
                    with st.spinner("Extracting statutes..."):
                        statute_result = st.session_state.statute_agent.analyze_statutes(
                            safe_case_text, max_tokens=1500
                        )
                        results['statutes'] = statute_result
                
                # 3. News Analysis
                if enable_news:
                    with st.spinner("Searching relevant news..."):
                        news_result = st.session_state.news_agent.find_relevant_news(
                            safe_case_text, max_tokens=1500
                        )
                        results['news'] = news_result
                
                # 4. Bench Bias
                if enable_bench and 'similar_cases' in precedent_result:
                    with st.spinner("Analyzing judicial patterns..."):
                        bench_result = st.session_state.bench_agent.analyze_bench_from_cases(
                            precedent_result['similar_cases'], max_tokens=1500
                        )
                        results['bench'] = bench_result
                
                st.session_state.results = results
                st.success("✅ Analysis complete!")
                
            except Exception as e:
                st.error(f"❌ Error during analysis: {e}")
                import traceback
                st.code(traceback.format_exc())
    
    # Display results in tabs
    if st.session_state.results:
        results = st.session_state.results
        
        tabs = []
        if 'precedents' in results:
            tabs.append("🏛️ Precedents")
        if 'statutes' in results:
            tabs.append("⚖️ Statutes")
        if 'news' in results:
            tabs.append("📰 News")
        if 'bench' in results:
            tabs.append("👨‍⚖️ Bench")
        tabs.append("💬 Chat")  # Always add Chat tab
        
        tab_objects = st.tabs(tabs)
        
        # Tab 1: Precedents
        if 'precedents' in results:
            with tab_objects[0]:
                st.markdown('<div class="agent-header">Precedent Analysis</div>', 
                           unsafe_allow_html=True)
                
                prec = results['precedents']
                
                # Metrics
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Similar Cases Found", prec['num_similar_cases'])
                with col2:
                    st.metric("Vector Store", "FAISS")
                
                st.markdown("---")
                
                # Hallucination check warning
                if results.get('hallucination_check', {}).get('has_hallucinations'):
                    st.warning(f"⚠️ {results['hallucination_check']['num_suspected']} reference(s) could not be verified")
                
                # Analysis
                st.markdown("### 📊 AI Analysis")
                st.markdown(prec['analysis'])
                
                # Start Chat button
                st.markdown("---")
                if st.button("💬 Start Chat About This Case", use_container_width=True, key="start_chat_btn"):
                    # Create new chat session
                    try:
                        chat_result = st.session_state.chat_manager.start_new_chat(
                            user_id=st.session_state.user_info['username'],
                            case_text=st.session_state.case_text_for_chat,
                            case_title=st.session_state.case_text_for_chat[:100],
                            similar_cases=prec.get('similar_cases', [])
                        )
                        
                        if chat_result['success']:
                            st.session_state.current_chat_session = chat_result['session_id']
                            st.session_state.chat_messages = []
                            st.success("✅ Chat session started! Switch to 'Chat' tab to continue.")
                    except Exception as e:
                        st.error(f"Failed to start chat: {e}")
                
                st.markdown("---")
                
                # Similar cases
                st.markdown("### 📚 Similar Cases Reference")
                for i, case in enumerate(prec['similar_cases'], 1):
                    with st.expander(f"Case {i}: {case['case_title']}"):
                        st.write(f"**Citation:** {case['citation']}")
                        st.write(f"**Case Number:** {case['case_number']}")
                        st.write(f"**Page:** {case.get('page_number', 'N/A')}")
                        if case['s3_url']:
                            # Convert S3 URL to direct HTTPS URL
                            try:
                                # Convert s3://bucket/key to https://bucket.s3.amazonaws.com/key
                                if case['s3_url'].startswith('s3://'):
                                    s3_path = case['s3_url'][5:]  # Remove 's3://'
                                    bucket, key = s3_path.split('/', 1)
                                    direct_url = f"https://{bucket}.s3.amazonaws.com/{key}"
                                    st.markdown(f"[📄 View PDF]({direct_url})")
                                else:
                                    # Already in HTTPS format
                                    st.markdown(f"[📄 View PDF]({case['s3_url']})")
                            except Exception as e:
                                st.write(f"📄 PDF available (URL error: {str(e)[:50]}...)")
        
        # Tab 2: Statutes
        if 'statutes' in results:
            tab_idx = 1 if 'precedents' in results else 0
            with tab_objects[tab_idx]:
                st.markdown('<div class="agent-header">Statute Reference</div>', 
                           unsafe_allow_html=True)
                
                stat = results['statutes']
                
                # Metrics
                st.metric("Legal Provisions Found", stat['num_provisions'])
                
                if stat['num_provisions'] > 0:
                    st.markdown("---")
                    
                    # Extracted provisions
                    st.markdown("### 📋 Extracted Provisions")
                    for prov in stat['provisions_list']:
                        st.write(f"- {prov}")
                    
                    st.markdown("---")
                    
                    # Explanations
                    st.markdown("### 📖 Plain-English Explanations")
                    st.markdown(stat['explanation'])
                else:
                    st.info("No specific legal provisions were identified in the case text.")
        
        # Tab 3: News
        if 'news' in results:
            tab_idx = len([k for k in ['precedents', 'statutes'] if k in results])
            with tab_objects[tab_idx]:
                st.markdown('<div class="agent-header">News Relevance</div>', 
                           unsafe_allow_html=True)
                
                news = results['news']
                
                # Metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Articles Found", news['num_articles'])
                with col2:
                    st.metric("Keywords Used", len(news.get('keywords', [])))
                with col3:
                    st.metric("Time Period", "7 days")
                
                st.markdown("---")
                
                # Keywords
                if news.get('keywords'):
                    st.markdown("### 🔑 Search Keywords")
                    st.write(", ".join(news['keywords']))
                    st.markdown("---")
                
                # Analysis
                st.markdown("### 📊 News Analysis")
                st.markdown(news['analysis'])
                
                # Articles
                if news.get('articles'):
                    st.markdown("---")
                    st.markdown("### 📰 Articles")
                    for i, article in enumerate(news['articles'], 1):
                        with st.expander(f"{i}. {article['title']}"):
                            st.write(f"**Publisher:** {article['publisher']}")
                            st.write(f"**Published:** {article['published_date']}")
                            st.write(f"**Description:** {article['description']}")
                            st.markdown(f"[🔗 Read Article]({article['url']})")
        
        # Tab 4: Bench
        if 'bench' in results:
            tab_idx = len([k for k in ['precedents', 'statutes', 'news'] if k in results])
            with tab_objects[tab_idx]:
                st.markdown('<div class="agent-header">Bench Bias Analysis</div>', 
                           unsafe_allow_html=True)
                
                bench = results['bench']
                
                # Metrics
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Judges Analyzed", bench['num_judges'])
                with col2:
                    if bench.get('top_judges'):
                        st.metric("Most Active Judge", bench['top_judges'][0])
                
                st.markdown("---")
                
                # Analysis
                st.markdown("### 📊 Judicial Pattern Analysis")
                st.markdown(bench['analysis'])
                
                # Judge statistics
                if bench.get('judges'):
                    st.markdown("---")
                    st.markdown("### 📈 Judge Statistics")
                    judge_data = []
                    for judge, info in bench['judges'].items():
                        judge_data.append({
                            'Judge': judge,
                            'Cases': info['num_cases']
                        })
                    
                    import pandas as pd
                    df = pd.DataFrame(judge_data).sort_values('Cases', ascending=False)
                    st.dataframe(df, use_container_width=True)
        
        # Tab 5: Chat
        chat_tab_idx = len([k for k in ['precedents', 'statutes', 'news', 'bench'] if k in results])
        with tab_objects[chat_tab_idx]:
            show_chat_tab()
        
        # Download button
        st.markdown("---")
        if st.button("💾 Download Complete Report", use_container_width=True):
            report = generate_report(results, case_text if 'case_text' in locals() else st.session_state.case_text_for_chat)
            st.download_button(
                label="📥 Download Markdown Report",
                data=report,
                file_name="lexiq_analysis.md",
                mime="text/markdown"
            )


def generate_report(results: dict, case_text: str) -> str:
    """Generate downloadable markdown report."""
    report = "# LexiQ Legal Analysis Report\n\n"
    report += "## Case Description\n\n"
    report += case_text[:1000] + ("..." if len(case_text) > 1000 else "")
    report += "\n\n---\n\n"
    
    if 'precedents' in results:
        report += "## Precedent Analysis\n\n"
        report += results['precedents']['analysis']
        report += "\n\n---\n\n"
    
    if 'statutes' in results:
        report += "## Statute Reference\n\n"
        report += results['statutes']['explanation']
        report += "\n\n---\n\n"
    
    if 'news' in results:
        report += "## News Relevance\n\n"
        report += results['news']['analysis']
        report += "\n\n---\n\n"
    
    if 'bench' in results:
        report += "## Bench Bias Analysis\n\n"
        report += results['bench']['analysis']
        report += "\n\n"
    
    return report


if __name__ == "__main__":
    main()

