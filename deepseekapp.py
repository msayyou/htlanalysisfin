# hotel_financial_dashboard.py
# Application d'analyse financière hôtelière
# Exécution: streamlit run hotel_financial_dashboard.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Analyse Financiere Hotelière",
    page_icon="🏨",
    layout="wide"
)

# Titre principal
st.title("🏨 Dashboard d'Analyse Financière Hôtelière")
st.markdown("**Basé sur l'étude de Jawabreh et al. (2017) et les KPIs Fáilte Ireland**")
st.markdown("---")

# Sidebar pour la navigation
st.sidebar.header("📊 Navigation")
section = st.sidebar.selectbox(
    "Choisissez une section",
    [
        "1. Vue d_ensemble - KPIs Globaux",
        "2. Analyse de Sensibilite du Profit",
        "3. Taux d_Occupation",
        "4. Departement Hebergement",
        "5. Departement Restauration (F&B)",
        "6. Departement Spa & Loisirs",
        "7. Depenses des Clients",
        "8. Rentabilite par Activite",
        "9. Taux de Couts d_Exploitation",
        "10. Comparaison avec les Normes Sectorielles",
        "11. Rapport Complet"
    ]
)


# ============================================================================
# FONCTIONS POUR LES KPIs GLOBAUX
# ============================================================================

def calculate_hotel_kpis(data):
    """Calcule tous les KPIs globaux de l'hotel"""
    
    total_revenue = data["total_revenue"]
    rooms_revenue = data["accommodation_revenue"]
    f_and_b_revenue = data["food_revenue"]
    other_revenue = data["other_revenue"]
    
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
        "Total Revenue (€)": total_revenue,
        "Gross Operating Profit (€)": gross_operating_profit,
        "Total Department Profit (€)": total_department_profit
    }
    return kpis


def calculate_rooms_kpis(data):
    """Calcule les KPIs du département Hebergement"""
    
    rooms_revenue = data["accommodation_revenue"]
    rooms_costs = data["accommodation_costs"]
    rooms_profit = rooms_revenue - rooms_costs
    available_rooms = data["available_rooms"]
    occupied_rooms = data["occupied_rooms"]
    commissions = data.get("commissions", rooms_revenue * 0.10)
    payroll_costs = data.get("rooms_payroll", rooms_revenue * 0.15)
    other_costs = rooms_costs - payroll_costs - commissions
    
    kpis = {
        "Occupancy (%)": (occupied_rooms / available_rooms) * 100 if available_rooms > 0 else 0,
        "ADR (€)": rooms_revenue / occupied_rooms if occupied_rooms > 0 else 0,
        "RevPAR (€)": rooms_revenue / available_rooms if available_rooms > 0 else 0,
        "RevPAR (Occupancy x ADR)": ((occupied_rooms / available_rooms) * (rooms_revenue / occupied_rooms)) if occupied_rooms > 0 and available_rooms > 0 else 0,
        "Total Rooms Dept Profit (%)": (rooms_profit / rooms_revenue) * 100 if rooms_revenue > 0 else 0,
        "Commissions (%)": (commissions / rooms_revenue) * 100 if rooms_revenue > 0 else 0,
        "Rooms Payroll Cost (%)": (payroll_costs / rooms_revenue) * 100 if rooms_revenue > 0 else 0,
        "Other Rooms Dept Cost (%)": (other_costs / rooms_revenue) * 100 if rooms_revenue > 0 else 0,
        "Total Rooms Dept Cost (%)": (rooms_costs / rooms_revenue) * 100 if rooms_revenue > 0 else 0,
        "Cost per occupied Room (€)": rooms_costs / occupied_rooms if occupied_rooms > 0 else 0,
        "Rooms Profit (€)": rooms_profit,
        "Rooms Revenue (€)": rooms_revenue
    }
    return kpis


def calculate_fandb_kpis(data):
    """Calcule les KPIs du département Restauration (F&B)"""
    
    food_revenue = data["food_revenue"]
    beverage_revenue = data.get("beverage_revenue", food_revenue * 0.40)
    total_fandb_revenue = food_revenue + beverage_revenue
    
    food_cogs = data.get("food_cogs", food_revenue * 0.30)
    beverage_cogs = data.get("beverage_cogs", beverage_revenue * 0.25)
    total_fandb_costs = data["food_costs"] + data.get("beverage_costs", 0)
    fandb_profit = total_fandb_revenue - total_fandb_costs
    
    occupied_rooms = data["occupied_rooms"]
    available_rooms = data["available_rooms"]
    num_covers = data.get("num_covers", data["num_guests"] * 2)
    seats_available = data.get("seats_available", 120)
    operating_hours = data.get("operating_hours", 12)
    tables_available = data.get("tables_available", 30)
    tables_served = data.get("tables_served", 45)
    wait_staff = data.get("wait_staff", 15)
    guest_nights = data.get("guest_nights", data["total_nights"])
    breakfast_covers = data.get("breakfast_covers", data["num_guests"] * 0.85)
    
    kpis = {
        "Total F&B Dept Profit (%)": (fandb_profit / total_fandb_revenue) * 100 if total_fandb_revenue > 0 else 0,
        "Gross Food Margin (%)": ((food_revenue - food_cogs) / food_revenue) * 100 if food_revenue > 0 else 0,
        "Gross Beverage Margin (%)": ((beverage_revenue - beverage_cogs) / beverage_revenue) * 100 if beverage_revenue > 0 else 0,
        "Average Spend per Cover (€)": total_fandb_revenue / num_covers if num_covers > 0 else 0,
        "F&B Revenue POR (€)": total_fandb_revenue / occupied_rooms if occupied_rooms > 0 else 0,
        "F&B Revenue PAR (€)": total_fandb_revenue / available_rooms if available_rooms > 0 else 0,
        "Revenue per available seat per hour (€)": total_fandb_revenue / (seats_available * operating_hours) if seats_available > 0 and operating_hours > 0 else 0,
        "Table Turn Rate": tables_served / tables_available if tables_available > 0 else 0,
        "Average Table Occupancy (%)": (tables_served / (tables_available * 2)) * 100 if tables_available > 0 else 0,
        "F&B Revenue per wait staff (€)": total_fandb_revenue / wait_staff if wait_staff > 0 else 0,
        "Breakfast sit down rate (%)": (breakfast_covers / guest_nights) * 100 if guest_nights > 0 else 0,
        "Food Cost of Sales (%)": (food_cogs / food_revenue) * 100 if food_revenue > 0 else 0,
        "Beverage Cost of Sales (%)": (beverage_cogs / beverage_revenue) * 100 if beverage_revenue > 0 else 0,
        "Total F&B Cost of Sales (%)": ((food_cogs + beverage_cogs) / total_fandb_revenue) * 100 if total_fandb_revenue > 0 else 0,
        "F&B Payroll Cost (%)": (data.get("fandb_payroll", total_fandb_revenue * 0.35) / total_fandb_revenue) * 100 if total_fandb_revenue > 0 else 0,
        "Other F&B Dept Cost (%)": ((total_fandb_costs - data.get("fandb_payroll", total_fandb_revenue * 0.35)) / total_fandb_revenue) * 100 if total_fandb_revenue > 0 else 0,
    }
    return kpis


def calculate_spa_kpis(data):
    """Calcule les KPIs du département Spa & Loisirs"""
    
    spa_revenue = data.get("spa_revenue", 25000)
    spa_costs = data.get("spa_costs", 15000)
    spa_profit = spa_revenue - spa_costs
    
    treatment_hours_sold = data.get("treatment_hours_sold", 320)
    treatment_hours_available = data.get("treatment_hours_available", 500)
    total_treatments_sold = data.get("total_treatments_sold", 180)
    treatment_revenue = data.get("treatment_revenue", spa_revenue * 0.70)
    
    spa_customers = data.get("spa_customers", 450)
    occupied_rooms = data["occupied_rooms"]
    total_guests = data["num_guests"]
    spa_guests = data.get("spa_guests", 380)
    retail_guests = data.get("retail_guests", 120)
    
    leisure_revenue = data.get("leisure_revenue", 15000)
    num_members = data.get("num_members", 200)
    class_revenue = data.get("class_revenue", 5000)
    num_classes = data.get("num_classes", 50)
    leisure_area_sqm = data.get("leisure_area_sqm", 300)
    
    cost_of_sales = data.get("spa_cogs", spa_revenue * 0.15)
    therapist_hours_performed = data.get("therapist_hours_performed", 280)
    therapist_hours_available = data.get("therapist_hours_available", 400)
    
    kpis = {
        "Treatment Room Utilisation (TRU) (%)": (treatment_hours_sold / treatment_hours_available) * 100 if treatment_hours_available > 0 else 0,
        "Average Treatment Rate (ATR) (€)": treatment_revenue / total_treatments_sold if total_treatments_sold > 0 else 0,
        "Revenue Per Available Treatment Room (€)": spa_revenue / treatment_hours_available if treatment_hours_available > 0 else 0,
        "Average Spend per Spa Customer (€)": spa_revenue / spa_customers if spa_customers > 0 else 0,
        "Total Spa/Leisure Dept Profit (%)": (spa_profit / spa_revenue) * 100 if spa_revenue > 0 else 0,
        "Spa Revenue POR (€)": spa_revenue / occupied_rooms if occupied_rooms > 0 else 0,
        "Guest Capture Rate (%)": (spa_guests / total_guests) * 100 if total_guests > 0 else 0,
        "Retail Capture Rate (%)": (retail_guests / spa_guests) * 100 if spa_guests > 0 else 0,
        "Revenue per Member (€)": leisure_revenue / num_members if num_members > 0 else 0,
        "Revenue per square metre (€)": leisure_revenue / leisure_area_sqm if leisure_area_sqm > 0 else 0,
        "Average revenue per class (€)": class_revenue / num_classes if num_classes > 0 else 0,
        "Cost of Sales (%)": (cost_of_sales / spa_revenue) * 100 if spa_revenue > 0 else 0,
        "Spa and Leisure Payroll Cost (%)": (data.get("spa_payroll", spa_revenue * 0.40) / spa_revenue) * 100 if spa_revenue > 0 else 0,
        "Other Spa/Leisure Dept Cost (%)": ((spa_costs - data.get("spa_payroll", spa_revenue * 0.40) - cost_of_sales) / spa_revenue) * 100 if spa_revenue > 0 else 0,
        "Total Spa/Leisure Dept Cost (%)": (spa_costs / spa_revenue) * 100 if spa_revenue > 0 else 0,
        "Therapist Utilisation (%)": (therapist_hours_performed / therapist_hours_available) * 100 if therapist_hours_available > 0 else 0,
    }
    return kpis


def calculate_profit_sensitivity(guests, avg_spending, var_material, var_wages, admin_exp, general_exp, change_percent=0.10):
    """Calcule le multiplicateur de profit selon la methode de l'auteur"""
    
    sales = guests * avg_spending
    var_costs = guests * (var_material + var_wages)
    fixed_costs = admin_exp + general_exp
    net_income = sales - var_costs - fixed_costs
    
    results = {}
    
    # 1. Variation du nombre de guests
    guests_new = guests * (1 + change_percent)
    sales_new = guests_new * avg_spending
    var_costs_new = guests_new * (var_material + var_wages)
    net_income_new = sales_new - var_costs_new - fixed_costs
    change_ratio = (net_income_new - net_income) / net_income if net_income != 0 else 0
    profit_multiplier = change_ratio / change_percent if change_percent != 0 else 0
    results["Nombre de clients"] = {
        "new_value": guests_new,
        "net_income": net_income_new,
        "change_ratio": change_ratio,
        "multiplier": profit_multiplier
    }
    
    # 2. Variation du pouvoir de depense moyen
    spending_new = avg_spending * (1 + change_percent)
    sales_new = guests * spending_new
    net_income_new = sales_new - var_costs - fixed_costs
    change_ratio = (net_income_new - net_income) / net_income if net_income != 0 else 0
    profit_multiplier = change_ratio / change_percent if change_percent != 0 else 0
    results["Pouvoir de depense/client"] = {
        "new_value": spending_new,
        "net_income": net_income_new,
        "change_ratio": change_ratio,
        "multiplier": profit_multiplier
    }
    
    # 3. Variation du cout des materiaux
    material_new = var_material * (1 + change_percent)
    var_costs_new = guests * (material_new + var_wages)
    net_income_new = sales - var_costs_new - fixed_costs
    change_ratio = (net_income_new - net_income) / net_income if net_income != 0 else 0
    profit_multiplier = change_ratio / change_percent if change_percent != 0 else 0
    results["Cout des materiaux"] = {
        "new_value": material_new,
        "net_income": net_income_new,
        "change_ratio": change_ratio,
        "multiplier": profit_multiplier
    }
    
    # 4. Variation des salaires variables
    wages_new = var_wages * (1 + change_percent)
    var_costs_new = guests * (var_material + wages_new)
    net_income_new = sales - var_costs_new - fixed_costs
    change_ratio = (net_income_new - net_income) / net_income if net_income != 0 else 0
    profit_multiplier = change_ratio / change_percent if change_percent != 0 else 0
    results["Salaires variables"] = {
        "new_value": wages_new,
        "net_income": net_income_new,
        "change_ratio": change_ratio,
        "multiplier": profit_multiplier
    }
    
    # 5. Variation des frais administratifs
    admin_new = admin_exp * (1 + change_percent)
    fixed_costs_new = admin_new + general_exp
    net_income_new = sales - var_costs - fixed_costs_new
    change_ratio = (net_income_new - net_income) / net_income if net_income != 0 else 0
    profit_multiplier = change_ratio / change_percent if change_percent != 0 else 0
    results["Frais administratifs"] = {
        "new_value": admin_new,
        "net_income": net_income_new,
        "change_ratio": change_ratio,
        "multiplier": profit_multiplier
    }
    
    # 6. Variation des frais generaux
    general_new = general_exp * (1 + change_percent)
    fixed_costs_new = admin_exp + general_new
    net_income_new = sales - var_costs - fixed_costs_new
    change_ratio = (net_income_new - net_income) / net_income if net_income != 0 else 0
    profit_multiplier = change_ratio / change_percent if change_percent != 0 else 0
    results["Frais generaux"] = {
        "new_value": general_new,
        "net_income": net_income_new,
        "change_ratio": change_ratio,
        "multiplier": profit_multiplier
    }
    
    return results, net_income


# ============================================================================
# DONNEES PAR DEFAUT
# ============================================================================

default_data = {
    "total_revenue": 144000,
    "accommodation_revenue": 88762.5,
    "food_revenue": 39839.25,
    "beverage_revenue": 15935.7,
    "other_revenue": 15396.3,
    "spa_revenue": 25000,
    "leisure_revenue": 15000,
    "accommodation_costs": 15396.3,
    "food_costs": 15396.3,
    "beverage_costs": 3983.9,
    "other_costs": 15396.3,
    "spa_costs": 15000,
    "spa_cogs": 3750,
    "spa_payroll": 10000,
    "admin_costs": 34500,
    "sales_promotion_costs": 2000,
    "total_payroll": 25000,
    "fandb_payroll": 13943,
    "rooms_payroll": 13314,
    "depreciation": 5000,
    "commissions": 8876.25,
    "available_rooms": 600,
    "occupied_rooms": 322,
    "num_guests": 1200,
    "total_nights": 3600,
    "num_meals": 2500,
    "num_covers": 2400,
    "guest_nights": 3600,
    "breakfast_covers": 1020,
    "seats_available": 120,
    "operating_hours": 12,
    "tables_available": 30,
    "tables_served": 45,
    "wait_staff": 15,
    "treatment_hours_sold": 320,
    "treatment_hours_available": 500,
    "total_treatments_sold": 180,
    "treatment_revenue": 17500,
    "spa_customers": 450,
    "spa_guests": 380,
    "retail_guests": 120,
    "therapist_hours_performed": 280,
    "therapist_hours_available": 400,
    "leisure_revenue": 15000,
    "num_members": 200,
    "class_revenue": 5000,
    "num_classes": 50,
    "leisure_area_sqm": 300,
    "guests": 1200,
    "avg_spending": 120,
    "var_material": 25,
    "var_wages": 15,
    "admin_exp": 34500,
    "general_exp": 25000,
    "food_cogs": 11951.78,
    "beverage_cogs": 3983.93,
    "energy_costs": 3000,
    "maintenance_costs": 2500,
}

st.sidebar.header("📝 Parametres de l'hotel")
use_defaults = st.sidebar.checkbox("Utiliser les donnees par defaut (Hotel Al Zaitonia)", value=True)

if use_defaults:
    data = default_data.copy()
else:
    data = default_data.copy()


# ============================================================================
# SECTION 1: VUE D'ENSEMBLE
# ============================================================================

if section == "1. Vue d_ensemble - KPIs Globaux":
    st.header("🏆 Vue d'ensemble - KPIs Globaux")
    st.markdown("""
    **Indicateurs Clés de Performance (KPIs) selon Fáilte Ireland**
    
    Cette section presente les principaux KPIs pour evaluer la performance globale de l'hotel.
    """)
    
    kpis = calculate_hotel_kpis(data)
    
    st.subheader("💰 KPIs de Revenus")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Occupancy", f"{kpis['Occupancy (%)']:.1f}%")
        st.caption("Taux d'occupation")
    with col2:
        st.metric("ADR", f"{kpis['ADR (€)']:.2f} €")
        st.caption("Prix moyen par chambre")
    with col3:
        st.metric("RevPAR", f"{kpis['RevPAR (€)']:.2f} €")
        st.caption("Revenu par chambre disponible")
    with col4:
        st.metric("TRevPAR", f"{kpis['TRevPAR (€)']:.2f} €")
        st.caption("Revenu total par chambre dispo")
    with col5:
        st.metric("TRevPOR", f"{kpis['TRevPOR (€)']:.2f} €")
        st.caption("Revenu total par chambre occupee")
    
    st.subheader("📈 KPIs de Profitabilite")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Department Profit", f"{kpis['Total Department Profit (%)']:.1f}%", 
                  delta=f"{kpis['Total Department Profit (€)']:,.0f} €")
    with col2:
        st.metric("Gross Operating Profit", f"{kpis['Gross Operating Profit (%)']:.1f}%",
                  delta=f"{kpis['Gross Operating Profit (€)']:,.0f} €")
    with col3:
        st.metric("EBITDA", f"{kpis['EBITDA (%)']:.1f}%", delta=None)
    
    st.subheader("📉 KPIs de Couts")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Department Cost", f"{kpis['Total Department Cost (%)']:.1f}%", delta=None)
    with col2:
        st.metric("Total Payroll Cost", f"{kpis['Total Payroll Cost (%)']:.1f}%", delta=None)
    with col3:
        st.metric("Undistributed Cost", f"{kpis['Undistributed Cost (%)']:.1f}%", delta=None)
    
    # Graphique de synthese
    st.subheader("📊 Dashboard visuel des KPIs")
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Structure des revenus", "Taux d'occupation vs ADR vs RevPAR",
                        "Repartition des couts", "Profitabilite par departement")
    )
    
    revenue_composition = {
        "Hebergement": data["accommodation_revenue"],
        "Restauration": data["food_revenue"],
        "Spa & Loisirs": data.get("spa_revenue", 0) + data.get("leisure_revenue", 0),
        "Autres": data["other_revenue"]
    }
    fig.add_trace(
        go.Pie(labels=list(revenue_composition.keys()), values=list(revenue_composition.values()), 
               name="Revenus", hole=0.3),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(x=["ADR", "Occupancy", "RevPAR"], 
               y=[kpis['ADR (€)'], kpis['Occupancy (%)'], kpis['RevPAR (€)']],
               marker_color=["#2E86AB", "#A23B72", "#F18F01"]),
        row=1, col=2
    )
    
    cost_composition = {
        "Couts directs hebergement": data["accommodation_costs"],
        "Couts directs restauration": data["food_costs"],
        "Frais administratifs": data["admin_costs"],
        "Autres couts": data["other_costs"]
    }
    fig.add_trace(
        go.Bar(x=list(cost_composition.keys()), y=list(cost_composition.values()), name="Couts"),
        row=2, col=1
    )
    
    dept_profits = {
        "Hebergement": data["accommodation_revenue"] - data["accommodation_costs"],
        "Restauration": data["food_revenue"] - data["food_costs"],
        "Spa & Loisirs": data.get("spa_revenue", 0) + data.get("leisure_revenue", 0) - data.get("spa_costs", 0),
        "Autres": data["other_revenue"] - data["other_costs"]
    }
    fig.add_trace(
        go.Bar(x=list(dept_profits.keys()), y=list(dept_profits.values()), 
               name="Profit", marker_color="green"),
        row=2, col=2
    )
    
    fig.update_layout(height=700, showlegend=False, title_text="Tableau de bord des KPIs")
    fig.update_xaxes(tickangle=45)
    st.plotly_chart(fig, use_container_width=True)
    
    # Benchmarking
    st.subheader("📊 Benchmarking - Comparaison avec les standards")
    
    benchmarks = {
        "Indicateur": ["Occupancy", "ADR", "RevPAR", "GOP %", "Payroll %"],
        "Hotel": [f"{kpis['Occupancy (%)']:.1f}%", f"{kpis['ADR (€)']:.0f}€", 
                  f"{kpis['RevPAR (€)']:.0f}€", f"{kpis['Gross Operating Profit (%)']:.1f}%",
                  f"{kpis['Total Payroll Cost (%)']:.1f}%"],
        "Standard secteur": ["65-75%", "120-150€", "80-110€", "30-40%", "25-35%"],
        "Performance": ["🟡 A ameliorer" if kpis['Occupancy (%)'] < 65 else "🟢 Bonne",
                        "🟢 Bonne" if 120 <= kpis['ADR (€)'] <= 150 else "🟡 A ameliorer",
                        "🟡 A ameliorer" if kpis['RevPAR (€)'] < 80 else "🟢 Bonne",
                        "🟡 A ameliorer" if kpis['Gross Operating Profit (%)'] < 30 else "🟢 Bonne",
                        "🟢 Bonne" if 25 <= kpis['Total Payroll Cost (%)'] <= 35 else "🔴 Alerte"]
    }
    benchmark_df = pd.DataFrame(benchmarks)
    st.dataframe(benchmark_df, use_container_width=True, hide_index=True)


# ============================================================================
# SECTION 2: ANALYSE DE SENSIBILITE
# ============================================================================

elif section == "2. Analyse de Sensibilite du Profit":
    st.header("📈 Analyse de Sensibilite du Profit")
    st.markdown("""
    **Methodologie selon Jawabreh et al. (2017)**
    
    L'analyse de sensibilite mesure l'impact de la variation de chaque facteur controlant sur le benefice net.
    Le **multiplicateur de profit** est calcule comme suit:
    
