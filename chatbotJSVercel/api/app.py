"""
Backend Flask para o Chatbot Técnico (JS/TS & .NET)

- Serve o frontend estático (index.html + style.css) pela MESMA origem/porta → evita CORS.
- Endpoints:
    • POST /api/ask        → responde à pergunta em Markdown
    • POST /api/summarize  → retorna resumo em Markdown das últimas interações
    • GET  /api/health     → healthcheck simples
"""

from __future__ import annotations

import os
from typing import List, Dict, Any

from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv, find_dotenv
import google.generativeai as genai

# ============================================================
# 1) Carrega variáveis de ambiente (.env local / Vercel)
# ============================================================
load_dotenv(find_dotenv(), override=True)  # procura e carrega o .env mais próximo

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError(
        "Defina GEMINI_API_KEY nas variáveis de ambiente (.env local ou Vercel Settings)."
    )

# ============================================================
# 2) Configura o SDK do Gemini
# ============================================================
genai.configure(api_key=API_KEY)

# Instrução de sistema: define o "perfil" do assistente
DOMAIN_CONTEXT = """
Você é um assistente técnico especializado em:
- JavaScript e TypeScript (DOM, eventos, Promises, async/await, Fetch/AJAX, módulos, boas práticas)
- C# e .NET (ASP.NET Core, Web API, EF Core, LINQ, async/await, injeção de dependência, DTOs vs Domain Models)

Regras:
- Responda SEMPRE em português do Brasil.
- Seja objetivo e didático. Dê exemplos curtos quando útil.
- Se a pergunta fugir deste domínio, diga brevemente que o escopo é JS/TS/AJAX e C#/.NET e ofereça redirecionar.
- Onde couber, cite rapidamente boas práticas (tratamento de erros, camadas, validação, performance).
"""

# Parâmetros do modelo 
MODEL_NAME = "gemini-2.0-flash"
GENERATION_CONFIG = {
    "temperature": 0.4,
    "top_p": 0.9,
    "max_output_tokens": 800,
}

# Instancia o modelo com a instrução de sistema e config de geração
model = genai.GenerativeModel(
    model_name=MODEL_NAME,
    system_instruction=DOMAIN_CONTEXT,
    generation_config=GENERATION_CONFIG,
)

# ============================================================
# 3) Inicializa o Flask e aponta a pasta estática do frontend
# ============================================================
# PROJECT_ROOT: pasta raiz do projeto (um nível acima de /api)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC_DIR = os.path.join(PROJECT_ROOT, "public")

# static_folder = PUBLIC_DIR permite servir /style.css, imagens, etc.
# static_url_path = "" coloca os arquivos estáticos na raiz ("/style.css")
app = Flask(__name__, static_folder=PUBLIC_DIR, static_url_path="")

# Garante que JSON devolvido preserve acentos
app.json.ensure_ascii = False 


# ============================================================
# 4) Helpers de negócio (isolam chamadas ao modelo)
# ============================================================
def generate_markdown_answer(question: str) -> str:
    """
    Gera uma resposta em Markdown para a pergunta fornecida.
    Mantemos o prompt claro para obter títulos/listas/código quando fizer sentido.
    """
    prompt = (
        "Responda no contexto acima **em Markdown**. "
        "Use títulos curtos (##), listas quando fizer sentido e blocos de código com a linguagem quando houver trechos de código. "
        f"\nPergunta do usuário: {question}"
    )
    resp = model.generate_content(prompt)
    answer = (getattr(resp, "text", "") or "").strip()
    return answer or "Não consegui gerar resposta."


def summarize_markdown(qa: List[Dict[str, Any]]) -> str:
    """
    Recebe uma lista de objetos { q: str, a: str } e devolve um resumo em Markdown.
    """
    linhas = [
        "Resuma de forma objetiva as interações abaixo.",
        "• Traga ATÉ 8 tópicos (bullets).",
        "• Termine com 'Próximas ações:' e 3 itens.",
        "",
        "Conteúdo para resumir:",
    ]
    for i, item in enumerate(qa, start=1):
        q = (item or {}).get("q", "")
        a = (item or {}).get("a", "")
        linhas.append(f"- Pergunta {i}: {q}")
        linhas.append(f"- Resposta {i}: {a}")

    resp = model.generate_content("\n".join(linhas))
    resumo = (getattr(resp, "text", "") or "").strip()
    return resumo or "Não foi possível gerar o resumo."


# ============================================================
# 5) Rotas do frontend (mesma origem → sem CORS)
# ============================================================
@app.route("/")
def index():
    """Serve o arquivo HTML principal do frontend."""
    return send_from_directory(PUBLIC_DIR, "index.html")


# ============================================================
# 6) Endpoints de API
# ============================================================
@app.route("/api/health", methods=["GET"])
def health():
    """Healthcheck simples para verificar se a função está online."""
    return jsonify({"ok": True})


@app.route("/api/ask", methods=["POST"])
def ask():
    """
    Recebe { question: string } e devolve { answer: string } em Markdown.
    """
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()

    if not question:
        return jsonify({"error": "Campo 'question' é obrigatório"}), 400

    try:
        answer = generate_markdown_answer(question)
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": f"Erro ao gerar resposta: {e}"}), 500


@app.route("/api/summarize", methods=["POST"])
def summarize():
    """
    Recebe { qa: [{ q: string, a: string }, ...] } e devolve { summary: string } em Markdown.
    Usado pelo frontend a cada 3 interações.
    """
    data = request.get_json(silent=True) or {}
    qa = data.get("qa")

    if not qa or not isinstance(qa, list):
        return jsonify({"error": "Campo 'qa' deve ser uma lista"}), 400

    try:
        summary = summarize_markdown(qa)
        return jsonify({"summary": summary})
    except Exception as e:
        return jsonify({"error": f"Erro ao gerar resumo: {e}"}), 500


# ============================================================
# 7) Execução local (dev)
# ============================================================
if __name__ == "__main__":
    if not os.path.isdir(PUBLIC_DIR):
        print(f"[aviso] pasta 'public' não encontrada em: {PUBLIC_DIR}")

    # Rode: python api/app.py
    # Acesse: http://127.0.0.1:8000/
    app.run(debug=True, port=8000)
