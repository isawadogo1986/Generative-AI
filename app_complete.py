import streamlit as st
import os
import json
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

# PREMIÈRE COMMANDE STREAMLIT
st.set_page_config(
    page_title="Assistant Complet RAG + 11 Agents",
    page_icon="🤖",
    layout="wide"
)

load_dotenv()

# =============================================================================
# AGENTS FINANCIERS SPÉCIALISÉS
# =============================================================================

class PortfolioAnalyzerAgent:
    def __init__(self):
        self.portfolio_data = self.load_portfolio()
    
    def load_portfolio(self):
        """Charge les données du portefeuille fictif"""
        return {
            "actions": [
                {"nom": "Apple", "symbol": "AAPL", "quantité": 10, "prix_achat": 150, "prix_actuel": 180},
                {"nom": "Microsoft", "symbol": "MSFT", "quantité": 5, "prix_achat": 300, "prix_actuel": 350},
                {"nom": "Tesla", "symbol": "TSLA", "quantité": 8, "prix_achat": 200, "prix_actuel": 220}
            ],
            "obligations": [
                {"nom": "Obligation France 10Y", "rendement": 2.5, "maturité": "2034"},
                {"nom": "Corporate Bond AAA", "rendement": 4.2, "maturité": "2030"}
            ],
            "liquidity": 5000
        }
    
    def analyze_performance(self) -> str:
        """Analyse la performance du portefeuille"""
        total_investi = 0
        total_actuel = 0
        
        for action in self.portfolio_data["actions"]:
            investi = action["quantité"] * action["prix_achat"]
            actuel = action["quantité"] * action["prix_actuel"]
            total_investi += investi
            total_actuel += actuel
        
        performance = ((total_actuel - total_investi) / total_investi) * 100
        
        analysis = "📊 **Analyse du Portefeuille**\n\n"
        analysis += f"• **Valeur totale**: {total_actuel:,.0f} €\n"
        analysis += f"• **Performance globale**: {performance:+.1f}%\n"
        analysis += f"• **Liquidités disponibles**: {self.portfolio_data['liquidity']:,.0f} €\n"
        
        # Top performers
        analysis += "\n**🎯 Top Performers:**\n"
        for action in self.portfolio_data["actions"]:
            perf_action = ((action["prix_actuel"] - action["prix_achat"]) / action["prix_achat"]) * 100
            analysis += f"• {action['nom']}: {perf_action:+.1f}%\n"
        
        return analysis
    
    def calculate_var(self, confidence_level: float = 0.95) -> str:
        """Calcule la Value at Risk (simulée)"""
        var_95 = -8.5
        var_99 = -12.3
        
        return f"⚡ **Value at Risk (VaR):**\n• Niveau 95%: {var_95}%\n• Niveau 99%: {var_99}%"
    
    def diversification_analysis(self) -> str:
        """Analyse la diversification du portefeuille"""
        sectors = {
            "Technologie": 60,
            "Automobile": 25, 
            "Obligations": 15
        }
        
        analysis = "🌐 **Analyse de Diversification**\n\n"
        for sector, percentage in sectors.items():
            analysis += f"• {sector}: {percentage}%\n"
        
        analysis += "\n**Recommandations:**\n"
        if sectors["Technologie"] > 50:
            analysis += "⚠️ Surpondération technologie - envisager de diversifier\n"
        else:
            analysis += "✅ Diversification adéquate\n"
            
        return analysis

class InvestmentSimulatorAgent:
    def simulate_investment(self, montant: float, duree_ans: int, rendement_annuel: float) -> str:
        """Simule un investissement avec intérêts composés"""
        try:
            capital_final = montant * (1 + rendement_annuel/100) ** duree_ans
            gain = capital_final - montant
            
            result = f"💰 **Simulation d'Investissement**\n\n"
            result += f"• **Capital initial**: {montant:,.0f} €\n"
            result += f"• **Durée**: {duree_ans} ans\n"
            result += f"• **Rendement annuel**: {rendement_annuel}%\n"
            result += f"• **Capital final**: {capital_final:,.0f} €\n"
            result += f"• **Gain total**: {gain:,.0f} €\n"
            
            # Tableau d'évolution
            result += "\n**📈 Évolution:**\n"
            for annee in range(1, min(6, duree_ans + 1)):
                capital_annee = montant * (1 + rendement_annuel/100) ** annee
                result += f"• Année {annee}: {capital_annee:,.0f} €\n"
            
            if duree_ans > 5:
                result += f"• ...\n• Année {duree_ans}: {capital_final:,.0f} €\n"
                
            return result
        except Exception as e:
            return f"❌ Erreur de simulation: {str(e)}"
    
    def calculate_rentabilite(self, prix_achat: float, prix_vente: float, dividendes: float = 0) -> str:
        """Calcule la rentabilité d'un investissement"""
        gain_capital = prix_vente - prix_achat
        rendement_capital = (gain_capital / prix_achat) * 100
        rendement_total = ((gain_capital + dividendes) / prix_achat) * 100
        
        return f"📈 **Rentabilité de l'Investissement:**\n• Gain en capital: {gain_capital:,.0f} € ({rendement_capital:+.1f}%)\n• Dividendes: {dividendes:,.0f} €\n• Rendement total: {rendement_total:+.1f}%"

class FinancialRatiosAgent:
    def calculate_ratios(self, chiffre_affaires: float, benefice_net: float, actifs: float, passifs: float) -> str:
        """Calcule les ratios financiers clés"""
        try:
            marge_nette = (benefice_net / chiffre_affaires) * 100
            roa = (benefice_net / actifs) * 100
            roe = (benefice_net / (actifs - passifs)) * 100
            dette_ratio = (passifs / actifs) * 100
            
            analysis = "📊 **Ratios Financiers**\n\n"
            analysis += f"• **Marge nette**: {marge_nette:.1f}%\n"
            analysis += f"• **Return on Assets (ROA)**: {roa:.1f}%\n"
            analysis += f"• **Return on Equity (ROE)**: {roe:.1f}%\n"
            analysis += f"• **Ratio d'endettement**: {dette_ratio:.1f}%\n"
            
            # Interprétation
            analysis += "\n**📋 Interprétation:**\n"
            if marge_nette > 15:
                analysis += "✅ Excellente profitabilité\n"
            elif marge_nette > 8:
                analysis += "⚠️ Profitabilité moyenne\n"
            else:
                analysis += "❌ Profitabilité faible\n"
                
            if dette_ratio < 50:
                analysis += "✅ Structure financière saine\n"
            else:
                analysis += "⚠️ Niveau d'endettement élevé\n"
                
            return analysis
        except Exception as e:
            return f"❌ Erreur de calcul: {str(e)}"

class RetirementPlannerAgent:
    def calculate_retirement(self, age_actuel: int, age_retraite: int, epargne_actuelle: float, 
                           epargne_mensuelle: float, rendement_annuel: float) -> str:
        """Calcule la préparation à la retraite"""
        try:
            annees_restantes = age_retraite - age_actuel
            mois_restants = annees_restantes * 12
            
            # Calcul de l'épargne future
            epargne_future = epargne_actuelle
            for mois in range(mois_restants):
                epargne_future = epargne_future * (1 + rendement_annuel/100/12) + epargne_mensuelle
            
            # Règle des 4% pour les retraits
            retrait_annuel = epargne_future * 0.04
            retrait_mensuel = retrait_annuel / 12
            
            result = "🏖️ **Planificateur de Retraite**\n\n"
            result += f"• **Âge actuel**: {age_actuel} ans\n"
            result += f"• **Âge de retraite**: {age_retraite} ans\n"
            result += f"• **Épargne actuelle**: {epargne_actuelle:,.0f} €\n"
            result += f"• **Épargne mensuelle**: {epargne_mensuelle:,.0f} €\n"
            result += f"• **Épargne à la retraite**: {epargne_future:,.0f} €\n"
            result += f"• **Retrait annuel sécurisé**: {retrait_annuel:,.0f} €\n"
            result += f"• **Retrait mensuel**: {retrait_mensuel:,.0f} €\n"
            
            # Recommandations
            result += "\n**💡 Recommandations:**\n"
            if retrait_mensuel < 2000:
                result += "⚠️ Envisagez d'augmenter votre épargne mensuelle\n"
            else:
                result += "✅ Niveau d'épargne adéquat pour une retraite confortable\n"
                
            return result
        except Exception as e:
            return f"❌ Erreur de calcul: {str(e)}"

class MarketAnalyzerAgent:
    def __init__(self):
        self.indices = {
            "CAC 40": {"valeur": 7500, "variation": +1.2, "secteur": "France"},
            "S&P 500": {"valeur": 4500, "variation": +0.8, "secteur": "USA"},
            "NASDAQ": {"valeur": 14000, "variation": +1.5, "secteur": "Technologie"},
            "DAX": {"valeur": 16000, "variation": +0.9, "secteur": "Allemagne"}
        }
    
    def get_market_overview(self) -> str:
        """Donne un aperçu des marchés"""
        overview = "🌍 **Aperçu des Marchés**\n\n"
        
        for indice, data in self.indices.items():
            variation_str = f"+{data['variation']}%" if data['variation'] >= 0 else f"{data['variation']}%"
            overview += f"• **{indice}**: {data['valeur']} ({variation_str})\n"
        
        # Tendances
        overview += "\n**📈 Tendances:**\n"
        positive_count = sum(1 for data in self.indices.values() if data['variation'] > 0)
        if positive_count >= 3:
            overview += "✅ Marchés globalement haussiers\n"
        else:
            overview += "⚠️ Marchés en consolidation\n"
            
        return overview
    
    def analyze_sector(self, secteur: str) -> str:
        """Analyse un secteur spécifique"""
        sectors_analysis = {
            "technologie": "📱 **Secteur Technologie**: Forte croissance, volatilité élevée. Opportunités dans l'IA et le cloud computing.",
            "énergie": "⚡ **Secteur Énergie**: Impacté par les prix des commodités. Transition vers les énergies renouvelables.",
            "santé": "🏥 **Secteur Santé**: Défensif, résilient en période de crise. Innovation biotech.",
            "finance": "🏦 **Secteur Finance**: Sensible aux taux d'intérêt. Digitalisation en cours."
        }
        
        secteur_lower = secteur.lower()
        if secteur_lower in sectors_analysis:
            return sectors_analysis[secteur_lower]
        else:
            return f"❌ Analyse non disponible pour le secteur {secteur}"

class EmailAgent:
    def __init__(self):
        self.email_config = self.load_email_config()
    
    def load_email_config(self):
        """Charge la configuration email depuis le fichier .env"""
        config = {
            "smtp_server": os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com"),
            "smtp_port": int(os.getenv("EMAIL_SMTP_PORT", "587")),
            "email_address": os.getenv("EMAIL_ADDRESS"),
            "email_password": os.getenv("EMAIL_PASSWORD"),
            "email_name": os.getenv("EMAIL_NAME", "Assistant Financier")
        }
        return config
    
    def send_email(self, recipient: str, subject: str, message: str, 
                  is_html: bool = False) -> str:
        """Envoie un email"""
        try:
            # Vérifier la configuration
            if not self.email_config["email_address"] or not self.email_config["email_password"]:
                return "❌ Configuration email manquante. Vérifiez EMAIL_ADDRESS et EMAIL_PASSWORD dans .env"
            
            # Créer le message
            msg = MIMEMultipart()
            msg['From'] = f"{self.email_config['email_name']} <{self.email_config['email_address']}>"
            msg['To'] = recipient
            msg['Subject'] = subject
            
            # Corps du message
            if is_html:
                msg.attach(MIMEText(message, 'html'))
            else:
                msg.attach(MIMEText(message, 'plain'))
            
            # Connexion et envoi
            with smtplib.SMTP(self.email_config["smtp_server"], self.email_config["smtp_port"]) as server:
                server.starttls()
                server.login(self.email_config["email_address"], self.email_config["email_password"])
                server.send_message(msg)
            
            return f"✅ Email envoyé à {recipient} avec succès!"
            
        except Exception as e:
            return f"❌ Erreur d'envoi d'email: {str(e)}"
    
    def send_portfolio_report(self, recipient: str) -> str:
        """Envoie un rapport de portefeuille par email"""
        portfolio_data = {
            'total_value': 125000.50,
            'performance': 8.7,
            'assets': [
                {'name': 'Apple (AAPL)', 'quantity': 10, 'value': 1800.00, 'performance': 12.5},
                {'name': 'Microsoft (MSFT)', 'quantity': 5, 'value': 1750.00, 'performance': 8.2},
            ],
            'recommendations': [
                "Envisager de prendre des bénéfices sur les positions les plus performantes",
                "Renforcer la diversification"
            ]
        }
        
        subject = f"📊 Rapport de Portefeuille - {datetime.now().strftime('%d/%m/%Y')}"
        
        # Créer le message HTML
        message = f"""
        <html>
        <body>
            <h1>📊 Rapport de Portefeuille</h1>
            <p>Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            
            <h2>Performance Globale</h2>
            <p><strong>Valeur totale:</strong> {portfolio_data['total_value']:,.2f} €</p>
            <p><strong>Performance:</strong> {portfolio_data['performance']:+.2f}%</p>
            
            <p><em>Ce rapport a été généré automatiquement par votre Assistant Financier.</em></p>
        </body>
        </html>
        """
        
        return self.send_email(recipient, subject, message, is_html=True)

# =============================================================================
# OUTILS DES 5 AGENTS DE BASE
# =============================================================================

class CalculatorAgent:
    def calculate(self, expression: str) -> str:
        """Agent Calculatrice - Effectue des calculs mathématiques"""
        try:
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
# ASSISTANT COMPLET AVEC 11 AGENTS
# =============================================================================

class CompleteAssistant:
    def __init__(self):
        # Initialiser les 11 agents
        self.calculator = CalculatorAgent()
        self.weather = WeatherAgent()
        self.web_search = WebSearchAgent()
        self.todo = TodoAgent()
        self.calendar = CalendarAgent()
        self.rag = RagAgent()
        
        # Nouveaux agents financiers
        self.portfolio_analyzer = PortfolioAnalyzerAgent()
        self.investment_simulator = InvestmentSimulatorAgent()
        self.financial_ratios = FinancialRatiosAgent()
        self.retirement_planner = RetirementPlannerAgent()
        self.market_analyzer = MarketAnalyzerAgent()
        
        # Agent Email
        self.email_agent = EmailAgent()
    
    def process_message(self, message: str) -> str:
        """Traite les messages en routant vers le bon agent"""
        message_lower = message.lower().strip()
        
        # 1. Agent Calculatrice (priorité haute pour les calculs)
        if any(op in message for op in ["+", "-", "*", "/"]) or any(word in message_lower for word in ["calcule", "calculer", "combien fait"]):
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
        
        # 6. Agent Analyseur de Portefeuille
        if any(word in message_lower for word in ["analyse portefeuille", "performance portefeuille", "diversification"]):
            if "diversification" in message_lower:
                return self.portfolio_analyzer.diversification_analysis()
            elif "var" in message_lower or "value at risk" in message_lower:
                return self.portfolio_analyzer.calculate_var()
            else:
                return self.portfolio_analyzer.analyze_performance()
        
        # 7. Agent Simulateur d'Investissement
        if any(word in message_lower for word in ["simuler investissement", "calculer rendement", "intérêts composés"]):
            if "rentabilité" in message_lower:
                numbers = re.findall(r'\d+', message)
                if len(numbers) >= 2:
                    return self.investment_simulator.calculate_rentabilite(
                        float(numbers[0]), float(numbers[1])
                    )
            return "💰 Utilisez: 'Simuler investissement 10000 10 7' pour 10.000€ sur 10 ans à 7%"
        
        # 8. Agent Ratios Financiers
        if any(word in message_lower for word in ["ratios financiers", "marge nette", "roe", "roa"]):
            numbers = re.findall(r'\d+', message)
            if len(numbers) >= 4:
                return self.financial_ratios.calculate_ratios(
                    float(numbers[0]), float(numbers[1]), float(numbers[2]), float(numbers[3])
                )
            return "📊 Utilisez: 'Calculer ratios 100000 15000 200000 80000' pour CA=100k, bénéfice=15k, actifs=200k, passifs=80k"
        
        # 9. Agent Planificateur Retraite
        if any(word in message_lower for word in ["retraite", "planification retraite", "épargne retraite"]):
            numbers = re.findall(r'\d+', message)
            if len(numbers) >= 5:
                return self.retirement_planner.calculate_retirement(
                    int(numbers[0]), int(numbers[1]), float(numbers[2]), float(numbers[3]), float(numbers[4])
                )
            return "🏖️ Utilisez: 'Planifier retraite 35 65 50000 500 6' pour 35→65 ans, 50k€ épargne, 500€/mois, 6% rendement"
        
        # 10. Agent Analyseur de Marché
        if any(word in message_lower for word in ["marché", "indices", "cac 40", "s&p 500"]):
            if any(word in message_lower for word in ["technologie", "énergie", "santé", "finance"]):
                for secteur in ["technologie", "énergie", "santé", "finance"]:
                    if secteur in message_lower:
                        return self.market_analyzer.analyze_sector(secteur)
            return self.market_analyzer.get_market_overview()
        
        # 11. Agent Email
        if any(word in message_lower for word in ["envoyer email", "envoyer un email", "envoie email"]):
            return self.handle_email_command(message)
        
        if "rapport portefeuille" in message_lower and "envoyer" in message_lower:
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', message)
            if email_match:
                email = email_match.group(0)
                return self.email_agent.send_portfolio_report(email)
            else:
                return "❌ Veuillez spécifier une adresse email valide"
        
        # 12. Agent RAG (par défaut pour les autres questions)
        return self.rag.search_documents(message)
    
    def extract_math_expression(self, message: str) -> str:
        """Extrait une expression mathématique du message"""
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
    
    def handle_email_command(self, message: str) -> str:
        """Gère les commandes d'envoi d'email"""
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', message)
        if not email_match:
            return "❌ Aucune adresse email valide trouvée dans le message"
        
        recipient = email_match.group(0)
        
        # Extraire le sujet
        sujet_match = re.search(r'sujet\s+(.+?)(?:\s+message|\s+corps|$)', message, re.IGNORECASE)
        subject = "Message de votre Assistant Financier"
        if sujet_match:
            subject = sujet_match.group(1).strip()
        
        # Extraire le message
        corps_match = re.search(r'(?:message|corps)\s+(.+)', message, re.IGNORECASE)
        if corps_match:
            message_text = corps_match.group(1).strip()
            return self.email_agent.send_email(recipient, subject, message_text)
        else:
            return f"❌ Veuillez spécifier un message. Format: 'envoyer email à {recipient} sujet [sujet] message [votre message]'"

# =============================================================================
# APPLICATION STREAMLIT
# =============================================================================

def main():
    st.title("🤖 Assistant Complet RAG + 11 Agents")
    st.markdown("**Calculatrice • Météo • Recherche Web • Todo • Calendrier • Recherche Documents • 5 Agents Financiers • Email**")
    
    # Vérifications
    if not os.getenv("OPENAI_API_KEY"):
        st.error("🔑 OPENAI_API_KEY manquante")
        st.info("Ajoutez votre clé OpenAI dans un fichier .env")
    
    # Initialisation
    if "assistant" not in st.session_state:
        with st.spinner("🚀 Initialisation des 11 agents..."):
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
        
        # Nouveaux agents financiers
        st.success("✅ Analyseur Portefeuille")
        st.success("✅ Simulateur Investissement")
        st.success("✅ Ratios Financiers")
        st.success("✅ Planificateur Retraite")
        st.success("✅ Analyseur Marché")
        
        if os.getenv("EMAIL_ADDRESS") and os.getenv("EMAIL_PASSWORD"):
            st.success("✅ Agent Email")
        else:
            st.warning("⚠️ Agent Email (configuration manquante)")
        
        st.header("🛠️ 11 Agents Disponibles")
        st.write("• 🧮 Calculatrice")
        st.write("• 🌤️ Météo")
        st.write("• 🔎 Recherche web")
        st.write("• 📝 Todo list")
        st.write("• 📅 Calendrier")
        st.write("• 📚 Recherche documents")
        st.write("• 📊 Analyseur Portefeuille")
        st.write("• 💰 Simulateur Investissement")
        st.write("• 📈 Ratios Financiers")
        st.write("• 🏖️ Planificateur Retraite")
        st.write("• 🌍 Analyseur Marché")
        st.write("• 📧 Agent Email")
        
        st.header("💡 Exemples par Agent")
        
        st.write("**🧮 Calculatrice:**")
        st.code("Calcule 125 * 48")
        
        st.write("**🌤️ Météo:**")
        st.code("Météo à Paris")
        
        st.write("**🔎 Recherche Web:**")
        st.code("Recherche actualités IA")
        
        st.write("**📊 Analyseur Portefeuille:**")
        st.code("Analyse mon portefeuille")
        st.code("Diversification de mon portefeuille")
        
        st.write("**💰 Simulateur Investissement:**")
        st.code("Simuler investissement 10000 10 7")
        st.code("Calculer rentabilité 150 180 50")
        
        st.write("**📈 Ratios Financiers:**")
        st.code("Calculer ratios 100000 15000 200000 80000")
        
        st.write("**🏖️ Planificateur Retraite:**")
        st.code("Planifier retraite 35 65 50000 500 6")
        
        st.write("**🌍 Analyseur Marché:**")
        st.code("Aperçu des marchés")
        st.code("Analyse secteur technologie")
        
        st.write("**📧 Agent Email:**")
        st.code("Envoyer email à test@email.com sujet Rapport message Voici le rapport")
        st.code("Envoyer rapport portefeuille à client@banque.com")
        
        if st.button("🔄 Nouvelle Session"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Chat
    if "messages" not in st.session_state:
        welcome_message = """**🤖 Assistant Complet avec 11 Agents**

Je dispose de plusieurs spécialistes pour vous aider :

• 🧮 **Calculatrice** - Calculs mathématiques
• 🌤️ **Météo** - Météo des villes  
• 🔎 **Recherche Web** - Informations actuelles
• 📝 **Todo List** - Gestion des tâches
• 📅 **Calendrier** - Événements et planning
• 📚 **Recherche Documents** - Analyse de vos fichiers
• 📊 **Analyseur Portefeuille** - Performance et diversification
• 💰 **Simulateur Investissement** - Projections financières
• 📈 **Ratios Financiers** - Analyse d'entreprise
• 🏖️ **Planificateur Retraite** - Préparation financière
• 🌍 **Analyseur Marché** - Tendances et indices
• 📧 **Agent Email** - Envoi de rapports

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