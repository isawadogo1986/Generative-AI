import streamlit as st
import os
from dotenv import load_dotenv
import openai
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.settings import Settings
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
import chromadb
from typing import Optional
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import tempfile
import shutil
import json
import math
import yfinance as yf
from dateutil.relativedelta import relativedelta
import re
import smtplib
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# Charger les variables d'environnement
load_dotenv()

# Configuration des prompts détaillés
DETAILED_PROMPT = """
En tant qu'expert financier senior, fournissez une analyse approfondie et structurée.
Structurez systématiquement votre réponse comme suit :

📊 **ANALYSE DÉTAILLÉE :**
- Examinez chaque aspect de manière systématique et méthodique
- Présentez les données brutes, calculs intermédiaires et méthodologies utilisées
- Analysez les tendances historiques, ratios clés et indicateurs de performance
- Identifiez les forces, faiblesses, opportunités et menaces de manière objective
- Fournissez des comparaisons sectorielles et des benchmarks lorsque disponibles

🔍 **OBSERVATIONS CLÉS :**
- Synthétisez les points saillants de l'analyse détaillée
- Soulignez les éléments nécessitant une attention particulière
- Présentez les écarts par rapport aux attentes ou aux standards du secteur
- Identifiez les facteurs de risque et les opportunités sous-estimées

✅ **CONCLUSION ET RECOMMANDATIONS :**
- Synthèse argumentée basée sur l'analyse préalable
- Recommandations actionnables hiérarchisées par priorité
- Perspectives à court, moyen et long terme
- Scénarios alternatifs et sensibilité aux hypothèses

Utilisez un langage professionnel mais accessible. Fournissez des chiffres précis, pourcentages, et références sectorielles. Justifiez systématiquement vos conclusions par des éléments d'analyse concrets.
"""

# Fonction de génération de réponse améliorée
def generate_enhanced_response(query, context, chat_engine):
    """Génère une réponse détaillée et structurée"""
    
    enhanced_query = f"""
    Question: {query}
    
    Contexte: {context}
    
    Veuillez fournir une analyse financière structurée selon le format demandé, avec analyse détaillée avant toute conclusion.
    """
    
    try:
        # Utilisation du chat engine avec le prompt système
        response = chat_engine.chat(enhanced_query)
        return str(response)
    except Exception as e:
        return f"Erreur lors de la génération de la réponse: {str(e)}"

# ============================================================================
# FONCTIONS POUR RÉPONSES SIMPLES ET CALCULS
# ============================================================================

def gerer_salutations(question):
    """Gère les salutations et questions simples"""
    question_lower = question.lower().strip()
    
    salutations = {
        "bonjour": "Bonjour ! 👋 Je suis votre assistant financier IA. En quoi puis-je vous aider aujourd'hui ?",
        "salut": "Salut ! 😊 Je suis là pour vous assister dans vos analyses financières. Quelle est votre question ?",
        "hello": "Hello ! 🤗 Comment puis-je vous aider avec vos besoins financiers ?",
        "coucou": "Coucou ! 😄 Je suis votre expert financier virtuel. Que souhaitez-vous savoir ?",
        "bonsoir": "Bonsoir ! 🌙 Je suis à votre disposition pour des analyses financières.",
        "bonne nuit": "Bonne nuit ! 😴 N'hésitez pas à me consulter demain pour vos questions financières.",
        "merci": "Je vous en prie ! 👍 N'hésitez pas si vous avez d'autres questions.",
        "au revoir": "Au revoir ! 👋 À bientôt pour de nouvelles analyses financières.",
        "bye": "Bye ! 😊 Revenez quand vous voulez pour des conseils financiers.",
        "comment ça va": "Je vais très bien, merci ! 😊 Prêt à vous aider avec vos analyses financières.",
        "ça va": "Très bien, merci ! 😄 En quoi puis-je vous assister aujourd'hui ?"
    }
    
    for mot, reponse in salutations.items():
        if mot in question_lower:
            return reponse
    
    return None

def effectuer_calcul_simple(question):
    """Effectue des calculs mathématiques simples"""
    # Nettoyer la question pour les calculs
    question_propre = question.lower().replace('=', '').replace('?', '').strip()
    
    # Détecter les calculs simples (chiffres et opérateurs basiques)
    pattern_calcul = r'^[\d\s\+\-\*\/\(\)\.]+$'
    
    # Expressions régulières pour différents types de calculs
    patterns = [
        r'combien font (\d+)\s*\+\s*(\d+)',
        r'calculer (\d+)\s*\+\s*(\d+)',
        r'(\d+)\s*\+\s*(\d+)',
        r'(\d+)\s*\-\s*(\d+)',
        r'(\d+)\s*\*\s*(\d+)',
        r'(\d+)\s*\/\s*(\d+)',
        r'quelle est la somme de (\d+) et (\d+)',
        r'additionne (\d+) et (\d+)',
        r'soustrais (\d+) de (\d+)',
        r'multiplie (\d+) par (\d+)',
        r'divise (\d+) par (\d+)'
    ]
    
    try:
        # Essayer d'évaluer directement si c'est une expression mathématique simple
        if re.match(pattern_calcul, question_propre):
            resultat = eval(question_propre)
            return f"🧮 **Calcul :** {question_propre} = **{resultat}**"
        
        # Vérifier les patterns spécifiques
        for pattern in patterns:
            match = re.search(pattern, question_propre)
            if match:
                nombres = [float(x) for x in match.groups()]
                
                if '+' in question_propre or 'somme' in question_propre or 'additionne' in question_propre:
                    resultat = sum(nombres)
                    return f"🧮 **Addition :** {nombres[0]} + {nombres[1]} = **{resultat}**"
                
                elif '-' in question_propre or 'soustrais' in question_propre:
                    resultat = nombres[1] - nombres[0] if 'soustrais' in question_propre else nombres[0] - nombres[1]
                    return f"🧮 **Soustraction :** {nombres[0]} - {nombres[1]} = **{resultat}**"
                
                elif '*' in question_propre or 'multiplie' in question_propre:
                    resultat = nombres[0] * nombres[1]
                    return f"🧮 **Multiplication :** {nombres[0]} × {nombres[1]} = **{resultat}**"
                
                elif '/' in question_propre or 'divise' in question_propre:
                    if nombres[1] == 0:
                        return "❌ **Erreur :** Division par zéro impossible"
                    resultat = nombres[0] / nombres[1]
                    return f"🧮 **Division :** {nombres[0]} ÷ {nombres[1]} = **{resultat}**"
    
    except Exception as e:
        return None
    
    return None

def reponse_par_defaut(question):
    """Fournit une réponse par défaut pour les questions non reconnues"""
    reponses_amicales = [
        "Je suis spécialisé dans l'analyse financière. Pouvez-vous reformuler votre question en lien avec la finance, l'investissement ou l'analyse de documents financiers ?",
        "En tant qu'assistant financier, je peux vous aider avec l'analyse de rapports financiers, les calculs d'investissement, ou les conseils stratégiques. Quelle est votre question ?",
        "Je me concentre sur les sujets financiers. Avez-vous une question sur l'analyse d'entreprises, la gestion de portefeuille ou les tendances de marché ?",
        "Pour une meilleure assistance, pourriez-vous préciser votre question en rapport avec la finance ou l'analyse économique ?"
    ]
    
    return np.random.choice(reponses_amicales)

# ============================================================================
# FONCTIONS D'ENVOI D'EMAIL CORRIGÉES (MOT DE PASSE D'APPLICATION)
# ============================================================================

def envoyer_email_smtp(destinataire, sujet, message, piece_jointe=None):
    """
    Envoie un email via Gmail en utilisant le mot de passe d'application
    Utilise l'adresse erimondh7@gmail.com comme expéditeur
    """
    try:
        # Récupérer le mot de passe d'application depuis les variables d'environnement
        app_password = os.getenv("GMAIL_APP_PASSWORD")
        expediteur = "erimondh7@gmail.com"
        
        if not app_password:
            return False, "Mot de passe d'application Gmail non configuré. Veuillez configurer GMAIL_APP_PASSWORD dans votre .env"
        
        # Nettoyer le mot de passe (enlever les espaces)
        app_password_clean = app_password.replace(" ", "")
        
        # Configuration du serveur SMTP Gmail
        smtp_server = "smtp.gmail.com"
        port = 587  # Port pour TLS
        
        # Création du message
        msg = MIMEMultipart()
        msg['From'] = expediteur
        msg['To'] = destinataire
        msg['Subject'] = sujet
        
        # Ajout du message texte
        msg.attach(MIMEText(message, 'plain', 'utf-8'))
        
        # Gestion de la pièce jointe
        if piece_jointe is not None:
            fichier_data = piece_jointe.getvalue()
            part = MIMEApplication(fichier_data, Name=piece_jointe.name)
            part['Content-Disposition'] = f'attachment; filename="{piece_jointe.name}"'
            msg.attach(part)
        
        # Connexion sécurisée au serveur SMTP
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()  # Activation de la connexion sécurisée TLS
        server.login(expediteur, app_password_clean)
        
        # Envoi de l'email
        text = msg.as_string()
        server.sendmail(expediteur, destinataire, text)
        server.quit()
        
        return True, f"✅ Email envoyé avec succès à {destinataire}"
        
    except smtplib.SMTPAuthenticationError:
        return False, "❌ Erreur d'authentification. Vérifiez le mot de passe d'application Gmail."
    except smtplib.SMTPException as e:
        return False, f"❌ Erreur SMTP: {str(e)}"
    except Exception as e:
        return False, f"❌ Erreur lors de l'envoi: {str(e)}"

def traiter_demande_email(question, reponse_ia=None):
    """
    Traite les demandes d'envoi d'email dans les questions
    Retourne un tuple (success, message, doit_envoyer)
    """
    question_lower = question.lower()
    
    # Mots-clés pour détecter les demandes d'email
    mots_email = ["envoyer", "envoie", "email", "courriel", "mail", "envoyez"]
    
    if not any(mot in question_lower for mot in mots_email):
        return False, "", False
    
    try:
        # Extraction de l'adresse email avec regex
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, question)
        
        if not emails:
            return False, "❌ Aucune adresse email valide trouvée dans votre demande.", False
        
        destinataire = emails[0]
        
        # Extraction du sujet
        sujet_match = re.search(r'sujet[:\s]+([^\n\.\?]+)', question_lower)
        if sujet_match:
            sujet = sujet_match.group(1).strip().title()
        else:
            # Sujet par défaut basé sur le contexte
            if "analyse" in question_lower or "rapport" in question_lower:
                sujet = "Analyse Financière"
            elif "recommandation" in question_lower:
                sujet = "Recommandations d'Investissement"
            else:
                sujet = "Message de votre Assistant Financier"
        
        # Détermination du contenu
        if reponse_ia:
            contenu = reponse_ia
        else:
            # Extraction du contenu spécifique si fourni
            contenu_match = re.search(r'contenu[:\s]+([^\n]+)', question_lower)
            if contenu_match:
                contenu = contenu_match.group(1).strip()
            else:
                contenu = "Veuillez trouver ci-joint les informations demandées."
        
        # Envoi de l'email
        success, resultat = envoyer_email_smtp(destinataire, sujet, contenu)
        
        if success:
            return True, f"✅ Email envoyé avec succès à {destinataire}\nSujet: {sujet}", True
        else:
            return False, f"❌ Échec de l'envoi: {resultat}", True
            
    except Exception as e:
        return False, f"❌ Erreur lors du traitement de la demande d'email: {str(e)}", True

# ============================================================================
# AGENTS SPÉCIALISÉS
# ============================================================================

def agent_calculatrice(question):
    """Agent calculatrice financière - répond aux questions de calcul"""
    st.subheader("🧮 Calculatrice Financière")
    
    # D'abord vérifier les calculs simples
    calcul_simple = effectuer_calcul_simple(question)
    if calcul_simple:
        st.success(calcul_simple)
        return
    
    # Si pas de calcul simple, traiter comme calcul financier
    if any(mot in question.lower() for mot in ["intérêt", "composé", "capitalisation"]):
        # Calcul d'intérêts composés
        try:
            montants = [float(s) for s in re.findall(r'\d+', question) if float(s) > 0]
            capital = montants[0] if montants else 1000
            taux = 5.0
            duree = 10
            
            montant_final = capital * (1 + taux/100) ** duree
            interets = montant_final - capital
            
            response = f"""
            **Calcul d'intérêts composés:**
            - Capital initial: **{capital:,.2f} €**
            - Taux annuel: **{taux}%**
            - Durée: **{duree} ans**
            - Capital final: **{montant_final:,.2f} €**
            - Intérêts perçus: **{interets:,.2f} €**
            """
            st.success(response)
            
        except Exception as e:
            st.error(f"Erreur dans le calcul: {str(e)}")
            
    elif any(mot in question.lower() for mot in ["prêt", "mensualité", "emprunt"]):
        # Calcul de prêt
        try:
            montant = 100000
            taux = 3.0
            annees = 20
            
            taux_mensuel = taux / 100 / 12
            nb_mensualites = annees * 12
            mensualite = (montant * taux_mensuel) / (1 - (1 + taux_mensuel) ** -nb_mensualites)
            cout_total = mensualite * nb_mensualites
            
            response = f"""
            **Calcul de prêt immobilier:**
            - Montant: **{montant:,.0f} €**
            - Taux annuel: **{taux}%**
            - Durée: **{annees} ans**
            - Mensualité: **{mensualite:,.2f} €**
            - Coût total: **{cout_total:,.0f} €**
            - Intérêts totaux: **{cout_total - montant:,.0f} €**
            """
            st.success(response)
            
        except Exception as e:
            st.error(f"Erreur dans le calcul: {str(e)}")
    
    else:
        st.info("""
        **Calculatrice Financière - Utilisation:**
        Posez des questions comme:
        - "Calculer les intérêts composés sur 1000€ à 5% sur 10 ans"
        - "Quelle serait la mensualité pour un prêt de 100000€ à 3% sur 20 ans?"
        - Ou des calculs simples: "2+3", "15*8", etc.
        """)

def agent_meteo(question):
    """Agent météo pour impacts économiques"""
    st.subheader("🌤️ Météo & Impacts Économiques")
    
    # Extraction de la ville de la question
    villes = ["paris", "londres", "new york", "tokyo", "singapour", "francfort"]
    ville_trouvee = None
    for ville in villes:
        if ville in question.lower():
            ville_trouvee = ville
            break
    
    ville = ville_trouvee or "Paris"
    
    try:
        # Simulation de données météo
        st.success(f"""
        **Météo à {ville.title()}:**
        - Température: **15°C**
        - Conditions: **partiellement nuageux**
        - Humidité: **65%**
        - Vent: **12 km/h**
        """)
        
        # Analyse des impacts économiques
        st.info("""
        **Impacts économiques possibles:**
        - 🛒 **Commerce:** Conditions favorables pour le retail
        - ☀️ **Énergie:** Demande stable en énergie
        - 🚗 **Transport:** Conditions normales
        - 🏭 **Construction:** Bonnes conditions pour les travaux
        """)
        
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données météo: {str(e)}")

def agent_recherche_web(question):
    """Agent de recherche web financière"""
    st.subheader("🔍 Recherche Web Financière")
    
    # Simulation de résultats de recherche basés sur la question
    st.info(f"🔍 Recherche de: '{question}'")
    
    resultats_simules = [
        {
            "titre": "Marchés financiers - Actualités récentes", 
            "source": "Financial Times", 
            "date": "Aujourd'hui",
            "resume": "Les marchés européens affichent une stabilité remarquable malgré les incertitudes géopolitiques."
        },
        {
            "titre": "Analyse sectorielle - Technologies", 
            "source": "Bloomberg", 
            "date": "Hier",
            "resume": "Le secteur technologique continue sa croissance avec une attention particulière sur l'IA."
        },
        {
            "titre": "Indicateurs économiques clés", 
            "source": "Reuters", 
            "date": "Cette semaine",
            "resume": "L'inflation montre des signes de modération tandis que la croissance reste résiliente."
        },
    ]
    
    for i, resultat in enumerate(resultats_simules):
        with st.expander(f"📰 {resultat['titre']}"):
            st.write(f"**Source:** {resultat['source']}")
            st.write(f"**Date:** {resultat['date']}")
            st.write(f"**Résumé:** {resultat['resume']}")

def agent_calendrier(question):
    """Agent calendrier économique"""
    st.subheader("📅 Calendrier Économique")
    
    aujourdhui = datetime.now()
    
    # Événements économiques simulés
    evenements = [
        {"date": aujourdhui + timedelta(days=1), "evenement": "Publication IPC Zone Euro", "impact": "Élevé", "pays": "🇪🇺 UE"},
        {"date": aujourdhui + timedelta(days=3), "evenement": "Décision taux BCE", "impact": "Très élevé", "pays": "🇪🇺 UE"},
        {"date": aujourdhui + timedelta(days=7), "evenement": "Compte-rendu FED", "impact": "Très élevé", "pays": "🇺🇸 USA"},
        {"date": aujourdhui + timedelta(days=10), "evenement": "Chiffre du chômage France", "impact": "Moyen", "pays": "🇫🇷 France"},
        {"date": aujourdhui + timedelta(days=14), "evenement": "Publication PIB trimestriel", "impact": "Élevé", "pays": "🇩🇪 Allemagne"},
    ]
    
    st.subheader("📊 Événements à venir (15 jours)")
    
    for event in evenements:
        with st.container():
            col1, col2, col3, col4 = st.columns([1, 3, 2, 1])
            with col1:
                st.write(event["pays"])
            with col2:
                st.write(f"**{event['evenement']}**")
            with col3:
                st.write(event["date"].strftime("%d/%m/%Y"))
            with col4:
                if event["impact"] == "Très élevé":
                    st.error("🔴")
                elif event["impact"] == "Élevé":
                    st.warning("🟠")
                else:
                    st.info("🟢")
            st.markdown("---")

def agent_simulateur_investissement(question):
    """Agent simulateur d'investissement"""
    st.subheader("💹 Simulateur d'Investissement")
    
    # Paramètres par défaut basés sur la question
    capital = 10000
    apport_mensuel = 500
    duree = 20
    rendement = 7.0
    
    # Simulation de projection
    capital_courant = capital
    data = []
    
    for annee in range(1, duree + 1):
        for mois in range(12):
            capital_courant *= (1 + rendement/100/12)
            capital_courant += apport_mensuel
        data.append({
            "Année": annee,
            "Capital": capital_courant,
            "Apports cumulés": capital + apport_mensuel * 12 * annee
        })
    
    df = pd.DataFrame(data)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Capital final", f"{df.iloc[-1]['Capital']:,.0f} €")
    with col2:
        st.metric("Apports totaux", f"{df.iloc[-1]['Apports cumulés']:,.0f} €")
    with col3:
        plus_value = df.iloc[-1]['Capital'] - df.iloc[-1]['Apports cumulés']
        st.metric("Plus-value", f"{plus_value:,.0f} €")
    
    st.line_chart(df.set_index('Année'))

def agent_planificateur_retraite(question):
    """Agent planificateur de retraite"""
    st.subheader("🏖️ Planificateur de Retraite")
    
    # Paramètres par défaut
    age_actuel = 40
    age_retraite = 65
    revenu_actuel = 50000
    epargne_actuelle = 50000
    epargne_annuelle = 10000
    rendement = 5.0
    
    # Calculs
    annees_epargne = age_retraite - age_actuel
    capital_projete = epargne_actuelle
    
    for annee in range(annees_epargne):
        capital_projete *= (1 + rendement/100)
        capital_projete += epargne_annuelle
    
    revenu_souhaite = revenu_actuel * 0.7  # 70% du revenu actuel
    capital_necessaire = revenu_souhaite * 20  # règle des 20x
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Capital projeté", f"{capital_projete:,.0f} €")
    with col2:
        st.metric("Capital nécessaire", f"{capital_necessaire:,.0f} €")
    with col3:
        ecart = capital_projete - capital_necessaire
        if ecart >= 0:
            st.success(f"Excédent: {ecart:,.0f} €")
        else:
            st.error(f"Déficit: {abs(ecart):,.0f} €")
    
    # Recommandations
    if ecart < 0:
        st.error("**Recommandations:**")
        st.write("- Augmenter l'épargne annuelle")
        st.write("- Revoir l'âge de départ à la retraite")
        st.write("- Optimiser le rendement des placements")
    else:
        st.success("**Votre plan retraite est sur la bonne voie!**")

def detecter_agent(question):
    """
    Détecte automatiquement l'agent approprié en fonction de la question
    """
    question_lower = question.lower()
    
    # Vérifier d'abord les salutations
    if gerer_salutations(question):
        return "salutation"
    
    # Vérifier les calculs simples
    if effectuer_calcul_simple(question):
        return "calcul_simple"
    
    # Mots-clés pour chaque agent
    calcul_mots = ["calcul", "intérêt", "prêt", "taux", "mensualité", "emprunt", "capitalisation", "mathématique", "combien font"]
    meteo_mots = ["météo", "temps", "climat", "température", "météorologique"]
    recherche_mots = ["actualité", "nouvelle", "news", "recherche", "information", "dernier", "récents"]
    calendrier_mots = ["calendrier", "événement", "date", "quand", "programme", "agenda", "prochain"]
    investissement_mots = ["simuler", "investissement", "placement", "rendement", "projet", "capital", "épargne", "bourse"]
    retraite_mots = ["retraite", "pension", "vieillesse", "senior", "avenir", "prévoyance"]
    
    # Calcul des scores
    scores = {
        "calculatrice": sum(1 for mot in calcul_mots if mot in question_lower),
        "meteo": sum(1 for mot in meteo_mots if mot in question_lower),
        "recherche": sum(1 for mot in recherche_mots if mot in question_lower),
        "calendrier": sum(1 for mot in calendrier_mots if mot in question_lower),
        "investissement": sum(1 for mot in investissement_mots if mot in question_lower),
        "retraite": sum(1 for mot in retraite_mots if mot in question_lower),
    }
    
    # Trouver l'agent avec le score le plus élevé
    agent_max = max(scores, key=scores.get)
    score_max = scores[agent_max]
    
    # Si aucun mot-clé n'est détecté, utiliser l'assistant financier par défaut
    if score_max == 0:
        return "assistant"
    
    return agent_max

# Fonction pour charger les documents depuis le dossier "documents"
def charger_documents():
    """Charge les documents depuis le dossier 'documents' et crée l'index vectoriel"""
    documents_path = "documents"
    
    if not os.path.exists(documents_path):
        st.warning(f"⚠️ Le dossier '{documents_path}' n'existe pas. Création du dossier...")
        os.makedirs(documents_path)
        return None
    
    try:
        # Vérifier s'il y a des documents dans le dossier
        fichiers = [f for f in os.listdir(documents_path) if os.path.isfile(os.path.join(documents_path, f))]
        if not fichiers:
            st.warning(f"📁 Aucun document trouvé dans le dossier '{documents_path}'. Veuillez ajouter des documents.")
            return None
        
        st.info(f"📚 Chargement de {len(fichiers)} document(s) depuis le dossier '{documents_path}'...")
        
        # Charger les documents avec LlamaIndex
        documents = SimpleDirectoryReader(documents_path).load_data()
        
        # Créer l'index vectoriel
        index = VectorStoreIndex.from_documents(documents)
        
        st.success("✅ Documents chargés et indexés avec succès!")
        return index
        
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement des documents: {str(e)}")
        return None

# ============================================================================
# APPLICATION STREAMLIT PRINCIPALE
# ============================================================================

# Configuration de l'application Streamlit
st.set_page_config(
    page_title="Plateforme Financière Intelligente",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Interface utilisateur principale
st.title("🚀 Plateforme Financière Intelligente")
st.markdown("""
<div style="background-color:#f0f2f6;padding:20px;border-radius:10px;margin-bottom:20px;">
<h3 style="color:#1f77b4;margin:0;">Système Multi-Agents Automatique</h3>
<p style="margin:10px 0 0 0;color:#555;">
L'IA choisit automatiquement l'agent le plus adapté à votre question
</p>
</div>
""", unsafe_allow_html=True)

# Initialisation de l'index vectoriel
if "vector_index" not in st.session_state:
    with st.spinner("🔍 Chargement des documents depuis le dossier 'documents'..."):
        st.session_state.vector_index = charger_documents()

# Gestion de l'historique des conversations
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_question" not in st.session_state:
    st.session_state.user_question = ""
if "agent_actuel" not in st.session_state:
    st.session_state.agent_actuel = "assistant"

# Section de chat principale
st.header("💬 Posez votre question financière")

# Input utilisateur
user_question = st.text_area(
    "Votre question:",
    value=st.session_state.user_question,
    height=100,
    placeholder="Exemple: 'Bonjour', '2+3', 'Calculer les intérêts sur 5000€', 'Envoyer cette analyse à client@email.com' ou 'Quelles sont les actualités financières?'..."
)

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    analyze_btn = st.button("🚀 Analyser", type="primary", use_container_width=True)
with col2:
    clear_btn = st.button("🗑️ Effacer", use_container_width=True)
with col3:
    export_btn = st.button("📁 Exporter", use_container_width=True)

if clear_btn:
    st.session_state.chat_history = []
    st.session_state.user_question = ""
    st.session_state.agent_actuel = "assistant"
    st.rerun()

# Fonction principale d'analyse
if analyze_btn and user_question:
    # Détection automatique de l'agent
    agent_detecte = detecter_agent(user_question)
    st.session_state.agent_actuel = agent_detecte
    
    # Affichage de l'agent détecté
    noms_agents = {
        "assistant": "🤖 Assistant Financier IA",
        "salutation": "👋 Assistant Conversationnel",
        "calcul_simple": "🧮 Calculatrice Simple",
        "calculatrice": "🧮 Calculatrice Financière", 
        "meteo": "🌤️ Météo & Impacts Économiques",
        "recherche": "🔍 Recherche Web Financière",
        "calendrier": "📅 Calendrier Économique",
        "investissement": "💹 Simulateur d'Investissement",
        "retraite": "🏖️ Planificateur de Retraite"
    }
    
    # Traitement selon l'agent détecté
    if agent_detecte == "salutation":
        reponse = gerer_salutations(user_question)
        st.success(reponse)
        
        # Ajout à l'historique
        st.session_state.chat_history.append({
            "question": user_question,
            "answer": reponse,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "agent": "Assistant Conversationnel"
        })
    
    elif agent_detecte == "calcul_simple":
        reponse = effectuer_calcul_simple(user_question)
        st.success(reponse)
        
        # Ajout à l'historique
        st.session_state.chat_history.append({
            "question": user_question,
            "answer": reponse,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "agent": "Calculatrice Simple"
        })
    
    elif agent_detecte == "assistant":
        # Vérifier que la clé API OpenAI est configurée
        if not os.getenv("OPENAI_API_KEY"):
            st.error("🔑 La clé API OpenAI n'est pas configurée. Veuillez la définir dans le fichier .env")
            st.stop()
        
        try:
            with st.spinner("🔍 Analyse en cours par l'Assistant Financier IA..."):
                # Configuration LlamaIndex
                from llama_index.llms.openai import OpenAI as LlamaOpenAI
                from llama_index.embeddings.openai import OpenAIEmbedding
                
                # Configuration des paramètres
                Settings.llm = LlamaOpenAI(
                    model="gpt-3.5-turbo",
                    temperature=0.1,
                    max_tokens=2000
                )
                Settings.embed_model = OpenAIEmbedding()
                
                # Initialisation de la mémoire de chat
                memory = ChatMemoryBuffer.from_defaults(token_limit=4000)
                
                # Utiliser l'index vectoriel chargé depuis les documents
                if st.session_state.vector_index:
                    chat_engine = st.session_state.vector_index.as_chat_engine(
                        chat_mode="context",
                        memory=memory,
                        system_prompt=DETAILED_PROMPT
                    )
                    
                    # Génération de la réponse améliorée
                    response = generate_enhanced_response(
                        query=user_question,
                        context="Documents financiers chargés depuis le dossier 'documents'",
                        chat_engine=chat_engine
                    )
                else:
                    # Réponse sans contexte de documents
                    response = "ℹ️ Analyse basée sur les connaissances générales (aucun document spécifique chargé).\n\n"
                    
                    # Utiliser OpenAI directement pour une réponse de base
                    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                    completion = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": DETAILED_PROMPT},
                            {"role": "user", "content": user_question}
                        ]
                    )
                    response += completion.choices[0].message.content
                
                # Vérifier s'il y a une demande d'envoi d'email
                success_email, message_email, doit_envoyer = traiter_demande_email(user_question, response)
                
                if doit_envoyer:
                    if success_email:
                        response += f"\n\n---\n{message_email}"
                    else:
                        response += f"\n\n---\n{message_email}"
                
                # Ajout à l'historique
                st.session_state.chat_history.append({
                    "question": user_question,
                    "answer": response,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "agent": "Assistant Financier IA"
                })
                
                st.success(response)
                
        except Exception as e:
            st.error(f"❌ Erreur lors de l'analyse: {str(e)}")
    
    else:
        # Exécution de l'agent spécialisé
        st.info(f"**Agent détecté automatiquement:** {noms_agents[agent_detecte]}")
        
        # Appel de l'agent approprié
        if agent_detecte == "calculatrice":
            agent_calculatrice(user_question)
        elif agent_detecte == "meteo":
            agent_meteo(user_question)
        elif agent_detecte == "recherche":
            agent_recherche_web(user_question)
        elif agent_detecte == "calendrier":
            agent_calendrier(user_question)
        elif agent_detecte == "investissement":
            agent_simulateur_investissement(user_question)
        elif agent_detecte == "retraite":
            agent_planificateur_retraite(user_question)
        
        # Ajout à l'historique
        st.session_state.chat_history.append({
            "question": user_question,
            "answer": f"Traité par {noms_agents[agent_detecte]}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "agent": noms_agents[agent_detecte]
        })
    
    st.session_state.user_question = ""

# Affichage de l'historique des conversations
st.markdown("---")
st.subheader("📝 Historique des Interactions")

for i, chat in enumerate(reversed(st.session_state.chat_history)):
    with st.container():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**Question ({chat['timestamp']}):**")
        with col2:
            st.markdown(f"*{chat['agent']}*")
        
        st.info(chat['question'])
        
        if chat['agent'] in ["Assistant Financier IA", "Assistant Conversationnel", "Calculatrice Simple"]:
            st.markdown(f"**Réponse:**")
            st.success(chat['answer'])
        
        st.markdown("---")

# Fonction d'export
if export_btn and st.session_state.chat_history:
    export_data = {
        "export_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "analysis_sessions": st.session_state.chat_history
    }
    
    st.download_button(
        label="📥 Télécharger l'historique complet (JSON)",
        data=json.dumps(export_data, ensure_ascii=False, indent=2),
        file_name=f"historique_financier_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

# Section d'information sur les agents
with st.sidebar.expander("🤖 Agents Disponibles"):
    st.markdown("""
    ### 🎯 Agents Automatiques:
    
    **👋 Assistant Conversationnel**
    - Salutations et questions simples
    - Réponses courtoises
    
    **🧮 Calculatrice Simple**
    - Calculs mathématiques basiques
    - Additions, soustractions, multiplications, divisions
    
    **🤖 Assistant Financier IA**
    - Analyse de documents
    - Questions complexes
    - Recommandations stratégiques
    - **Envoi d'emails** intégré
    
    **🧮 Calculatrice Financière**
    - Intérêts composés
    - Calculs de prêts
    - Mensualités
    
    **🌤️ Météo & Impacts**
    - Données météo
    - Analyses économiques
    - Impacts sectoriels
    
    **🔍 Recherche Web**
    - Actualités financières
    - Tendances marché
    - Analyses sectorielles
    
    **📅 Calendrier Économique**
    - Événements à venir
    - Publications importantes
    - Dates clés
    
    **💹 Simulateur Investissement**
    - Projections de capital
    - Simulations de rendement
    - Analyses de scénarios
    
    **🏖️ Planificateur Retraite**
    - Calculs de retraite
    - Projections d'épargne
    - Plans financiers
    """)

# Section d'information sur les documents
with st.sidebar.expander("📁 Gestion des Documents"):
    st.markdown("""
    ### 📍 Emplacement des documents
    Les documents sont automatiquement chargés depuis le dossier **`documents/`** dans votre projet.
    
    ### 📝 Formats supportés
    - PDF, DOCX, TXT, CSV, Excel
    
    ### 🔄 Recharger les documents
    Si vous ajoutez de nouveaux documents dans le dossier, rechargez la page pour les prendre en compte.
    """)
    
    # Afficher les documents actuels
    documents_path = "documents"
    if os.path.exists(documents_path):
        fichiers = [f for f in os.listdir(documents_path) if os.path.isfile(os.path.join(documents_path, f))]
        if fichiers:
            st.markdown("### 📋 Documents chargés:")
            for fichier in fichiers:
                st.write(f"• {fichier}")
        else:
            st.info("ℹ️ Aucun document dans le dossier 'documents'")

# Section de configuration email CORRIGÉE
with st.sidebar.expander("📧 Configuration Email"):
    st.markdown("""
    ### 🔐 Configuration Mot de Passe d'Application Gmail
    
    **Expéditeur fixe :** erimondh7@gmail.com
    
    **Configuration actuelle :**
    - ✅ Utilisation du mot de passe d'application Gmail
    - ✅ SMTP avec authentification sécurisée
    - ✅ Support des pièces jointes
    
    **Utilisation :**
    - "Envoyer cette analyse à client@entreprise.com"
    - "Envoie un email à john@doe.com avec sujet 'Rapport'"
    - "Envoyez cette réponse à contact@societe.fr"
    
    **Vérification de la configuration :**
    """)
    
    # Vérifier la configuration email
    app_password = os.getenv("GMAIL_APP_PASSWORD")
    if app_password:
        st.success("✅ GMAIL_APP_PASSWORD est configuré")
        st.code(f"Mot de passe: {'*' * 16}")
    else:
        st.error("❌ GMAIL_APP_PASSWORD non configuré")
        st.info("""
        **Pour configurer :**
        1. Allez dans les paramètres de votre compte Google
        2. Activez la vérification en 2 étapes
        3. Générez un mot de passe d'application
        4. Ajoutez dans votre .env :
        ```
        GMAIL_APP_PASSWORD="votre_mot_de_passe_16_caracteres"
        ```
        """)

# Styles CSS améliorés
st.markdown("""
<style>
    .stButton button {
        width: 100%;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .stTextArea textarea {
        border-radius: 8px;
        border: 2px solid #e0e0e0;
        transition: border-color 0.3s ease;
    }
    
    .stTextArea textarea:focus {
        border-color: #1f77b4;
    }
    
    .stSuccess {
        background-color: #f8fff8;
        border-left: 4px solid #00cc00;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .stInfo {
        background-color: #f0f8ff;
        border-left: 4px solid #1f77b4;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)