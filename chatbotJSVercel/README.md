# Chatbot Técnico (JS/TS & .NET)

Assistente web que responde dúvidas de **JavaScript/TypeScript** e **C#/.NET** e, **a cada 3 interações**, gera um **resumo em Markdown** das últimas perguntas e respostas.  
Frontend simples (HTML/CSS/JS) renderiza Markdown com **marked** e sanitiza com **DOMPurify**. Backend em **Flask** usando **Google Gemini**.

## 🎥 Vídeo da execução

Assista à demonstração no YouTube:  
➡️ **https://youtu.be/8zZTY2Hrpwo**

---

## 🧰 Stack (resumo)

- **Frontend:** HTML, CSS, JS (marked + DOMPurify)
- **Backend:** Python (Flask)
- **IA:** Google Generative AI (Gemini)

---

## 🖥️ Como reproduzir localmente (o que é necessário)

1. **Pré-requisitos**

   - Python **3.11+**
   - Uma chave do **Google Generative AI** (Gemini)

2. **Variável de ambiente** python api/app.py

   - Crie um arquivo `.env` na **raiz** do projeto com:
     ```
     GEMINI_API_KEY=COLOQUE_SUA_CHAVE_AQUI
     ```

3. **Instalar dependências**

   ```bash
   pip install -r requirements.txt
   ```

4. **Iniciar ChatBot**

   ```bash
    python api/app.py
   ```

5. **Acessar no navegador**
   Abra http://127.0.0.1:8000/
