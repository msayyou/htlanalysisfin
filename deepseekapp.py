# hotel_financial_dashboard.py
# Application d'analyse financière hôtelière
# Exécution: streamlit run hotel_financial_dashboard.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Dashboard Analyse Financiere Hotelière",
    page_icon="🏨",
    layout="wide"
)

st.title("🏨 Dashboard d'Analyse Financière Hôtelière")
st.markdown("**Basé sur l'étude de Jawabreh et al. (2017) et les KPIs Fáilte Ireland**")
st.markdown("---")

st.sidebar.header("📊 Navigation")
section = st.sidebar.selectbox(
    "Choisissez une section",
    [
        "1. Vue d'ensemble - KPIs Globaux",
        "2. Analyse de Sensibilite du Profit",
        "3. Taux d'Occupation",
        "4. Departement Hebergement",
        "5. Departement Restauration (F&B)",
        "6. Departement Spa & Loisirs",
        "7. Depenses des Clients",
        "8. Rentabilite par Activite",
        "9. Taux de Couts d'Exploitation",
        "10. Comparaison avec les Normes",
        "11. Rapport Complet"
    ]
)


# ============================================================================
# FONCTIONS
# ============================================================================

def calculate_hotel_kpis(data):
    total_revenue = data["total_revenue"]
    rooms_revenue = data["accommodation_revenue"]
    available_rooms = data["available_rooms"]
    occupied_rooms = data["occupied_rooms"]
    
    rooms_profit = data["accommodation_revenue"] - data["accommodation_costs"]
    f_and_b_profit = data["food_revenue"] - data["food_costs"]
    other_profit = data["other_revenue"] - data["other_costs"]
    total_department_profit = rooms_profit + f_and_b_profit + other_profit
    gross_operating_profit = total_department_profit - data["admin_costs"] - data["sales_promotion_costs"]
    
    kpis = {
        "Occupancy (%)": (occupied_rooms / available_rooms) * 100 if available_rooms > 0 else 0,
        "ADR (€)": rooms_revenue / occupied_rooms if occupied_rooms > 0 else 0,
        "RevPAR (€)": rooms_revenue / available_rooms if available_rooms > 0 else 0,
        "TRevPAR (€)": total_revenue / available_rooms if available_rooms > 0 else 0,
        "TRevPOR (€)": total_revenue / occupied_rooms if occupied_rooms > 0 else 0,
        "Total Department Profit (%)": (total_department_profit / total_revenue) * 100 if total_revenue > 0 else 0,
        "Gross Operating Profit (%)": (gross_operating_profit / total_revenue) * 100 if total_revenue > 0 else 0,
        "EBITDA (%)": ((gross_operating_profit + data.get("depreciation", 0)) / total_revenue) * 100 if total_revenue > 0 else 0,
        "Total Department Cost (%)": ((data["accommodation_costs"] + data["food_costs"] + data["other_costs"]) / total_revenue) * 100 if total_revenue > 0 else 0,
        "Total Payroll Cost (%)": (data.get("total_payroll", 25000) / total_revenue) * 100 if total_revenue > 0 else 0,
        "Undistributed Cost (%)": ((data["admin_costs"] + data["sales_promotion_costs"]) / total_revenue) * 100 if total_revenue > 0 else 0,
    }
    return kpis


def calculate_rooms_kpis(data):
    rooms_revenue = data["accommodation_revenue"]
    rooms_costs = data["accommodation_costs"]
    rooms_profit = rooms_revenue - rooms_costs
    available_rooms = data["available_rooms"]
    occupied_rooms = data["occupied_rooms"]
    
    kpis = {
        "Occupancy (%)": (occupied_rooms / available_rooms) * 100 if available_rooms > 0 else 0,
        "ADR (€)": rooms_revenue / occupied_rooms if occupied_rooms > 0 else 0,
        "RevPAR (€)": rooms_revenue / available_rooms if available_rooms > 0 else 0,
        "Total Rooms Dept Profit (%)": (rooms_profit / rooms_revenue) * 100 if rooms_revenue > 0 else 0,
        "Total Rooms Dept Cost (%)": (rooms_costs / rooms_revenue) * 100 if rooms_revenue > 0 else 0,
        "Cost per occupied Room (€)": rooms_costs / occupied_rooms if occupied_rooms > 0 else 0,
    }
    return kpis


def calculate_fandb_kpis(data):
    food_revenue = data["food_revenue"]
    beverage_revenue = data.get("beverage_revenue", food_revenue * 0.40)
    total_fandb_revenue = food_revenue + beverage_revenue
    total_fandb_costs = data["food_costs"] + data.get("beverage_costs", 0)
    fandb_profit = total_fandb_revenue - total_fandb_costs
    
    occupied_rooms = data["occupied_rooms"]
    available_rooms = data["available_rooms"]
    num_covers = data.get("num_covers", data["num_guests"] * 2)
    
    kpis = {
        "Total F&B Dept Profit (%)": (fandb_profit / total_fandb_revenue) * 100 if total_fandb_revenue > 0 else 0,
        "Average Spend per Cover (€)": total_fandb_revenue / num_covers if num_covers > 0 else 0,
        "F&B Revenue POR (€)": total_fandb_revenue / occupied_rooms if occupied_rooms > 0 else 0,
        "F&B Revenue PAR (€)": total_fandb_revenue / available_rooms if available_rooms > 0 else 0,
        "Food Cost of Sales (%)": (data.get("food_cogs", food_revenue * 0.30) / food_revenue) * 100 if food_revenue > 0 else 0,
    }
    return kpis


def calculate_spa_kpis(data):
    spa_revenue = data.get("spa_revenue", 25000)
    spa_costs = data.get("spa_costs", 15000)
    spa_profit = spa_revenue - spa_costs
    
    treatment_hours_sold = data.get("treatment_hours_sold", 320)
    treatment_hours_available = data.get("treatment_hours_available", 500)
    occupied_rooms = data["occupied_rooms"]
    total_guests = data["num_guests"]
    spa_guests = data.get("spa_guests", 380)
    
    kpis = {
        "Treatment Room Utilisation (%)": (treatment_hours_sold / treatment_hours_available) * 100 if treatment_hours_available > 0 else 0,
        "Total Spa Dept Profit (%)": (spa_profit / spa_revenue) * 100 if spa_revenue > 0 else 0,
        "Spa Revenue POR (€)": spa_revenue / occupied_rooms if occupied_rooms > 0 else 0,
        "Guest Capture Rate (%)": (spa_guests / total_guests) * 100 if total_guests > 0 else 0,
        "Total Spa Dept Cost (%)": (spa_costs / spa_revenue) * 100 if spa_revenue > 0 else 0,
    }
    return kpis


def calculate_profit_sensitivity(guests, avg_spending, var_material, var_wages, admin_exp, general_exp, change_percent=0.10):
    sales = guests * avg_spending
    var_costs = guests * (var_material + var_wages)
    fixed_costs = admin_exp + general_exp
    net_income = sales - var_costs - fixed_costs
    
    results = {}
    
    # 1. Variation du nombre de clients
    guests_new = guests * (1 + change_percent)
    sales_new = guests_new * avg_spending
    var_costs_new = guests_new * (var_material + var_wages)
    net_income_new = sales_new - var_costs_new - fixed_costs
    change_ratio = (net_income_new - net_income) / net_income if net_income != 0 else 0
    profit_multiplier = change_ratio / change_percent if change_percent != 0 else 0
    results["Nombre de clients"] = profit_multiplier
    
    # 2. Variation du pouvoir de depense moyen
    spending_new = avg_spending * (1 + change_percent)
    sales_new = guests * spending_new
    net_income_new = sales_new - var_costs - fixed_costs
    change_ratio = (net_income_new - net_income) / net_income if net_income != 0 else 0
    profit_multiplier = change_ratio / change_percent if change_percent != 0 else 0
    results["Pouvoir de depense/client"] = profit_multiplier
    
    # 3. Variation du cout des materiaux
    material_new = var_material * (1 + change_percent)
    var_costs_new = guests * (material_new + var_wages)
    net_income_new = sales - var_costs_new - fixed_costs
    change_ratio = (net_income_new - net_income) / net_income if net_income != 0 else 0
    profit_multiplier = change_ratio / change_percent if change_percent != 0 else 0
    results["Cout des materiaux"] = profit_multiplier
    
    # 4. Variation des salaires variables
    wages_new = var_wages * (1 + change_percent)
    var_costs_new = guests * (var_material + wages_new)
    net_income_new = sales - var_costs_new - fixed_costs
    change_ratio = (net_income_new - net_income) / net_income if net_income != 0 else 0
    profit_multiplier = change_ratio / change_percent if change_percent != 0 else 0
    results["Salaires variables"] = profit_multiplier
    
    # 5. Variation des frais administratifs
    admin_new = admin_exp * (1 + change_percent)
    fixed_costs_new = admin_new + general_exp
    net_income_new = sales - var_costs - fixed_costs_new
    change_ratio = (net_income_new - net_income) / net_income if net_income != 0 else 0
    profit_multiplier = change_ratio / change_percent if change_percent != 0 else 0
    results["Frais administratifs"] = profit_multiplier
    
    # 6. Variation des frais generaux
    general_new = general_exp * (1 + change_percent)
    fixed_costs_new = admin_exp + general_new
    net_income_new = sales - var_costs - fixed_costs_new
    change_ratio = (net_income_new - net_income) / net_income if net_income != 0 else 0
    profit_multiplier = change_ratio / change_percent if change_percent != 0 else 0
    results["Frais generaux"] = profit_multiplier
    
    return results, net_income


# ============================================================================
# DONNEES PAR DEFAUT
# ============================================================================

default_data = {
    "total_revenue": 144000,
    "accommodation_revenue": 88762.5,
    "food_revenue": 39839.25,
    "other_revenue": 15396.3,
    "accommodation_costs": 15396.3,
    "food_costs": 15396.3,
    "other_costs": 15396.3,
    "admin_costs": 34500,
    "sales_promotion_costs": 2000,
    "total_payroll": 25000,
    "depreciation": 5000,
    "available_rooms": 600,
    "occupied_rooms": 322,
    "num_guests": 1200,
    "total_nights": 3600,
    "num_meals": 2500,
    "guests": 1200,
    "avg_spending": 120,
    "var_material": 25,
    "var_wages": 15,
    "admin_exp": 34500,
    "general_exp": 25000,
    "spa_revenue": 25000,
    "spa_costs": 15000,
    "beverage_revenue": 15935.7,
    "beverage_costs": 3983.9,
    "food_cogs": 11951.78,
    "treatment_hours_sold": 320,
    "treatment_hours_available": 500,
    "spa_guests": 380,
    "num_covers": 2400,
    "energy_costs": 3000,
    "maintenance_costs": 2500,
}

use_defaults = st.sidebar.checkbox("Utiliser les donnees par defaut (Hotel Al Zaitonia)", value=True)
data = default_data.copy() if use_defaults else default_data.copy()


# ============================================================================
# SECTION 1: VUE D'ENSEMBLE
# ============================================================================

if section == "1. Vue d'ensemble - KPIs Globaux":
    st.header("🏆 Vue d'ensemble - KPIs Globaux")
    
    kpis = calculate_hotel_kpis(data)
    
    st.subheader("💰 KPIs de Revenus")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Occupancy", f"{kpis['Occupancy (%)']:.1f}%")
    col2.metric("ADR", f"{kpis['ADR (€)']:.2f} €")
    col3.metric("RevPAR", f"{kpis['RevPAR (€)']:.2f} €")
    col4.metric("TRevPAR", f"{kpis['TRevPAR (€)']:.2f} €")
    col5.metric("TRevPOR", f"{kpis['TRevPOR (€)']:.2f} €")
    
    st.subheader("📈 KPIs de Profitabilite")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Department Profit", f"{kpis['Total Department Profit (%)']:.1f}%")
    col2.metric("Gross Operating Profit", f"{kpis['Gross Operating Profit (%)']:.1f}%")
    col3.metric("EBITDA", f"{kpis['EBITDA (%)']:.1f}%")
    
    st.subheader("📉 KPIs de Couts")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Department Cost", f"{kpis['Total Department Cost (%)']:.1f}%")
    col2.metric("Total Payroll Cost", f"{kpis['Total Payroll Cost (%)']:.1f}%")
    col3.metric("Undistributed Cost", f"{kpis['Undistributed Cost (%)']:.1f}%")
    
    # Graphique
    fig = go.Figure()
    categories = ["Occupancy", "ADR/20", "RevPAR", "GOP%", "EBITDA%"]
    values = [kpis['Occupancy (%)'], kpis['ADR (€)']/20, kpis['RevPAR (€)'], 
              kpis['Gross Operating Profit (%)'], kpis['EBITDA (%)']]
    fig.add_trace(go.Bar(x=categories, y=values, marker_color='steelblue'))
    fig.update_layout(title="Indicateurs clés de performance", height=500)
    st.plotly_chart(fig, use_container_width=True)


# ============================================================================
# SECTION 2: ANALYSE DE SENSIBILITE
# ============================================================================

elif section == "2. Analyse de Sensibilite du Profit":
    st.header("📈 Analyse de Sensibilite du Profit")
    
    st.markdown("""
    **Multiplicateur de profit** = (Variation % du benefice net) / (Variation % du facteur)
    
    Facteurs controlants: Nombre de clients, Pouvoir de depense, Couts des materiaux,
    Salaires variables, Frais administratifs, Frais generaux.
    """)
    
    change_percent = st.slider("Variation des facteurs (%)", 1, 30, 10) / 100
    
    results, base_net_income = calculate_profit_sensitivity(
        data["guests"], data["avg_spending"], data["var_material"], 
        data["var_wages"], data["admin_exp"], data["general_exp"], change_percent
    )
    
    st.metric("Benefice net initial", f"{base_net_income:,.2f} JOD")
    
    ranking = sorted(results.items(), key=lambda x: x[1], reverse=True)
    ranking_df = pd.DataFrame(ranking, columns=["Facteur controlant", "Multiplicateur"])
    ranking_df.index = range(1, len(ranking_df) + 1)
    st.dataframe(ranking_df, use_container_width=True)
    
    fig = px.bar(ranking_df, x="Facteur controlant", y="Multiplicateur", 
                 title="Multiplicateur de profit", color="Multiplicateur")
    st.plotly_chart(fig, use_container_width=True)


# ============================================================================
# SECTION 3: TAUX D'OCCUPATION
# ============================================================================

elif section == "3. Taux d'Occupation":
    st.header("🏠 Taux d'Occupation")
    
    available_rooms = st.number_input("Chambres disponibles", value=data["available_rooms"], min_value=1)
    occupied_rooms = st.number_input("Chambres occupees", value=data["occupied_rooms"], min_value=0)
    
    occupancy_rate = (occupied_rooms / available_rooms) * 100
    st.metric("Taux d'occupation", f"{occupancy_rate:.1f}%")
    
    monthly_data = pd.DataFrame({
        "Mois": ["Jan", "Fev", "Mar", "Avr", "Mai", "Juin", "Juil", "Aou", "Sep", "Oct", "Nov", "Dec"],
        "Taux (%)": [42, 33, 47, 50, 55, 67, 75, 70, 58, 50, 38, 50]
    })
    
    fig = px.line(monthly_data, x="Mois", y="Taux (%)", title="Evolution mensuelle", markers=True)
    fig.add_hline(y=monthly_data["Taux (%)"].mean(), line_dash="dash", 
                  annotation_text=f"Moyenne: {monthly_data['Taux (%)'].mean():.1f}%")
    st.plotly_chart(fig, use_container_width=True)


# ============================================================================
# SECTION 4: DEPARTEMENT HEBERGEMENT
# ============================================================================

elif section == "4. Departement Hebergement":
    st.header("🛏️ Departement Hebergement")
    
    rooms_kpis = calculate_rooms_kpis(data)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Occupancy", f"{rooms_kpis['Occupancy (%)']:.1f}%")
    col2.metric("ADR", f"{rooms_kpis['ADR (€)']:.2f} €")
    col3.metric("RevPAR", f"{rooms_kpis['RevPAR (€)']:.2f} €")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Profitabilite", f"{rooms_kpis['Total Rooms Dept Profit (%)']:.1f}%")
    col2.metric("Taux de cout", f"{rooms_kpis['Total Rooms Dept Cost (%)']:.1f}%")
    col3.metric("Cout par chambre occupee", f"{rooms_kpis['Cost per occupied Room (€)']:.2f} €")


# ============================================================================
# SECTION 5: DEPARTEMENT RESTAURATION
# ============================================================================

elif section == "5. Departement Restauration (F&B)":
    st.header("🍽️ Departement Restauration (F&B)")
    
    fandb_kpis = calculate_fandb_kpis(data)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Profitabilite F&B", f"{fandb_kpis['Total F&B Dept Profit (%)']:.1f}%")
    col2.metric("Depense moyenne par couvert", f"{fandb_kpis['Average Spend per Cover (€)']:.2f} €")
    col3.metric("F&B Revenue POR", f"{fandb_kpis['F&B Revenue POR (€)']:.2f} €")
    
    col1, col2 = st.columns(2)
    col1.metric("F&B Revenue PAR", f"{fandb_kpis['F&B Revenue PAR (€)']:.2f} €")
    col2.metric("Food Cost of Sales", f"{fandb_kpis['Food Cost of Sales (%)']:.1f}%")


# ============================================================================
# SECTION 6: DEPARTEMENT SPA & LOISIRS
# ============================================================================

elif section == "6. Departement Spa & Loisirs":
    st.header("💆 Departement Spa & Loisirs")
    
    spa_kpis = calculate_spa_kpis(data)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Taux d'utilisation salles", f"{spa_kpis['Treatment Room Utilisation (%)']:.1f}%")
    col2.metric("Profitabilite Spa", f"{spa_kpis['Total Spa Dept Profit (%)']:.1f}%")
    col3.metric("Spa Revenue POR", f"{spa_kpis['Spa Revenue POR (€)']:.2f} €")
    col4.metric("Guest Capture Rate", f"{spa_kpis['Guest Capture Rate (%)']:.1f}%")


# ============================================================================
# SECTION 7: DEPENSES DES CLIENTS
# ============================================================================

elif section == "7. Depenses des Clients":
    st.header("💰 Depenses des Clients")
    
    total_revenue = data["total_revenue"]
    num_guests = data["num_guests"]
    accommodation_revenue = data["accommodation_revenue"]
    food_revenue = data["food_revenue"]
    other_revenue = data["other_revenue"]
    num_meals = data["num_meals"]
    total_nights = data["total_nights"]
    
    avg_spending = total_revenue / num_guests
    avg_accommodation = accommodation_revenue / num_guests
    avg_food = food_revenue / num_guests
    avg_other = other_revenue / num_guests
    avg_per_meal = food_revenue / num_meals if num_meals > 0 else 0
    avg_stay = total_nights / num_guests
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Depense moyenne generale", f"{avg_spending:.2f} JOD")
    col2.metric("Depense moyenne hebergement", f"{avg_accommodation:.2f} JOD")
    col3.metric("Depense moyenne repas", f"{avg_food:.2f} JOD")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Depense moyenne autres", f"{avg_other:.2f} JOD")
    col2.metric("Depense moyenne par repas", f"{avg_per_meal:.2f} JOD")
    col3.metric("Duree moyenne sejour", f"{avg_stay:.1f} nuits")
    
    composition = pd.DataFrame({
        "Service": ["Hebergement", "Repas", "Autres"],
        "Revenu": [accommodation_revenue, food_revenue, other_revenue]
    })
    fig = px.pie(composition, values="Revenu", names="Service", title="Repartition du revenu")
    st.plotly_chart(fig, use_container_width=True)


# ============================================================================
# SECTION 8: RENTABILITE PAR ACTIVITE
# ============================================================================

elif section == "8. Rentabilite par Activite":
    st.header("📊 Rentabilite par Activite")
    
    acc_rev = data["accommodation_revenue"]
    acc_cost = data["accommodation_costs"]
    food_rev = data["food_revenue"]
    food_cost = data["food_costs"]
    other_rev = data["other_revenue"]
    other_cost = data["other_costs"]
    
    acc_rent = ((acc_rev - acc_cost) / acc_cost) * 100 if acc_cost > 0 else 0
    food_rent = ((food_rev - food_cost) / food_cost) * 100 if food_cost > 0 else 0
    other_rent = ((other_rev - other_cost) / other_cost) * 100 if other_cost > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Rentabilite Hebergement", f"{acc_rent:.1f}%")
    col2.metric("Rentabilite Repas", f"{food_rent:.1f}%")
    col3.metric("Rentabilite Autres", f"{other_rent:.1f}%")
    
    fig = px.bar(x=["Hebergement", "Repas", "Autres"], y=[acc_rent, food_rent, other_rent],
                 title="Taux de rentabilite par activite", color=[acc_rent, food_rent, other_rent])
    st.plotly_chart(fig, use_container_width=True)


# ============================================================================
# SECTION 9: TAUX DE COUTS D'EXPLOITATION
# ============================================================================

elif section == "9. Taux de Couts d'Exploitation":
    st.header("📉 Taux de Couts d'Exploitation")
    
    total_revenue = data["total_revenue"]
    
    direct_acc = (data["accommodation_costs"] / data["accommodation_revenue"]) * 100 if data["accommodation_revenue"] > 0 else 0
    direct_food = (data["food_costs"] / data["food_revenue"]) * 100 if data["food_revenue"] > 0 else 0
    admin_rate = (data["admin_costs"] / total_revenue) * 100 if total_revenue > 0 else 0
    promo_rate = (data["sales_promotion_costs"] / total_revenue) * 100 if total_revenue > 0 else 0
    
    col1, col2 = st.columns(2)
    col1.subheader("Couts directs")
    col1.metric("Hebergement", f"{direct_acc:.1f}%")
    col1.metric("Repas", f"{direct_food:.1f}%")
    
    col2.subheader("Couts indirects")
    col2.metric("Administratifs", f"{admin_rate:.1f}%")
    col2.metric("Promotion", f"{promo_rate:.1f}%")


# ============================================================================
# SECTION 10: COMPARAISON AVEC LES NORMES
# ============================================================================

elif section == "10. Comparaison avec les Normes":
    st.header("🏆 Comparaison avec les Normes Sectorielles")
    
    standards = pd.DataFrame({
        "Categorie": ["Revenus - Hebergement", "Revenus - Restauration", "Couts directs - Hebergement"],
        "Norme min": ["45%", "35%", "15%"],
        "Norme max": ["50%", "40%", "25%"],
        "Hotel": [
            f"{data['accommodation_revenue']/data['total_revenue']*100:.1f}%",
            f"{data['food_revenue']/data['total_revenue']*100:.1f}%",
            f"{data['accommodation_costs']/data['accommodation_revenue']*100:.1f}%"
        ]
    })
    st.dataframe(standards, use_container_width=True)
    
    hotel_values = [
        data['accommodation_revenue']/data['total_revenue']*100,
        data['food_revenue']/data['total_revenue']*100,
        data['other_revenue']/data['total_revenue']*100
    ]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Hotel", x=["Hebergement", "Restauration", "Autres"], y=hotel_values, marker_color="blue"))
    fig.add_trace(go.Bar(name="Norme min", x=["Hebergement", "Restauration", "Autres"], y=[45, 35, 5], marker_color="lightgray"))
    fig.add_trace(go.Bar(name="Norme max", x=["Hebergement", "Restauration", "Autres"], y=[50, 40, 10], marker_color="darkgray"))
    fig.update_layout(title="Structure des revenus - Comparaison", barmode="group")
    st.plotly_chart(fig, use_container_width=True)


# ============================================================================
# SECTION 11: RAPPORT COMPLET
# ============================================================================

else:
    st.header("📑 Rapport d'Analyse Financiere Complet")
    
    kpis = calculate_hotel_kpis(data)
    rooms_kpis = calculate_rooms_kpis(data)
    fandb_kpis = calculate_fandb_kpis(data)
    spa_kpis = calculate_spa_kpis(data)
    
    st.subheader("🎯 Tableau de bord strategique")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Occupancy", f"{kpis['Occupancy (%)']:.1f}%")
    col2.metric("ADR", f"{kpis['ADR (€)']:.2f}€")
    col3.metric("RevPAR", f"{kpis['RevPAR (€)']:.2f}€")
    col4.metric("GOP %", f"{kpis['Gross Operating Profit (%)']:.1f}%")
    
    sensitivity_results, _ = calculate_profit_sensitivity(
        data["guests"], data["avg_spending"], data["var_material"], 
        data["var_wages"], data["admin_exp"], data["general_exp"], 0.10
    )
    
    st.subheader("🔍 Leviers de profitabilite")
    ranking = sorted(sensitivity_results.items(), key=lambda x: x[1], reverse=True)
    for i, (factor, mult) in enumerate(ranking[:3], 1):
        st.write(f"**{i}. {factor}** : Multiplicateur = {mult:.2f}x")
    
    st.subheader("📝 Recommandations")
    if kpis['Occupancy (%)'] < 65:
        st.write("🟡 Ameliorer l'occupation avec des offres hors saison")
    if kpis['Gross Operating Profit (%)'] < 30:
        st.write("🟡 Optimiser les couts pour ameliorer la profitabilite")
    if fandb_kpis['Total F&B Dept Profit (%)'] < 20:
        st.write("🟡 Revoir la strategie prix du restaurant")
    
    with st.expander("📚 Formules utilisees"):
        st.markdown("""
        - **Occupancy** = Chambres occupees / Chambres disponibles
        - **ADR** = Revenu hebergement / Chambres occupees
        - **RevPAR** = Revenu hebergement / Chambres disponibles = Occupancy x ADR
        - **TRevPAR** = Revenu total / Chambres disponibles
        - **GOP%** = (Revenu total - Couts d'exploitation) / Revenu total
        - **Multiplicateur de profit** = (Δ% Benefice net) / (Δ% Facteur controlant)
        """)

st.markdown("---")
st.caption("Dashboard d'Analyse Financiere Hotelière | Jawabreh et al. (2017) + Fáilte Ireland KPIs")
