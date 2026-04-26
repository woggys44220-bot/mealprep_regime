import csv
import json
from pathlib import Path
from typing import Dict, List, Optional

import streamlit as st

DATA_DIR = Path("data")
RECIPES_FILE = DATA_DIR / "recipes.json"
FOODS_FILE = DATA_DIR / "foods.json"
UNITS = ["g", "kg", "ml", "l", "pièce", "cuillère", "tasse"]

DEFAULT_FOODS: List[Dict[str, float | str]] = [
    {"name": "pâtes sèches", "calories": 371, "proteines": 13.0, "glucides": 75.0, "lipides": 1.5},
    {"name": "riz cru", "calories": 360, "proteines": 7.0, "glucides": 79.0, "lipides": 0.6},
    {"name": "pommes de terre", "calories": 77, "proteines": 2.0, "glucides": 17.0, "lipides": 0.1},
    {"name": "patate douce", "calories": 86, "proteines": 1.6, "glucides": 20.0, "lipides": 0.1},
    {"name": "bœuf haché maigre", "calories": 137, "proteines": 21.0, "glucides": 0.0, "lipides": 5.0},
    {"name": "poulet", "calories": 165, "proteines": 31.0, "glucides": 0.0, "lipides": 3.6},
    {"name": "thon", "calories": 132, "proteines": 29.0, "glucides": 0.0, "lipides": 1.0},
    {"name": "œuf", "calories": 143, "proteines": 13.0, "glucides": 0.7, "lipides": 10.0},
    {"name": "tomates", "calories": 18, "proteines": 0.9, "glucides": 3.9, "lipides": 0.2},
    {"name": "oignons", "calories": 40, "proteines": 1.1, "glucides": 9.3, "lipides": 0.1},
    {"name": "poivrons", "calories": 31, "proteines": 1.0, "glucides": 6.0, "lipides": 0.3},
    {"name": "courgettes", "calories": 17, "proteines": 1.2, "glucides": 3.1, "lipides": 0.3},
    {"name": "épinards", "calories": 23, "proteines": 2.9, "glucides": 3.6, "lipides": 0.4},
    {"name": "carottes", "calories": 41, "proteines": 0.9, "glucides": 9.6, "lipides": 0.2},
    {"name": "fromage râpé", "calories": 356, "proteines": 25.0, "glucides": 2.0, "lipides": 27.0},
    {"name": "huile d’olive", "calories": 884, "proteines": 0.0, "glucides": 0.0, "lipides": 100.0},
    {"name": "banane", "calories": 89, "proteines": 1.1, "glucides": 23.0, "lipides": 0.3},
    {"name": "pomme", "calories": 52, "proteines": 0.3, "glucides": 14.0, "lipides": 0.2},
    {"name": "avoine", "calories": 389, "proteines": 16.9, "glucides": 66.0, "lipides": 6.9},
    {"name": "graines de chia", "calories": 486, "proteines": 16.5, "glucides": 42.0, "lipides": 30.7},
    {"name": "graines de lin", "calories": 534, "proteines": 18.3, "glucides": 28.9, "lipides": 42.2},
]


def ensure_data_files() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    if not RECIPES_FILE.exists():
        RECIPES_FILE.write_text("[]", encoding="utf-8")
    if not FOODS_FILE.exists():
        FOODS_FILE.write_text(json.dumps(DEFAULT_FOODS, indent=2, ensure_ascii=False), encoding="utf-8")


def load_recipes() -> List[Dict]:
    ensure_data_files()
    try:
        data = json.loads(RECIPES_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def save_recipes(recipes: List[Dict]) -> None:
    RECIPES_FILE.write_text(json.dumps(recipes, indent=2, ensure_ascii=False), encoding="utf-8")


def load_foods() -> List[Dict]:
    ensure_data_files()
    try:
        data = json.loads(FOODS_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def save_foods(foods: List[Dict]) -> None:
    FOODS_FILE.write_text(json.dumps(foods, indent=2, ensure_ascii=False), encoding="utf-8")


def quantity_to_grams(quantity: float, unit: str) -> Optional[float]:
    if unit == "g":
        return quantity
    if unit == "kg":
        return quantity * 1000
    return None


def compute_ingredient_macros(ingredient: Dict, foods_map: Dict[str, Dict]) -> Dict:
    ing = dict(ingredient)
    food_name = str(ing.get("food", "")).strip()
    auto = bool(ing.get("auto", False))
    grams = quantity_to_grams(float(ing.get("quantity", 0) or 0), str(ing.get("unit", "g")))

    if auto and food_name and grams is not None and food_name in foods_map:
        factor = grams / 100.0
        food = foods_map[food_name]
        ing["name"] = food_name
        ing["calories"] = round(float(food.get("calories", 0) or 0) * factor, 2)
        ing["proteines"] = round(float(food.get("proteines", 0) or 0) * factor, 2)
        ing["glucides"] = round(float(food.get("glucides", 0) or 0) * factor, 2)
        ing["lipides"] = round(float(food.get("lipides", 0) or 0) * factor, 2)

    return ing


def sanitize_ingredients(raw_ingredients: List[Dict], foods_map: Dict[str, Dict]) -> List[Dict]:
    clean_ingredients = []
    for ing in raw_ingredients:
        computed = compute_ingredient_macros(ing, foods_map)
        food_name = str(computed.get("food", "")).strip()
        display_name = str(computed.get("name", "")).strip() or food_name
        if not display_name:
            continue
        clean_ingredients.append(
            {
                "name": display_name,
                "food": food_name,
                "auto": bool(computed.get("auto", False)),
                "quantity": float(computed.get("quantity", 0) or 0),
                "unit": str(computed.get("unit", "g")),
                "calories": float(computed.get("calories", 0) or 0),
                "proteines": float(computed.get("proteines", 0) or 0),
                "glucides": float(computed.get("glucides", 0) or 0),
                "lipides": float(computed.get("lipides", 0) or 0),
            }
        )
    return clean_ingredients


def recipe_totals(recipe: Dict) -> Dict[str, float]:
    totals = {"calories": 0.0, "proteines": 0.0, "glucides": 0.0, "lipides": 0.0}
    for ing in recipe.get("ingredients", []):
        totals["calories"] += float(ing.get("calories", 0) or 0)
        totals["proteines"] += float(ing.get("proteines", 0) or 0)
        totals["glucides"] += float(ing.get("glucides", 0) or 0)
        totals["lipides"] += float(ing.get("lipides", 0) or 0)

    portions = max(int(recipe.get("portions", 1) or 1), 1)
    totals["calories_par_portion"] = totals["calories"] / portions
    totals["proteines_par_portion"] = totals["proteines"] / portions
    totals["glucides_par_portion"] = totals["glucides"] / portions
    totals["lipides_par_portion"] = totals["lipides"] / portions
    return totals


def update_recipe_in_list(recipes: List[Dict], recipe_name: str, updated: Dict) -> List[Dict]:
    for idx, recipe in enumerate(recipes):
        if recipe.get("name") == recipe_name:
            recipes[idx] = updated
            return recipes
    recipes.append(updated)
    return recipes


def build_shopping_list(selected_recipes: List[Dict]) -> Dict[str, Dict[str, float]]:
    shopping: Dict[str, Dict[str, float]] = {}
    for recipe in selected_recipes:
        for ing in recipe.get("ingredients", []):
            name = ing.get("name", "").strip()
            unit = ing.get("unit", "")
            qty = float(ing.get("quantity", 0) or 0)
            if not name:
                continue
            key = f"{name}__{unit}"
            if key not in shopping:
                shopping[key] = {"name": name, "unit": unit, "quantity": 0.0}
            shopping[key]["quantity"] += qty
    return shopping


def recipes_to_csv_rows(recipes: List[Dict]) -> List[List[str]]:
    rows = [[
        "recette", "portions", "ingredient", "quantite", "unite",
        "calories", "proteines", "glucides", "lipides"
    ]]
    for recipe in recipes:
        for ing in recipe.get("ingredients", []):
            rows.append([
                recipe.get("name", ""),
                str(recipe.get("portions", 1)),
                ing.get("name", ""),
                str(ing.get("quantity", "")),
                ing.get("unit", ""),
                str(ing.get("calories", "")),
                str(ing.get("proteines", "")),
                str(ing.get("glucides", "")),
                str(ing.get("lipides", "")),
            ])
    return rows


def shopping_to_csv_rows(shopping: Dict[str, Dict[str, float]]) -> List[List[str]]:
    rows = [["ingredient", "quantite", "unite"]]
    for item in shopping.values():
        rows.append([item["name"], str(round(item["quantity"], 2)), item["unit"]])
    return rows


def rows_to_csv_bytes(rows: List[List[str]]) -> bytes:
    from io import StringIO

    output = StringIO()
    writer = csv.writer(output)
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")


def normalize_ingredient_for_editor(ingredient: Dict) -> Dict:
    row = dict(ingredient)
    row.setdefault("food", row.get("name", ""))
    row.setdefault("auto", True)
    row.setdefault("name", "")
    row.setdefault("quantity", 0.0)
    row.setdefault("unit", "g")
    row.setdefault("calories", 0.0)
    row.setdefault("proteines", 0.0)
    row.setdefault("glucides", 0.0)
    row.setdefault("lipides", 0.0)
    return row


def default_ingredient_row() -> Dict:
    return {
        "food": "",
        "name": "",
        "auto": True,
        "quantity": 0.0,
        "unit": "g",
        "calories": 0.0,
        "proteines": 0.0,
        "glucides": 0.0,
        "lipides": 0.0,
    }


def main() -> None:
    st.set_page_config(page_title="Meal Prep Régime", layout="wide")
    st.title("🥗 Meal Prep Régime (V1)")

    foods = load_foods()
    foods_map = {str(food.get("name", "")).strip(): food for food in foods if str(food.get("name", "")).strip()}

    recipes = load_recipes()
    recipe_names = [r.get("name") for r in recipes]

    tab1, tab2, tab3 = st.tabs(["Recettes", "Meal Prep", "Exports CSV"])

    with tab1:
        st.subheader("Créer / Modifier une recette")
        mode = st.radio("Mode", ["Créer", "Modifier"], horizontal=True)

        selected_recipe = None
        default_name = ""
        default_portions = 1
        default_ingredients: List[Dict] = []

        if mode == "Modifier":
            if not recipe_names:
                st.info("Aucune recette à modifier pour le moment.")
            else:
                selected_name = st.selectbox("Choisir une recette", recipe_names)
                selected_recipe = next((r for r in recipes if r.get("name") == selected_name), None)
                if selected_recipe:
                    default_name = selected_recipe.get("name", "")
                    default_portions = int(selected_recipe.get("portions", 1) or 1)
                    default_ingredients = [normalize_ingredient_for_editor(ing) for ing in selected_recipe.get("ingredients", [])]

        with st.form("recipe_form"):
            recipe_name = st.text_input("Nom de la recette", value=default_name)
            portions = st.number_input("Nombre de portions", min_value=1, step=1, value=default_portions)
            st.markdown("### Ingrédients")
            st.caption("Les aliments de base sont définis pour 100 g. Si `Auto` est activé et l'unité en g/kg, les macros sont calculées automatiquement selon la quantité.")
            ingredients = st.data_editor(
                default_ingredients if default_ingredients else [default_ingredient_row()],
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "food": st.column_config.SelectboxColumn("Aliment (base)", options=sorted(foods_map.keys())),
                    "name": st.column_config.TextColumn("Nom affiché"),
                    "auto": st.column_config.CheckboxColumn("Auto"),
                    "quantity": st.column_config.NumberColumn("Quantité", min_value=0.0, step=0.1),
                    "unit": st.column_config.SelectboxColumn("Unité", options=UNITS),
                    "calories": st.column_config.NumberColumn("Calories", min_value=0.0, step=1.0),
                    "proteines": st.column_config.NumberColumn("Protéines", min_value=0.0, step=0.1),
                    "glucides": st.column_config.NumberColumn("Glucides", min_value=0.0, step=0.1),
                    "lipides": st.column_config.NumberColumn("Lipides", min_value=0.0, step=0.1),
                },
            )

            submitted = st.form_submit_button("💾 Sauvegarder la recette")

        if submitted:
            if not recipe_name.strip():
                st.error("Le nom de la recette est obligatoire.")
            else:
                clean_ingredients = sanitize_ingredients(ingredients, foods_map)
                recipe_obj = {
                    "name": recipe_name.strip(),
                    "portions": int(portions),
                    "ingredients": clean_ingredients,
                }

                if mode == "Modifier" and selected_recipe:
                    recipes = [r for r in recipes if r.get("name") != selected_recipe.get("name")]

                recipes = update_recipe_in_list(recipes, recipe_obj["name"], recipe_obj)
                save_recipes(recipes)
                st.success("Recette sauvegardée.")
                st.rerun()

        st.divider()
        st.subheader("Base d'aliments (valeurs pour 100 g)")
        with st.form("foods_form"):
            edited_foods = st.data_editor(
                foods if foods else DEFAULT_FOODS,
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "name": st.column_config.TextColumn("Aliment"),
                    "calories": st.column_config.NumberColumn("Calories", min_value=0.0, step=1.0),
                    "proteines": st.column_config.NumberColumn("Protéines", min_value=0.0, step=0.1),
                    "glucides": st.column_config.NumberColumn("Glucides", min_value=0.0, step=0.1),
                    "lipides": st.column_config.NumberColumn("Lipides", min_value=0.0, step=0.1),
                },
            )
            save_foods_clicked = st.form_submit_button("💾 Sauvegarder la base d'aliments")

        if save_foods_clicked:
            clean_foods = []
            seen_names = set()
            for food in edited_foods:
                name = str(food.get("name", "")).strip()
                if not name:
                    continue
                if name.lower() in seen_names:
                    st.error(f"Aliment en double ignoré : {name}")
                    continue
                seen_names.add(name.lower())
                clean_foods.append(
                    {
                        "name": name,
                        "calories": float(food.get("calories", 0) or 0),
                        "proteines": float(food.get("proteines", 0) or 0),
                        "glucides": float(food.get("glucides", 0) or 0),
                        "lipides": float(food.get("lipides", 0) or 0),
                    }
                )
            save_foods(clean_foods)
            st.success("Base d'aliments sauvegardée.")
            st.rerun()

        st.divider()
        st.subheader("Recettes enregistrées")

        if not recipes:
            st.info("Aucune recette enregistrée.")
        else:
            for recipe in recipes:
                totals = recipe_totals(recipe)
                with st.expander(f"{recipe['name']} ({recipe['portions']} portions)"):
                    st.write(
                        f"Calories totales: **{totals['calories']:.1f} kcal** | "
                        f"Calories/portion: **{totals['calories_par_portion']:.1f} kcal**"
                    )
                    st.write(
                        f"Protéines/portion: **{totals['proteines_par_portion']:.1f} g** | "
                        f"Glucides/portion: **{totals['glucides_par_portion']:.1f} g** | "
                        f"Lipides/portion: **{totals['lipides_par_portion']:.1f} g**"
                    )
                    st.dataframe(recipe.get("ingredients", []), use_container_width=True)
                    if st.button(f"🗑️ Supprimer {recipe['name']}", key=f"del_{recipe['name']}"):
                        new_recipes = [r for r in recipes if r.get("name") != recipe.get("name")]
                        save_recipes(new_recipes)
                        st.warning(f"Recette '{recipe['name']}' supprimée.")
                        st.rerun()

    with tab2:
        st.subheader("Générer une liste de courses")
        if not recipes:
            st.info("Ajoutez au moins une recette pour générer une liste de courses.")
        else:
            choices = st.multiselect("Sélectionner les recettes", recipe_names, default=recipe_names)
            selected = [r for r in recipes if r.get("name") in choices]
            shopping = build_shopping_list(selected)

            if not shopping:
                st.info("Aucun ingrédient trouvé pour la sélection.")
            else:
                shopping_rows = [
                    {
                        "ingredient": item["name"],
                        "quantite_totale": round(item["quantity"], 2),
                        "unite": item["unit"],
                    }
                    for item in shopping.values()
                ]
                st.dataframe(shopping_rows, use_container_width=True)

    with tab3:
        st.subheader("Exports CSV")
        recipes_csv = rows_to_csv_bytes(recipes_to_csv_rows(recipes))
        st.download_button(
            "⬇️ Exporter les recettes (CSV)",
            data=recipes_csv,
            file_name="recipes_export.csv",
            mime="text/csv",
            disabled=not recipes,
        )

        if recipes:
            selected_for_csv = build_shopping_list(recipes)
            shopping_csv = rows_to_csv_bytes(shopping_to_csv_rows(selected_for_csv))
            st.download_button(
                "⬇️ Exporter la liste de courses (CSV)",
                data=shopping_csv,
                file_name="shopping_list_export.csv",
                mime="text/csv",
                disabled=not selected_for_csv,
            )


if __name__ == "__main__":
    main()
