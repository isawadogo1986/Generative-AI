import streamlit as st
import os
import json
import re
from datetime import datetime
from dotenv import load_dotenv

# PREMIÈRE COMMANDE STREAMLIT
st.set_page_config(
    page_title="Assistant Complet RAG + 5 Agents",
    page_icon="🤖",
    layout="wide" 
)

load_dotenv()

# =============================================================================
# OUTILS DES 5 AGENTS
# =============================================================================

class CalculatorAgent:
    def calculate(self, expression: str) -> str:
        """Agent Calculatrice - Effectue des calculs mathématiques"""
        try:
            # Sécurité : seulement caractères mathématiques autorisés
            allowed_chars = set("0123456789+-*/.() ")
            if not all(c in allowed_chars for c in expression):
                return "❌ Caractères non autorisés. Utilisez seulement: chiffres, +, -, *, /, ., (, )"
            
            expression = expression.replace(',', '.')
            result = eval(expression)
            return f"🧮 {expression} = {result}"
        except Exception as e:
            return f"❌ Erreur de calcul: {str(e)}"

class WeatherAgent:
    def get_weather(self, city: str) -> str:
        """Agent Météo - Donne la météo d'une ville"""
        weather_data = {
            "paris": "🌤️ 18°C, Partiellement nuageux",
            "lyon": "☀️ 22°C, Ensoleillé",
            "marseille": "☀️ 25°C, Grand soleil",
            "londres": "🌧️ 12°C, Pluvieux",
            "new york": "⛅ 20°C, Nuageux",
            "tokyo": "🌤️ 19°C, Légèrement nuageux",
            "berlin": "☀️ 21°C, Ensoleillé",
            "madrid": "🌤️ 24°C, Partiellement nuageux"
        }
        
        city_lower = city.lower().strip()
        if city_lower in weather_data:
            return f"🌤️ Météo à {city.title()}: {weather_data[city_lower]}"
        else:
            return f"🌤️ Météo simulée pour {city}: 20°C, Ensoleillé"

class WebSearchAgent:
    def search_web(self, query: str) -> str:
        """Agent Recherche Web - Recherche des informations actuelles"""
        if not os.getenv("TAVILY_API_KEY"):
            return "❌ Clé API Tavily manquante. Ajoutez TAVILY_API_KEY dans .env"
        
        try:
            from tavily import TavilyClient
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
            
        except ImportError:
            return "❌ Bibliothèque Tavily non installée. Exécutez: pip install tavily-python"
        except Exception as e:
            return f"❌ Erreur de recherche: {str(e)}"

class TodoAgent:
    def __init__(self):
        self.todo_list = self.load_todo_list()
    
    def load_todo_list(self):
        """Charge la liste de tâches"""
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
    
    def view_tasks(self) -> str:
        """Affiche toutes les tâches"""
        if not self.todo_list:
            return "📝 **Liste de tâches vide**\nUtilisez 'ajouter [tâche]' pour ajouter une tâche."
        
        todo_text = "📝 **Votre liste de tâches:**\n\n"
        for i, task in enumerate(self.todo_list, 1):
            status = "✅" if task.get('done', False) else "⏳"
            todo_text += f"{i}. {status} {task['task']}\n"
        
        return todo_text
    
    def add_task(self, task_description: str) -> str:
        """Ajoute une nouvelle tâche"""
        if not task_description.strip():
            return "❌ Veuillez spécifier une tâche à ajouter."
        
        self.todo_list.append({"task": task_description.strip(), "done": False})
        self.save_todo_list()
        return f"✅ Tâche ajoutée: '{task_description.strip()}'"
    
    def complete_task(self, task_number: int) -> str:
        """Marque une tâche comme terminée"""
        if not self.todo_list:
            return "❌ Aucune tâche à marquer comme terminée"
        
        if 1 <= task_number <= len(self.todo_list):
            self.todo_list[task_number-1]['done'] = True
            self.save_todo_list()
            task_name = self.todo_list[task_number-1]['task']
            return f"✅ Tâche {task_number} terminée: '{task_name}'"
        else:
            return f"❌ Numéro de tâche invalide. Choisissez entre 1 et {len(self.todo_list)}"
    
    def delete_task(self, task_number: int) -> str:
        """Supprime une tâche"""
        if not self.todo_list:
            return "❌ Aucune tâche à supprimer"
        
        if 1 <= task_number <= len(self.todo_list):
            removed_task = self.todo_list.pop(task_number-1)
            self.save_todo_list()
            return f"✅ Tâche supprimée: '{removed_task['task']}'"
        else:
            return f"❌ Numéro de tâche invalide. Choisissez entre 1 et {len(self.todo_list)}"

class CalendarAgent:
    def __init__(self):
        self.events = self.load_calendar()
    
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
                json.dump(self.events, f, ensure_ascii=False, indent=2)
        except Exception as e:
            st.sidebar.error(f"❌ Erreur sauvegarde calendrier: {e}")
    
    def view_events(self) -> str:
        """Affiche tous les événements"""
        if not self.events:
            return "📅 **Calendrier vide**\nUtilisez 'ajouter [événement]' pour planifier."
        
        calendar_text = "📅 **Votre calendrier:**\n\n"
        for i, event in enumerate(self.events, 1):
            calendar_text += f"{i}. **{event['title']}**\n"
            calendar_text += f"   📅 {event['date']}\n"
            if event.get('time'):
                calendar_text += f"   ⏰ {event['time']}\n"
            if event.get('description'):
                calendar_text += f"   📝 {event['description']}\n"
            calendar_text += "\n"
        
        return calendar_text
    
    def add_event(self, event_description: str) -> str:
        """Ajoute un nouvel événement"""
        if not event_description.strip():
            return "❌ Veuillez spécifier un événement."
        
        new_event = {
            "title": event_description.strip(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": "09:00",
            "description": "Événement ajouté via l'assistant"
        }
        self.events.append(new_event)
        self.save_calendar()
        return f"✅ Événement ajouté: '{event_description.strip()}' pour aujourd'hui à 09:00"

# =============================================================================
# AGENT RAG AVEC LLAMAINDEX
# =============================================================================

class RagAgent:
    def __init__(self):
        self.query_engine = None
        self.setup_rag()
    
    def setup_rag(self):
        """Configure la recherche RAG avec LlamaIndex"""
        try:
            from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
            from llama_index.llms.openai import OpenAI
            from llama_index.embeddings.openai import OpenAIEmbedding
            
            # Vérifier la clé API
            if not os.getenv("OPENAI_API_KEY"):
                return
                
            # Vérifier les documents
            documents_path = "documents"
            if not os.path.exists(documents_path) or not os.listdir(documents_path):
                return
            
            # Charger les documents
            reader = SimpleDirectoryReader(documents_path)
            documents = reader.load_data()
            
            # Configurer LLM et embeddings
            llm = OpenAI(
                model="gpt-3.5-turbo",
                api_key=os.getenv("OPENAI_API_KEY")
            )
            
            embed_model = OpenAIEmbedding(
                api_key=os.getenv("OPENAI_API_KEY")
            )
            
            # Créer l'index et le moteur de requête
            index = VectorStoreIndex.from_documents(
                documents, 
                embed_model=embed_model
            )
            
            self.query_engine = index.as_query_engine(llm=llm)
            
            st.sidebar.success(f"📚 RAG activé - {len(documents)} documents")
            
        except ImportError as e:
            st.sidebar.warning("📚 LlamaIndex non installé - RAG désactivé")
        except Exception as e:
            st.sidebar.error(f"❌ Erreur RAG: {e}")
    
    def search_documents(self, question: str) -> str:
        """Recherche dans les documents avec RAG"""
        if not self.query_engine:
            return "❌ RAG non disponible. Ajoutez des documents dans 'documents/' et vérifiez l'installation."
        
        try:
            response = self.query_engine.query(question)
            return f"📄 **Réponse basée sur vos documents:**\n\n{response}"
        except Exception as e:
            return f"❌ Erreur de recherche: {str(e)}"

# =============================================================================
# ASSISTANT COMPLET AVEC 6 AGENTS
# =============================================================================

class CompleteAssistant:
    def __init__(self):
        # Initialiser les 6 agents
        self.calculator = CalculatorAgent()
        self.weather = WeatherAgent()
        self.web_search = WebSearchAgent()
        self.todo = TodoAgent()
        self.calendar = CalendarAgent()
        self.rag = RagAgent()
    
    def process_message(self, message: str) -> str:
        """Traite les messages en routant vers le bon agent"""
        message_lower = message.lower().strip()
        
        # 1. Agent Calculatrice (priorité haute pour les calculs)
        if any(op in message for op in ["+", "-", "*", "/"]) or any(word in message_lower for word in ["calcule", "calculer", "combien fait"]):
            # Extraire l'expression mathématique
            math_expression = self.extract_math_expression(message)
            if math_expression:
                return self.calculator.calculate(math_expression)
        
        # 2. Agent Météo
        if any(word in message_lower for word in ["météo", "weather", "temps à", "température à"]):
            city = self.extract_city(message_lower)
            if city:
                return self.weather.get_weather(city)
            else:
                return "❌ Veuillez spécifier une ville. Exemple: 'Météo à Paris'"
        
        # 3. Agent Recherche Web
        if any(word in message_lower for word in ["recherche", "search", "cherche", "trouve"]) and len(message) > 10:
            return self.web_search.search_web(message)
        
        # 4. Agent Todo List
        if any(word in message_lower for word in ["todo", "tâche", "task"]):
            return self.handle_todo_command(message_lower)
        
        # 5. Agent Calendrier
        if any(word in message_lower for word in ["calendrier", "agenda", "événement", "rendez-vous"]):
            return self.handle_calendar_command(message_lower)
        
        # 6. Agent RAG (par défaut pour les autres questions)
        return self.rag.search_documents(message)
    
    def extract_math_expression(self, message: str) -> str:
        """Extrait une expression mathématique du message"""
        # Supprimer les mots non mathématiques
        cleaned = re.sub(r'[^\d+\-*/.() ]', '', message)
        return cleaned.strip() if cleaned.strip() else message
    
    def extract_city(self, message: str) -> str:
        """Extrait le nom de ville du message"""
        for word in ["météo", "weather", "temps à", "température à"]:
            message = message.replace(word, "")
        return message.strip()
    
    def handle_todo_command(self, message: str) -> str:
        """Gère les commandes todo list"""
        if any(word in message for word in ["voir", "afficher", "liste", "show"]):
            return self.todo.view_tasks()
        elif any(word in message for word in ["ajouter", "add", "nouveau"]):
            task_text = re.sub(r'(ajouter|add|nouveau)', '', message, flags=re.IGNORECASE).strip()
            return self.todo.add_task(task_text)
        elif any(word in message for word in ["terminer", "fait", "done"]):
            numbers = re.findall(r'\d+', message)
            if numbers:
                return self.todo.complete_task(int(numbers[0]))
            return "❌ Spécifiez un numéro de tâche"
        elif any(word in message for word in ["supprimer", "delete", "remove"]):
            numbers = re.findall(r'\d+', message)
            if numbers:
                return self.todo.delete_task(int(numbers[0]))
            return "❌ Spécifiez un numéro de tâche"
        else:
            return self.todo.view_tasks()
    
    def handle_calendar_command(self, message: str) -> str:
        """Gère les commandes calendrier"""
        if any(word in message for word in ["voir", "afficher", "show"]):
            return self.calendar.view_events()
        elif any(word in message for word in ["ajouter", "add", "nouveau"]):
            event_text = re.sub(r'(ajouter|add|nouveau)', '', message, flags=re.IGNORECASE).strip()
            return self.calendar.add_event(event_text)
        else:
            return self.calendar.view_events()

# =============================================================================
# APPLICATION STREAMLIT
# =============================================================================

def main():
    st.title("🤖 Assistant Complet RAG + 5 Agents")
    st.markdown("**Calculatrice • Météo • Recherche Web • Todo • Calendrier • Recherche Documents**")
    
    # Vérifications
    if not os.getenv("OPENAI_API_KEY"):
        st.error("🔑 OPENAI_API_KEY manquante")
        st.info("Ajoutez votre clé OpenAI dans un fichier .env")
    
    # Initialisation
    if "assistant" not in st.session_state:
        with st.spinner("🚀 Initialisation des 6 agents..."):
            st.session_state.assistant = CompleteAssistant()
    
    # Sidebar
    with st.sidebar:
        st.header("📊 Statut des Agents")
        
        # Vérifier le statut de chaque agent
        st.success("✅ Calculatrice")
        st.success("✅ Météo")
        
        if os.getenv("TAVILY_API_KEY"):
            st.success("✅ Recherche Web")
        else:
            st.warning("⚠️ Recherche Web (Tavily non configuré)")
        
        st.success("✅ Todo List")
        st.success("✅ Calendrier")
        
        if hasattr(st.session_state.assistant.rag, 'query_engine') and st.session_state.assistant.rag.query_engine:
            st.success("✅ Recherche Documents (RAG)")
        else:
            st.info("📚 RAG: ajoutez des fichiers dans 'documents/'")
        
        st.header("🛠️ 6 Agents Disponibles")
        st.write("• 🧮 Calculatrice")
        st.write("• 🌤️ Météo")
        st.write("• 🔎 Recherche web")
        st.write("• 📝 Todo list")
        st.write("• 📅 Calendrier")
        st.write("• 📚 Recherche documents")
        
        st.header("💡 Exemples par Agent")
        
        st.write("**🧮 Calculatrice:**")
        st.code("Calcule 125 * 48")
        st.code("Combien fait (15 + 27) * 3")
        
        st.write("**🌤️ Météo:**")
        st.code("Météo à Paris")
        st.code("Quel temps fait-il à Londres ?")
        
        st.write("**🔎 Recherche Web:**")
        st.code("Recherche actualités IA")
        st.code("Trouve des infos sur le marché financier")
        
        st.write("**📝 Todo List:**")
        st.code("Voir ma todo list")
        st.code("Ajouter tâche: Préparer réunion")
        st.code("Terminer la tâche 1")
        
        st.write("**📅 Calendrier:**")
        st.code("Voir calendrier")
        st.code("Ajouter événement: Réunion équipe")
        
        st.write("**📚 Recherche Documents:**")
        st.code("Quelle allocation d'actifs recommandez-vous ?")
        st.code("Quels sont les critères de sélection des actions ?")
        
        if st.button("🔄 Nouvelle Session"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Chat
    if "messages" not in st.session_state:
        welcome_message = """**🤖 Assistant Complet avec 6 Agents**

Je dispose de plusieurs spécialistes pour vous aider :

• 🧮 **Calculatrice** - Calculs mathématiques
• 🌤️ **Météo** - Météo des villes  
• 🔎 **Recherche Web** - Informations actuelles
• 📝 **Todo List** - Gestion des tâches
• 📅 **Calendrier** - Événements et planning
• 📚 **Recherche Documents** - Analyse de vos fichiers

**Comment puis-je vous aider ?**"""
        
        st.session_state.messages = [{"role": "assistant", "content": welcome_message}]
    
    # Afficher l'historique
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Input utilisateur
    if prompt := st.chat_input("Tapez votre message ici..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("🤔 Analyse en cours..."):
                response = st.session_state.assistant.process_message(prompt)
                st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()