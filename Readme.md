# QG Quiz English - Conquête des 5 Continents

> Apprendre l'anglais en conquérant le monde. 5 continents, 1 pays par continent pour le MVP.
> Projet L3 - Développé et testé par Ando, première cliente.

### Concept

Au lieu d'un simple quiz avec un pourcentage, c'est devenu un jeu de conquête:
- Tu commences par **l'Afrique (Madagascar)**
- Si tu as **80%**, tu débloques l'Europe, puis l'Asie, etc.
- Chaque continent a ses points: 10 pts (Afrique), 15 pts (Europe), 20 pts (Asie/Amérique/Océanie)

### Fonctionnalités V1 - Quiz

- **5 Continents MVP**: Afrique/Madagascar, Europe/France, Asie/Japan, Amérique/Brazil, Océanie/Australia
- Architecture prévue pour 195 pays (champ `pays_suivants` dans le code)
- **Système de points**: 10/15/20 selon difficulté
- **Règle 80%**: Il faut 80% pour conquérir un continent et débloquer le suivant
- **Mélange des choix**: Les réponses sont mélangées à chaque partie
- **Règle pédagogique**: Au lieu de "Erreur: ...", on affiche "💡 Règle: ..." (ex: "He/She/It + doesn't")
- **Bug trouvé en tant que testeuse**: Q7 Afrique `He __ not like vary` avait une double négation + faute de frappe, corrigé en `He ___ like vary rice`

### Stack

- **Frontend**: Kivy - `NiceButton`, `Card` avec `RoundedRectangle`
- **Backend**: FastAPI
- **Questions**: Écrites à la main avec capitales des pays

### Structure
quiz_english/
├── # API: /continents, /mission/{id}, /verifier/{id}
├── # App Kivy: carte du monde + mission
└── README.md
