import streamlit as st
import requests
import json
import time
from datetime import datetime
import base64

class CommunicaAI:
    def __init__(self):
        self.API_KEY = st.secrets.get("WATSON_API_KEY", "29b2c13f-14f4-436a-92c2-bfe5dcc7f8ff")
        self.SCORING_URL = "https://us-south.ml.cloud.ibm.com/ml/v4/deployments/9a25c432-dafa-4c43-b2ce-2eabd6aec8e5/ai_service_stream?version=2021-05-01"
        self.access_token = None
        self.is_connected = False
        
    def get_access_token(self):
        """Get IBM Cloud access token"""
        try:
            response = requests.post(
                "https://iam.cloud.ibm.com/identity/token",
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json"
                },
                data="grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey={self.API_KEY}"
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get("access_token")
                return True
            else:
                st.error(f"Failed to get access token: {response.status_code}")
                return False
                
        except Exception as e:
            st.error(f"Error getting access token: {str(e)}")
            return False
    
    def send_to_watson(self, messages):
        """Send message to Watsonx API"""
        if not self.access_token:
            if not self.get_access_token():
                return None
        
        try:
            payload = {
                "messages": messages
            }
            
            response = requests.post(
                self.SCORING_URL,
                headers={
                    "Accept": "application/json",
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json;charset=UTF-8"
                },
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"API request failed: {response.status_code}")
                return None
                
        except Exception as e:
            st.error(f"Error communicating with Watsonx: {str(e)}")
            return None
    
    def get_fallback_greeting(self):
        """Return fallback greeting message"""
        return """Welcome to CommunicaAI! 🎯

I'm your specialized AI assistant focused on communication tasks. I can help you with:

• Content creation and writing assistance
• Multi-language translation
• Voice synthesis and script writing
• Communication strategy development
• Presentation and speech preparation
• Social media content creation

What communication challenge can I help you solve today?"""
    
    def get_fallback_suggestions(self):
        """Return fallback quick actions"""
        return [
            {"text": "Help me write a professional email", "icon": "✉️"},
            {"text": "Translate this text to Spanish", "icon": "🌐"},
            {"text": "Create a social media post", "icon": "📱"},
            {"text": "Write a presentation outline", "icon": "📊"}
        ]
    
    def extract_suggestions_from_response(self, response):
        """Extract quick actions from API response"""
        try:
            response_text = json.dumps(response).lower()
            suggestions = []
            
            quick_action_patterns = [
                {"pattern": r"email|mail", "suggestion": "Help me write a professional email", "icon": "✉️"},
                {"pattern": r"presentation|speech", "suggestion": "Create a presentation outline", "icon": "📊"},
                {"pattern": r"translate|language", "suggestion": "Translate text to Spanish", "icon": "🌐"},
                {"pattern": r"social.media|post", "suggestion": "Write a social media post", "icon": "📱"},
                {"pattern": r"summary|summarize", "suggestion": "Summarize this document", "icon": "📄"},
                {"pattern": r"voice|audio", "suggestion": "Generate voiceover script", "icon": "🔊"},
                {"pattern": r"meeting|agenda", "suggestion": "Create meeting agenda", "icon": "📅"}
            ]
            
            for pattern_data in quick_action_patterns:
                if len(suggestions) < 4 and pattern_data["pattern"] in response_text:
                    suggestions.append({
                        "text": pattern_data["suggestion"],
                        "icon": pattern_data["icon"]
                    })
            
            return suggestions if suggestions else None
            
        except Exception:
            return None

def main():
    # Page configuration
    st.set_page_config(
        page_title="CommunicaAI Assistant",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
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
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        animation: fadeIn 0.5s ease-in;
    }
    .user-message {
        background-color: #e8f4ff;
        border-left: 4px solid #0062ff;
        margin-left: 2rem;
    }
    .assistant-message {
        background-color: #f0f9ff;
        border-left: 4px solid #00d4aa;
        margin-right: 2rem;
    }
    .quick-action {
        background-color: white;
        border: 1px solid #e0e0e0;
        border-radius: 20px;
        padding: 0.5rem 1rem;
        margin: 0.25rem;
        cursor: pointer;
        transition: all 0.2s;
        display: inline-block;
    }
    .quick-action:hover {
        background-color: #f4f4f4;
        border-color: #c6c6c6;
        transform: translateY(-1px);
    }
    .status-connected {
        color: #24a148;
        font-weight: 500;
    }
    .status-connecting {
        color: #f1c21b;
        font-weight: 500;
    }
    .status-error {
        color: #da1e28;
        font-weight: 500;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .stButton button {
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "communica_ai" not in st.session_state:
        st.session_state.communica_ai = CommunicaAI()
    if "initialized" not in st.session_state:
        st.session_state.initialized = False
    if "quick_actions" not in st.session_state:
        st.session_state.quick_actions = []
    
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
        
        st.markdown("### AI ASSISTANT")
        st.button("💬 Chat", use_container_width=True)
        st.button("⚙️ Settings", use_container_width=True)
        st.button("📊 Analytics", use_container_width=True)
        
        st.markdown("---")
        st.markdown("### CAPABILITIES")
        st.button("🔊 Voice Synthesis", use_container_width=True)
        st.button("🌐 Multi-language", use_container_width=True)
        st.button("📝 Content Creation", use_container_width=True)
        
        st.markdown("---")
        st.markdown("### TOOLS")
        st.button("🛠️ API Console", use_container_width=True)
        st.button("📚 Documentation", use_container_width=True)
        
        st.markdown("---")
        
        # API Configuration
        st.markdown("### API Configuration")
        with st.expander("Manage API Settings"):
            api_key = st.text_input(
                "IBM Watson API Key",
                value=st.session_state.communica_ai.API_KEY,
                type="password",
                help="Enter your IBM Watson API key"
            )
            if st.button("Update API Key"):
                st.session_state.communica_ai.API_KEY = api_key
                st.session_state.initialized = False
                st.rerun()
            
            if st.button("Test Connection"):
                with st.spinner("Testing connection..."):
                    if st.session_state.communica_ai.get_access_token():
                        st.success("✅ Connection successful!")
                    else:
                        st.error("❌ Connection failed")
    
    # Main content area
    st.markdown('<div class="main-header">CommunicaAI Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Advanced communication AI powered by IBM watsonx.ai</div>', unsafe_allow_html=True)
    
    # Initialize connection and load initial content
    if not st.session_state.initialized:
        with st.spinner("🔄 Connecting to CommunicaAI..."):
            if st.session_state.communica_ai.get_access_token():
                st.session_state.communica_ai.is_connected = True
                
                # Load initial content
                initial_response = st.session_state.communica_ai.send_to_watson([{
                    "role": "user",
                    "content": "Generate a welcome message for CommunicaAI - a communication-focused AI assistant that helps with content creation, language translation, voice synthesis, and communication strategies. Also provide 4-5 quick action suggestions relevant to communication tasks."
                }])
                
                if initial_response:
                    # Extract greeting
                    greeting = ""
                    if "choices" in initial_response and initial_response["choices"]:
                        greeting = initial_response["choices"][0].get("message", {}).get("content", "")
                    elif "result" in initial_response and "output" in initial_response["result"]:
                        greeting = initial_response["result"]["output"].get("generic", [{}])[0].get("text", "")
                    
                    if greeting:
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": greeting,
                            "timestamp": datetime.now()
                        })
                    else:
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": st.session_state.communica_ai.get_fallback_greeting(),
                            "timestamp": datetime.now()
                        })
                    
                    # Extract quick actions
                    suggestions = st.session_state.communica_ai.extract_suggestions_from_response(initial_response)
                    st.session_state.quick_actions = suggestions or st.session_state.communica_ai.get_fallback_suggestions()
                
                else:
                    # Fallback content
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": st.session_state.communica_ai.get_fallback_greeting(),
                        "timestamp": datetime.now()
                    })
                    st.session_state.quick_actions = st.session_state.communica_ai.get_fallback_suggestions()
                
                st.session_state.initialized = True
                st.rerun()
            else:
                st.error("❌ Failed to connect to CommunicaAI. Please check your API key.")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": st.session_state.communica_ai.get_fallback_greeting(),
                    "timestamp": datetime.now()
                })
                st.session_state.quick_actions = st.session_state.communica_ai.get_fallback_suggestions()
                st.session_state.initialized = True
    
    # Status indicator
    status_emoji = "🟢" if st.session_state.communica_ai.is_connected else "🔴"
    status_text = "Connected" if st.session_state.communica_ai.is_connected else "Disconnected"
    status_class = "status-connected" if st.session_state.communica_ai.is_connected else "status-error"
    
    st.markdown(f'<div class="{status_class}">{status_emoji} {status_text} to CommunicaAI</div>', unsafe_allow_html=True)
    
    # Chat messages
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <div style="font-weight: 500; margin-bottom: 0.5rem;">👤 You</div>
                    <div>{message['content']}</div>
                    <div style="font-size: 0.8rem; color: #666; margin-top: 0.5rem;">
                        {message['timestamp'].strftime('%H:%M')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <div style="font-weight: 500; margin-bottom: 0.5rem;">🤖 CommunicaAI</div>
                    <div>{message['content']}</div>
                    <div style="font-size: 0.8rem; color: #666; margin-top: 0.5rem;">
                        {message['timestamp'].strftime('%H:%M')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Quick actions
    if st.session_state.quick_actions:
        st.markdown("### Quick Actions")
        cols = st.columns(4)
        for idx, action in enumerate(st.session_state.quick_actions):
            with cols[idx % 4]:
                if st.button(f"{action['icon']} {action['text']}", use_container_width=True):
                    # Add the quick action as a user message
                    st.session_state.messages.append({
                        "role": "user",
                        "content": action['text'],
                        "timestamp": datetime.now()
                    })
                    
                    # Get AI response
                    with st.spinner("🤔 Thinking..."):
                        conversation_history = [
                            {"role": msg["role"], "content": msg["content"]} 
                            for msg in st.session_state.messages[:-1]  # Exclude the current user message
                        ]
                        
                        response = st.session_state.communica_ai.send_to_watson(conversation_history + [
                            {"role": "user", "content": action['text']}
                        ])
                        
                        if response:
                            bot_response = ""
                            if "choices" in response and response["choices"]:
                                bot_response = response["choices"][0].get("message", {}).get("content", "")
                            elif "result" in response and "output" in response["result"]:
                                bot_response = response["result"]["output"].get("generic", [{}])[0].get("text", "")
                            
                            if bot_response:
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": bot_response,
                                    "timestamp": datetime.now()
                                })
                            else:
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": "I understand you'd like help with that. How can I assist you further?",
                                    "timestamp": datetime.now()
                                })
                        else:
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": "I'm having trouble processing your request right now. Please try again.",
                                "timestamp": datetime.now()
                            })
                    
                    st.rerun()
    
    st.markdown("---")
    
    # Chat input
    col1, col2 = st.columns([6, 1])
    
    with col1:
        user_input = st.text_area(
            "Your message",
            placeholder="Ask CommunicaAI anything about communication, content creation, or language...",
            key="user_input",
            height=100,
            label_visibility="collapsed"
        )
    
    with col2:
        send_button = st.button("Send", use_container_width=True, type="primary")
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.initialized = False
            st.rerun()
    
    with col2:
        if st.button("📥 Export Chat", use_container_width=True):
            # Create export content
            export_content = "CommunicaAI Conversation Export\n"
            export_content += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            export_content += "=" * 50 + "\n\n"
            
            for msg in st.session_state.messages:
                role = "You" if msg["role"] == "user" else "CommunicaAI"
                export_content += f"{role} ({msg['timestamp'].strftime('%H:%M')}):\n"
                export_content += f"{msg['content']}\n\n"
            
            # Create download link
            b64 = base64.b64encode(export_content.encode()).decode()
            href = f'<a href="data:file/txt;base64,{b64}" download="communicaai_chat_export.txt">Download Chat Export</a>'
            st.markdown(href, unsafe_allow_html=True)
    
    with col3:
        if st.button("🎤 Voice Input", use_container_width=True):
            st.info("Voice input feature coming soon!")
    
    # Handle send button
    if send_button and user_input.strip():
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": user_input.strip(),
            "timestamp": datetime.now()
        })
        
        # Get AI response
        with st.spinner("🤔 CommunicaAI is thinking..."):
            conversation_history = [
                {"role": msg["role"], "content": msg["content"]} 
                for msg in st.session_state.messages[:-1]  # Exclude the current user message
            ]
            
            response = st.session_state.communica_ai.send_to_watson(conversation_history + [
                {"role": "user", "content": user_input.strip()}
            ])
            
            if response:
                bot_response = ""
                if "choices" in response and response["choices"]:
                    bot_response = response["choices"][0].get("message", {}).get("content", "")
                elif "result" in response and "output" in response["result"]:
                    bot_response = response["result"]["output"].get("generic", [{}])[0].get("text", "")
                elif "predictions" in response and response["predictions"]:
                    bot_response = response["predictions"][0]
                elif "text" in response:
                    bot_response = response["text"]
                
                if bot_response:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": bot_response,
                        "timestamp": datetime.now()
                    })
                else:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "I received your message but couldn't generate a proper response. Please try again.",
                        "timestamp": datetime.now()
                    })
            else:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "I'm having trouble connecting to the service right now. Please check your API key and try again.",
                    "timestamp": datetime.now()
                })
        
        st.rerun()

if __name__ == "__main__":
    main()