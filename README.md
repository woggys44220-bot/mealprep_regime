# Meal Prep Régime (V1)

Application locale Python (Streamlit) pour gérer des recettes de régime, calculer les macros par portion, organiser un meal prep et générer une liste de courses.

## Fonctionnalités V1

- Créer une recette
- Ajouter/modifier des ingrédients avec : nom, quantité, unité, calories, protéines, glucides, lipides
- Définir le nombre de portions
- Calcul automatique :
  - calories totales
  - calories par portion
  - protéines/glucides/lipides par portion
- Sauvegarde locale des recettes en JSON (`data/recipes.json`)
- Modifier ou supprimer une recette
- Générer une liste de courses simple (agrégation des ingrédients)
- Export CSV des recettes et de la liste de courses

## Nouveauté : base d'aliments préenregistrés

- Nouveau fichier : `data/foods.json`
- Base d'aliments courants fournie par défaut (valeurs nutritionnelles **pour 100 g**)
- Dans l'éditeur d'ingrédients, tu peux sélectionner un aliment depuis la base
- Si `Auto` est activé et que l'unité est `g` ou `kg`, les calories/macros sont recalculées automatiquement selon la quantité
- Tu peux toujours modifier les calories/macros à la main (désactive `Auto` pour conserver tes valeurs personnalisées)
- Tu peux ajouter, modifier et supprimer des aliments dans la section **Base d'aliments**
- La base est sauvegardée localement en JSON

## Structure

- `app.py`
- `data/recipes.json`
- `data/foods.json`
- `requirements.txt`
- `README.md`

## Lancer l'application sur Windows

### 1) Ouvrir PowerShell

Place-toi dans le dossier du projet, par exemple :

```powershell
cd C:\chemin\vers\mealprep_regime
```

### 2) Créer un environnement virtuel

```powershell
python -m venv .venv
```

### 3) Activer l'environnement virtuel

```powershell
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloque l'exécution des scripts, lance cette commande une fois, puis réessaie l'activation :

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

### 4) Installer les dépendances

```powershell
pip install -r requirements.txt
```

### 5) Lancer l'application

```powershell
streamlit run app.py
```

Ensuite, ouvre l'URL affichée dans le terminal (souvent `http://localhost:8501`).

## Utilisation rapide

1. Onglet **Recettes** : crée ou modifie une recette.
2. Pour chaque ingrédient :
   - sélectionne un aliment (facultatif) dans la base,
   - indique la quantité,
   - laisse `Auto` activé pour calculer calories/macros automatiquement en `g`/`kg`.
3. Sauvegarde la recette.
4. Onglet **Recettes** > section **Base d'aliments** : ajoute/modifie/supprime les aliments de référence.
5. Onglet **Meal Prep** : sélectionne des recettes pour générer la liste de courses.
6. Onglet **Exports CSV** : exporte les recettes ou la liste de courses.

## Notes

- L'application fonctionne **sans internet** une fois les dépendances installées.
- Toutes les données sont stockées localement dans `data/recipes.json` et `data/foods.json`.
- Aucun compte utilisateur, aucune clé API.
