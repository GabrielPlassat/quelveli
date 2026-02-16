# quelveli

# 🚗 30VELI - Dashboard de Recommandation de Véhicules

Un dashboard interactif pour recommander le véhicule le plus adapté en fonction de vos besoins : cas d'usage, territoire, couverture, météo...

## 📋 Fonctionnalités

- **Recommandations personnalisées** : Obtenez les véhicules les mieux adaptés à vos critères
- **Système de scoring intelligent** : Basé sur les retours d'expérience réels
- **Comparaison de véhicules** : Comparez jusqu'à 4 véhicules côte à côte
- **Statistiques détaillées** : Avantages, difficultés, satisfaction par véhicule
- **Filtres multiples** :
  - Type de territoire (plat, vallonné, montagneux)
  - Cas d'usage multiples (domicile-travail, courses, loisirs, médical, école)
  - Couverture du véhicule
  - Conditions météo

## 🚀 Déploiement sur Streamlit Cloud (GRATUIT)

### Étape 1 : Créer un compte GitHub

1. Allez sur [github.com](https://github.com)
2. Cliquez sur "Sign up" (Inscription)
3. Créez votre compte gratuitement

### Étape 2 : Créer un nouveau dépôt

1. Connectez-vous à GitHub
2. Cliquez sur le `+` en haut à droite
3. Sélectionnez "New repository"
4. Nommez-le : `30veli-dashboard`
5. Sélectionnez "Public"
6. Cochez "Add a README file"
7. Cliquez sur "Create repository"

### Étape 3 : Ajouter les fichiers

1. Dans votre dépôt, cliquez sur "Add file" > "Upload files"
2. Téléversez les 3 fichiers suivants :
   - `app.py`
   - `requirements.txt`
   - `README.md`
3. Cliquez sur "Commit changes"

### Étape 4 : Déployer sur Streamlit Cloud

1. Allez sur [share.streamlit.io](https://share.streamlit.io)
2. Cliquez sur "Sign up with GitHub"
3. Autorisez Streamlit à accéder à votre compte GitHub
4. Cliquez sur "New app"
5. Sélectionnez :
   - **Repository** : `votre-nom/30veli-dashboard`
   - **Branch** : `main`
   - **Main file path** : `app.py`
6. Cliquez sur "Deploy!"

⏱️ Le déploiement prend 2-3 minutes.

### Étape 5 : Utiliser votre dashboard

1. Une fois déployé, vous obtenez une URL type : `https://votre-app.streamlit.app`
2. Partagez cette URL avec qui vous voulez !
3. L'application se met à jour automatiquement quand vous modifiez les fichiers sur GitHub

## 📱 Utilisation

### Interface principale

1. **Sidebar gauche** : Configurez vos critères
   - Sélectionnez le type de territoire
   - Choisissez un ou plusieurs cas d'usage
   - Indiquez la couverture souhaitée
   - (Optionnel) Sélectionnez les conditions météo

2. **Onglet "Recommandations"** :
   - Cliquez sur "🔍 Trouver les véhicules adaptés"
   - Consultez le TOP 3 des véhicules recommandés
   - Chaque véhicule affiche :
     - Score de recommandation
     - Nombre de trajets
     - Taux de satisfaction
     - Distance moyenne
     - Avantages principaux
     - Difficultés rencontrées
     - Retours d'expérience

3. **Onglet "Comparaison"** :
   - Sélectionnez 2 à 4 véhicules
   - Comparez leurs performances
   - Visualisez les graphiques comparatifs

4. **Onglet "Statistiques"** :
   - Vue d'ensemble de tous les véhicules
   - Graphiques de répartition
   - Statistiques globales

## 🛠️ Structure du projet

```
30veli-dashboard/
│
├── app.py              # Application Streamlit principale
├── requirements.txt    # Dépendances Python
└── README.md          # Ce fichier
```

## 📊 Source des données

Les données sont chargées automatiquement depuis :
`https://30veli.fabmob.io/cache/30veli_export_experiences.csv`

## 🎨 Personnalisation

### Modifier les couleurs

Dans `app.py`, modifiez la section CSS :
```python
st.markdown("""
    <style>
    .main-header {
        color: #1f77b4;  /* Changez cette couleur */
    }
    </style>
""", unsafe_allow_html=True)
```

### Ajouter des critères

Dans `app.py`, trouvez la section `cas_usage_options` et ajoutez vos critères :
```python
cas_usage_options = [
    "Domicile-Travail",
    "Courses",
    "Votre nouveau critère",  # Ajoutez ici
]
```

## 🔧 Mise à jour de l'application

1. Modifiez les fichiers sur GitHub
2. L'application se redéploie automatiquement
3. Rafraîchissez la page après quelques secondes

## ❓ Résolution de problèmes

### L'application ne démarre pas
- Vérifiez que tous les fichiers sont bien présents dans GitHub
- Consultez les logs dans Streamlit Cloud (bouton "Manage app" > "Logs")

### Les données ne se chargent pas
- Vérifiez que l'URL du CSV est accessible
- Essayez de rafraîchir la page

### Erreur de dépendances
- Vérifiez que `requirements.txt` est bien présent
- Assurez-vous qu'il n'y a pas d'espace ou de caractère bizarre

## 📞 Support

Pour toute question sur le projet 30VELI :
- Site web : [30veli.fabmob.io](https://30veli.fabmob.io)

## 📝 Licence

Ce projet est développé dans le cadre de l'expérimentation 30VELI.

---

**Développé avec ❤️ pour faciliter le choix de véhicules adaptés**
