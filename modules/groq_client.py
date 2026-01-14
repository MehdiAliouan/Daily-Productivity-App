import os
import streamlit as st
from groq import Groq, GroqError
from config.prompts import GROQ_PROMPTS

class GroqClient:
    def __init__(self):
        # Prioritize Secrets, then Env
        self.api_key = None
        if "GROQ_API_KEY" in st.secrets:
            self.api_key = st.secrets["GROQ_API_KEY"]
        elif os.getenv("GROQ_API_KEY"):
            self.api_key = os.getenv("GROQ_API_KEY")
             
        if self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                st.error(f"Failed to initialize Groq Client: {e}")
                self.client = None
        else:
            self.client = None

    def get_completion(self, prompt_key, **kwargs):
        if not self.client:
            return "Please configure your GROQ_API_KEY to use AI features."
        
        prompt_template = GROQ_PROMPTS.get(prompt_key)
        if not prompt_template:
            return "Error: Prompt key not found."
            
        formatted_prompt = prompt_template.format(**kwargs)
        
        # Simple Session State Caching
        cache_key = f"groq_cache_{hash(formatted_prompt)}"
        if cache_key in st.session_state:
            return st.session_state[cache_key]
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": formatted_prompt,
                    }
                ],
                model="llama-3.3-70b-versatile",
            )
            response_content = chat_completion.choices[0].message.content
            
            # Cache the response
            st.session_state[cache_key] = response_content
            return response_content
            
        except GroqError as e:
            return f"Groq API Error: {str(e)}"
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"
