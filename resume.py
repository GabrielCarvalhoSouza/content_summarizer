import os
from dotenv import load_dotenv
import google.generativeai as genai
from youtube import manager

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)
gemini_model = genai.GenerativeModel("models/gemini-2.0-flash")

def resume():
    with open(f"cache\\{manager.yt.video_id}\\transcription.txt", "r", encoding="utf-8") as f:
            prompt = f"""
            Você receberá uma transcrição de um vídeo, por favor o resuma
            Algumas instruções:
                Você pode resumir o vídeo completamente
                O resumo pode ser longo, mas precisa ser claro e conciso
                Se você perceber que o vídeo é mais zoeiro tu pode resumir ele zoando tbm, com brincadeiras e tal
                Se ele tiver uma estrutura semelhante a tópicos tu pode rezumir em tópicos
                SEMPRE resuma em PT-BR
                SEMPRE em markdown
                Tenha a liberdade que quiser para resumir, pode gastar até 600 palavras
            Esta é a transcrição: {f.read()} 
            """
    res = gemini_model.generate_content(prompt)
    with open(f"cache\\{manager.yt.video_id}\\resume.md", "w", encoding="utf-8") as f:
        f.write(res.text)