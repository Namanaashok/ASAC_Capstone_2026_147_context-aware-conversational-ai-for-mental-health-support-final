from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
try:
    from langchain_ollama import OllamaLLM
except ImportError:
    from langchain_community.llms import Ollama as OllamaLLM

# Safety Keywords for Crisis Intervention
CRISIS_KEYWORDS = [
    "suicide", "kill myself", "want to die", "end it all", "harm myself", 
    "cut myself", "self harm", "useless", "hopeless", "can't take it anymore"
]

CRISIS_RESPONSE = """
I hear that you are going through an incredibly difficult time right now, and I want you to know that you are not alone. 
Your life has value, and there is support available for you. 
Please consider reaching out to people who can help:

- **National Suicide Prevention Lifeline**: Call or text 988 (US/Canada)
- **Crisis Text Line**: Text HOME to 741741
- **Emergency Services**: Call 911 (US/Canada) or your local emergency number.

Please talk to someone who can support you. I am an AI, but I care about your safety.
"""

class BotEngine:
    def __init__(self, model_name="phi3:latest"):
        # Initialize the local LLM using Ollama
        try:
            self.llm = OllamaLLM(model=model_name)
        except Exception as e:
            print(f"Error initializing Ollama: {e}")
            self.llm = None
            
        self.memory = ConversationBufferWindowMemory(k=5, memory_key="chat_history", input_key="user_input")
        
        # Domain-specific prompt for a mental health chatbot
        self.system_prompt = """You are Aura, an empathetic, supportive, and context-aware mental health AI assistant.
Your goal is to provide a safe, non-judgmental space for the user to express their feelings.

Guidelines:
1. Be empathetic, warm, and validating.
2. DO NOT provide medical advice or diagnose any conditions. Recommend seeking professional help if appropriate.
3. Keep responses concise and conversational. Do not write extremely long paragraphs.
4. Adapt your tone based on the user's detected sentiment. If the user is negative, be extra gentle and supportive. If positive, be encouraging.

Current User Sentiment: {sentiment}

Chat History:
{chat_history}

User: {user_input}
Aura:"""
        
        self.prompt_template = PromptTemplate(
            input_variables=["sentiment", "chat_history", "user_input"],
            template=self.system_prompt
        )
        
            
    def check_for_crisis(self, text):
        text_lower = text.lower()
        for keyword in CRISIS_KEYWORDS:
            if keyword in text_lower:
                return True
        return False
        
    def get_response_stream(self, user_input, sentiment):
        if not self.llm:
            yield "Error: Local LLM (Ollama) is not initialized properly. Please ensure Ollama is running."
            return
            
        # 1. Check for crisis keywords
        if self.check_for_crisis(user_input):
            yield CRISIS_RESPONSE
            return
            
        # 2. Get response from LLM using streaming
        try:
            prompt_text = self.prompt_template.format(
                sentiment=sentiment, 
                chat_history=self.memory.buffer_as_str, 
                user_input=user_input
            )
            
            full_response = ""
            for chunk in self.llm.stream(prompt_text):
                full_response += chunk
                yield chunk
                
            # Manually save context to memory since we bypassed the chain
            self.memory.save_context({"user_input": user_input}, {"output": full_response})
            
        except Exception as e:
            yield f"I'm sorry, I'm having trouble connecting to Ollama. Make sure it is running. (Error: {str(e)})"
