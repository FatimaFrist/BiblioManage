import streamlit as st
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime

# Connexion à MongoDB
client = MongoClient('localhost', 27017)
db = client.bibliotheque
collection = db.ouvrages

# Initialisation de st.session_state si nécessaire
if 'page' not in st.session_state:
    st.session_state.page = "accueil"

# Fonction pour insérer un ouvrage
def inserer_ouvrage(ouvrage):
    collection.insert_one(ouvrage)
    st.success("Ouvrage inséré avec succès.")

# Fonction pour mettre à jour un ouvrage
def mettre_a_jour_ouvrage(id, updates):
    if ObjectId.is_valid(id):
        collection.update_one({"_id": ObjectId(id)}, {"$set": updates})
    else:
        collection.update_one({"_id": int(id)}, {"$set": updates})
    st.success("Ouvrage mis à jour avec succès.")

# Fonction pour supprimer un ouvrage
def supprimer_ouvrage(id):
    if ObjectId.is_valid(id):
        collection.delete_one({"_id": ObjectId(id)})
    else:
        collection.delete_one({"_id": int(id)})
    st.success("Ouvrage supprimé avec succès.")

# Fonction pour afficher les ouvrages
def afficher_ouvrages():
    ouvrages = collection.find()
    return list(ouvrages)

# Custom CSS for styling the sidebar and main page buttons
custom_css = """
<style>
[data-testid="stSidebar"][role="navigation"] {
    background-color: transparent !important;
    box-shadow: none !important;
    border: none !important;
    padding: 0;
    margin: 0;
}

[data-testid="stSidebar"] button {
    border: none !important;
    background-color: transparent !important;
    box-shadow: none !important;
    color: inherit !important;
    padding: 0.5rem 1rem !important;
    margin: 0 !important;
    width: 100% !important;
    text-align: left !important;
}

/* Custom styles for buttons in the main pages */
button[key="ajouter_button"] {
    background-color: #4CAF50 !important; /* Green background */
    color: white !important; /* White text */
    border: none !important; /* No border */
    padding: 0.5rem 1rem !important; /* Padding */
    margin: 0.5rem 0 !important; /* Margin */
    cursor: pointer !important; /* Pointer cursor */
    border-radius: 4px !important; /* Rounded corners */
}
button[key="ajouter_button"]:hover {
    background-color: #45a049 !important; /* Darker green on hover */
}

button[key="mettre_a_jour_button"] {
    background-color: #2196F3 !important; /* Blue background */
    color: white !important; /* White text */
    border: none !important; /* No border */
    padding: 0.5rem 1rem !important; /* Padding */
    margin: 0.5rem 0 !important; /* Margin */
    cursor: pointer !important; /* Pointer cursor */
    border-radius: 4px !important; /* Rounded corners */
}
button[key="mettre_a_jour_button"]:hover {
    background-color: #1976D2 !important; /* Darker blue on hover */
}

button[key^="del_"] {
    background-color: #f44336 !important; /* Red background */
    color: white !important; /* White text */
    border: none !important; /* No border */
    padding: 0.5rem 1rem !important; /* Padding */
    margin: 0.5rem 0 !important; /* Margin */
    cursor: pointer !important; /* Pointer cursor */
    border-radius: 4px !important; /* Rounded corners */
}
button[key^="del_"]:hover {
    background-color: #d32f2f !important; /* Darker red on hover */
}
</style>
"""

# Inject custom CSS
st.markdown(custom_css, unsafe_allow_html=True)

# Interface utilisateur avec Streamlit
st.title("Gestion de la Bibliothèque")

# Affichage des options l'une en dessous de l'autre
if st.sidebar.button("Ajouter", key="sidebar_ajouter"):
    st.session_state.page = "ajouter"

if st.sidebar.button("Mettre à jour", key="sidebar_mettre_a_jour"):
    st.session_state.page = "mettre_a_jour"

if st.sidebar.button("Voir", key="sidebar_voir"):
    st.session_state.page = "voir"

# Définition des pages

# Page d'accueil
def page_accueil():
    # Formulaire d'ajout d'un nouvel ouvrage
    st.subheader("Ajouter un nouvel ouvrage")
    titre = st.text_input("Titre")
    dispo = st.checkbox("Disponible", value=True)
    type_doc = st.selectbox("Type de document", ["livres", "periodique"])
    
    if type_doc == "livres":
        annee = st.date_input("Année d'édition", value=datetime.date(2000, 1, 1), min_value=datetime.date(1900, 1, 1), max_value=datetime.date.today()).year
        edition = st.text_input("Maison d'édition")
        auteur = st.text_input("Auteur")
        exemplaires = st.text_area("Exemplaires (séparés par des virgules)").split(',')
        details = {"année": annee, "edition": edition, "auteur": auteur}
        ouvrage = {
            "titre": titre,
            "dispo": int(dispo),
            "type": type_doc,
            "exemplaires": exemplaires,
            "détails": details
        }
    else:
        date = st.date_input("Date de parution")
        periodicite = st.selectbox("Périodicité", ["hebdomadaire", "mensuel", "journalier"])
        details = {"date": date.isoformat(), "peridicité": periodicite}
        ouvrage = {
            "titre": titre,
            "dispo": int(dispo),
            "type": type_doc,
            "détails": details
        }

    if st.button("Ajouter", key="ajouter_button"):
        inserer_ouvrage(ouvrage)

# Page de mise à jour d'un ouvrage existant
def page_mettre_a_jour():
    st.subheader("Mettre à jour un ouvrage existant")
    ouvrages = afficher_ouvrages()
    id_titres = {str(ouvrage['_id']): ouvrage['titre'] for ouvrage in ouvrages}
    selection = st.selectbox("Sélectionner un ouvrage", list(id_titres.keys()), format_func=lambda x: id_titres[x])
    
    if selection:
        if ObjectId.is_valid(selection):
            ouvrage = collection.find_one({"_id": ObjectId(selection)})
        else:
            ouvrage = collection.find_one({"_id": int(selection)})
        
        titre = st.text_input("Titre", value=ouvrage['titre'])
        dispo = st.checkbox("Disponible", value=bool(ouvrage['dispo']))
        type_doc = ouvrage['type']

        if type_doc == "livres":
            try:
                annee = ouvrage['détails']['année']
                if 1900 <= annee <= datetime.date.today().year:
                    annee = datetime.date(annee, 1, 1)
                else:
                    annee = datetime.date(2000, 1, 1)
            except:
                annee = datetime.date(2000, 1, 1)
                
            annee = st.date_input("Année d'édition", value=annee, min_value=datetime.date(1900, 1, 1), max_value=datetime.date.today()).year
            edition = st.text_input("Maison d'édition", value=ouvrage['détails']['edition'])
            auteur = st.text_input("Auteur", value=ouvrage['détails']['auteur'])
            exemplaires = st.text_area("Exemplaires (séparés par des virgules)", value=",".join(ouvrage['exemplaires'])).split(',')
            details = {"année": annee, "edition": edition, "auteur": auteur}
        else:
            date = st.date_input("Date de parution", value=datetime.datetime.strptime(ouvrage['détails']['date'], "%Y-%m-%d").date())
            periodicite = st.selectbox("Périodicité", ["hebdomadaire", "mensuel", "journalier"], index=["hebdomadaire", "mensuel", "journalier"].index(ouvrage['détails']['peridicité']))
            details = {"date": date.isoformat(), "peridicité": periodicite}

        updates = {
            "titre": titre,
            "dispo": int(dispo),
            "détails": details
        }
        if type_doc == "livres":
            updates["exemplaires"] = exemplaires
        
        if st.button("Mettre à jour", key="mettre_a_jour_button"):
            mettre_a_jour_ouvrage(selection, updates)

# Page de visualisation des ouvrages
def page_voir():
    st.subheader("Liste des ouvrages")
    types_documents = ["Tous", "Livres", "Périodiques"]
    type_selectionne = st.selectbox("Afficher par type de document", types_documents)

    ouvrages = afficher_ouvrages()

    if type_selectionne == "Livres":
        ouvrages = [ouvrage for ouvrage in ouvrages if ouvrage['type'] == 'livres']
    elif type_selectionne == "Périodiques":
        ouvrages = [ouvrage for ouvrage in ouvrages if ouvrage['type'] == 'periodique']

    for ouvrage in ouvrages:
        st.write(f"ID: {ouvrage['_id']}")
        st.write(f"Titre: {ouvrage['titre']}")
        st.write(f"Disponible: {'Oui' if ouvrage['dispo'] else 'Non'}")
        st.write(f"Type: {ouvrage['type']}")
        st.write(f"Détails: {ouvrage['détails']}")
        if ouvrage['type'] == "livres":
            st.write(f"Exemplaires: {', '.join(ouvrage['exemplaires'])}")
        if st.button(f"Supprimer {ouvrage['titre']}", key=f"del_{ouvrage['_id']}"):
            supprimer_ouvrage(str(ouvrage['_id']))
            st.experimental_rerun()
        st.write("---")

# Gestion de la navigation multipage avec les paramètres d'URL
if st.session_state.page == "ajouter":
    page_accueil()  # Affiche directement le formulaire dans la page d'accueil
elif st.session_state.page == "mettre_a_jour":
    page_mettre_a_jour()
elif st.session_state.page == "voir":
    page_voir()
else:
    page_accueil()
