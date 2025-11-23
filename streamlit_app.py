import streamlit as st
import streamlit.components.v1 as components
import time

def create_watson_orchestrate_embed(theme="light", height=600):
    """Create Watson Orchestrate embed code with customizable options"""
    
    embed_code = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CommunicaAI Chat</title>
        <style>
            body {{
                margin: 0;
                padding: 0;
                font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, sans-serif;
                background: {'#ffffff' if theme == 'light' else '#1e1e1e'};
            }}
            #wxochat-root {{
                width: 100%;
                height: {height}px;
                border: 1px solid {'#e0e0e0' if theme == 'light' else '#444'};
                border-radius: 10px;
                background: {'#ffffff' if theme == 'light' : '#2d2d2d'};
            }}
            .loading-container {{
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                height: 100%;
                background: {'#f8f9fa' if theme == 'light' : '#1e1e1e'};
                color: {'#666' if theme == 'light' : '#ccc'};
                border-radius: 10px;
            }}
            .loading-spinner {{
                border: 3px solid {'#f3f3f3' if theme == 'light' : '#444'};
                border-top: 3px solid #0062ff;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin-bottom: 1rem;
            }}
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
        </style>
    </head>
    <body>
        <div id="wxochat-root">
            <div class="loading-container">
                <div class="loading-spinner"></div>
                <div>Initializing CommunicaAI Assistant...</div>
            </div>
        </div>

        <script>
        // Watson Orchestrate Configuration
        window.wxOConfiguration = {{
            orchestrationID: "6d0cb62cc8d140a099412fb3f764e334_ca184c97-b115-44bf-901e-10adc85c71df",
            hostURL: "https://ca-tor.watson-orchestrate.cloud.ibm.com",
            rootElementID: "wxochat-root",
            deploymentPlatform: "ibmcloud",
            crn: "crn:v1:bluemix:public:watsonx-orchestrate:ca-tor:a/6d0cb62cc8d140a099412fb3f764e334:ca184c97-b115-44bf-901e-10adc85c71df::",
            chatOptions: {{
                agentId: "b9c59d96-f740-4b5e-9b9d-1e49bb083750",
                agentEnvironmentId: "03fd4b11-7bd2-4e72-8fc0-14ee1a9430bc",
            }}
        }};

        // Load Watson Orchestrate
        function loadWatsonOrchestrate() {{
            const script = document.createElement('script');
            script.src = `${{window.wxOConfiguration.hostURL}}/wxochat/wxoLoader.js?embed=true`;
            script.onload = function() {{
                if (typeof wxoLoader !== 'undefined') {{
                    wxoLoader.init();
                }}
            }};
            script.onerror = function() {{
                document.getElementById('wxochat-root').innerHTML = `
                    <div class="loading-container">
                        <div style="color: #dc3545; margin-bottom: 1rem;">⚠️</div>
                        <div>Failed to load chat interface</div>
                        <div style="font-size: 0.8rem; margin-top: 0.5rem;">Please check your connection and refresh</div>
                    </div>
                `;
            }};
            document.head.appendChild(script);
        }}

        // Start loading
        setTimeout(loadWatsonOrchestrate, 100);

        // Fallback if chat doesn't load
        setTimeout(function() {{
            const chatRoot = document.getElementById('wxochat-root');
            if (chatRoot) {{
                const hasChat = chatRoot.querySelector('.wxo-chat-container');
                if (!hasChat) {{
                    chatRoot.innerHTML = `
                        <div class="loading-container">
                            <div style="color: #f1c21b; margin-bottom: 1rem;">⏳</div>
                            <div>Taking longer than expected...</div>
                            <button onclick="window.location.reload()" style="
                                margin-top: 1rem;
                                padding: 0.5rem 1rem;
                                background: #0062ff;
                                color: white;
                                border: none;
                                border-radius: 5px;
                                cursor: pointer;
                            ">Refresh Page</button>
                        </div>
                    `;
                }}
            }}
        }}, 10000);
        </script>
    </body>
    </html>
    """
    
    return embed_code

def main_enhanced():
    """Enhanced version with more features"""
    
    st.set_page_config(
        page_title="CommunicaAI Orchestrate",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .header-container {
        background: linear-gradient(135deg, #0062ff, #00d4aa);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🤖</div>
            <div style="font-size: 1.5rem; font-weight: bold;">CommunicaAI</div>
            <div style="color: #666; font-size: 0.9rem;">Watsonx Orchestrate</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### Configuration")
        
        # Theme selector
        theme = st.selectbox(
            "Chat Theme",
            ["light", "dark"],
            index=0,
            help="Choose the chat interface theme"
        )
        
        # Height selector
        height = st.slider(
            "Chat Height",
            min_value=400,
            max_value=800,
            value=600,
            step=50,
            help="Adjust the chat window height"
        )
        
        st.markdown("---")
        st.markdown("### Quick Actions")
        
        if st.button("🔄 Reload Chat", use_container_width=True):
            st.rerun()
            
        if st.button("📊 View Analytics", use_container_width=True):
            st.info("Analytics dashboard coming soon!")
            
        if st.button("🔧 Settings", use_container_width=True):
            st.info("Settings panel coming soon!")
    
    # Main content
    st.markdown("""
    <div class="header-container">
        <h1 style="color: white; margin: 0;">CommunicaAI Assistant</h1>
        <p style="color: white; opacity: 0.9; margin: 0;">Powered by IBM Watsonx Orchestrate</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 2rem; color: #0062ff;">💬</div>
            <h4>Smart Conversations</h4>
            <p style="color: #666; font-size: 0.9rem;">Natural dialogue with context awareness</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 2rem; color: #00d4aa;">🌐</div>
            <h4>Multi-language</h4>
            <p style="color: #666; font-size: 0.9rem;">Translation and localization support</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 2rem; color: #ff6b6b;">📝</div>
            <h4>Content Creation</h4>
            <p style="color: #666; font-size: 0.9rem;">Writing assistance and ideation</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Chat interface
    st.markdown("### 💬 Chat Interface")
    
    with st.spinner("Loading CommunicaAI Assistant..."):
        embed_code = create_watson_orchestrate_embed(theme=theme, height=height)
        components.html(embed_code, height=height + 50)
    
    # Additional controls
    st.markdown("---")
    st.markdown("### 🔧 Controls")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Force Refresh", key="force_refresh"):
            st.success("Refreshing chat interface...")
            time.sleep(1)
            st.rerun()
    
    with col2:
        if st.button("📋 Copy Config", key="copy_config"):
            config = {
                "orchestrationID": "6d0cb62cc8d140a099412fb3f764e334_ca184c97-b115-44bf-901e-10adc85c71df",
                "agentId": "b9c59d96-f740-4b5e-9b9d-1e49bb083750",
                "agentEnvironmentId": "03fd4b11-7bd2-4e72-8fc0-14ee1a9430bc"
            }
            st.code(json.dumps(config, indent=2), language="json")
    
    with col3:
        if st.button("ℹ️ Help", key="help"):
            st.markdown("""
            **Need Help?**
            - Ensure JavaScript is enabled
            - Check your internet connection
            - Refresh if chat doesn't load
            - Contact support for persistent issues
            """)

if __name__ == "__main__":
    # Run the enhanced version
    main_enhanced()