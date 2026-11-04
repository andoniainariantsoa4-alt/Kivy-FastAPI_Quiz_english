# backend.py - QG Grammar : Conquete des 5 Continents
# Auteure: Ando - Premiere cliente / testeuse
# MVP: 1 pays par continent, architecture prete pour 195 pays

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import random
import requests

app = FastAPI(title="QG World Conquest API")

# Ma carte du monde - 5 continents, 1 pays par continent pour la soutenance
# J'ai mis pays_suivants pour montrer que j'ai prevu le monde entier apres
CONTINENTS = {
    "africa": {"nom": "Afrique", "pays_actuel": "Madagascar", "capitale": "Antananarivo", "drapeau": "https://flagcdn.com/w320/mg.png", "couleur": [0.18, 0.8, 0.44, 1], "pays_suivants": ["Maroc", "Kenya"], "points": 10, "nb_q": 10},
    "europe": {"nom": "Europe", "pays_actuel": "France", "capitale": "Paris", "drapeau": "https://flagcdn.com/w320/fr.png", "couleur": [0.35, 0.45, 0.98, 1], "pays_suivants": ["Allemagne", "Italie"], "points": 15, "nb_q": 8},
    "asia": {"nom": "Asie", "pays_actuel": "Japan", "capitale": "Tokyo", "drapeau": "https://flagcdn.com/w320/jp.png", "couleur": [0.95, 0.32, 0.32, 1], "pays_suivants": ["Coree", "Inde"], "points": 20, "nb_q": 5},
    "america": {"nom": "Amérique", "pays_actuel": "Brazil", "capitale": "Brasilia", "drapeau": "https://flagcdn.com/w320/br.png", "couleur": [0.98, 0.6, 0.15, 1], "pays_suivants": ["USA", "Canada"], "points": 20, "nb_q": 5},
    "oceania": {"nom": "Océanie", "pays_actuel": "Australia", "capitale": "Canberra", "drapeau": "https://flagcdn.com/w320/au.png", "couleur": [0.6, 0.4, 0.9, 1], "pays_suivants": ["New Zealand"], "points": 20, "nb_q": 5},
}

# Pool de questions par continent - J'ai ecrit les questions moi-meme avec la capitale du pays
QUESTIONS_POOL = {
    "africa": [
        {"q": "Madagascar ___ in Africa", "choix": ["is", "are", "am", "be"], "rep": 0, "err": "Madagascar is... (singulier)"},
        {"q": "Antananarivo ___ the capital of Madagascar", "choix": ["is", "are", "am", "be"], "rep": 0, "err": "The capital is..."},
        {"q": "They ___ from Madagascar", "choix": ["is", "are", "am", "be"], "rep": 1, "err": "They are"},
        {"q": "I ___ from Madagascar", "choix": ["am", "is", "are", "be"], "rep": 0, "err": "I am"},
        {"q": "He ___  like vary", "choix": ["don't", "doesn't", "not", "no"], "rep": 1, "err": "He doesn't"},
        {"q": "We ___ live in Africa", "choix": ["don't", "doesn't", "not", "no"], "rep": 0, "err": "We don't"},
        {"q": "She ___ malagasy", "choix": ["is", "are", "am", "be"], "rep": 0, "err": "She is"},
        {"q": "___ you from Tana?", "choix": ["Is", "Are", "Am", "Be"], "rep": 1, "err": "Are you?"},
        {"q": "My name ___ Ando", "choix": ["is", "are", "am", "be"], "rep": 0, "err": "My name is"},
        {"q": "___ name is Madagascar", "choix": ["Its", "It's", "It", "Its'"], "rep": 1, "err": "It's = It is"},
    ],
    "europe": [
        {"q": "France ___ in Europe", "choix": ["is", "are", "am", "be"], "rep": 0, "err": "France is"},
        {"q": "Paris ___ beautiful", "choix": ["is", "are", "am", "be"], "rep": 0, "err": "Paris is"},
        {"q": "I have been to France ___ 2022", "choix": ["since", "for", "during", "from"], "rep": 0, "err": "Since = date"},
        {"q": "I lived in France ___ 2 years", "choix": ["since", "for", "during", "from"], "rep": 1, "err": "For = duree"},
        {"q": "Yesterday I ___ to Paris", "choix": ["go", "went", "goed", "going"], "rep": 1, "err": "Go/Went/Gone"},
        {"q": "How ___ cheese do you want?", "choix": ["many", "much", "few", "a lot"], "rep": 1, "err": "Much + incountable"},
        {"q": "There are ___ monuments in Paris", "choix": ["much", "many", "much of", "a lot"], "rep": 1, "err": "Many + countable"},
        {"q": "Paris is ___ than Tana", "choix": ["big", "bigger", "more big", "biggest"], "rep": 1, "err": "Bigger than"},
    ],
    "asia": [
        {"q": "If I ___ you, I would go to Japan", "choix": ["am", "was", "were", "be"], "rep": 2, "err": "If I were"},
        {"q": "Tokyo has ___ been my dream", "choix": ["never", "ever", "just", "yet"], "rep": 2, "err": "Has just been"},
        {"q": "The sushi ___ made in Japan", "choix": ["is", "was", "were", "are"], "rep": 1, "err": "Was made (passive)"},
        {"q": "I wish I ___ in Tokyo", "choix": ["am", "was", "were", "be"], "rep": 2, "err": "I wish I were"},
        {"q": "I ___ in Japan for 3 years", "choix": ["live", "have lived", "lived", "am living"], "rep": 1, "err": "Have lived for"},
    ],
    "america": [
        {"q": "If it rains in Brazil, I ___ stay", "choix": ["would", "will", "would have", "had"], "rep": 1, "err": "If + present, will"},
        {"q": "I have never ___ to Brazil", "choix": ["been", "went", "go", "going"], "rep": 0, "err": "Have never been"},
        {"q": "The Amazon ___ by many people", "choix": ["is visited", "visited", "visits", "are visited"], "rep": 0, "err": "Is visited (passive)"},
        {"q": "He said he ___ tired in Brazil", "choix": ["is", "was", "were", "be"], "rep": 1, "err": "He said he was"},
        {"q": "Brazil is ___ than Madagascar", "choix": ["big", "bigger", "more big", "biggest"], "rep": 1, "err": "Bigger than"},
    ],
    "oceania": [
        {"q": "Australia ___ an island", "choix": ["is", "are", "am", "be"], "rep": 0, "err": "Australia is"},
        {"q": "If I were in Australia, I ___ surf", "choix": ["will", "would", "would have", "had"], "rep": 1, "err": "Would (conditionnel)"},
        {"q": "I have ___ seen a kangaroo", "choix": ["never", "ever", "just", "yet"], "rep": 0, "err": "Have never seen"},
        {"q": "Sydney ___ built near the sea", "choix": ["is", "was", "were", "are"], "rep": 1, "err": "Was built"},
        {"q": "I wish I ___ in Australia", "choix": ["am", "was", "were", "be"], "rep": 2, "err": "I wish I were"},
    ]
}

derniers = {} # pour retenir la bonne reponse melangee

def melanger(q_dict, points):
    items = list(enumerate(q_dict["choix"]))
    random.shuffle(items)
    new_choix = [t for i,t in items]
    new_rep = [new_i for new_i, (old_i, t) in enumerate(items) if old_i == q_dict["rep"]][0]
    return {"question": q_dict["q"], "choix": new_choix, "erreur": q_dict["err"], "points": points, "rep_cache": new_rep}

@app.get("/")
def home(): return {"message": "QG World API OK"}

@app.get("/continents")
def get_continents(): return CONTINENTS

@app.get("/mission/{continent_id}")
def get_mission(continent_id: str):
    conf = CONTINENTS[continent_id]
    pool = QUESTIONS_POOL[continent_id]
    # On tire au hasard selon le nb de questions du niveau
    selection = random.sample(pool, k=min(conf["nb_q"], len(pool)))
    result = []
    for q in selection:
        m = melanger(q, conf["points"])
        result.append(m)
    return {"continent": conf, "questions": result, "seuil": 80}

@app.post("/verifier/{continent_id}/{qid}/{choix}")
def verifier(continent_id: str, qid: int, choix: int):
    # qid = index de la question dans la mission envoyee
    # On doit retrouver la bonne reponse depuis la derniere mission
    # Simplifie: on stocke pas, on renvoie juste si c'est correct via le cache
    # Pour MVP debutant, on fait simple: le client connait deja la reponse cachee
    # Ici on fait confiance au stockage local (derniers) - version simple
    # Pour cette version, on va juste verifier via le parametre choix vs rep_cache envoye par le client dans une vraie app
    # Ici on simule: on dit que tout est stocke dans derniers
    bonne = derniers.get(f"{continent_id}_{qid}")
    if bonne is None:
        # Si pas en cache, on ne peut pas verifier, on renvoie false mais on donne la correction
        return {"correct": False}
    return {"correct": (choix == bonne)}

# Version plus simple et fiable pour toi: le backend renvoie la bonne position
# On va utiliser une variable globale simple pour la demo
missions_cache = {}

@app.get("/mission/v2/{continent_id}")
def get_mission_v2(continent_id: str):
    conf = CONTINENTS[continent_id]
    pool = QUESTIONS_POOL[continent_id]
    selection = random.sample(pool, k=min(conf["nb_q"], len(pool)))
    result = []
    for idx, q in enumerate(selection):
        m = melanger(q, conf["points"])
        # je sauve la bonne reponse
        missions_cache[f"{continent_id}_{idx}"] = m["rep_cache"]
        del m["rep_cache"]
        m["id"] = idx
        m["bonne_reponse_texte"] = q["choix"][q["rep"]] # pour afficher apres
        result.append(m)
    return {"continent": conf, "questions": result, "seuil": 80, "total_points_possibles": conf["points"]*len(result)}

@app.post("/verifier/v2/{continent_id}/{qid}/{choix}")
def verifier_v2(continent_id: str, qid: int, choix: int):
    key = f"{continent_id}_{qid}"
    bonne = missions_cache.get(key)
    conf = CONTINENTS[continent_id]
    pool_item = QUESTIONS_POOL[continent_id][qid % len(QUESTIONS_POOL[continent_id])] # simplification
    # On retrouve la vraie question pour la correction
    # Pour etre sur, on prend depuis le cache
    is_correct = (bonne == choix) if bonne is not None else False
    return {"correct": is_correct, "points_gagnes": conf["points"] if is_correct else 0}
