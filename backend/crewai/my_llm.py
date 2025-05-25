import os

from crewai import LLM
from dotenv import load_dotenv

load_dotenv()

class MyLLM():
    GTP4o_mini            = LLM(model='gpt-4o-mini', base_url='https://api.openai.com/v1',api_key=os.getenv('OPENAI_API_KEY'))
    GPT4o_mini_2024_07_18 = LLM(model='gpt-4o-mini-2024-07-18', base_url='https://api.openai.com/v1',api_key=os.getenv('OPENAI_API_KEY'))
    GPT_4o_2024_08_06     = LLM(model='gpt-4o-2024-08-06', base_url='https://api.openai.com/v1',api_key=os.getenv('OPENAI_API_KEY'))
    GTP4o                 = LLM(model='gpt4o', base_url='https://api.openai.com/v1',api_key=os.getenv('OPENAI_API_KEY'))
    GPT_o1                = LLM(model='o1-preview', base_url='https://api.openai.com/v1',api_key=os.getenv('OPENAI_API_KEY'))
    GPT_o1_mini           = LLM(model='o1-mini', base_url='https://api.openai.com/v1',api_key=os.getenv('OPENAI_API_KEY'))
    Ollama_llama_3_1      = LLM(model="ollama/llama3.1", base_url="http://localhost:11434")
    Claude_3_opus         = LLM(model='claude-3-opus-20240229')
    LLAMA3_70B            = LLM(model='groq/llama3-70b-8192', base_url='https://api.groq.com/openai/v1', api_key=os.getenv('GROQ_API_KEY'))
    GROQ_LLAMA            = LLM(model='groq/llama-3.2-3b-preview', base_url='https://api.groq.com/openai/v1', api_key=os.getenv('GROQ_API_KEY'))
    GROQ_LLAMA2           = LLM(model='groq/llama-3.2-11b-vision-preview', base_url='https://api.groq.com/openai/v1', api_key=os.getenv('GROQ_API_KEY'))
    GROQ_MIXTRAL          = LLM(model='groq/mixtral-8x7b-32768', base_url='https://api.groq.com/openai/v1', api_key=os.getenv('GROQ_API_KEY'))
    DEEPSEEK_R1           = LLM(model='deepseek/deepseek-reasoner', base_url='https://api.deepseek.com',api_key=os.getenv('DEEPSEEK_API_KEY'))
    DEEPSEEK_CHAT         = LLM(model='deepseek/deepseek-chat', base_url='https://api.deepseek.com',api_key=os.getenv('DEEPSEEK_API_KEY'))