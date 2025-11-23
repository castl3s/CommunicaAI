import streamlit as st
import streamlit.components.v1 as components
import base64
from datetime import datetime
import json

def main():
    # Page configuration
    st.set_page_config(
        page_title="CommunicaAI Assistant",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 300;
        color: #161616;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #525252;
        margin-bottom: 2rem;
    }
    .chat-container {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        height: 700px;
        background: white;
    }
    .info-box {
        background: #f0f9ff;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #0062ff;
        margin: 1rem 0;
    }
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }
    .feature-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        text-align: center;
    }
    .stButton button {
        border-radius: 6px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if "chat_loaded" not in st.session_state:
        st.session_state.chat_loaded = False
    
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 2rem;">
            <div style="width: 32px; height: 32px; background: linear-gradient(135deg, #0062ff, #00d4aa); 
                     border-radius: 6px; display: flex; align-items: center; justify-content: center; 
                     color: white; font-weight: bold; font-size: 14px;">CAI</div>
            <div style="font-size: 18px; font-weight: 600; color: #161616;">CommunicaAI</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🎯 AI Assistant")
        st.button("💬 Chat", use_container_width=True, type="primary")
        st.button("⚙️ Settings", use_container_width=True)
        st.button("📊 Analytics", use_container_width=True)
        
        st.markdown("---")
        st.markdown("### 🔧 Configuration")
        
        with st.expander("Deployment Info", expanded=True):
            st.markdown("""
            **Platform:** IBM Watson Orchestrate
            **Status:** 🟢 Connected
            **Agent:** CommunicaAI
            **Environment:** Production
            """)
            
            if st.button("🔄 Refresh Chat", use_container_width=True):
                st.session_state.chat_loaded = False
                st.rerun()
        
        st.markdown("---")
        st.markdown("### 📋 Quick Actions")
        
        if st.button("🗑️ Clear Session", use_container_width=True):
            st.session_state.chat_loaded = False
            st.rerun()
            
        if st.button("📖 Documentation", use_container_width=True):
            st.info("Opening documentation...")
    
    # Main content area
    st.markdown('<div class="main-header">CommunicaAI Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Powered by IBM Watsonx Orchestrate with advanced communication capabilities</div>', unsafe_allow_html=True)
    
    # Feature highlights
    st.markdown("""
    <div class="feature-grid">
        <div class="feature-card">
            <div style="font-size: 2rem;">💬</div>
            <div style="font-weight: 600;">Smart Chat</div>
            <div style="font-size: 0.8rem; color: #666;">Natural conversations</div>
        </div>
        <div class="feature-card">
            <div style="font-size: 2rem;">🌐</div>
            <div style="font-weight: 600;">Multi-language</div>
            <div style="font-size: 0.8rem; color: #666;">Translation support</div>
        </div>
        <div class="feature-card">
            <div style="font-size: 2rem;">📝</div>
            <div style="font-weight: 600;">Content Creation</div>
            <div style="font-size: 0.8rem; color: #666;">Writing assistance</div>
        </div>
        <div class="feature-card">
            <div style="font-size: 2rem;">🔊</div>
            <div style="font-weight: 600;">Voice Ready</div>
            <div style="font-size: 0.8rem; color: #666;">Audio capabilities</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Information box
    st.markdown("""
    <div class="info-box">
        <h4>🚀 Ready to Chat!</h4>
        <p>This assistant is powered by IBM Watsonx Orchestrate with the CommunicaAI agent. 
        You can ask about communication strategies, content creation, translations, and more.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Watson Orchestrate Chat Embed
    st.markdown("### 💬 Chat with CommunicaAI")
    
    # Create the Watson Orchestrate embed code
    watson_orchestrate_embed = """
    <script>
    window.wxOConfiguration = {
        orchestrationID: "6d0cb62cc8d140a099412fb3f764e334_ca184c97-b115-44bf-901e-10adc85c71df",
        hostURL: "https://ca-tor.watson-orchestrate.cloud.ibm.com",
        rootElementID: "wxochat-root",
        deploymentPlatform: "ibmcloud",
        crn: "crn:v1:bluemix:public:watsonx-orchestrate:ca-tor:a/6d0cb62cc8d140a099412fb3f764e334:ca184c97-b115-44bf-901e-10adc85c71df::",
        chatOptions: {
            agentId: "b9c59d96-f740-4b5e-9b9d-1e49bb083750",
            agentEnvironmentId: "03fd4b11-7bd2-4e72-8fc0-14ee1a9430bc",
        }
    };
    
    setTimeout(function () {
        const script = document.createElement('script');
        script.src = `${window.wxOConfiguration.hostURL}/wxochat/wxoLoader.js?embed=true`;
        script.addEventListener('load', function () {
            if (typeof wxoLoader !== 'undefined') {
                wxoLoader.init();
            }
        });
        document.head.appendChild(script);
    }, 0);
    </script>
    
    <style>
    #wxochat-root {
        width: 100%;
        height: 600px;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        background: white;
    }
    
    /* Custom styling for Watson Orchestrate chat */
    .wxo-chat-container {
        border-radius: 10px !important;
    }
    
    /* Loading state */
    .chat-loading {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 600px;
        background: #f8f9fa;
        border-radius: 10px;
        color: #666;
        font-size: 1.1rem;
    }
    </style>
    
    <div id="wxochat-root">
        <div class="chat-loading">
            <div>Loading CommunicaAI Assistant...</div>
        </div>
    </div>
    
    <script>
    // Add error handling for chat loading
    setTimeout(function() {
        const chatRoot = document.getElementById('wxochat-root');
        if (chatRoot && chatRoot.children.length <= 1) {
            // Chat didn't load properly
            chatRoot.innerHTML = `
                <div class="chat-loading">
                    <div>
                        <div style="font-size: 2rem; margin-bottom: 1rem;">🤖</div>
                        <div>CommunicaAI Assistant</div>
                        <div style="font-size: 0.9rem; color: #888; margin-top: 0.5rem;">
                            If chat doesn't load, please refresh the page
                        </div>
                    </div>
                </div>
            `;
        }
    }, 5000);
    </script>
    """
    
    # Render the chat component
    with st.container():
        components.html(watson_orchestrate_embed, height=650)
    
    # Additional information and controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Reload Chat Interface", use_container_width=True):
            st.session_state.chat_loaded = False
            st.rerun()
    
    with col2:
        if st.button("📋 Conversation Tips", use_container_width=True):
            st.info("""
            **💡 Conversation Tips:**
            - Ask about communication strategies
            - Request content creation help
            - Get translation assistance
            - Discuss presentation ideas
            - Seek writing guidance
            """)
    
    with col3:
        if st.button("🔧 Troubleshoot", use_container_width=True):
            st.markdown("""
            **🛠️ If chat isn't loading:**
            1. Refresh the page
            2. Check your internet connection
            3. Ensure JavaScript is enabled
            4. Try a different browser
            5. Contact support if issues persist
            """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        <p>Powered by <strong>IBM Watsonx Orchestrate</strong> • CommunicaAI Assistant v2.0</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()