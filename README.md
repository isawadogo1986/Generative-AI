# Plateforme Financière Intelligente - Résumé
📋 Description
Application web Streamlit avec système multi-agents automatique spécialisé en analyse financière. L'IA détecte automatiquement l'agent le plus adapté à chaque question.

🎯 Fonctionnalités Principales
🤖 Agents Automatiques
Assistant Financier IA : Analyse documentaire et questions complexes

Calculatrices : Simple (2+3) et financière (intérêts, prêts)

Météo & Impacts : Données réeles + analyses économiques

Recherche Web : Actualités financières réelles

Calendrier Économique : Événements à venir

Simulateurs : Investissement et planification retraite

Envoi d'Emails : Intégration Gmail automatique

🚀 Fonctionnalités Clés
Détection automatique du type de question

Analyse de documents (PDF, DOCX, TXT, CSV, Excel)

Historique des conversations avec export JSON

Interface moderne et responsive

⚡ Démarrage Rapide
bash
# Installation
git clone <repository>
cd plateforme-financiere-intelligente
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sur Windows
pip install -r requirements.txt

# Configuration (.env)
OPENAI_API_KEY="votre-clé-openai"
GMAIL_APP_PASSWORD="votre-mot-de-passe"

# Lancement
streamlit run app.py
🔧 Configuration Essentielle
1. OpenAI API
Obtenez une clé sur platform.openai.com

Ajoutez OPENAI_API_KEY="sk-..." dans .env

2. Gmail App Password
Activez la vérification 2 facteurs

Générez un mot de passe d'application

Ajoutez GMAIL_APP_PASSWORD="..." dans .env

3. Documents
Créez un dossier documents/

Ajoutez vos fichiers financiers

💡 Exemples d'Utilisation
Questions courantes :

"Bonjour" → Agent conversationnel

"2+3" → Calculatrice simple

"Calculer intérêts 5000€ à 3%" → Calculatrice financière

"Envoyer analyse à client@email.com" → Envoi email automatique

"Analyser ce document" → Assistant IA avec contexte

🛠️ Architecture
Frontend : Streamlit

IA : OpenAI + LlamaIndex

Stockage : ChromaDB (vecteurs)

Email : SMTP Gmail

Documents : Dossier local documents/

🔒 Sécurité
Variables sensibles dans .env

Mots de passe d'application uniquement

Données stockées localement

🌟 Points Forts
✅ Détection automatique d'agents

✅ Aucune clé API nécessaire pour la météo (données simulées)

✅ Configuration email simplifiée

✅ Interface intuitive

✅ Export des résultats

Accès : http://localhost:8501 après lancement

Plateforme tout-en-un pour l'analyse financière assistée par IA