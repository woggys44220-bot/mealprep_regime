import csv
import json
from pathlib import Path
from typing import Dict, List

import streamlit as st

DATA_DIR = Path("data")
RECIPES_FILE = DATA_DIR / "recipes.json"
UNITS = ["g", "kg", "ml", "l", "pièce", "cuillère", "tasse"]


def ensure_data_file() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    if not RECIPES_FILE.exists():
        RECIPES_FILE.write_text("[]", encoding="utf-8")


def load_recipes() -> List[Dict]:
    ensure_data_file()
    try:
        data = json.loads(RECIPES_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def save_recipes(recipes: List[Dict]) -> None:
    RECIPES_FILE.write_text(json.dumps(recipes, indent=2, ensure_ascii=False), encoding="utf-8")


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


def main() -> None:
    st.set_page_config(page_title="Meal Prep Régime", layout="wide")
    st.title("🥗 Meal Prep Régime (V1)")

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
                    default_ingredients = selected_recipe.get("ingredients", [])

        with st.form("recipe_form"):
            recipe_name = st.text_input("Nom de la recette", value=default_name)
            portions = st.number_input("Nombre de portions", min_value=1, step=1, value=default_portions)
            st.markdown("### Ingrédients")
            ingredients = st.data_editor(
                default_ingredients if default_ingredients else [
                    {
                        "name": "",
                        "quantity": 0.0,
                        "unit": "g",
                        "calories": 0.0,
                        "proteines": 0.0,
                        "glucides": 0.0,
                        "lipides": 0.0,
                    }
                ],
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "name": st.column_config.TextColumn("Ingrédient"),
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
                clean_ingredients = []
                for ing in ingredients:
                    if not str(ing.get("name", "")).strip():
                        continue
                    clean_ingredients.append(
                        {
                            "name": str(ing.get("name", "")).strip(),
                            "quantity": float(ing.get("quantity", 0) or 0),
                            "unit": str(ing.get("unit", "g")),
                            "calories": float(ing.get("calories", 0) or 0),
                            "proteines": float(ing.get("proteines", 0) or 0),
                            "glucides": float(ing.get("glucides", 0) or 0),
                            "lipides": float(ing.get("lipides", 0) or 0),
                        }
                    )

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
            selected_export = st.multiselect(
                "Recettes pour la liste de courses CSV",
                recipe_names,
                default=recipe_names,
                key="export_select",
            )
            shopping_export = build_shopping_list([r for r in recipes if r.get("name") in selected_export])
            shopping_csv = rows_to_csv_bytes(shopping_to_csv_rows(shopping_export))
            st.download_button(
                "⬇️ Exporter la liste de courses (CSV)",
                data=shopping_csv,
                file_name="shopping_list_export.csv",
                mime="text/csv",
                disabled=not shopping_export,
            )


if __name__ == "__main__":
    main()
