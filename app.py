import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import numpy as np

# Configuration de la page
st.set_page_config(
    page_title="30VELI - Conseiller Véhicules",
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
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Charger les données depuis l'URL"""
    try:
        df = pd.read_csv('https://30veli.fabmob.io/cache/30veli_export_experiences.csv')
        
        # Nettoyage des données
        df['Model'] = df['Model'].fillna(df['vehicule'])
        df = df[df['Model'].notna()]
        
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {e}")
        return None

def analyze_vehicle_data(df, vehicule, territoire=None, cas_usage=None):
    """Analyser les données pour un véhicule donné"""
    # Filtrer par véhicule
    df_vehicle = df[df['Model'] == vehicule].copy()
    
    # Filtrer par territoire si spécifié
    if territoire and territoire != "Tous":
        if territoire == "Plutôt plat":
            df_vehicle = df_vehicle[df_vehicle['territoire'].str.contains('Commune|CC', na=False)]
        elif territoire == "Vallonné":
            df_vehicle = df_vehicle[df_vehicle['territoire'].str.contains('CC', na=False)]
        elif territoire == "Montagneux":
            df_vehicle = df_vehicle[df_vehicle['territoire'].str.contains('PNR|Montagne', na=False)]
    
    # Filtrer par cas d'usage si spécifié
    if cas_usage:
        motif_keywords = {
            "Domicile-Travail": ["Travail", "Domicile / travail", "travail"],
            "Courses": ["Courses", "courses"],
            "Loisirs": ["Loisirs", "loisirs"],
            "Médical": ["Médical", "médical", "kiné", "rdv"],
            "École": ["école", "École", "enfant"],
        }
        
        if cas_usage in motif_keywords:
            keywords = motif_keywords[cas_usage]
            df_vehicle = df_vehicle[df_vehicle['motif'].str.contains('|'.join(keywords), case=False, na=False)]
    
    if len(df_vehicle) == 0:
        return None
    
    # Calcul des scores
    total_trips = len(df_vehicle)
    
    # Score de satisfaction (basé sur les bilans)
    bilan_counts = df_vehicle['bilan'].value_counts()
    satisfaction_score = (
        bilan_counts.get('Très positif', 0) * 1.0 +
        bilan_counts.get('Positif', 0) * 0.7 +
        bilan_counts.get('Négatif', 0) * 0.0
    ) / total_trips if total_trips > 0 else 0
    
    # Avantages
    avantage_cols = [col for col in df_vehicle.columns if col.startswith('avantage_') and col != 'avantage_aucun' and col != 'avantage_autre']
    avantages = {}
    for col in avantage_cols:
        count = df_vehicle[col].sum()
        if count > 0:
            avantages[col.replace('avantage_', '').capitalize()] = int(count)
    
    # Difficultés
    difficulte_cols = [col for col in df_vehicle.columns if col.startswith('difficulte_') and col != 'difficulte_aucune' and col != 'difficulte_autre']
    difficultes = {}
    for col in difficulte_cols:
        count = df_vehicle[col].sum()
        if count > 0:
            difficultes[col.replace('difficulte_', '').capitalize()] = int(count)
    
    # Distance moyenne
    distances = df_vehicle['totalDistanceKm'].dropna()
    avg_distance = distances.mean() if len(distances) > 0 else 0
    
    # Commentaires récents
    commentaires = df_vehicle[df_vehicle['commentaires'].notna()]['commentaires'].head(5).tolist()
    
    return {
        'vehicule': vehicule,
        'total_trips': total_trips,
        'satisfaction_score': satisfaction_score,
        'avantages': avantages,
        'difficultes': difficultes,
        'avg_distance': avg_distance,
        'bilan_counts': bilan_counts.to_dict(),
        'commentaires': commentaires
    }

def display_vehicle_card(analysis):
    """Afficher une carte de véhicule avec ses statistiques"""
    if not analysis:
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Trajets", analysis['total_trips'])
    
    with col2:
        score = analysis['satisfaction_score'] * 100
        st.metric("Satisfaction", f"{score:.0f}%")
    
    with col3:
        st.metric("Distance moy.", f"{analysis['avg_distance']:.1f} km")
    
    with col4:
        # Bilan général
        max_bilan = max(analysis['bilan_counts'].items(), key=lambda x: x[1], default=('Positif', 0))
        st.metric("Bilan général", max_bilan[0])
    
    # Avantages et difficultés
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("**🎯 Avantages principaux**")
        if analysis['avantages']:
            sorted_avantages = sorted(analysis['avantages'].items(), key=lambda x: x[1], reverse=True)[:5]
            for avantage, count in sorted_avantages:
                st.write(f"- {avantage} ({count})")
        else:
            st.write("_Aucun avantage spécifique mentionné_")
    
    with col_b:
        st.markdown("**⚠️ Difficultés rencontrées**")
        if analysis['difficultes']:
            sorted_difficultes = sorted(analysis['difficultes'].items(), key=lambda x: x[1], reverse=True)[:5]
            for difficulte, count in sorted_difficultes:
                st.write(f"- {difficulte} ({count})")
        else:
            st.write("_Aucune difficulté majeure_")
    
    # Commentaires
    if analysis['commentaires']:
        with st.expander("📝 Voir les retours d'expérience"):
            for i, comment in enumerate(analysis['commentaires'], 1):
                st.markdown(f"**Retour {i}:** {comment[:200]}{'...' if len(comment) > 200 else ''}")

def calculate_recommendation_score(analysis, territoire, cas_usage_list, couverture):
    """Calculer un score de recommandation basé sur les critères"""
    if not analysis:
        return 0
    
    score = analysis['satisfaction_score'] * 50  # Max 50 points pour la satisfaction
    
    # Bonus pour nombre de trajets (indicateur de fiabilité)
    score += min(analysis['total_trips'] / 10, 20)  # Max 20 points
    
    # Pénalités pour difficultés
    if analysis['difficultes']:
        nb_difficultes = sum(analysis['difficultes'].values())
        score -= min(nb_difficultes * 2, 20)  # Max -20 points
    
    # Bonus pour avantages
    if analysis['avantages']:
        nb_avantages = sum(analysis['avantages'].values())
        score += min(nb_avantages, 20)  # Max +20 points
    
    # Ajustement pour couverture (si le véhicule est partiellement couvert)
    # On regarde si le véhicule a des avantages "confort" ou "bien_etre"
    if couverture == "Partiellement couvert":
        if 'Confort' in analysis['avantages'] or 'Bien_etre' in analysis['avantages']:
            score += 5
    
    return max(0, min(score, 100))  # Score entre 0 et 100

# Interface principale
def main():
    st.markdown('<p class="main-header">🚗 30VELI - Conseiller Véhicules</p>', unsafe_allow_html=True)
    st.markdown("### Trouvez le véhicule le plus adapté à vos besoins")
    
    # Charger les données
    df = load_data()
    
    if df is None:
        st.error("Impossible de charger les données. Veuillez vérifier votre connexion.")
        return
    
    # Sidebar avec filtres
    st.sidebar.header("🎯 Vos critères")
    
    # Récupérer les véhicules disponibles
    vehicules_disponibles = sorted(df['Model'].unique())
    
    # Filtres
    territoire = st.sidebar.selectbox(
        "Type de territoire",
        ["Tous", "Plutôt plat", "Vallonné", "Montagneux"]
    )
    
    # Cas d'usage multiples
    cas_usage_options = [
        "Domicile-Travail",
        "Courses",
        "Loisirs",
        "Médical",
        "École",
    ]
    
    cas_usage = st.sidebar.multiselect(
        "Cas d'usage (plusieurs choix possibles)",
        cas_usage_options
    )
    
    couverture = st.sidebar.radio(
        "Couverture du véhicule",
        ["Totalement couvert", "Partiellement couvert", "Non couvert"]
    )
    
    meteo = st.sidebar.multiselect(
        "Conditions météo habituelles",
        ["Ensoleillé", "Nuageux", "Pluvieux", "Venteux"]
    )
    
    # Bouton de recherche
    rechercher = st.sidebar.button("🔍 Trouver les véhicules adaptés", type="primary")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["🏆 Recommandations", "📊 Comparaison", "📈 Statistiques"])
    
    with tab1:
        st.markdown("## Véhicules recommandés pour vous")
        
        if rechercher or not cas_usage:
            # Analyser tous les véhicules
            recommendations = []
            
            for vehicule in vehicules_disponibles:
                # Si plusieurs cas d'usage, on analyse chacun
                if cas_usage:
                    analyses = []
                    for cu in cas_usage:
                        analysis = analyze_vehicle_data(df, vehicule, territoire, cu)
                        if analysis:
                            analyses.append(analysis)
                    
                    # Moyenne des analyses
                    if analyses:
                        combined_analysis = {
                            'vehicule': vehicule,
                            'total_trips': sum(a['total_trips'] for a in analyses),
                            'satisfaction_score': np.mean([a['satisfaction_score'] for a in analyses]),
                            'avantages': {},
                            'difficultes': {},
                            'avg_distance': np.mean([a['avg_distance'] for a in analyses]),
                            'bilan_counts': {},
                            'commentaires': []
                        }
                        
                        # Combiner avantages
                        for a in analyses:
                            for k, v in a['avantages'].items():
                                combined_analysis['avantages'][k] = combined_analysis['avantages'].get(k, 0) + v
                            for k, v in a['difficultes'].items():
                                combined_analysis['difficultes'][k] = combined_analysis['difficultes'].get(k, 0) + v
                            combined_analysis['commentaires'].extend(a['commentaires'])
                        
                        score = calculate_recommendation_score(combined_analysis, territoire, cas_usage, couverture)
                        recommendations.append((vehicule, score, combined_analysis))
                else:
                    # Pas de filtre sur cas d'usage
                    analysis = analyze_vehicle_data(df, vehicule, territoire, None)
                    if analysis:
                        score = calculate_recommendation_score(analysis, territoire, cas_usage, couverture)
                        recommendations.append((vehicule, score, analysis))
            
            # Trier par score
            recommendations.sort(key=lambda x: x[1], reverse=True)
            
            if recommendations:
                # Afficher le top 3
                st.markdown("### 🥇 Top 3 des véhicules recommandés")
                
                for i, (vehicule, score, analysis) in enumerate(recommendations[:3], 1):
                    medal = ["🥇", "🥈", "🥉"][i-1]
                    with st.container():
                        st.markdown(f"### {medal} {vehicule}")
                        st.progress(score / 100)
                        st.markdown(f"**Score de recommandation : {score:.0f}/100**")
                        
                        display_vehicle_card(analysis)
                        
                        st.markdown("---")
                
                # Afficher les autres
                if len(recommendations) > 3:
                    with st.expander("Voir les autres véhicules"):
                        for vehicule, score, analysis in recommendations[3:]:
                            st.markdown(f"### {vehicule}")
                            st.progress(score / 100)
                            st.markdown(f"**Score : {score:.0f}/100**")
                            display_vehicle_card(analysis)
                            st.markdown("---")
            else:
                st.info("Aucun véhicule ne correspond à vos critères. Essayez d'élargir votre recherche.")
    
    with tab2:
        st.markdown("## Comparaison de véhicules")
        
        # Sélection de véhicules à comparer
        vehicules_compare = st.multiselect(
            "Sélectionnez 2 à 4 véhicules à comparer",
            vehicules_disponibles,
            max_selections=4
        )
        
        if len(vehicules_compare) >= 2:
            # Créer un tableau comparatif
            comparison_data = []
            
            for vehicule in vehicules_compare:
                analysis = analyze_vehicle_data(df, vehicule, territoire, cas_usage[0] if cas_usage else None)
                if analysis:
                    comparison_data.append({
                        'Véhicule': vehicule,
                        'Trajets': analysis['total_trips'],
                        'Satisfaction': f"{analysis['satisfaction_score']*100:.0f}%",
                        'Distance moy.': f"{analysis['avg_distance']:.1f} km",
                        'Avantages': len(analysis['avantages']),
                        'Difficultés': len(analysis['difficultes'])
                    })
            
            if comparison_data:
                df_compare = pd.DataFrame(comparison_data)
                st.dataframe(df_compare, use_container_width=True)
                
                # Graphiques comparatifs
                col1, col2 = st.columns(2)
                
                with col1:
                    # Graphique de satisfaction
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=[d['Véhicule'] for d in comparison_data],
                        y=[float(d['Satisfaction'].rstrip('%')) for d in comparison_data],
                        marker_color='lightblue'
                    ))
                    fig.update_layout(
                        title="Taux de satisfaction",
                        yaxis_title="%",
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Graphique avantages vs difficultés
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        name='Avantages',
                        x=[d['Véhicule'] for d in comparison_data],
                        y=[d['Avantages'] for d in comparison_data],
                        marker_color='green'
                    ))
                    fig.add_trace(go.Bar(
                        name='Difficultés',
                        x=[d['Véhicule'] for d in comparison_data],
                        y=[d['Difficultés'] for d in comparison_data],
                        marker_color='red'
                    ))
                    fig.update_layout(
                        title="Avantages vs Difficultés",
                        barmode='group',
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sélectionnez au moins 2 véhicules pour les comparer.")
    
    with tab3:
        st.markdown("## Statistiques générales")
        
        # Vue d'ensemble
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Véhicules testés", len(vehicules_disponibles))
        
        with col2:
            st.metric("Trajets recensés", len(df))
        
        with col3:
            avg_satisfaction = df['bilan'].value_counts(normalize=True).get('Très positif', 0) + df['bilan'].value_counts(normalize=True).get('Positif', 0) * 0.7
            st.metric("Satisfaction moyenne", f"{avg_satisfaction*100:.0f}%")
        
        with col4:
            total_distance = df['totalDistanceKm'].sum()
            st.metric("Distance totale", f"{total_distance:.0f} km")
        
        # Graphiques
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribution des véhicules
            vehicle_counts = df['Model'].value_counts()
            fig = px.bar(
                x=vehicle_counts.index,
                y=vehicle_counts.values,
                labels={'x': 'Véhicule', 'y': 'Nombre de trajets'},
                title="Répartition des trajets par véhicule"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Distribution des bilans
            bilan_counts = df['bilan'].value_counts()
            fig = px.pie(
                values=bilan_counts.values,
                names=bilan_counts.index,
                title="Répartition des bilans",
                color_discrete_sequence=['green', 'lightgreen', 'orange', 'red']
            )
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
