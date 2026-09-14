import re

import pandas as pd
import streamlit as st

AFFICHER_POIDS = False    
AFFICHER_ORIGINE = True    
LONGUEUR_MAX = 128        

PAYS = {
    "AR": "Argentine", "BE": "Belgique", "BJ": "Bénin", "BR": "Brésil",
    "CI": "Côte d'Ivoire", "CL": "Chili", "CN": "Chine", "CO": "Colombie",
    "CR": "Costa Rica", "DE": "Allemagne", "DZ": "Algérie", "EC": "Équateur",
    "EG": "Égypte", "ES": "Espagne", "FR": "France", "IL": "Israël",
    "IT": "Italie", "MA": "Maroc", "MZ": "Mozambique", "NL": "Pays-Bas",
    "NZ": "Nouvelle-Zélande", "PE": "Pérou", "PL": "Pologne", "PT": "Portugal",
    "SN": "Sénégal", "TH": "Thaïlande", "TN": "Tunisie", "TR": "Turquie",
    "US": "États-Unis", "VE": "Venezuela", "VN": "Viêt Nam", "ZA": "Afrique du Sud",
}


FAMILLES_MASQUEES = {
    "EXO", "BULBE", "RACINE", "FEUILLE", "HERBE", "COQUE", "SALADE",
    "PECH/NEC", "FECULENT", "SEC", "ROUGE 125 GR",
}
FAMILLES_RENOMMEES = {"PDT": "Pomme de terre"}

FAMILLES_CONDITIONNEES = {"ROUGE 125 GR": "barquette 125 g"}

MOTS = {
    "PECHE": "pêche", "PASTEQUE": "pastèque", "CLEMENTINE": "clémentine",
    "ECHALOTE": "échalote", "ECHALION": "échalion", "CEBETTE": "cébette",
    "CRIMEE": "Crimée", "COTELÉE": "côtelée", "COTELEE": "côtelée",
    "GREEN": "green", "MEAT": "meat", "BLUE": "blue", "PECHES": "pêches", "CELERI": "céleri", "FEVE": "fève",
    "EPINARD": "épinard", "CHATAIGNE": "châtaigne", "MACHE": "mâche",
    "FRISEE": "frisée", "FRISE": "frisé", "CEPE": "cèpe", "NEFLE": "nèfle",
    "SECHE": "sèche", "FRAICHE": "fraîche", "COUPE": "coupé", "COTES": "côtes",
    "CHENE": "chêne", "TREVISE": "trévise", "DELICATESSE": "délicatesse",
    "TOURBEE": "tourbée", "SPECIALE": "spéciale", "CONFERENCE": "Conférence",
    "AMERE": "amère", "JUBILE": "Jubilé", "COEUR": "cœur", "MAIS": "maïs",
    "JALAPENO": "jalapeño", "CREME": "crème", "GRECQUE": "grecque",
    "MELI": "méli", "MELO": "mélo", "PATE": "pâte", "BLETTES": "blettes",
    "GRAFFITI": "graffiti", "BOTTE": "botte", "LITEE": "litée",
    "PIED": "pied", "ENTIER": "entier", "BLOND": "blond", "COND": "conditionné",
    "BQ": "barquette", "QTE": "quantité", "CAL": "calibre",
    "FR": "France", "IMPORT": "import", "ESP": "Espagne", "MAR": "Maroc",
}
VARIETES = set("""
GOLDEN GALA ROYAL PINK LADY GRANNY SMITH FUJI ELSTAR IDARED JAZZ PINOVA BOSKOOP
CANADA CHANTECLERC CRIPS DELBARD GOLDRUSH RUBINETTE SCILATE SKYFRESH STORY ROCKIT
REINETTES REINE COMICE GUYOT ABATE ANGELYS CELINA WILLIAM XENIA PIRA ROCHA MORGANE
LIMONERA HARROW SUNDOW FRED NASHI CRASSANE LOUISE BONNE MIRABELLE QUETSCH CLAUDE
STANLEY AMANDINE RATTE AGATA SPUNTA CELTIANE CHARLOTTE BINTJE VITELOTTE NOIRMOUTIER
GRENAILLE MITRAILLE SWEET VICTORIA CHARENTAIS GARIGUETTE CIFLORETTE CLERY MARA
DREAM FAVORI TORINO MARMANDE ROMA MARZANO BERNE ZEBRA REBELLION FOLFER MEDJOUL
LERIDA PADRON SIVRI CARLI KIL BATAVIA ICEBERG SUCRINE ROMAINE SCAROLE LOLO ROSSA
CASTEL FRANCO KALE ROMANESCO BUTTERNUT POTIMARRON PATIDOU PATISSON MUSCADE
SPAGHETTI NOA ORRI CLEMENVILLA TAROCCO CARA MALTAISE POMELOS FLORIDE PARIS
FRANCE ESPAGNE ITALIE PORTUGAL CORSE MAROC BELGIQUE HOLLANDE BRUXELLES ANTILLAIS
CHINOIS THAILANDAISE JAPONAIS VIGNE DESSERT JUS PLANTEUR FRECINETTE BARBARIE
""".split())

MINUSCULES = {
    "de", "du", "des", "la", "le", "les", "à", "au", "aux", "en", "et",
    "d'", "par", "sur",
}
EXCEPTIONS = {
    "CHOU - FLEUR": "Chou-fleur",
    "CHOU - FLEUR GRAFFITI": "Chou-fleur graffiti",
    "CHOU - RAVE": "Chou-rave",
    "CHOU - BRUXELLES": "Chou de Bruxelles",
    "CHOU - BROCOLI": "Brocoli",
    "CHOU - CHOUCROUTE": "Chou à choucroute",
    "CHOU - CIMA DE RAPA": "Cima di rapa",
    "CHOU - FRISEE": "Chou frisé",
    "CELERI - RAVE": "Céleri-rave",
    "FIGUE - BARBARIE": "Figue de Barbarie",
    "PASTEQUE - BOX": "Pastèque",
    "CELERI - BRANCHE": "Céleri branche",
    "SEC - ABRICOT": "Abricot sec",
    "SEC - FIGUE LERIDA": "Figue sèche Lerida",
    "SEC - DATTE BRANCHE": "Datte sur branche",
    "SEC - DATTE FRAICHE": "Datte fraîche",
    "SEC - PRUNEAU VANILLE": "Pruneau à la vanille",
    "COQUE - NOIX SECHE": "Noix sèche",
    "FEUILLE - BLETTES COTES": "Côtes de blettes",
    "FEUILLE - BLETTES PIED": "Pied de blettes",
    "FEUILLE - EPINARD JEUNE POUSSE": "Épinard jeune pousse",
    "NAVET - BOULE D OR": "Navet boule d'or",
    "HERBE - SOJA COND 500GR": "Pousses de soja (sachet 500 g)",
    "EXO - TAMARIN (BQ 450GR)": "Tamarin (barquette 450 g)",
    "TOMATE - CERISE 250GR": "Tomate cerise (barquette 250 g)",
    "FRAISE - CAISSETTE 1KG": "Fraise (caissette 1 kg)",
    "FRAISE - CLERY 1KG": "Fraise Cléry (caissette 1 kg)",
    "ABRICOT - CAISSE 5KG": "Abricot (caisse 5 kg)",
    "CHAMPIGNON - PARIS A LA GRECQUE": "Champignon de Paris à la grecque",
    "CHAMPIGNON - PARIS PIED COUPE BLANC": "Champignon de Paris pied coupé, blanc",
    "CHAMPIGNON - PARIS PIED COUPE BLOND": "Champignon de Paris pied coupé, blond",
    "CHAMPIGNON - PARIS PIED ENTIER BLANC": "Champignon de Paris pied entier, blanc",
    "CHAMPIGNON - PARIS PIED ENTIER BLOND": "Champignon de Paris pied entier, blond",
    "PDT - PATATE DOUCE L1": "Patate douce",
    "TOMATE - NOIRE DE CRIMEE": "Tomate noire de Crimée",
    "TOMATE - CERISE MELI MÉLO": "Tomate cerise méli-mélo",
    "CHAMPIGNON - TROMPETTE DE LA MORT": "Trompette de la mort",
    "CHAMPIGNON - PIED DE MOUTON": "Pied-de-mouton",
    "HERBE - PERSIL FRISE": "Persil frisé",
    "PDT - PATATE DOUCE L1": "Patate douce",
    "RACINE - RHUBARBE": "Rhubarbe",
    "HARICOT - POIS GOURMAND": "Pois gourmand",
    "HARICOT - PETIT POIS": "Petit pois",
    "HARICOT - FEVE": "Fève",
    "HARICOT - COCO PLAT": "Haricot coco plat",
}


def _mot(mot, premier):
    """Met un mot en forme : accents, casse, sigles conservés."""
    brut = mot.strip()
    if not brut:
        return ""
    cle = brut.upper()
    if re.fullmatch(r"[A-Z]{0,2}\d+[A-Z+]*(?:/\d+[A-Z+]*)?", cle):
        return brut                      # calibres : C18, P20, 170/200, C07/08
    if cle in VARIETES:
        return cle.capitalize()
    if cle in MOTS:
        sortie = MOTS[cle]
    elif brut.lower() in MINUSCULES:
        sortie = brut.lower()
    elif len(cle) <= 2 and cle.isalpha():
        return brut.capitalize()
    else:
        sortie = brut.lower()
    if premier:
        return sortie[0].upper() + sortie[1:]
    if sortie.lower() in MINUSCULES:
        return sortie.lower()
    return sortie


def joli_libelle(libelle):
    """ABRICOT - C2A -> Abricot C2A"""
    texte = str(libelle).strip()
    if texte in EXCEPTIONS:
        return EXCEPTIONS[texte]

    famille, _, reste = texte.partition(" - ")
    famille = famille.strip()
    reste = reste.strip()
    if AFFICHER_ORIGINE:                
        reste = re.sub(r"(?:\s+|^)(IMPORT|FR|ESP|MAR|ESP/MAR)$", "", reste)
    conditionnement = FAMILLES_CONDITIONNEES.get(famille)

    if not reste:
        morceaux = [famille]
    elif famille in FAMILLES_MASQUEES:
        morceaux = [reste]
    elif famille in FAMILLES_RENOMMEES:
        morceaux = [FAMILLES_RENOMMEES[famille], reste]
    else:
        morceaux = [famille, reste]

    mots = " ".join(morceaux).split()
    nom = " ".join(_mot(m, i == 0) for i, m in enumerate(mots))
    nom = re.sub(r"\s+", " ", nom).strip()
    if conditionnement:
        nom = f"{nom} ({conditionnement})"
    return nom


def joli_poids(poids_kg):
    if not poids_kg or poids_kg <= 0:
        return ""
    if poids_kg >= 1:
        valeur = f"{poids_kg:.1f}".replace(".0", "").replace(".", ",")
        return f"env. {valeur} kg"
    return f"env. {int(round(poids_kg * 1000))} g"


def conditionnement(unite, quantite, poids_kg):
    """à la pièce / lot de 10 (env. 490 g)"""
    unite = str(unite).strip().lower()
    try:
        qte = int(float(quantite))
    except (TypeError, ValueError):
        qte = 0

    if unite == "p":
        base = f"lot de {qte} pièces" if qte > 1 else "à la pièce"
    elif qte > 1:
        base = f"lot de {qte}"
    else:
        base = ""

    poids = joli_poids(poids_kg) if AFFICHER_POIDS else ""
    if base and poids:
        return f"{base} ({poids})"
    return base or poids


def creer_nom_client(row):
    parties = [joli_libelle(row["Libellé"])]

    if AFFICHER_ORIGINE:
        code = str(row["Code pays"]).strip().upper()
        if code and code not in ("NAN", "NONE"):
            parties.append(f"Origine {PAYS.get(code, code)}")

    deja_conditionne = any(
        m in parties[0].lower()
        for m in ("barquette", "caissette", "caisse", "sachet")
    )
    cond = "" if deja_conditionne else conditionnement(
        row["Unité de Vente"], row["Quantité par lot"], row["_poids"]
    )
    if cond:
        parties.append(cond)

    nom = " - ".join(parties)
    return nom[:LONGUEUR_MAX].rstrip(" –")


def nettoyer_valeur_numerique(valeur):
    if pd.isna(valeur):
        return 0.0
    propre = str(valeur).replace("€", "").replace(" ", "").replace(",", ".")
    nombre = pd.to_numeric(propre, errors="coerce")
    return 0.0 if pd.isna(nombre) else float(nombre)


def traduire_tva(taux_tva):
    propre = str(taux_tva).strip().replace(",", ".").replace("%", "")
    try:
        taux = float(propre)
    except ValueError:
        return ""
    if taux == 5.5:
        return "3"
    if taux == 20.0:
        return "1"
    return ""


def determiner_categorie(libelle):
    if pd.isna(libelle):
        return "Accueil"
    libelle_maj = str(libelle).upper()
    correspondances = {
        "CITRON": "6, 4", "ORANGE": "6, 4", "CLEMENTINE": "6, 4", "PAMPLEMOUSSE": "6, 4",
        "ABRICOT": "12, 4", "CERISE": "12, 4", "PECH": "12, 4", "PRUNE": "12, 4",
        "ANANAS": "7, 4", "BANANE": "7, 4", "KIWI": "7, 4", "KAKI": "7, 4",
        "AVOCAT": "7, 4", "FIGUE": "7, 4", "EXO": "7, 4", "FRAISE": "9, 4",
        "ROUGE": "9, 4", "MELON": "13, 4", "PASTEQUE": "13, 4", "POMME": "15, 4",
        "POIRE": "14, 4", "RAISIN": "16, 4", "SEC": "10, 4", "COQUE": "11, 4",
        "TOMATE": "31, 3", "PDT": "30, 3", "CHAMPIGNON": "17, 3", "AIL": "18, 3",
        "OIGNON": "18, 3", "ECHALOTE": "18, 3", "BULBE": "18, 3", "CAROTTE": "28, 3",
        "NAVET": "28, 3", "RADIS": "28, 3", "RACINE": "28, 3", "AUBERGINE": "26, 3",
        "COURGETTE": "26, 3", "COURGE": "26, 3", "CONCOMBRE": "26, 3", "POIVRON": "26, 3",
        "PIMENT": "26, 3", "SALADE": "19, 3", "CHOU": "19, 3", "FEUILLE": "19, 3",
        "HERBE": "19, 3", "ASPERGE": "29, 3", "CELERI": "29, 3", "CARDON": "29, 3",
        "FENOUIL": "29, 3", "ARTICHAUT": "25, 3", "HARICOT": "27, 3", "PETIT POIS": "27, 3",
    }
    for mot_cle, categorie in correspondances.items():
        if mot_cle in libelle_maj:
            return categorie
    return "2"


def traiter_mercuriale(fichier_entree):
    try:
        df = pd.read_excel(fichier_entree, dtype=str)
    except Exception as e:
        raise RuntimeError(f"Impossible de lire le fichier Excel : {e}")

    df.columns = [str(c).strip() for c in df.columns]

    attendues = [
        "Réf.", "Libellé", "Prix Vente HT", "Code pays", "Taux TVA",
        "Poids du lot", "Quantité par lot", "En vente", "Unité de Vente",
    ]
    manquantes = [c for c in attendues if c not in df.columns]
    if manquantes:
        raise ValueError(f"Il manque des colonnes : {manquantes}")

    df["_prix"] = df["Prix Vente HT"].apply(nettoyer_valeur_numerique)
    df["_poids"] = df["Poids du lot"].apply(nettoyer_valeur_numerique)
    df["_actif"] = pd.to_numeric(df["En vente"], errors="coerce").fillna(0).astype(int)

    sortie = pd.DataFrame()
    sortie["Ignorer"] = ""
    sortie["Référence"] = df["Réf."]
    sortie["Nom"] = df.apply(creer_nom_client, axis=1)
    sortie["Catégories (x,y,z...)"] = df["Libellé"].apply(determiner_categorie)
    sortie["Montant HT"] = df["_prix"].round(2)
    sortie["Poids"] = df["_poids"].round(3)
    sortie["ID_tax_rules_group"] = df["Taux TVA"].apply(traduire_tva)
    sortie["Actif (0/1)"] = df["_actif"]

    try:
        csv_data = sortie.to_csv(index=False, sep=";", encoding="utf-8-sig")
    except Exception as e:
        raise RuntimeError(f"Échec lors de la génération du fichier de sortie: {e}")

    return csv_data.encode("utf-8-sig"), len(sortie)


st.title("Conversion de la mercuriale")
st.write(
    "Téléversez un fichier Excel de mercuriale pour générer un fichier CSV "
    "compatible avec l'importation PrestaShop."
)
fichier = st.file_uploader(
    "Sélectionnez le fichier Excel",
    type=["xlsx", "xlsm"],
)

if fichier is not None:
    try:
        csv_data, nombre_produits = traiter_mercuriale(fichier)
        st.success(f"{nombre_produits} produits exportés.")
        st.download_button(
            "Télécharger import_prestashop.csv",
            data=csv_data,
            file_name="import_prestashop.csv",
            mime="text/csv",
        )
    except Exception as e:
        st.error(str(e))
