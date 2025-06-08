import os
from dotenv import load_dotenv
import google.generativeai as genai
from youtube import manager

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)  #type: ignore[reportPrivateImportUsage]
gemini_model = genai.GenerativeModel("models/gemini-2.0-flash")  #type: ignore[reportPrivateImportUsage]

def resume():
    with open(f"cache\\{manager.yt.video_id}\\transcription.txt", "r", encoding="utf-8") as f:
            prompt = f"""
                Você vai receber a transcrição de um vídeo e precisa fazer um resumo claro, direto e natural, como se fosse uma pessoa falando sobre ele.

                Regras:
                - Resuma tudo que for importante, com clareza e objetividade.
                - Pode usar tópicos, texto corrido ou um formato híbrido, dependendo do que ficar mais legal e claro.
                - Use até 1000 palavras, só se realmente precisar.
                - Se o vídeo for mais descontraído e zoeiro, pode entrar na brincadeira, mas sem perder a clareza e o conteúdo.
                - Se o vídeo for sério, evite exagerar na zoeira; pode usar uma ou outra piada leve só pra quebrar o clima.
                - Não mencione que é um resumo de vídeo ou transcrição, nem diga "aqui está o resumo".
                - Resuma sempre em português e em formato markdown.

                Conteúdo: {f.read()}
                """

    res = gemini_model.generate_content(prompt)
    with open(f"cache\\{manager.yt.video_id}\\resume.md", "w", encoding="utf-8") as f:
        f.write(res.text)