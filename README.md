# 🧠 Assistant Intelligent Multi-Compétences (RAG + Agents)

## 🎯 Objectif
Un assistant intelligent combinant **RAG (Retrieval-Augmented Generation)** et **Agents LangChain** pour répondre à des questions à partir :
- de documents internes (PDF/DOCX/TXT),
- de sources externes (outils : calculatrice, météo, recherche web).

## ⚙️ Architecture
```text
+------------------------------+
|        Interface UI          |
| (Streamlit)                  |
+--------------+---------------+
               |
               v
+--------------------------------------------+
|  LangChain Orchestrator                    |
|---------------------------------------------|
| - Memory (ConversationBufferMemory)         |
| - Agent (Zero-Shot-React-Description)       |
| - Tools: calculator, weather, web_search    |
| - RAG: ConversationalRetrievalChain         |
+--------------------------------------------+
               |
               v
+--------------------------------------------+
|  Vector Store (Chroma + OpenAIEmbeddings)   |
|  -> Documents locaux indexés                |
+--------------------------------------------+

