import streamlit as st
import requests
import json
from datetime import datetime
import base64
import time

class CommunicaAI:
    def __init__(self):
        # Initialize with empty API key, will be set from secrets or user input
        self.API_KEY = ""
        self.SCORING_URL = "https://us-south.ml.cloud.ibm.com/ml/v4/deployments/9a25c432-dafa-4c43-b2ce-2eabd6aec8e5/ai_service_stream?version=2021-05-01"
        self.access_token = None
        self.is_connected = False
        self.last_token_refresh = None
        
    def set_api_key(self, api_key):
        """Set and validate API key"""
        self.API_KEY = api_key.strip()
        # Reset connection state when API key changes
        self.access_token = None
        self.is_connected = False
        self.last_token_refresh = None
        
    def validate_api_key(self, api_key):
        """Validate API key format"""
        if not api_key:
            return False, "API key cannot be empty"
        
        api_key = api_key.strip()
        
        # Basic format validation for IBM API keys
        if not api_key.startswith(('ApiKey-', 'iam-')):
            return False, "API key should start with 'ApiKey-' or 'iam-'"
        
        if len(api_key) < 20:
            return False, "API key appears too short"
        
        return True, "Valid"
    
    def get_access_token(self):
        """Get IBM Cloud access token with comprehensive error handling"""
        if not self.API_KEY:
            return False, "No API key provided"
            
        # Validate API key first
        is_valid, message = self.validate_api_key(self.API_KEY)
        if not is_valid:
            return False, f"Invalid API key: {message}"
        
        try:
            # Use params instead of data string for better encoding
            response = requests.post(
                "https://iam.cloud.ibm.com/identity/token",
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                    "User-Agent": "CommunicaAI-Streamlit/1.0"
                },
                data={
                    "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                    "apikey": self.API_KEY
                },
                timeout=30
            )
            
            # Enhanced HTTP status code handling
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get("access_token")
                if self.access_token:
                    self.is_connected = True
                    self.last_token_refresh = datetime.now()
                    return True, "Successfully authenticated with IBM Cloud"
                else:
                    return False, "No access token in response"
                    
            elif response.status_code == 400:
                error_info = self.parse_400_error(response)
                return False, f"Authentication failed: {error_info['message']}"
                
            elif response.status_code == 401:
                return False, "Unauthorized - The API key is invalid or has been revoked"
                
            elif response.status_code == 429:
                return False, "Rate limit exceeded - Too many requests"
                
            elif response.status_code >= 500:
                return False, f"IBM Cloud service error (HTTP {response.status_code}) - Try again later"
                
            else:
                return False, f"Unexpected error (HTTP {response.status_code}): {response.text[:200]}"
                
        except requests.exceptions.Timeout:
            return False, "Request timeout - Check your internet connection"
        except requests.exceptions.ConnectionError:
            return False, "Connection error - Check your internet connection and DNS"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
    
    def parse_400_error(self, response):
        """Parse 400 error responses for better user guidance"""
        try:
            error_data = response.json()
            error_code = error_data.get('errorCode', '')
            error_msg = error_data.get('errorDescription') or error_data.get('errorMessage', 'Unknown error')
            
            suggestions = {
                'BXNIM0415E': 'API key is malformed or incomplete',
                'BXNIM0425E': 'API key has expired',
                'BXNIM0400E': 'Invalid grant type or parameters',
            }
            
            suggestion = suggestions.get(error_code)
            if not suggestion:
                if 'apikey' in error_msg.lower():
                    suggestion = 'Check if your API key is correct and properly formatted'
                elif 'expired' in error_msg.lower():
                    suggestion = 'Your API key may have expired. Generate a new one in IBM Cloud'
                elif 'invalid' in error_msg.lower():
                    suggestion = 'The API key appears to be invalid. Verify it in IBM Cloud Console'
                else:
                    suggestion = 'Check your API key format and ensure it has the required permissions'
            
            return {
                'message': error_msg,
                'suggestion': suggestion,
                'code': error_code
            }
            
        except:
            return {
                'message': response.text[:200],
                'suggestion': 'Check your API key format and network connection',
                'code': 'UNKNOWN'
            }
    
    def is_token_expired(self):
        """Check if token needs refresh (IBM tokens typically last 1 hour)"""
        if not self.last_token_refresh:
            return True
        time_diff = datetime.now() - self.last_token_refresh
        return time_diff.total_seconds() > 3500  # Refresh after 58 minutes
    
    def send_to_watson(self, messages):
        """Send message to Watsonx API with comprehensive error handling"""
        # Refresh token if expired or not present
        if not self.access_token or self.is_token_expired():
            success, message = self.get_access_token()
            if not success:
                return None, message
        
        try:
            # Try different payload formats
            payloads_to_try = [
                {"input": {"messages": messages}},
                {"messages": messages},
                {"parameters": {"messages": messages}}
            ]
            
            for payload in payloads_to_try:
                response = requests.post(
                    self.SCORING_URL,
                    headers={
                        "Accept": "application/json",
                        "Authorization": f"Bearer {self.access_token}",
                        "Content-Type": "application/json"
                    },
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    return response.json(), "Success"
                elif response.status_code == 401:
                    # Token might be expired, try to refresh once
                    success, message = self.get_access_token()
                    if success:
                        continue  # Retry with new token
                    else:
                        return None, f"Authentication failed: {message}"
                elif response.status_code == 400:
                    # Try next payload format
                    continue
                else:
                    # If all payload formats fail, return the last error
                    if payload == payloads_to_try[-1]:
                        return None, f"API request failed: HTTP {response.status_code} - {response.text[:200]}"
            
            return None, "All payload formats failed"
            
        except requests.exceptions.Timeout:
            return None, "Request timeout - Watsonx service took too long to respond"
        except requests.exceptions.ConnectionError:
            return None, "Connection error - Cannot reach Watsonx service"
        except Exception as e:
            return None, f"Unexpected error: {str(e)}"

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

def init_session_state():
    """Initialize all session state variables"""
    defaults = {
        "messages": [],
        "communica_ai": CommunicaAI(),
        "api_key": st.secrets.get("WATSON_API_KEY", ""),
        "initialized": False,
        "quick_actions": [],
        "connection_attempted": False,
        "last_error": None
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def show_error_diagnosis(error_message):
    """Show detailed error diagnosis and solutions"""
    with st.expander("🔧 Error Diagnosis & Solutions", expanded=True):
        st.error(f"**Error:** {error_message}")
        
        if "API key" in error_message or "apikey" in error_message.lower():
            st.markdown("""
            **Possible Solutions:**
            1. **Verify API Key Format:** Should start with `ApiKey-` or `iam-`
            2. **Check IBM Cloud Console:** Ensure the API key exists and is active
            3. **Regenerate Key:** Create a new API key in IBM Cloud
            4. **Check Permissions:** Ensure key has Watsonx.ai access
            """)
            
        elif "timeout" in error_message.lower():
            st.markdown("""
            **Possible Solutions:**
            1. **Check Internet Connection**
            2. **Try Different Network**
            3. **Check Firewall Settings**
            4. **Retry Later** - IBM Cloud might be experiencing issues
            """)
            
        elif "connection" in error_message.lower():
            st.markdown("""
            **Possible Solutions:**
            1. **Check Internet Connectivity**
            2. **Verify DNS Settings**
            3. **Try Different Browser/Network**
            4. **Check Corporate Firewall**
            """)
            
        else:
            st.markdown("""
            **General Solutions:**
            1. **Refresh the page** and try again
            2. **Check IBM Cloud Status** for service outages
            3. **Verify API Key** in IBM Cloud Console
            4. **Contact Support** if issue persists
            """)
        
        st.markdown("---")
        st.markdown("**📋 Quick Checks:**")
        if st.button("🔄 Retry Connection"):
            st.session_state.connection_attempted = False
            st.session_state.last_error = None
            st.rerun()

def render_chat_interface():
    """Render the main chat interface"""
    # Status header
    status_col1, status_col2 = st.columns([3, 1])
    
    with status_col1:
        if st.session_state.communica_ai.is_connected:
            st.success("🟢 **Connected to IBM Watsonx**")
            if st.session_state.communica_ai.last_token_refresh:
                st.caption(f"Last refreshed: {st.session_state.communica_ai.last_token_refresh.strftime('%H:%M:%S')}")
        else:
            st.error("🔴 **Not connected** - Configure API key in sidebar")
    
    with status_col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.session_state.connection_attempted = False
            st.rerun()
    
    # Chat messages
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div style="padding: 1rem; background-color: #e8f4ff; border-radius: 0.5rem; 
                         border-left: 4px solid #0062ff; margin-bottom: 1rem; margin-left: 2rem;
                         animation: fadeIn 0.5s ease-in;">
                    <div style="font-weight: 500; margin-bottom: 0.5rem;">👤 You</div>
                    <div>{message['content']}</div>
                    <div style="font-size: 0.8rem; color: #666; margin-top: 0.5rem;">
                        {message['timestamp'].strftime('%H:%M')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="padding: 1rem; background-color: #f0f9ff; border-radius: 0.5rem; 
                         border-left: 4px solid #00d4aa; margin-bottom: 1rem; margin-right: 2rem;
                         animation: fadeIn 0.5s ease-in;">
                    <div style="font-weight: 500; margin-bottom: 0.5rem;">🤖 CommunicaAI</div>
                    <div style="white-space: pre-wrap;">{message['content']}</div>
                    <div style="font-size: 0.8rem; color: #666; margin-top: 0.5rem;">
                        {message['timestamp'].strftime('%H:%M')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Quick actions (only show when connected)
    if st.session_state.communica_ai.is_connected and st.session_state.quick_actions:
        st.markdown("### 💡 Quick Actions")
        cols = st.columns(4)
        for idx, action in enumerate(st.session_state.quick_actions):
            with cols[idx % 4]:
                if st.button(f"{action['icon']} {action['text']}", use_container_width=True, key=f"quick_{idx}"):
                    handle_quick_action(action['text'])

def handle_quick_action(action_text):
    """Handle quick action button clicks"""
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": action_text,
        "timestamp": datetime.now()
    })
    
    # Get AI response
    with st.spinner("🤔 Thinking..."):
        conversation_history = [
            {"role": msg["role"], "content": msg["content"]} 
            for msg in st.session_state.messages[:-1]
        ]
        
        response, error_message = st.session_state.communica_ai.send_to_watson(
            conversation_history + [{"role": "user", "content": action_text}]
        )
        
        if response:
            bot_response = extract_bot_response(response)
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
                "content": f"I'm having trouble processing your request: {error_message}",
                "timestamp": datetime.now()
            })
    
    st.rerun()

def extract_bot_response(response):
    """Extract bot response from various API response formats"""
    try:
        if "choices" in response and response["choices"]:
            return response["choices"][0].get("message", {}).get("content", "")
        elif "result" in response and "output" in response["result"]:
            return response["result"]["output"].get("generic", [{}])[0].get("text", "")
        elif "predictions" in response and response["predictions"]:
            return response["predictions"][0]
        elif "text" in response:
            return response["text"]
        else:
            # Try to find any text in the response
            response_str = json.dumps(response)
            if "content" in response_str:
                # Extract content from JSON string as fallback
                import re
                content_match = re.search(r'"content":\s*"([^"]+)"', response_str)
                if content_match:
                    return content_match.group(1)
            return ""
    except:
        return ""

def render_api_configuration():
    """Render the API configuration sidebar"""
    st.markdown("### 🔧 API Configuration")
    
    with st.expander("API Settings", expanded=True):
        api_key = st.text_input(
            "IBM Watson API Key",
            value=st.session_state.api_key,
            type="password",
            help="Enter your IBM Cloud API key",
            placeholder="ApiKey-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
            key="api_key_input"
        )
        
        st.markdown("""
        <div style="font-size: 0.8rem; color: #666; margin-top: 0.5rem;">
        💡 Get your API key from:<br>
        IBM Cloud Console → Manage → Access (IAM) → API keys
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔗 Test Connection", use_container_width=True, type="primary"):
                if api_key:
                    st.session_state.communica_ai.set_api_key(api_key)
                    st.session_state.api_key = api_key
                    st.session_state.connection_attempted = True
                    
                    with st.spinner("Testing connection..."):
                        success, message = st.session_state.communica_ai.get_access_token()
                        if success:
                            st.session_state.initialized = True
                            st.session_state.last_error = None
                            # Load initial content
                            load_initial_content()
                            st.success("✅ Connection successful!")
                        else:
                            st.session_state.last_error = message
                            st.session_state.initialized = False
                else:
                    st.error("Please enter an API key")
        
        with col2:
            if st.button("💾 Save Key", use_container_width=True):
                if api_key:
                    st.session_state.communica_ai.set_api_key(api_key)
                    st.session_state.api_key = api_key
                    st.success("API key saved!")
                else:
                    st.error("Please enter an API key")
        
        # Show last error if any
        if st.session_state.last_error:
            show_error_diagnosis(st.session_state.last_error)

def load_initial_content():
    """Load initial greeting and quick actions"""
    # Use fallback content initially
    if not any(msg["role"] == "assistant" for msg in st.session_state.messages):
        st.session_state.messages.append({
            "role": "assistant",
            "content": st.session_state.communica_ai.get_fallback_greeting(),
            "timestamp": datetime.now()
        })
    
    st.session_state.quick_actions = st.session_state.communica_ai.get_fallback_suggestions()
    
    # Try to get dynamic content from API
    try:
        response, error = st.session_state.communica_ai.send_to_watson([{
            "role": "user",
            "content": "Generate a welcome message for CommunicaAI - a communication-focused AI assistant. Also provide 4 quick action suggestions for communication tasks."
        }])
        
        if response:
            bot_response = extract_bot_response(response)
            if bot_response:
                # Update the welcome message
                st.session_state.messages = [{
                    "role": "assistant",
                    "content": bot_response,
                    "timestamp": datetime.now()
                }]
            
            # Extract suggestions from response
            suggestions = st.session_state.communica_ai.extract_suggestions_from_response(response)
            if suggestions:
                st.session_state.quick_actions = suggestions
    except:
        pass  # Fallback content already loaded

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
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .stButton button {
        border-radius: 6px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    init_session_state()
    
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
        
        # API Configuration
        render_api_configuration()
        
        st.markdown("---")
        
        # Navigation
        st.markdown("### 🚀 Quick Actions")
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
            
        if st.button("📊 Connection Info", use_container_width=True):
            st.session_state.connection_attempted = True
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 📁 Tools")
        st.button("🛠️ API Console", use_container_width=True)
        st.button("📚 Documentation", use_container_width=True)
    
    # Main content area
    st.markdown('<div class="main-header">CommunicaAI Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Advanced communication AI powered by IBM watsonx.ai</div>', unsafe_allow_html=True)
    
    # Show connection prompt if not initialized
    if not st.session_state.initialized and not st.session_state.connection_attempted:
        st.info("""
        🚀 **Get Started:** 
        1. Enter your IBM Watson API key in the sidebar
        2. Click **"Test Connection"** to verify
        3. Start chatting with CommunicaAI!
        """)
        
        # Auto-initialize if API key is present in secrets
        if st.session_state.api_key and not st.session_state.connection_attempted:
            if st.button("🎯 Auto-Initialize with Saved Key", type="primary"):
                st.session_state.connection_attempted = True
                with st.spinner("Initializing..."):
                    st.session_state.communica_ai.set_api_key(st.session_state.api_key)
                    success, message = st.session_state.communica_ai.get_access_token()
                    if success:
                        st.session_state.initialized = True
                        load_initial_content()
                        st.rerun()
                    else:
                        st.session_state.last_error = message
    
    # Render chat interface if connected
    if st.session_state.initialized:
        render_chat_interface()
        
        # Chat input
        st.markdown("---")
        user_input = st.text_area(
            "💭 Your message to CommunicaAI:",
            placeholder="Ask about communication strategies, content creation, translations, or anything else...",
            key="user_input",
            height=100,
            label_visibility="collapsed"
        )
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("📤 Send Message", use_container_width=True, type="primary"):
                if user_input.strip():
                    handle_user_message(user_input.strip())
        
        with col2:
            if st.button("📥 Export Chat", use_container_width=True):
                export_chat_history()
        
        with col3:
            if st.button("🎤 Voice Input", use_container_width=True):
                st.info("Voice input feature coming soon!")

def handle_user_message(user_input):
    """Handle user message submission"""
    # Add user message to chat
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now()
    })
    
    # Get AI response
    with st.spinner("🤔 CommunicaAI is thinking..."):
        conversation_history = [
            {"role": msg["role"], "content": msg["content"]} 
            for msg in st.session_state.messages[:-1]
        ]
        
        response, error_message = st.session_state.communica_ai.send_to_watson(
            conversation_history + [{"role": "user", "content": user_input}]
        )
        
        if response:
            bot_response = extract_bot_response(response)
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
                "content": f"I'm having trouble connecting to the service: {error_message}",
                "timestamp": datetime.now()
            })
    
    st.rerun()

def export_chat_history():
    """Export chat history as downloadable file"""
    if not st.session_state.messages:
        st.warning("No chat history to export")
        return
        
    export_content = "CommunicaAI Conversation Export\n"
    export_content += "=" * 50 + "\n"
    export_content += f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    export_content += f"Total Messages: {len(st.session_state.messages)}\n"
    export_content += "=" * 50 + "\n\n"
    
    for msg in st.session_state.messages:
        role = "You" if msg["role"] == "user" else "CommunicaAI"
        timestamp = msg["timestamp"].strftime('%H:%M')
        export_content += f"{role} ({timestamp}):\n{msg['content']}\n\n"
    
    # Create download link
    b64 = base64.b64encode(export_content.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="communicaai_chat_export.txt" style="display: inline-block; padding: 0.5rem 1rem; background: #0062ff; color: white; text-decoration: none; border-radius: 4px;">📥 Download Chat Export</a>'
    st.markdown(href, unsafe_allow_html=True)

if __name__ == "__main__":
    main()