🚀 Plateforme Financière Multi-Agents Intelligente
Une plateforme complète d'intelligence artificielle pour l'analyse financière, intégrant plusieurs agents spécialisés capables de répondre automatiquement aux besoins des utilisateurs.

📋 Table des Matières
Architecture

Fonctionnalités

Dépendances

Installation

Configuration

Utilisation

Structure du Projet

Dépannage

🏗️ Architecture
Diagramme d'Architecture
text
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Interface     │    │   Système de     │    │   Base de       │
│   Streamlit     │◄──►│   Détection      │◄──►│   Connaissances │
│                 │    │   d'Agents       │    │   (Documents)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │
         │                        │
         ▼                        ▼
┌─────────────────┐    ┌─────────────────────────────────────┐
│   Historique    │    │            Agents Spécialisés       │
│   des Sessions  │    │                                     │
└─────────────────┘    ├─────────────────────────────────────┤
                       │  • 🤖 Assistant Financier IA        │
                       │  • 🧮 Calculatrice Simple           │
                       │  • 🧮 Calculatrice Financière       │
                       │  • 🌤️ Météo & Impacts Économiques  │
                       │  • 🔍 Recherche Web Financière      │
                       │  • 📅 Calendrier Économique         │
                       │  • 💹 Simulateur d'Investissement   │
                       │  • 🏖️ Planificateur de Retraite     │
                       │  • 📧 Agent d'Envoi d'Email         │
                       └─────────────────────────────────────┘
Composants Principaux
Interface Utilisateur : Application Streamlit avec navigation intuitive

Système de Détection d'Agents : IA qui route automatiquement vers l'agent approprié

Base de Connaissances : Documents financiers indexés via LlamaIndex

Agents Spécialisés : 9 agents métier pour différents besoins financiers

Gestion d'État : Persistance des sessions et historique des conversations

🌟 Fonctionnalités
Agents Disponibles
Agent	Icône	Description
Assistant Conversationnel	👋	Gère les salutations et questions simples
Calculatrice Simple	🧮	Effectue des calculs mathématiques basiques
Assistant Financier IA	🤖	Analyse approfondie des documents financiers
Calculatrice Financière	🧮	Calculs d'intérêts, prêts, mensualités
Météo & Impacts	🌤️	Données météo et analyses d'impacts économiques
Recherche Web	🔍	Actualités et tendances financières
Calendrier Économique	📅	Événements économiques à venir
Simulateur Investissement	💹	Projections de capital et simulations
Planificateur Retraite	🏖️	Calculs de retraite et plans d'épargne
Envoi d'Email	📧	Envoi d'emails professionnels via Gmail OAuth2
Détection Intelligente
Le système détecte automatiquement l'intention derrière chaque question et route vers l'agent le plus approprié :

Salutations : "Bonjour", "Merci", "Au revoir"

Calculs simples : "2+3", "combien font 15*8"

Questions financières : Analyse de documents, ratios, performances

Envoi d'emails : "envoyer un email", "contactez-moi"

📦 Dépendances
Dépendances Principales
txt
streamlit>=1.28.0
openai>=1.3.0
llama-index>=0.9.0
python-dotenv>=1.0.0
pandas>=2.0.0
numpy>=1.24.0
requests>=2.31.0
chromadb>=0.4.0
yfinance==0.2.18
python-dateutil==2.8.2
Dépendances Optionnelles (Email)
txt
google-api-python-client>=2.100.0
google-auth-httplib2>=0.1.0
google-auth-oauthlib>=1.0.0
Versions Python Testées
Python 3.9

Python 3.10

Python 3.11

🚀 Installation
1. Cloner le Repository
bash
git clone <votre-repository>
cd plateforme-financiere-ia
2. Créer un Environnement Virtuel
bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
3. Installer les Dépendances
bash
pip install -r requirements.txt
4. Configuration de l'Environnement
Créez un fichier .env à la racine du projet :

env
# Clé API OpenAI (obligatoire)
OPENAI_API_KEY=votre_cle_api_openai_ici

# Token OAuth Gmail (optionnel - pour l'envoi d'emails)
GMAIL_OAUTH_ACCESS_TOKEN=votre_token_oauth_ici

# Clé API Météo (optionnel - pour les données météo réelles)
OPENWEATHER_API_KEY=votre_cle_meteo_ici
5. Préparer les Documents
Créez un dossier documents/ et ajoutez vos fichiers financiers :

bash
mkdir documents
# Ajoutez vos PDF, DOCX, CSV, etc. dans le dossier documents/
⚙️ Configuration
Configuration OpenAI
Obtenez une clé API sur OpenAI Platform

Ajoutez-la au fichier .env

Configuration Gmail OAuth2 (Optionnel)
Aller sur Google OAuth Playground

Sélectionner l'API : Cherchez et sélectionnez https://mail.google.com

Autoriser les scopes : Cliquez sur "Authorize APIs"

Échanger le code : Cliquez sur "Exchange authorization code for tokens"

Copier le token : Ajoutez-le dans votre fichier .env

Structure des Documents Supportés
📄 PDF (rapports financiers, états comptables)

📝 DOCX (documents Word)

📊 CSV (données financières)

📋 Excel (feuilles de calcul)

📄 TXT (documents texte)

🎯 Utilisation
Lancement de l'Application
bash
streamlit run app_complete_financier.py
L'application sera accessible sur http://localhost:8501

Exemples de Questions
🤖 Assistant Financier IA
"Analysez la performance d'InnovTech SA sur les 3 dernières années"

"Comparez les marges EBITDA des entreprises technologiques et pharmaceutiques"

"Quels sont les ratios de solvabilité d'IssaKoffi & Frères ?"

🧮 Calculs
"2+3" → Calcul simple

"Calculer les intérêts sur 5000€ à 4% pendant 5 ans"

"Quelle serait la mensualité d'un prêt de 200000€ à 3.5% sur 25 ans ?"

📧 Emails
"Envoyer un rapport financier à client@entreprise.com"

Utiliser les templates prédéfinis pour différents types d'emails

📈 Simulations
"Simuler un investissement de 10000€ avec apport mensuel de 500€"

"Planifier ma retraite à 65 ans avec un revenu actuel de 50000€"

Workflow Typique
Chargement des Documents : Les documents sont automatiquement indexés au démarrage

Question Utilisateur : Posez votre question dans l'interface

Détection Automatique : L'IA identifie l'agent le plus approprié

Traitement : L'agent spécialisé génère la réponse

Historique : Toutes les interactions sont sauvegardées et exportables

📁 Structure du Projet
text
plateforme-financiere-ia/
├── app_complete_financier.py      # Application principale
├── generation_rapports.py         # Module de génération de rapports
├── requirements.txt               # Dépendances Python
├── .env                          # Variables d'environnement
├── .gitignore                    # Fichiers ignorés par Git
├── documents/                    # Dossier des documents financiers
│   ├── rapport_annuel_*.pdf
│   ├── rapport_trimestriel_*.pdf
│   └── guides_*.md
├── temp_docs/                    # Documents temporaires (auto-généré)
└── README.md                     # Ce fichier
🔧 Dépannage
Problèmes Courants
❌ "Clé API OpenAI non configurée"
Solution : Vérifiez que votre clé API OpenAI est correctement définie dans le fichier .env

❌ "Aucun document trouvé"
Solution : Assurez-vous que le dossier documents/ existe et contient des fichiers supportés

❌ "Erreur de connexion Gmail"
Solution :

Vérifiez que le token OAuth est valide et non expiré

Régénérez un nouveau token sur OAuth Playground

Vérifiez que les scopes Gmail sont autorisés

❌ "Module non trouvé"
Solution : Réinstallez les dépendances :

bash
pip install -r requirements.txt
Optimisation des Performances
Indexation des Documents : L'indexation initiale peut prendre du temps pour de gros documents

Token OpenAI : Utilisez gpt-3.5-turbo pour des réponses rapides, gpt-4 pour des analyses complexes

Mémoire : L'historique des conversations est limité à 4000 tokens

Sécurité
🔒 Variables d'Environnement : Les clés API sont stockées de manière sécurisée

🔒 Token OAuth : Les tokens Gmail ne sont pas persistés dans l'application

🔒 Documents : Les fichiers sont traités localement, pas d'envoi vers des serveurs externes

📊 Fonctionnalités Avancées
Export des Données
📥 Export JSON : Téléchargez l'historique complet des conversations

📊 Graphiques : Visualisations interactives des simulations financières

📋 Rapports : Génération automatique de rapports structurés

Personnalisation
Prompts Personnalisés : Modifiez DETAILED_PROMPT pour adapter le style des réponses

Templates Email : Ajoutez vos propres templates d'email professionnels

Seuils d'Alerte : Personnalisez les seuils pour les analyses de risque

🤝 Contribution
Les contributions sont les bienvenues ! Pour contribuer :

Forkez le projet

Créez une branche pour votre fonctionnalité (git checkout -b feature/nouvelle-fonctionnalite)

Committez vos changements (git commit -m 'Ajout nouvelle fonctionnalité')

Pushez la branche (git push origin feature/nouvelle-fonctionnalite)

Ouvrez une Pull Request

📄 Licence
Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

🙏 Remerciements
OpenAI pour les modèles de langue GPT

Streamlit pour le framework d'application web

LlamaIndex pour l'indexation des documents

Google pour l'API Gmail et OAuth2

💡 Astuce : Pour des performances optimales, organisez vos documents financiers par type (rapports annuels, trimestriels, études sectorielles) dans le dossier documents/.

🚀 Prêt à démarrer ? Lancez streamlit run app_complete_financier.py et explorez la puissance de l'IA financière !