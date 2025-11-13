import streamlit as st

# DOIT ÊTRE LA PREMIÈRE COMMANDE STREAMLIT
st.set_page_config(
    page_title="Assistant Complet RAG + Agents",
    page_icon="🤖",
    layout="wide"
)

import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# GESTION DES IMPORTS SIMPLIFIÉE
# =============================================================================

# Import Pydantic d'abord (le plus critique)
try:
    from pydantic import BaseModel, Field
    PYDANTIC_AVAILABLE = True
except ImportError as e:
    PYDANTIC_AVAILABLE = False
    st.error(f"❌ Pydantic non disponible: {e}")

# Essayer d'importer les composants LangChain
HAS_LANGCHAIN = False
TAVILY_AVAILABLE = False

try:
    # Essayer les nouveaux imports d'abord (langchain-community)
    try:
        from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
        from langchain_community.vectorstores import Chroma
        LANGCHAIN_NEW = True
    except ImportError:
        # Fallback aux anciens imports
        from langchain.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
        from langchain.vectorstores import Chroma
        LANGCHAIN_NEW = False
    
    # Imports communs
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.memory import ConversationBufferMemory
    from langchain.chains import ConversationalRetrievalChain
    from langchain.agents import initialize_agent, Tool, AgentType
    
    # Gestion OpenAI
    try:
        from langchain_openai import OpenAIEmbeddings, ChatOpenAI
        OPENAI_NEW = True
    except ImportError:
        from langchain.embeddings import OpenAIEmbeddings
        from langchain.chat_models import ChatOpenAI
        OPENAI_NEW = False
    
    HAS_LANGCHAIN = True
    
except ImportError as e:
    st.error(f"❌ Erreur d'importation LangChain: {e}")

# Import Tavily
try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False

# =============================================================================
# OUTILS DE BASE - VERSION SIMPLIFIÉE SANS PYDANTIC
# =============================================================================

class CalculatorTool:
    name = "calculator"
    description = "Effectue des calculs mathématiques. Exemple: '2 + 2' ou '15 * 3.5'"
    
    def run(self, expression: str) -> str:
        try:
            # Sécurité : seulement les caractères mathématiques autorisés
            allowed_chars = set("0123456789+-*/.() ")
            if not all(c in allowed_chars for c in expression):
                return "❌ Caractères non autorisés. Utilisez seulement: chiffres, +, -, *, /, ., (, )"
            
            expression = expression.replace(',', '.')
            result = eval(expression)
            return f"🧮 {expression} = {result}"
        except Exception as e:
            return f"❌ Erreur de calcul: {str(e)}"

class WeatherTool:
    name = "weather"
    description = "Donne la météo d'une ville. Exemple: 'Paris' ou 'Lyon'"
    
    def run(self, city: str) -> str:
        weather_data = {
            "paris": "🌤️ 18°C, Partiellement nuageux",
            "lyon": "☀️ 22°C, Ensoleillé",
            "marseille": "☀️ 25°C, Grand soleil",
            "londres": "🌧️ 12°C, Pluvieux",
            "new york": "⛅ 20°C, Nuageux",
            "tokyo": "🌤️ 19°C, Légèrement nuageux",
            "berlin": "☀️ 21°C, Ensoleillé"
        }
        
        city_lower = city.lower()
        if city_lower in weather_data:
            return f"🌤️ Météo à {city.title()}: {weather_data[city_lower]}"
        else:
            return f"🌤️ Météo simulée pour {city}: 20°C, Ensoleillé"

class WebSearchTool:
    name = "web_search"
    description = "Recherche des informations actuelles sur internet"
    
    def run(self, query: str) -> str:
        if not os.getenv("TAVILY_API_KEY"):
            return "❌ Clé API Tavily manquante. Ajoutez TAVILY_API_KEY dans .env"
        
        if not TAVILY_AVAILABLE:
            return "❌ Bibliothèque Tavily non installée. Exécutez: pip install tavily-python"
        
        try:
            tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
            response = tavily_client.search(query=query, max_results=3)
            
            if not response.get('results'):
                return f"❌ Aucun résultat trouvé pour: '{query}'"
            
            result_text = f"🔍 **Résultats pour '{query}':**\n\n"
            for i, result in enumerate(response['results'][:3], 1):
                title = result.get('title', 'Sans titre')
                content = result.get('content', 'Pas de contenu')
                url = result.get('url', '')
                
                result_text += f"**{i}. {title}**\n"
                result_text += f"{content[:150]}...\n"
                if url:
                    result_text += f"*Source: {url}*\n"
                result_text += "\n"
            
            return result_text
            
        except Exception as e:
            return f"❌ Erreur de recherche: {str(e)}"

# =============================================================================
# CLASSE PRINCIPALE DE L'ASSISTANT
# =============================================================================

class CompleteAssistant:
    def __init__(self):
        self.vector_store = None
        self.qa_chain = None
        self.agent = None
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True) if HAS_LANGCHAIN else None
        self.todo_list = self.load_todo_list()
        self.calendar_events = self.load_calendar()
        
        if HAS_LANGCHAIN:
            self.setup_rag()
            self.setup_agent()
    
    def load_todo_list(self):
        """Charge la liste de tâches depuis un fichier"""
        try:
            if os.path.exists("todo.json"):
                with open("todo.json", "r", encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return []
    
    def save_todo_list(self):
        """Sauvegarde la liste de tâches"""
        try:
            with open("todo.json", "w", encoding='utf-8') as f:
                json.dump(self.todo_list, f, ensure_ascii=False, indent=2)
        except Exception as e:
            st.sidebar.error(f"❌ Erreur sauvegarde todo: {e}")
    
    def load_calendar(self):
        """Charge les événements du calendrier"""
        try:
            if os.path.exists("calendar.json"):
                with open("calendar.json", "r", encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return []
    
    def save_calendar(self):
        """Sauvegarde le calendrier"""
        try:
            with open("calendar.json", "w", encoding='utf-8') as f:
                json.dump(self.calendar_events, f, ensure_ascii=False, indent=2)
        except Exception as e:
            st.sidebar.error(f"❌ Erreur sauvegarde calendrier: {e}")
    
    def load_documents(self, documents_path="documents"):
        """Charge les documents"""
        if not HAS_LANGCHAIN:
            return []
            
        documents = []
        
        if not os.path.exists(documents_path):
            os.makedirs(documents_path)
            return documents
        
        files = os.listdir(documents_path)
        if not files:
            return documents
        
        st.sidebar.info(f"📁 {len(files)} fichier(s) dans 'documents/'")
        
        for file in files:
            file_path = os.path.join(documents_path, file)
            try:
                if file.endswith('.pdf'):
                    loader = PyPDFLoader(file_path)
                    docs = loader.load()
                    documents.extend(docs)
                    st.sidebar.success(f"✅ PDF: {file}")
                elif file.endswith('.docx'):
                    loader = Docx2txtLoader(file_path)
                    docs = loader.load()
                    documents.extend(docs)
                    st.sidebar.success(f"✅ DOCX: {file}")
                elif file.endswith('.txt') or file.endswith('.md'):
                    loader = TextLoader(file_path, encoding='utf-8')
                    docs = loader.load()
                    documents.extend(docs)
                    st.sidebar.success(f"✅ TXT/MD: {file}")
                else:
                    st.sidebar.warning(f"⚠️ Format non supporté: {file}")
            except Exception as e:
                st.sidebar.error(f"❌ Erreur avec {file}: {str(e)}")
        
        return documents
    
    def setup_rag(self):
        """Configure RAG"""
        if not HAS_LANGCHAIN:
            return
        
        if not os.getenv("OPENAI_API_KEY"):
            st.sidebar.warning("❌ OPENAI_API_KEY manquante pour RAG")
            return
        
        documents = self.load_documents()
        
        if not documents:
            st.sidebar.info("📝 Aucun document trouvé. Ajoutez des fichiers dans le dossier 'documents/'")
            return
        
        try:
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            chunks = text_splitter.split_documents(documents)
            
            embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
            self.vector_store = Chroma.from_documents(chunks, embeddings, persist_directory="./chroma_db")
            
            llm = ChatOpenAI(
                temperature=0.7, 
                openai_api_key=os.getenv("OPENAI_API_KEY"),
                model="gpt-3.5-turbo"
            )
            
            self.qa_chain = ConversationalRetrievalChain.from_llm(
                llm=llm,
                retriever=self.vector_store.as_retriever(search_kwargs={"k": 3}),
                memory=self.memory,
                return_source_documents=True
            )
            
            st.sidebar.success(f"🔍 RAG activé - {len(chunks)} fragments")
            
        except Exception as e:
            st.sidebar.error(f"❌ Erreur RAG: {str(e)}")
    
    def todo_tool_function(self, action: str) -> str:
        """Fonction pour gérer la todo list"""
        action_lower = action.lower()
        
        # Voir les tâches
        if any(word in action_lower for word in ["voir", "afficher", "liste", "show", "display"]):
            if not self.todo_list:
                return "📝 **Liste de tâches vide**\nUtilisez 'ajouter [tâche]' pour ajouter une tâche."
            
            todo_text = "📝 **Votre liste de tâches:**\n\n"
            for i, task in enumerate(self.todo_list, 1):
                status = "✅" if task.get('done', False) else "⏳"
                todo_text += f"{i}. {status} {task['task']}\n"
            
            return todo_text
        
        # Ajouter une tâche
        elif any(word in action_lower for word in ["ajouter", "add", "nouveau", "new"]):
            task_text = action_lower.replace("ajouter", "").replace("add", "").replace("nouveau", "").replace("new", "").strip()
            if task_text:
                self.todo_list.append({"task": task_text, "done": False})
                self.save_todo_list()
                return f"✅ Tâche ajoutée: '{task_text}'"
            else:
                return "❌ Veuillez spécifier une tâche à ajouter. Exemple: 'ajouter Répondre aux emails'"
        
        # Marquer comme fait
        elif any(word in action_lower for word in ["terminer", "fait", "done", "complete"]):
            if not self.todo_list:
                return "❌ Aucune tâche à marquer comme terminée"
            
            # Essayer de trouver un numéro
            for word in action_lower.split():
                if word.isdigit():
                    task_num = int(word)
                    if 1 <= task_num <= len(self.todo_list):
                        self.todo_list[task_num-1]['done'] = True
                        self.save_todo_list()
                        return f"✅ Tâche {task_num} marquée comme terminée: '{self.todo_list[task_num-1]['task']}'"
            
            return "❌ Spécifiez le numéro de tâche. Exemple: 'terminer la tâche 1'"
        
        # Supprimer une tâche
        elif any(word in action_lower for word in ["supprimer", "delete", "remove"]):
            if not self.todo_list:
                return "❌ Aucune tâche à supprimer"
            
            for word in action_lower.split():
                if word.isdigit():
                    task_num = int(word)
                    if 1 <= task_num <= len(self.todo_list):
                        removed_task = self.todo_list.pop(task_num-1)
                        self.save_todo_list()
                        return f"✅ Tâche supprimée: '{removed_task['task']}'"
            
            return "❌ Spécifiez le numéro de tâche. Exemple: 'supprimer la tâche 1'"
        
        else:
            return "❌ Action non reconnue. Utilisez: 'voir', 'ajouter [tâche]', 'terminer [numéro]', 'supprimer [numéro]'"
    
    def calendar_tool_function(self, action: str) -> str:
        """Fonction pour gérer le calendrier"""
        action_lower = action.lower()
        
        # Voir le calendrier
        if any(word in action_lower for word in ["voir", "afficher", "calendrier", "agenda", "show"]):
            if not self.calendar_events:
                return "📅 **Calendrier vide**\nUtilisez 'ajouter événement' pour planifier."
            
            calendar_text = "📅 **Votre calendrier:**\n\n"
            for i, event in enumerate(self.calendar_events, 1):
                calendar_text += f"{i}. **{event['title']}**\n"
                calendar_text += f"   📅 {event['date']}\n"
                if event.get('time'):
                    calendar_text += f"   ⏰ {event['time']}\n"
                if event.get('description'):
                    calendar_text += f"   📝 {event['description']}\n"
                calendar_text += "\n"
            
            return calendar_text
        
        # Ajouter un événement
        elif any(word in action_lower for word in ["ajouter", "add", "nouveau", "new", "planifier"]):
            event_text = action_lower.replace("ajouter", "").replace("add", "").replace("nouveau", "").replace("new", "").replace("planifier", "").strip()
            if event_text:
                new_event = {
                    "title": event_text,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "time": "09:00",
                    "description": "Événement ajouté via l'assistant"
                }
                self.calendar_events.append(new_event)
                self.save_calendar()
                return f"✅ Événement ajouté: '{event_text}' pour aujourd'hui à 09:00"
            else:
                return "❌ Veuillez spécifier un événement. Exemple: 'ajouter Réunion équipe'"
        
        else:
            return "❌ Action non reconnue. Utilisez: 'voir calendrier' ou 'ajouter [événement]'"
    
    def rag_tool_function(self, question: str) -> str:
        """Fonction pour la recherche dans les documents"""
        if not self.qa_chain:
            return "❌ RAG non disponible. Aucun document chargé ou problème de configuration."
        
        try:
            result = self.qa_chain({"question": question})
            response = f"📄 **Réponse basée sur vos documents:**\n\n{result['answer']}"
            
            if 'source_documents' in result and result['source_documents']:
                sources = []
                for doc in result['source_documents'][:2]:
                    source = doc.metadata.get('source', 'Document')
                    sources.append(f"• {os.path.basename(source)}")
                
                if sources:
                    response += f"\n\n**Sources:**\n" + "\n".join(sources)
            
            return response
        except Exception as e:
            return f"❌ Erreur de recherche: {str(e)}"
    
    def setup_agent(self):
        """Configure l'agent"""
        if not HAS_LANGCHAIN:
            st.sidebar.error("❌ LangChain non disponible")
            return
        
        if not os.getenv("OPENAI_API_KEY"):
            st.sidebar.error("❌ OPENAI_API_KEY manquante")
            return
        
        try:
            llm = ChatOpenAI(
                temperature=0.7, 
                openai_api_key=os.getenv("OPENAI_API_KEY"),
                model="gpt-3.5-turbo"
            )
            
            # Créer les outils
            tools = []
            
            # Outil Calculatrice
            tools.append(Tool(
                name="calculator",
                description="Effectue des calculs mathématiques. Exemple: '2 + 2' ou '15 * 3.5'",
                func=CalculatorTool().run
            ))
            
            # Outil Météo
            tools.append(Tool(
                name="weather",
                description="Donne la météo d'une ville. Exemple: 'Paris' ou 'Lyon'",
                func=WeatherTool().run
            ))
            
            # Outil Recherche Web
            if os.getenv("TAVILY_API_KEY"):
                tools.append(Tool(
                    name="web_search",
                    description="Recherche des informations actuelles sur internet",
                    func=WebSearchTool().run
                ))
            
            # Outil Todo List
            tools.append(Tool(
                name="todo_list",
                description="Gère la liste de tâches. Utilisez: 'voir', 'ajouter [tâche]', 'terminer [numéro]', 'supprimer [numéro]'",
                func=self.todo_tool_function
            ))
            
            # Outil Calendrier
            tools.append(Tool(
                name="calendar",
                description="Gère le calendrier. Utilisez: 'voir' ou 'ajouter [événement]'",
                func=self.calendar_tool_function
            ))
            
            # Outil RAG si disponible
            if self.vector_store:
                tools.append(Tool(
                    name="document_search",
                    description="Recherche dans vos documents (PDF, DOCX, TXT, MD)",
                    func=self.rag_tool_function
                ))
            
            # Créer l'agent
            self.agent = initialize_agent(
                tools=tools,
                llm=llm,
                agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True,
                memory=self.memory,
                handle_parsing_errors=True
            )
            
            st.sidebar.success(f"🤖 Agent initialisé avec {len(tools)} outils")
            
        except Exception as e:
            st.sidebar.error(f"❌ Erreur lors de l'initialisation de l'agent: {str(e)}")
    
    def process_message(self, message: str) -> str:
        """Traite les messages"""
        if not self.agent:
            return "🤖 Agent non initialisé. Vérifiez la configuration (OpenAI API key et installation des dépendances)."
        
        try:
            response = self.agent.run(input=message)
            return response
        except Exception as e:
            return f"❌ Erreur: {str(e)}"

# =============================================================================
# APPLICATION STREAMLIT
# =============================================================================

def main():
    st.title("🤖 Assistant Complet RAG + Agents")
    st.markdown("**Recherche documents + Calculatrice + Météo + Recherche web + Todo + Calendrier**")
    
    # Vérifications d'environnement
    if not PYDANTIC_AVAILABLE:
        st.error("❌ Pydantic n'est pas installé. Exécutez: `pip install pydantic`")
    
    if not HAS_LANGCHAIN:
        st.error("""
        ❌ LangChain n'est pas correctement installé !
        
        Exécutez ces commandes :
        ```bash
        pip install langchain-core
        pip install langchain-community
        pip install langchain-openai
        pip install chromadb
        pip install python-docx
        pip install pydantic
        ```
        """)
    
    if not os.getenv("OPENAI_API_KEY"):
        st.error("🔑 OPENAI_API_KEY manquante")
        st.info("Créez un fichier `.env` avec : `OPENAI_API_KEY=votre_cle_api`")
    
    # Initialisation
    if "assistant" not in st.session_state:
        with st.spinner("🚀 Initialisation de l'assistant..."):
            st.session_state.assistant = CompleteAssistant()
    
    # Sidebar
    with st.sidebar:
        st.header("📊 Statut")
        
        if st.session_state.assistant.vector_store:
            st.success("✅ RAG activé")
        else:
            st.info("📝 RAG: ajoutez des fichiers dans 'documents/'")
            
        if st.session_state.assistant.agent:
            st.success("✅ Agent actif")
        else:
            st.error("❌ Agent non initialisé")
        
        st.header("🛠️ Outils Disponibles")
        st.write("• 🧮 Calculatrice")
        st.write("• 🌤️ Météo")
        if os.getenv("TAVILY_API_KEY"):
            st.write("• 🔎 Recherche web")
        st.write("• 📝 Todo list")
        st.write("• 📅 Calendrier")
        if st.session_state.assistant.vector_store:
            st.write("• 📚 Recherche documents")
        
        st.header("💡 Exemples")
        st.code("Calcule 125 * 48")
        st.code("Météo à Paris")
        if os.getenv("TAVILY_API_KEY"):
            st.code("Recherche actualités IA")
        st.code("Voir ma todo list")
        st.code("Ajouter tâche: Préparer réunion")
        st.code("Voir calendrier")
        
        if st.button("🔄 Redémarrer"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Chat
    if "messages" not in st.session_state:
        welcome_message = "👋 **Bonjour !** Je suis votre assistant avec plusieurs outils:\n\n"
        welcome_message += "• 🧮 Calculatrice\n• 🌤️ Météo\n"
        if os.getenv("TAVILY_API_KEY"):
            welcome_message += "• 🔎 Recherche web\n"
        welcome_message += "• 📝 Todo list\n• 📅 Calendrier\n"
        if st.session_state.assistant.vector_store:
            welcome_message += "• 📚 Recherche documents\n"
        welcome_message += "\nComment puis-je vous aider ?"
        
        st.session_state.messages = [{"role": "assistant", "content": welcome_message}]
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Tapez votre message ici..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("🤔 Réflexion..."):
                response = st.session_state.assistant.process_message(prompt)
                st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()