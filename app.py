import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import numpy as np

# Configuration de la page
st.set_page_config(
    page_title="30VELI - Conseiller Véhicules v3 (Filtrage intelligent)",
    page_icon="🚗",
    layout="wide"
)

# Styles CSS personnalisés
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .vehicle-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .positive {color: #28a745; font-weight: bold;}
    .negative {color: #dc3545; font-weight: bold;}
    .neutral {color: #ffc107; font-weight: bold;}
    .criteria-match {
        background-color: #d4edda;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.2rem 0;
    }
    .criteria-nomatch {
        background-color: #f8d7da;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.2rem 0;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Charger les données d'expérience depuis l'URL"""
    try:
        df = pd.read_csv('https://30veli.fabmob.io/cache/30veli_export_experiences.csv')
        df['Model'] = df['Model'].fillna(df['vehicule'])
        df = df[df['Model'].notna()]
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement des données d'expérience : {e}")
        return None

@st.cache_data
def load_vehicules_specs():
    """Charger les caractéristiques des véhicules depuis le fichier Excel"""
    try:
        # Tenter de charger depuis le fichier uploadé par l'utilisateur
        df = pd.read_excel('30veli_caracteristiques_vehicules.xlsx', sheet_name='Caractéristiques Véhicules')
        return df
    except:
        # Si le fichier n'existe pas encore, retourner None
        return None

def check_vehicle_match(vehicle_row, criteria):
    """Vérifier si un véhicule correspond aux critères"""
    score = 100
    matches = []
    mismatches = []
    
    def is_positive(value):
        """Vérifier si une valeur est positive (OUI, X, ou oui/x en minuscule)"""
        return str(value).upper().strip() in ['OUI', 'X']
    
    # Critère : Pédaler
    if 'pedaler' in criteria and criteria['pedaler'] is not None:
        vehicle_pedaler_value = vehicle_row.get('Nécessite de pédaler (OUI/NON/X)', '')
        vehicle_pedaler = is_positive(vehicle_pedaler_value)
        
        if criteria['pedaler'] == 'OUI' and vehicle_pedaler:
            matches.append("✅ Nécessite de pédaler")
        elif criteria['pedaler'] == 'NON' and not vehicle_pedaler:
            matches.append("✅ Pas besoin de pédaler")
        elif str(vehicle_pedaler_value).strip():  # Si une valeur existe
            mismatches.append(f"❌ Pédaler : {'requis' if vehicle_pedaler else 'non requis'}")
            score -= 20
    
    # Critère : Passagers enfants (ignorer si 0)
    if 'nb_enfants' in criteria and criteria['nb_enfants'] is not None and criteria['nb_enfants'] > 0:
        col_name = f"Passagers enfants - {criteria['nb_enfants']}"
        if col_name in vehicle_row.index:
            if is_positive(vehicle_row[col_name]):
                matches.append(f"✅ Peut transporter {criteria['nb_enfants']} enfant(s)")
            else:
                mismatches.append(f"❌ Ne peut pas transporter {criteria['nb_enfants']} enfant(s)")
                score -= 25
    
    # Critère : Passagers adultes (ignorer si 0)
    if 'nb_adultes' in criteria and criteria['nb_adultes'] is not None and criteria['nb_adultes'] > 0:
        col_name = f"Passagers adultes - {criteria['nb_adultes']}"
        if col_name in vehicle_row.index:
            if is_positive(vehicle_row[col_name]):
                matches.append(f"✅ Peut transporter {criteria['nb_adultes']} adulte(s)")
            else:
                mismatches.append(f"❌ Ne peut pas transporter {criteria['nb_adultes']} adulte(s)")
                score -= 25
    
    # Critère : Chargement
    if 'chargement' in criteria and criteria['chargement']:
        chargement_map = {
            "Petit sac (< 5kg)": "Chargement - Petit sac (< 5kg)",
            "Sacs courses semaine (10-30kg)": "Chargement - Sacs courses semaine (10-30kg)",
            "Charges lourdes (> 100kg)": "Chargement - Charges lourdes (> 100kg)"
        }
        col_name = chargement_map.get(criteria['chargement'])
        if col_name and col_name in vehicle_row.index:
            if is_positive(vehicle_row[col_name]):
                matches.append(f"✅ Capacité de chargement : {criteria['chargement']}")
            else:
                mismatches.append(f"❌ Capacité de chargement insuffisante")
                score -= 20
    
    # Critère : Couverture
    if 'couverture' in criteria and criteria['couverture']:
        if criteria['couverture'] == "Totalement couvert":
            if is_positive(vehicle_row.get('Totalement couvert (OUI/NON/X)', '')):
                matches.append("✅ Totalement couvert")
            else:
                mismatches.append("❌ Pas totalement couvert")
                score -= 15
        elif criteria['couverture'] == "Partiellement couvert":
            if is_positive(vehicle_row.get('Partiellement couvert (OUI/NON/X)', '')):
                matches.append("✅ Partiellement couvert")
            else:
                mismatches.append("⚠️ Couverture différente")
                score -= 10
    
    # Critère : Territoire
    if 'territoire' in criteria and criteria['territoire']:
        terrain_map = {
            "Plutôt plat": "Adapté terrain plat (OUI/NON/X)",
            "Vallonné": "Adapté terrain vallonné (OUI/NON/X)",
            "Montagneux": "Adapté terrain montagneux (OUI/NON/X)"
        }
        col_name = terrain_map.get(criteria['territoire'])
        if col_name and col_name in vehicle_row.index:
            if is_positive(vehicle_row[col_name]):
                matches.append(f"✅ Adapté terrain {criteria['territoire'].lower()}")
            else:
                mismatches.append(f"❌ Pas adapté terrain {criteria['territoire'].lower()}")
                score -= 20
    
    # Déterminer si le véhicule est compatible (éliminatoire)
    # Un véhicule est incompatible si :
    # - Il ne peut pas transporter le nombre de passagers demandé (critère éliminatoire)
    # - Le pédalage ne correspond pas (critère éliminatoire)
    
    is_compatible = True
    
    # Vérifier critères éliminatoires
    if 'nb_enfants' in criteria and criteria['nb_enfants'] is not None and criteria['nb_enfants'] > 0:
        col_name = f"Passagers enfants - {criteria['nb_enfants']}"
        if col_name in vehicle_row.index and not is_positive(vehicle_row[col_name]):
            is_compatible = False
    
    if 'nb_adultes' in criteria and criteria['nb_adultes'] is not None and criteria['nb_adultes'] > 0:
        col_name = f"Passagers adultes - {criteria['nb_adultes']}"
        if col_name in vehicle_row.index and not is_positive(vehicle_row[col_name]):
            is_compatible = False
    
    if 'pedaler' in criteria and criteria['pedaler'] is not None:
        vehicle_pedaler_value = vehicle_row.get('Nécessite de pédaler (OUI/NON/X)', '')
        vehicle_pedaler = is_positive(vehicle_pedaler_value)
        if str(vehicle_pedaler_value).strip():  # Si une valeur existe
            if (criteria['pedaler'] == 'OUI' and not vehicle_pedaler) or \
               (criteria['pedaler'] == 'NON' and vehicle_pedaler):
                is_compatible = False
    
    return max(0, score), matches, mismatches, is_compatible

def display_vehicle_recommendation(vehicle_name, vehicle_specs, experience_data, score, matches, mismatches):
    """Afficher une recommandation de véhicule avec toutes les infos"""
    
    st.markdown(f"### {vehicle_name}")
    
    # Barre de score
    if score >= 80:
        color = "green"
        label = "Excellent choix"
    elif score >= 60:
        color = "orange"
        label = "Bon choix"
    else:
        color = "red"
        label = "Peu adapté"
    
    st.progress(score / 100)
    st.markdown(f"**Score : {score}/100** - <span style='color:{color}'>{label}</span>", unsafe_allow_html=True)
    
    # Colonnes pour les caractéristiques
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**📋 Caractéristiques**")
        vitesse = vehicle_specs.get('Vitesse max (km/h)', 'N/A')
        autonomie = vehicle_specs.get('Autonomie (km)', 'N/A')
        st.write(f"🏎️ Vitesse max : {vitesse} km/h")
        st.write(f"🔋 Autonomie : {autonomie} km")
    
    with col2:
        st.markdown("**✅ Critères respectés**")
        if matches:
            for match in matches[:5]:
                st.markdown(f'<div class="criteria-match">{match}</div>', unsafe_allow_html=True)
        else:
            st.write("_Aucun critère spécifique_")
    
    with col3:
        st.markdown("**⚠️ Points d'attention**")
        if mismatches:
            for mismatch in mismatches[:5]:
                st.markdown(f'<div class="criteria-nomatch">{mismatch}</div>', unsafe_allow_html=True)
        else:
            st.write("_Tous les critères respectés_")
    
    # Retours d'expérience
    if experience_data is not None and len(experience_data) > 0:
        df_vehicle = experience_data[experience_data['Model'] == vehicle_name]
        if len(df_vehicle) > 0:
            with st.expander(f"📊 Retours d'expérience ({len(df_vehicle)} trajets)"):
                # Satisfaction
                bilan_counts = df_vehicle['bilan'].value_counts()
                satisfaction = (
                    bilan_counts.get('Très positif', 0) * 1.0 +
                    bilan_counts.get('Positif', 0) * 0.7
                ) / len(df_vehicle) * 100 if len(df_vehicle) > 0 else 0
                
                st.metric("Taux de satisfaction", f"{satisfaction:.0f}%")
                
                # Commentaires
                commentaires = df_vehicle[df_vehicle['commentaires'].notna()]['commentaires'].head(3).tolist()
                if commentaires:
                    st.markdown("**Derniers retours :**")
                    for i, comment in enumerate(commentaires, 1):
                        st.write(f"{i}. _{comment[:150]}{'...' if len(comment) > 150 else ''}_")
    
    # Remarques du fabricant
    remarques = vehicle_specs.get('Remarques', '')
    if remarques and str(remarques) != 'nan':
        st.info(f"💡 **Remarque :** {remarques}")
    
    st.markdown("---")

# Interface principale
def main():
    st.markdown('<p class="main-header">🚗 30VELI - Conseiller Véhicules v3</p>', unsafe_allow_html=True)
    st.markdown("### Trouvez le véhicule parfait selon vos besoins précis")
    
    # Charger les données
    experience_data = load_data()
    vehicules_specs = load_vehicules_specs()
    
    # Vérifier si le fichier de specs existe
    if vehicules_specs is None:
        st.warning("⚠️ **Fichier de caractéristiques manquant**")
        st.info("""
        Pour utiliser cette version améliorée du dashboard, vous devez :
        
        1. Télécharger le fichier Excel `30veli_caracteristiques_vehicules.xlsx`
        2. Le remplir avec les caractéristiques de chaque véhicule
        3. L'uploader dans votre repository GitHub à côté de `app.py`
        
        En attendant, vous pouvez utiliser la version basique du dashboard.
        """)
        
        # Proposer le téléchargement du template
        if st.button("📥 Comment obtenir le fichier Excel ?"):
            st.markdown("""
            Le fichier Excel vous a été fourni avec l'application. Il s'appelle :
            **30veli_caracteristiques_vehicules.xlsx**
            
            Ce fichier contient :
            - Une feuille "Caractéristiques Véhicules" à remplir
            - Une feuille "Instructions" avec le guide de remplissage
            - Une feuille "Exemple" pour vous aider
            """)
        
        return
    
    # Sidebar avec les nouveaux critères
    st.sidebar.header("🎯 Vos critères détaillés")
    
    # 1. Effort physique
    st.sidebar.markdown("### 💪 Effort physique")
    pedaler = st.sidebar.radio(
        "Souhaitez-vous pédaler ?",
        ["Indifférent", "Oui, je veux pédaler", "Non, sans effort"],
        index=0
    )
    
    # 2. Transport de passagers
    st.sidebar.markdown("### 👥 Transport de passagers")
    
    nb_enfants = st.sidebar.selectbox(
        "Nombre d'enfants à transporter",
        [0, 1, 2, 3, 4],
        index=0
    )
    
    nb_adultes = st.sidebar.selectbox(
        "Nombre d'adultes à transporter (en plus du conducteur)",
        [0, 1, 2, 3],
        index=0
    )
    
    # 3. Capacité de chargement
    st.sidebar.markdown("### 📦 Capacité de chargement")
    chargement = st.sidebar.selectbox(
        "Type de chargement",
        [
            "Aucun besoin spécifique",
            "Petit sac (< 5kg)",
            "Sacs courses semaine (10-30kg)",
            "Charges lourdes (> 100kg)"
        ],
        index=0
    )
    
    # 4. Couverture
    st.sidebar.markdown("### ☔ Protection météo")
    couverture = st.sidebar.selectbox(
        "Couverture souhaitée",
        ["Indifférent", "Totalement couvert", "Partiellement couvert", "Non couvert"],
        index=0
    )
    
    # 5. Territoire
    st.sidebar.markdown("### 🗺️ Type de terrain")
    territoire = st.sidebar.selectbox(
        "Relief habituel",
        ["Indifférent", "Plutôt plat", "Vallonné", "Montagneux"],
        index=0
    )
    
    # 6. Cas d'usage (de l'ancienne version)
    st.sidebar.markdown("### 🎯 Cas d'usage")
    cas_usage = st.sidebar.multiselect(
        "Type d'utilisation (optionnel)",
        ["Domicile-Travail", "Courses", "Loisirs", "Médical", "École"]
    )
    
    # Bouton de recherche
    rechercher = st.sidebar.button("🔍 Trouver les véhicules adaptés", type="primary")
    
    # Construire le dictionnaire de critères
    criteria = {
        'pedaler': 'OUI' if 'Oui' in pedaler else ('NON' if 'Non' in pedaler else None),
        'nb_enfants': nb_enfants,
        'nb_adultes': nb_adultes,
        'chargement': chargement if chargement != "Aucun besoin spécifique" else None,
        'couverture': couverture if couverture != "Indifférent" else None,
        'territoire': territoire if territoire != "Indifférent" else None,
        'cas_usage': cas_usage
    }
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["🏆 Recommandations", "📊 Tous les véhicules", "📈 Statistiques"])
    
    with tab1:
        st.markdown("## Véhicules recommandés pour vous")
        
        # Afficher les critères sélectionnés
        criteres_actifs = []
        if criteria['pedaler']:
            criteres_actifs.append(f"💪 {'Avec' if criteria['pedaler']=='OUI' else 'Sans'} pédalage")
        if criteria['nb_enfants'] > 0:
            criteres_actifs.append(f"👶 {criteria['nb_enfants']} enfant(s)")
        if criteria['nb_adultes'] > 0:
            criteres_actifs.append(f"👥 {criteria['nb_adultes']} adulte(s)")
        if criteria['chargement']:
            criteres_actifs.append(f"📦 {criteria['chargement']}")
        if criteria['couverture']:
            criteres_actifs.append(f"☔ {criteria['couverture']}")
        if criteria['territoire']:
            criteres_actifs.append(f"🗺️ Terrain {criteria['territoire'].lower()}")
        
        if criteres_actifs:
            st.info("**Critères sélectionnés :** " + " • ".join(criteres_actifs))
        
        if rechercher or len(criteres_actifs) > 0:
            # Analyser chaque véhicule
            recommendations = []
            filtered_out = []
            
            for idx, vehicle_row in vehicules_specs.iterrows():
                vehicle_name = vehicle_row['Véhicule']
                score, matches, mismatches, is_compatible = check_vehicle_match(vehicle_row, criteria)
                
                if is_compatible:
                    recommendations.append((vehicle_name, score, matches, mismatches, vehicle_row))
                else:
                    filtered_out.append((vehicle_name, mismatches))
            
            # Trier par score
            recommendations.sort(key=lambda x: x[1], reverse=True)
            
            if recommendations:
                # Afficher le nombre de véhicules filtrés
                if filtered_out:
                    with st.expander(f"ℹ️ {len(filtered_out)} véhicule(s) non compatible(s) masqué(s)"):
                        st.markdown("**Ces véhicules ne correspondent pas à vos critères essentiels :**")
                        for vehicle_name, reasons in filtered_out:
                            st.markdown(f"**{vehicle_name}**")
                            for reason in reasons[:3]:  # Afficher max 3 raisons
                                st.markdown(f"  {reason}")
                            st.markdown("")
                
                # Top 3
                st.markdown("### 🥇 Top 3 des véhicules les plus adaptés")
                
                for i, (vehicle_name, score, matches, mismatches, vehicle_specs) in enumerate(recommendations[:3], 1):
                    medal = ["🥇", "🥈", "🥉"][i-1]
                    with st.container():
                        st.markdown(f"## {medal} {vehicle_name}")
                        display_vehicle_recommendation(
                            vehicle_name, vehicle_specs, experience_data, 
                            score, matches, mismatches
                        )
                
                # Autres véhicules
                if len(recommendations) > 3:
                    with st.expander(f"📋 Voir les autres véhicules ({len(recommendations)-3})"):
                        for vehicle_name, score, matches, mismatches, vehicle_specs in recommendations[3:]:
                            display_vehicle_recommendation(
                                vehicle_name, vehicle_specs, experience_data,
                                score, matches, mismatches
                            )
            else:
                st.warning("😕 Aucun véhicule ne correspond à vos critères")
                
                if filtered_out:
                    st.info(f"""
                    **{len(filtered_out)} véhicule(s) ont été écartés** car ils ne remplissent pas vos critères essentiels :
                    
                    - Capacité de transport de passagers
                    - Besoin de pédaler ou non
                    
                    💡 **Suggestions :**
                    - Assouplissez vos critères (ex: accepter de pédaler)
                    - Réduisez le nombre de passagers
                    - Changez le type de chargement
                    """)
                    
                    with st.expander("Voir les véhicules non compatibles"):
                        for vehicle_name, reasons in filtered_out:
                            st.markdown(f"**{vehicle_name}**")
                            for reason in reasons:
                                st.markdown(f"  {reason}")
                            st.markdown("")
                else:
                    st.info("Aucun véhicule dans la base de données. Vérifiez que le fichier Excel est bien rempli.")
        else:
            st.info("👈 Sélectionnez vos critères dans le menu de gauche et cliquez sur 'Trouver les véhicules adaptés'")
    
    with tab2:
        st.markdown("## Catalogue complet des véhicules")
        
        if vehicules_specs is not None:
            # Afficher le tableau
            st.dataframe(vehicules_specs, use_container_width=True, height=400)
            
            # Permettre le téléchargement
            st.download_button(
                label="📥 Télécharger le tableau complet (CSV)",
                data=vehicules_specs.to_csv(index=False).encode('utf-8'),
                file_name='30veli_vehicules.csv',
                mime='text/csv',
            )
    
    with tab3:
        st.markdown("## Statistiques d'utilisation")
        
        if experience_data is not None:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Véhicules testés", len(vehicules_specs))
            
            with col2:
                st.metric("Trajets recensés", len(experience_data))
            
            with col3:
                avg_satisfaction = (
                    experience_data['bilan'].value_counts(normalize=True).get('Très positif', 0) +
                    experience_data['bilan'].value_counts(normalize=True).get('Positif', 0) * 0.7
                )
                st.metric("Satisfaction moyenne", f"{avg_satisfaction*100:.0f}%")
            
            with col4:
                total_distance = experience_data['totalDistanceKm'].sum()
                st.metric("Distance totale", f"{total_distance:.0f} km")
            
            # Graphiques
            col1, col2 = st.columns(2)
            
            with col1:
                vehicle_counts = experience_data['Model'].value_counts()
                fig = px.bar(
                    x=vehicle_counts.index,
                    y=vehicle_counts.values,
                    labels={'x': 'Véhicule', 'y': 'Nombre de trajets'},
                    title="Répartition des trajets par véhicule"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                bilan_counts = experience_data['bilan'].value_counts()
                fig = px.pie(
                    values=bilan_counts.values,
                    names=bilan_counts.index,
                    title="Répartition des bilans",
                    color_discrete_sequence=['green', 'lightgreen', 'orange', 'red']
                )
                st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
