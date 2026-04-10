# hotel_kpi_dashboard.py
# Application d'analyse financière hôtelière - Interface universelle
# Exécution: streamlit run hotel_kpi_dashboard.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="Dashboard KPIs Hôteliers",
    page_icon="🏨",
    layout="wide"
)

# Initialisation des données en session
if "hotel_data" not in st.session_state:
    st.session_state.hotel_data = {
        "hotel_name": "Mon Hôtel",
        "period": "2024",
        # Données globales
        "total_revenue": 100000,
        "total_available_rooms": 1000,
        "total_occupied_rooms": 650,
        "total_guests": 1200,
        "total_nights": 2800,
        # Hébergement
        "rooms_revenue": 65000,
        "rooms_cost": 19500,
        "rooms_payroll": 9750,
        "commissions": 6500,
        # Restauration
        "food_revenue": 25000,
        "beverage_revenue": 10000,
        "food_cost": 7500,
        "beverage_cost": 2500,
        "food_payroll": 8750,
        "num_covers": 2000,
        "num_breakfast_covers": 1100,
        "seats_available": 120,
        "operating_hours": 12,
        "tables_available": 30,
        "tables_served": 45,
        "wait_staff": 10,
        # Spa
        "spa_revenue": 15000,
        "spa_cost": 6000,
        "spa_payroll": 4500,
        "spa_cogs": 2250,
        "treatment_hours_sold": 300,
        "treatment_hours_available": 500,
        "total_treatments": 180,
        "treatment_revenue": 12000,
        "spa_customers": 400,
        "spa_visitors": 350,
        "retail_customers": 100,
        "therapist_hours_performed": 270,
        "therapist_hours_available": 400,
        # Centre de loisirs
        "leisure_revenue": 5000,
        "leisure_cost": 2000,
        "num_members": 150,
        "class_revenue": 2000,
        "num_classes": 40,
        "leisure_area_sqm": 250,
        # Autres coûts
        "admin_costs": 8000,
        "marketing_costs": 3000,
        "energy_costs": 4000,
        "maintenance_costs": 2500,
        "depreciation": 5000,
        # Analyse de sensibilité
        "num_guests_input": 1200,
        "avg_spending_input": 120,
        "var_material_input": 25,
        "var_wages_input": 15,
        "fixed_admin_input": 34500,
        "fixed_general_input": 25000,
    }

# Sidebar - Navigation
st.sidebar.header("🏨 Configuration")
hotel_name = st.sidebar.text_input("Nom de l'hôtel", value=st.session_state.hotel_data["hotel_name"])
period = st.sidebar.text_input("Période", value=st.session_state.hotel_data["period"])
st.session_state.hotel_data["hotel_name"] = hotel_name
st.session_state.hotel_data["period"] = period

st.sidebar.markdown("---")
st.sidebar.header("📊 Navigation")
section = st.sidebar.selectbox(
    "Choisissez une section",
    [
        "🏆 Tableau de bord général",
        "📈 Analyse de sensibilité",
        "🛏️ Département Hébergement",
        "🍽️ Département Restauration",
        "💆 Département Spa & Loisirs",
        "💰 Analyse des dépenses clients",
        "📉 Analyse des coûts",
        "📑 Rapport complet"
    ]
)

# Bouton pour réinitialiser avec des données exemple
if st.sidebar.button("🔄 Charger des données exemple"):
    st.session_state.hotel_data = {
        "hotel_name": "Hôtel Exemple",
        "period": "2024",
        "total_revenue": 100000,
        "total_available_rooms": 1000,
        "total_occupied_rooms": 650,
        "total_guests": 1200,
        "total_nights": 2800,
        "rooms_revenue": 65000,
        "rooms_cost": 19500,
        "rooms_payroll": 9750,
        "commissions": 6500,
        "food_revenue": 25000,
        "beverage_revenue": 10000,
        "food_cost": 7500,
        "beverage_cost": 2500,
        "food_payroll": 8750,
        "num_covers": 2000,
        "num_breakfast_covers": 1100,
        "seats_available": 120,
        "operating_hours": 12,
        "tables_available": 30,
        "tables_served": 45,
        "wait_staff": 10,
        "spa_revenue": 15000,
        "spa_cost": 6000,
        "spa_payroll": 4500,
        "spa_cogs": 2250,
        "treatment_hours_sold": 300,
        "treatment_hours_available": 500,
        "total_treatments": 180,
        "treatment_revenue": 12000,
        "spa_customers": 400,
        "spa_visitors": 350,
        "retail_customers": 100,
        "therapist_hours_performed": 270,
        "therapist_hours_available": 400,
        "leisure_revenue": 5000,
        "leisure_cost": 2000,
        "num_members": 150,
        "class_revenue": 2000,
        "num_classes": 40,
        "leisure_area_sqm": 250,
        "admin_costs": 8000,
        "marketing_costs": 3000,
        "energy_costs": 4000,
        "maintenance_costs": 2500,
        "depreciation": 5000,
        "num_guests_input": 1200,
        "avg_spending_input": 120,
        "var_material_input": 25,
        "var_wages_input": 15,
        "fixed_admin_input": 34500,
        "fixed_general_input": 25000,
    }
    st.sidebar.success("Données exemple chargées!")
    st.rerun()


# ============================================================================
# FONCTIONS DE CALCUL
# ============================================================================

def calculate_overall_kpis(data):
    """Calcule les KPIs généraux de l'hôtel"""
    total_revenue = data["total_revenue"]
    rooms_revenue = data["rooms_revenue"]
    available_rooms = data["total_available_rooms"]
    occupied_rooms = data["total_occupied_rooms"]
    
    # Coûts totaux par département
    total_rooms_cost = data["rooms_cost"]
    total_fb_cost = data["food_cost"] + data["beverage_cost"] + data["food_payroll"]
    total_spa_cost = data["spa_cost"]
    total_dept_cost = total_rooms_cost + total_fb_cost + total_spa_cost + data["leisure_cost"]
    
    # Profits
    total_dept_profit = total_revenue - total_dept_cost
    gross_operating_profit = total_dept_profit - data["admin_costs"] - data["marketing_costs"] - data["energy_costs"] - data["maintenance_costs"]
    ebitda = gross_operating_profit + data["depreciation"]
    
    return {
        "Occupancy (%)": (occupied_rooms / available_rooms) * 100 if available_rooms > 0 else 0,
        "ADR (€)": rooms_revenue / occupied_rooms if occupied_rooms > 0 else 0,
        "RevPAR (€)": rooms_revenue / available_rooms if available_rooms > 0 else 0,
        "TRevPAR (€)": total_revenue / available_rooms if available_rooms > 0 else 0,
        "TRevPOR (€)": total_revenue / occupied_rooms if occupied_rooms > 0 else 0,
        "Total Dept Profit (%)": (total_dept_profit / total_revenue) * 100 if total_revenue > 0 else 0,
        "Gross Operating Profit (%)": (gross_operating_profit / total_revenue) * 100 if total_revenue > 0 else 0,
        "EBITDA (%)": (ebitda / total_revenue) * 100 if total_revenue > 0 else 0,
        "Total Dept Cost (%)": (total_dept_cost / total_revenue) * 100 if total_revenue > 0 else 0,
        "Payroll Cost (%)": ((data["rooms_payroll"] + data["food_payroll"] + data["spa_payroll"]) / total_revenue) * 100 if total_revenue > 0 else 0,
        "Admin Cost (%)": (data["admin_costs"] / total_revenue) * 100 if total_revenue > 0 else 0,
        "Marketing Cost (%)": (data["marketing_costs"] / total_revenue) * 100 if total_revenue > 0 else 0,
        "Energy Cost (%)": (data["energy_costs"] / total_revenue) * 100 if total_revenue > 0 else 0,
        "Maintenance Cost (%)": (data["maintenance_costs"] / total_revenue) * 100 if total_revenue > 0 else 0,
    }


def calculate_rooms_kpis(data):
    """Calcule les KPIs du département Hébergement"""
    rooms_revenue = data["rooms_revenue"]
    rooms_cost = data["rooms_cost"]
    rooms_profit = rooms_revenue - rooms_cost
    available_rooms = data["total_available_rooms"]
    occupied_rooms = data["total_occupied_rooms"]
    
    return {
        "Occupancy (%)": (occupied_rooms / available_rooms) * 100 if available_rooms > 0 else 0,
        "ADR (€)": rooms_revenue / occupied_rooms if occupied_rooms > 0 else 0,
        "RevPAR (€)": rooms_revenue / available_rooms if available_rooms > 0 else 0,
        "RevPAR vérification (Occ x ADR)": ((occupied_rooms / available_rooms) * (rooms_revenue / occupied_rooms)) if occupied_rooms > 0 and available_rooms > 0 else 0,
        "Rooms Dept Profit (€)": rooms_profit,
        "Rooms Dept Profit (%)": (rooms_profit / rooms_revenue) * 100 if rooms_revenue > 0 else 0,
        "Rooms Dept Cost (%)": (rooms_cost / rooms_revenue) * 100 if rooms_revenue > 0 else 0,
        "Commissions (%)": (data["commissions"] / rooms_revenue) * 100 if rooms_revenue > 0 else 0,
        "Rooms Payroll (%)": (data["rooms_payroll"] / rooms_revenue) * 100 if rooms_revenue > 0 else 0,
        "Other Rooms Cost (%)": ((rooms_cost - data["commissions"] - data["rooms_payroll"]) / rooms_revenue) * 100 if rooms_revenue > 0 else 0,
        "Cost per occupied Room (€)": rooms_cost / occupied_rooms if occupied_rooms > 0 else 0,
    }


def calculate_fandb_kpis(data):
    """Calcule les KPIs du département Restauration"""
    food_revenue = data["food_revenue"]
    beverage_revenue = data["beverage_revenue"]
    total_revenue = food_revenue + beverage_revenue
    total_cost = data["food_cost"] + data["beverage_cost"] + data["food_payroll"]
    total_profit = total_revenue - total_cost
    
    food_gross_margin = ((food_revenue - data["food_cost"]) / food_revenue) * 100 if food_revenue > 0 else 0
    beverage_gross_margin = ((beverage_revenue - data["beverage_cost"]) / beverage_revenue) * 100 if beverage_revenue > 0 else 0
    
    occupied_rooms = data["total_occupied_rooms"]
    available_rooms = data["total_available_rooms"]
    
    return {
        "Total F&B Revenue (€)": total_revenue,
        "Total F&B Profit (€)": total_profit,
        "Total F&B Profit (%)": (total_profit / total_revenue) * 100 if total_revenue > 0 else 0,
        "Gross Food Margin (%)": food_gross_margin,
        "Gross Beverage Margin (%)": beverage_gross_margin,
        "Average Spend per Cover (€)": total_revenue / data["num_covers"] if data["num_covers"] > 0 else 0,
        "F&B Revenue POR (€)": total_revenue / occupied_rooms if occupied_rooms > 0 else 0,
        "F&B Revenue PAR (€)": total_revenue / available_rooms if available_rooms > 0 else 0,
        "Revenue per available seat/hour (€)": total_revenue / (data["seats_available"] * data["operating_hours"]) if data["seats_available"] > 0 and data["operating_hours"] > 0 else 0,
        "Table Turn Rate": data["tables_served"] / data["tables_available"] if data["tables_available"] > 0 else 0,
        "Average Table Occupancy (%)": (data["tables_served"] / (data["tables_available"] * 2)) * 100 if data["tables_available"] > 0 else 0,
        "F&B Revenue per wait staff (€)": total_revenue / data["wait_staff"] if data["wait_staff"] > 0 else 0,
        "Breakfast sit down rate (%)": (data["num_breakfast_covers"] / data["total_nights"]) * 100 if data["total_nights"] > 0 else 0,
        "Food Cost of Sales (%)": (data["food_cost"] / food_revenue) * 100 if food_revenue > 0 else 0,
        "Beverage Cost of Sales (%)": (data["beverage_cost"] / beverage_revenue) * 100 if beverage_revenue > 0 else 0,
        "Total F&B Cost of Sales (%)": ((data["food_cost"] + data["beverage_cost"]) / total_revenue) * 100 if total_revenue > 0 else 0,
        "F&B Payroll (%)": (data["food_payroll"] / total_revenue) * 100 if total_revenue > 0 else 0,
    }


def calculate_spa_kpis(data):
    """Calcule les KPIs du département Spa & Loisirs"""
    spa_revenue = data["spa_revenue"]
    spa_cost = data["spa_cost"]
    spa_profit = spa_revenue - spa_cost
    
    leisure_revenue = data["leisure_revenue"]
    leisure_cost = data["leisure_cost"]
    leisure_profit = leisure_revenue - leisure_cost
    
    total_revenue = spa_revenue + leisure_revenue
    total_cost = spa_cost + leisure_cost
    total_profit = total_revenue - total_cost
    
    occupied_rooms = data["total_occupied_rooms"]
    total_guests = data["total_guests"]
    
    # Spa KPIs
    tru = (data["treatment_hours_sold"] / data["treatment_hours_available"]) * 100 if data["treatment_hours_available"] > 0 else 0
    atr = data["treatment_revenue"] / data["total_treatments"] if data["total_treatments"] > 0 else 0
    revpatr = spa_revenue / data["treatment_hours_available"] if data["treatment_hours_available"] > 0 else 0
    
    return {
        "Total Spa Revenue (€)": spa_revenue,
        "Total Leisure Revenue (€)": leisure_revenue,
        "Total Spa/Leisure Profit (%)": (total_profit / total_revenue) * 100 if total_revenue > 0 else 0,
        "Treatment Room Utilisation - TRU (%)": tru,
        "Average Treatment Rate - ATR (€)": atr,
        "Revenue Per Available Treatment Room (€)": revpatr,
        "Revenue Per Available Treatment Room (ATR x TRU)": (atr * tru / 100) if atr > 0 else 0,
        "Average Spend per Spa Customer (€)": spa_revenue / data["spa_customers"] if data["spa_customers"] > 0 else 0,
        "Spa Revenue POR (€)": spa_revenue / occupied_rooms if occupied_rooms > 0 else 0,
        "Guest Capture Rate (%)": (data["spa_visitors"] / total_guests) * 100 if total_guests > 0 else 0,
        "Retail Capture Rate (%)": (data["retail_customers"] / data["spa_visitors"]) * 100 if data["spa_visitors"] > 0 else 0,
        "Revenue per Member (€)": leisure_revenue / data["num_members"] if data["num_members"] > 0 else 0,
        "Revenue per square metre (€)": leisure_revenue / data["leisure_area_sqm"] if data["leisure_area_sqm"] > 0 else 0,
        "Average revenue per class (€)": data["class_revenue"] / data["num_classes"] if data["num_classes"] > 0 else 0,
        "Cost of Sales (%)": (data["spa_cogs"] / spa_revenue) * 100 if spa_revenue > 0 else 0,
        "Spa Payroll (%)": (data["spa_payroll"] / spa_revenue) * 100 if spa_revenue > 0 else 0,
        "Other Spa Costs (%)": ((spa_cost - data["spa_cogs"] - data["spa_payroll"]) / spa_revenue) * 100 if spa_revenue > 0 else 0,
        "Total Spa Cost (%)": (spa_cost / spa_revenue) * 100 if spa_revenue > 0 else 0,
        "Therapist Utilisation (%)": (data["therapist_hours_performed"] / data["therapist_hours_available"]) * 100 if data["therapist_hours_available"] > 0 else 0,
    }


def calculate_guest_spending(data):
    """Calcule les dépenses moyennes par client"""
    total_revenue = data["total_revenue"]
    num_guests = data["total_guests"]
    rooms_revenue = data["rooms_revenue"]
    food_revenue = data["food_revenue"]
    beverage_revenue = data["beverage_revenue"]
    spa_revenue = data["spa_revenue"]
    total_nights = data["total_nights"]
    num_meals = data["num_covers"]
    
    return {
        "Dépense moyenne générale (€)": total_revenue / num_guests if num_guests > 0 else 0,
        "Dépense moyenne hébergement (€)": rooms_revenue / num_guests if num_guests > 0 else 0,
        "Dépense moyenne restauration (€)": (food_revenue + beverage_revenue) / num_guests if num_guests > 0 else 0,
        "Dépense moyenne spa (€)": spa_revenue / num_guests if num_guests > 0 else 0,
        "Dépense moyenne par repas (€)": (food_revenue + beverage_revenue) / num_meals if num_meals > 0 else 0,
        "Durée moyenne du séjour (nuits)": total_nights / num_guests if num_guests > 0 else 0,
    }


def calculate_profit_sensitivity(data, change_percent=0.10):
    """Calcule les multiplicateurs de profit"""
    guests = data["num_guests_input"]
    avg_spending = data["avg_spending_input"]
    var_material = data["var_material_input"]
    var_wages = data["var_wages_input"]
    fixed_admin = data["fixed_admin_input"]
    fixed_general = data["fixed_general_input"]
    
    sales = guests * avg_spending
    var_costs = guests * (var_material + var_wages)
    fixed_costs = fixed_admin + fixed_general
    net_income = sales - var_costs - fixed_costs
    
    results = {}
    
    # Nombre de clients
    guests_new = guests * (1 + change_percent)
    sales_new = guests_new * avg_spending
    var_costs_new = guests_new * (var_material + var_wages)
    net_new = sales_new - var_costs_new - fixed_costs
    change_ratio = (net_new - net_income) / net_income if net_income != 0 else 0
    results["Nombre de clients"] = change_ratio / change_percent if change_percent != 0 else 0
    
    # Dépense moyenne
    spending_new = avg_spending * (1 + change_percent)
    sales_new = guests * spending_new
    net_new = sales_new - var_costs - fixed_costs
    change_ratio = (net_new - net_income) / net_income if net_income != 0 else 0
    results["Dépense moyenne/client"] = change_ratio / change_percent if change_percent != 0 else 0
    
    # Coûts matériaux
    material_new = var_material * (1 + change_percent)
    var_costs_new = guests * (material_new + var_wages)
    net_new = sales - var_costs_new - fixed_costs
    change_ratio = (net_new - net_income) / net_income if net_income != 0 else 0
    results["Coût des matériaux"] = change_ratio / change_percent if change_percent != 0 else 0
    
    # Salaires variables
    wages_new = var_wages * (1 + change_percent)
    var_costs_new = guests * (var_material + wages_new)
    net_new = sales - var_costs_new - fixed_costs
    change_ratio = (net_new - net_income) / net_income if net_income != 0 else 0
    results["Salaires variables"] = change_ratio / change_percent if change_percent != 0 else 0
    
    # Frais fixes
    admin_new = fixed_admin * (1 + change_percent)
    fixed_costs_new = admin_new + fixed_general
    net_new = sales - var_costs - fixed_costs_new
    change_ratio = (net_new - net_income) / net_income if net_income != 0 else 0
    results["Frais administratifs"] = change_ratio / change_percent if change_percent != 0 else 0
    
    general_new = fixed_general * (1 + change_percent)
    fixed_costs_new = fixed_admin + general_new
    net_new = sales - var_costs - fixed_costs_new
    change_ratio = (net_new - net_income) / net_income if net_income != 0 else 0
    results["Frais généraux"] = change_ratio / change_percent if change_percent != 0 else 0
    
    return results, net_income


def get_industry_benchmarks():
    """Retourne les benchmarks du secteur"""
    return {
        "Occupancy": {"min": 65, "max": 75, "unite": "%"},
        "ADR": {"min": 100, "max": 150, "unite": "€"},
        "RevPAR": {"min": 70, "max": 110, "unite": "€"},
        "GOP %": {"min": 30, "max": 40, "unite": "%"},
        "Payroll %": {"min": 25, "max": 35, "unite": "%"},
        "Food Cost %": {"min": 28, "max": 35, "unite": "%"},
        "Beverage Cost %": {"min": 20, "max": 30, "unite": "%"},
        "Spa TRU": {"min": 60, "max": 75, "unite": "%"},
    }


# ============================================================================
# INTERFACE DE SAISIE DES DONNÉES
# ============================================================================

def show_data_input():
    """Affiche le formulaire de saisie des données"""
    with st.expander("📝 Saisie des données de l'hôtel", expanded=False):
        st.markdown("### Données générales")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.session_state.hotel_data["total_revenue"] = st.number_input("Revenu total (€)", value=st.session_state.hotel_data["total_revenue"], min_value=0)
            st.session_state.hotel_data["total_available_rooms"] = st.number_input("Chambres disponibles (total période)", value=st.session_state.hotel_data["total_available_rooms"], min_value=1)
            st.session_state.hotel_data["total_occupied_rooms"] = st.number_input("Chambres occupées (total période)", value=st.session_state.hotel_data["total_occupied_rooms"], min_value=0)
        with col2:
            st.session_state.hotel_data["total_guests"] = st.number_input("Nombre total de clients", value=st.session_state.hotel_data["total_guests"], min_value=0)
            st.session_state.hotel_data["total_nights"] = st.number_input("Nombre total de nuits", value=st.session_state.hotel_data["total_nights"], min_value=0)
            st.session_state.hotel_data["admin_costs"] = st.number_input("Frais administratifs (€)", value=st.session_state.hotel_data["admin_costs"], min_value=0)
        with col3:
            st.session_state.hotel_data["marketing_costs"] = st.number_input("Frais marketing (€)", value=st.session_state.hotel_data["marketing_costs"], min_value=0)
            st.session_state.hotel_data["energy_costs"] = st.number_input("Frais énergie (€)", value=st.session_state.hotel_data["energy_costs"], min_value=0)
            st.session_state.hotel_data["maintenance_costs"] = st.number_input("Frais maintenance (€)", value=st.session_state.hotel_data["maintenance_costs"], min_value=0)
        
        st.markdown("### 🛏️ Département Hébergement")
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.hotel_data["rooms_revenue"] = st.number_input("Revenu hébergement (€)", value=st.session_state.hotel_data["rooms_revenue"], min_value=0)
            st.session_state.hotel_data["rooms_cost"] = st.number_input("Coûts hébergement (€)", value=st.session_state.hotel_data["rooms_cost"], min_value=0)
        with col2:
            st.session_state.hotel_data["rooms_payroll"] = st.number_input("Payroll hébergement (€)", value=st.session_state.hotel_data["rooms_payroll"], min_value=0)
            st.session_state.hotel_data["commissions"] = st.number_input("Commissions (€)", value=st.session_state.hotel_data["commissions"], min_value=0)
        
        st.markdown("### 🍽️ Département Restauration")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.session_state.hotel_data["food_revenue"] = st.number_input("Revenu food (€)", value=st.session_state.hotel_data["food_revenue"], min_value=0)
            st.session_state.hotel_data["beverage_revenue"] = st.number_input("Revenu beverage (€)", value=st.session_state.hotel_data["beverage_revenue"], min_value=0)
        with col2:
            st.session_state.hotel_data["food_cost"] = st.number_input("Coût food (€)", value=st.session_state.hotel_data["food_cost"], min_value=0)
            st.session_state.hotel_data["beverage_cost"] = st.number_input("Coût beverage (€)", value=st.session_state.hotel_data["beverage_cost"], min_value=0)
        with col3:
            st.session_state.hotel_data["food_payroll"] = st.number_input("Payroll F&B (€)", value=st.session_state.hotel_data["food_payroll"], min_value=0)
            st.session_state.hotel_data["num_covers"] = st.number_input("Nombre de couverts", value=st.session_state.hotel_data["num_covers"], min_value=0)
        
        st.markdown("### 💆 Département Spa & Loisirs")
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.hotel_data["spa_revenue"] = st.number_input("Revenu spa (€)", value=st.session_state.hotel_data["spa_revenue"], min_value=0)
            st.session_state.hotel_data["spa_cost"] = st.number_input("Coûts spa (€)", value=st.session_state.hotel_data["spa_cost"], min_value=0)
            st.session_state.hotel_data["treatment_hours_sold"] = st.number_input("Heures traitement vendues", value=st.session_state.hotel_data["treatment_hours_sold"], min_value=0)
            st.session_state.hotel_data["treatment_hours_available"] = st.number_input("Heures traitement disponibles", value=st.session_state.hotel_data["treatment_hours_available"], min_value=1)
        with col2:
            st.session_state.hotel_data["leisure_revenue"] = st.number_input("Revenu centre loisirs (€)", value=st.session_state.hotel_data["leisure_revenue"], min_value=0)
            st.session_state.hotel_data["num_members"] = st.number_input("Nombre de membres", value=st.session_state.hotel_data["num_members"], min_value=0)
            st.session_state.hotel_data["spa_customers"] = st.number_input("Nombre clients spa", value=st.session_state.hotel_data["spa_customers"], min_value=0)
        
        st.markdown("### 📊 Analyse de sensibilité")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.session_state.hotel_data["num_guests_input"] = st.number_input("Nombre de clients (base)", value=st.session_state.hotel_data["num_guests_input"], min_value=0)
            st.session_state.hotel_data["avg_spending_input"] = st.number_input("Dépense moyenne (€)", value=st.session_state.hotel_data["avg_spending_input"], min_value=0)
        with col2:
            st.session_state.hotel_data["var_material_input"] = st.number_input("Coût matériaux/client (€)", value=st.session_state.hotel_data["var_material_input"], min_value=0)
            st.session_state.hotel_data["var_wages_input"] = st.number_input("Salaires variables/client (€)", value=st.session_state.hotel_data["var_wages_input"], min_value=0)
        with col3:
            st.session_state.hotel_data["fixed_admin_input"] = st.number_input("Frais administratifs fixes (€)", value=st.session_state.hotel_data["fixed_admin_input"], min_value=0)
            st.session_state.hotel_data["fixed_general_input"] = st.number_input("Frais généraux fixes (€)", value=st.session_state.hotel_data["fixed_general_input"], min_value=0)


# ============================================================================
# SECTION 1: TABLEAU DE BORD GÉNÉRAL
# ============================================================================

if section == "🏆 Tableau de bord général":
    st.header(f"🏆 Tableau de bord - {st.session_state.hotel_data['hotel_name']}")
    st.caption(f"Période: {st.session_state.hotel_data['period']}")
    
    show_data_input()
    
    kpis = calculate_overall_kpis(st.session_state.hotel_data)
    benchmarks = get_industry_benchmarks()
    
    # KPIs principaux
    st.subheader("📊 Indicateurs clés de performance")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        delta_occ = kpis["Occupancy (%)"] - benchmarks["Occupancy"]["min"]
        st.metric("Taux d'occupation", f"{kpis['Occupancy (%)']:.1f}%", delta=f"{delta_occ:.1f}% vs benchmark")
    with col2:
        st.metric("ADR", f"{kpis['ADR (€)']:.2f} €")
    with col3:
        st.metric("RevPAR", f"{kpis['RevPAR (€)']:.2f} €")
    with col4:
        st.metric("TRevPAR", f"{kpis['TRevPAR (€)']:.2f} €")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Marge GOP", f"{kpis['Gross Operating Profit (%)']:.1f}%")
    with col2:
        st.metric("EBITDA %", f"{kpis['EBITDA (%)']:.1f}%")
    with col3:
        st.metric("Charge personnel", f"{kpis['Payroll Cost (%)']:.1f}%")
    with col4:
        st.metric("Coûts admin", f"{kpis['Admin Cost (%)']:.1f}%")
    
    # Graphique des revenus par département
    st.subheader("📈 Répartition des revenus")
    
    revenue_by_dept = {
        "Hébergement": st.session_state.hotel_data["rooms_revenue"],
        "Restauration": st.session_state.hotel_data["food_revenue"] + st.session_state.hotel_data["beverage_revenue"],
        "Spa": st.session_state.hotel_data["spa_revenue"],
        "Loisirs": st.session_state.hotel_data["leisure_revenue"],
    }
    
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Revenus par département", "Coûts par département"))
    
    fig.add_trace(go.Pie(labels=list(revenue_by_dept.keys()), values=list(revenue_by_dept.values()), hole=0.3), row=1, col=1)
    
    costs_by_dept = {
        "Hébergement": st.session_state.hotel_data["rooms_cost"],
        "Restauration": st.session_state.hotel_data["food_cost"] + st.session_state.hotel_data["beverage_cost"] + st.session_state.hotel_data["food_payroll"],
        "Spa": st.session_state.hotel_data["spa_cost"],
        "Loisirs": st.session_state.hotel_data["leisure_cost"],
    }
    fig.add_trace(go.Pie(labels=list(costs_by_dept.keys()), values=list(costs_by_dept.values()), hole=0.3), row=1, col=2)
    
    fig.update_layout(height=500, showlegend=True)
    st.plotly_chart(fig, use_container_width=True)
    
    # Évolution mensuelle simulée
    st.subheader("📅 Évolution mensuelle de l'occupation")
    months = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Aoû", "Sep", "Oct", "Nov", "Déc"]
    occupancy_trend = [55, 58, 62, 68, 72, 78, 82, 80, 75, 68, 60, 56]
    
    fig = px.line(x=months, y=occupancy_trend, markers=True, title="Taux d'occupation mensuel")
    fig.add_hline(y=kpis["Occupancy (%)"], line_dash="dash", annotation_text=f"Moyenne: {kpis['Occupancy (%)']:.1f}%")
    fig.update_layout(xaxis_title="Mois", yaxis_title="Taux d'occupation (%)")
    st.plotly_chart(fig, use_container_width=True)


# ============================================================================
# SECTION 2: ANALYSE DE SENSIBILITÉ
# ============================================================================

elif section == "📈 Analyse de sensibilité":
    st.header("📈 Analyse de sensibilité du profit")
    
    st.markdown("""
    **Principe**: L'analyse de sensibilité mesure comment une variation d'un facteur (ex: nombre de clients) impacte le profit.
    
    **Multiplicateur de profit** = Variation % du profit / Variation % du facteur
    - Multiplicateur > 1 : facteur très influent
    - Multiplicateur < 1 : facteur peu influent
    """)
    
    change_percent = st.slider("Variation des facteurs (%)", 1, 30, 10) / 100
    
    results, base_profit = calculate_profit_sensitivity(st.session_state.hotel_data, change_percent)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Profit de base", f"{base_profit:,.2f} €")
    with col2:
        st.metric("Variation appliquée", f"{change_percent*100:.0f}%")
    
    # Classement
    ranking = sorted(results.items(), key=lambda x: x[1], reverse=True)
    ranking_df = pd.DataFrame(ranking, columns=["Facteur", "Multiplicateur"])
    ranking_df["Impact"] = ranking_df["Multiplicateur"].apply(
        lambda x: "🔴 Très élevé" if x > 2 else "🟠 Élevé" if x > 1 else "🟢 Faible"
    )
    
    st.subheader("📊 Classement des facteurs par impact")
    st.dataframe(ranking_df, use_container_width=True, hide_index=True)
    
    fig = px.bar(ranking_df, x="Facteur", y="Multiplicateur", color="Multiplicateur",
                 title="Multiplicateurs de profit", color_continuous_scale="RdYlGn")
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("""
    **Interprétation**:
    - Les facteurs avec multiplicateur > 1 sont des leviers de profitabilité
    - Priorisez les actions sur les facteurs ayant les multiplicateurs les plus élevés
    - La dépense moyenne par client est généralement le levier le plus puissant
    """)


# ============================================================================
# SECTION 3: DÉPARTEMENT HÉBERGEMENT
# ============================================================================

elif section == "🛏️ Département Hébergement":
    st.header("🛏️ Département Hébergement - KPIs")
    
    kpis = calculate_rooms_kpis(st.session_state.hotel_data)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Taux d'occupation", f"{kpis['Occupancy (%)']:.1f}%")
    col2.metric("ADR (Prix moyen)", f"{kpis['ADR (€)']:.2f} €")
    col3.metric("RevPAR", f"{kpis['RevPAR (€)']:.2f} €")
    
    st.subheader("📊 Profitabilité et coûts")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Marge départementale", f"{kpis['Rooms Dept Profit (%)']:.1f}%")
    col2.metric("Taux de commission", f"{kpis['Commissions (%)']:.1f}%")
    col3.metric("Charge personnel", f"{kpis['Rooms Payroll (%)']:.1f}%")
    col4.metric("Coût par chambre occupée", f"{kpis['Cost per occupied Room (€)']:.2f} €")
    
    # Graphique
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Hébergement", x=["Revenue", "Coûts", "Profit"], 
                         y=[st.session_state.hotel_data["rooms_revenue"], 
                            st.session_state.hotel_data["rooms_cost"],
                            st.session_state.hotel_data["rooms_revenue"] - st.session_state.hotel_data["rooms_cost"]],
                         marker_color=["green", "red", "blue"]))
    fig.update_layout(title="Performance du département Hébergement", height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Recommandations
    st.subheader("💡 Recommandations")
    if kpis["Occupancy (%)"] < 65:
        st.warning("⚠️ Taux d'occupation faible - Envisagez des offres promotionnelles hors saison")
    if kpis["Commissions (%)"] > 15:
        st.warning("⚠️ Commissions élevées - Négociez avec les OTAs")
    if kpis["Rooms Payroll (%)"] > 20:
        st.warning("⚠️ Charge personnel élevée - Optimisez les effectifs")


# ============================================================================
# SECTION 4: DÉPARTEMENT RESTAURATION
# ============================================================================

elif section == "🍽️ Département Restauration":
    st.header("🍽️ Département Restauration - KPIs")
    
    kpis = calculate_fandb_kpis(st.session_state.hotel_data)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Marge F&B", f"{kpis['Total F&B Profit (%)']:.1f}%")
    col2.metric("Marge brute food", f"{kpis['Gross Food Margin (%)']:.1f}%")
    col3.metric("Marge brute beverage", f"{kpis['Gross Beverage Margin (%)']:.1f}%")
    
    st.subheader("📊 Indicateurs d'efficacité")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Dépense moyenne/couvert", f"{kpis['Average Spend per Cover (€)']:.2f} €")
    col2.metric("F&B Revenue POR", f"{kpis['F&B Revenue POR (€)']:.2f} €")
    col3.metric("Taux de rotation tables", f"{kpis['Table Turn Rate']:.1f}")
    col4.metric("Taux petit-déjeuner", f"{kpis['Breakfast sit down rate (%)']:.1f}%")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Food Cost %", f"{kpis['Food Cost of Sales (%)']:.1f}%")
    col2.metric("Beverage Cost %", f"{kpis['Beverage Cost of Sales (%)']:.1f}%")
    col3.metric("Payroll F&B %", f"{kpis['F&B Payroll (%)']:.1f}%")
    
    # Graphique des marges
    fig = go.Figure()
    fig.add_trace(go.Bar(x=["Food", "Beverage", "Total F&B"], 
                         y=[kpis['Gross Food Margin (%)'], kpis['Gross Beverage Margin (%)'], kpis['Total F&B Profit (%)']],
                         marker_color=["#FF6B6B", "#4ECDC4", "#45B7D1"]))
    fig.update_layout(title="Marges du département Restauration", yaxis_title="Taux (%)", height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Benchmarks
    st.subheader("📊 Comparaison benchmarks")
    benchmark_data = pd.DataFrame({
        "Indicateur": ["Food Cost %", "Beverage Cost %", "Marge F&B %"],
        "Valeur": [f"{kpis['Food Cost of Sales (%)']:.1f}%", f"{kpis['Beverage Cost of Sales (%)']:.1f}%", f"{kpis['Total F&B Profit (%)']:.1f}%"],
        "Benchmark": ["28-35%", "20-30%", "25-35%"],
        "Statut": ["✅" if 28 <= kpis['Food Cost of Sales (%)'] <= 35 else "⚠️",
                   "✅" if 20 <= kpis['Beverage Cost of Sales (%)'] <= 30 else "⚠️",
                   "✅" if 25 <= kpis['Total F&B Profit (%)'] <= 35 else "⚠️"]
    })
    st.dataframe(benchmark_data, use_container_width=True, hide_index=True)


# ============================================================================
# SECTION 5: DÉPARTEMENT SPA & LOISIRS
# ============================================================================

elif section == "💆 Département Spa & Loisirs":
    st.header("💆 Département Spa & Loisirs - KPIs")
    
    kpis = calculate_spa_kpis(st.session_state.hotel_data)
    
    st.subheader("🧖 KPIs du Spa")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("TRU (Taux utilisation)", f"{kpis['Treatment Room Utilisation - TRU (%)']:.1f}%")
    col2.metric("ATR (Prix moyen)", f"{kpis['Average Treatment Rate - ATR (€)']:.2f} €")
    col3.metric("RevPATR", f"{kpis['Revenue Per Available Treatment Room (€)']:.2f} €")
    col4.metric("Marge Spa", f"{kpis['Total Spa/Leisure Profit (%)']:.1f}%")
    
    st.subheader("📊 Indicateurs clients")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Guest Capture Rate", f"{kpis['Guest Capture Rate (%)']:.1f}%")
    col2.metric("Dépense moyenne client", f"{kpis['Average Spend per Spa Customer (€)']:.2f} €")
    col3.metric("Spa Revenue POR", f"{kpis['Spa Revenue POR (€)']:.2f} €")
    col4.metric("Therapist Utilisation", f"{kpis['Therapist Utilisation (%)']:.1f}%")
    
    st.subheader("🏋️ KPIs Centre de Loisirs")
    col1, col2, col3 = st.columns(3)
    col1.metric("Revenue par membre", f"{kpis['Revenue per Member (€)']:.2f} €")
    col2.metric("Revenue par m²", f"{kpis['Revenue per square metre (€)']:.2f} €")
    col3.metric("Revenue moyen par cours", f"{kpis['Average revenue per class (€)']:.2f} €")
    
    # Graphique
    fig = go.Figure()
    fig.add_trace(go.Indicator(mode="gauge+number", value=kpis['Treatment Room Utilisation - TRU (%)'] ,
                               title={'text': "TRU - Taux d'utilisation des salles"},
                               domain={'x': [0, 1], 'y': [0, 1]},
                               gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "darkblue"},
                                      'steps': [
                                          {'range': [0, 50], 'color': "red"},
                                          {'range': [50, 75], 'color': "orange"},
                                          {'range': [75, 100], 'color': "green"}]}))
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)


# ============================================================================
# SECTION 6: ANALYSE DES DÉPENSES CLIENTS
# ============================================================================

elif section == "💰 Analyse des dépenses clients":
    st.header("💰 Analyse des dépenses par client")
    
    spending = calculate_guest_spending(st.session_state.hotel_data)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Dépense moyenne générale", f"{spending['Dépense moyenne générale (€)']:.2f} €")
    col2.metric("Dépense moyenne hébergement", f"{spending['Dépense moyenne hébergement (€)']:.2f} €")
    col3.metric("Dépense moyenne restauration", f"{spending['Dépense moyenne restauration (€)']:.2f} €")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Dépense moyenne spa", f"{spending['Dépense moyenne spa (€)']:.2f} €")
    col2.metric("Dépense moyenne par repas", f"{spending['Dépense moyenne par repas (€)']:.2f} €")
    col3.metric("Durée moyenne séjour", f"{spending['Durée moyenne du séjour (nuits)']:.1f} nuits")
    
    # Graphique
    spending_by_category = {
        "Hébergement": spending['Dépense moyenne hébergement (€)'],
        "Restauration": spending['Dépense moyenne restauration (€)'],
        "Spa": spending['Dépense moyenne spa (€)'],
    }
    
    fig = px.pie(values=list(spending_by_category.values()), names=list(spending_by_category.keys()),
                 title="Répartition de la dépense moyenne par client", hole=0.3)
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("""
    **Analyse**:
    - Plus la durée de séjour est longue, plus le potentiel de revenus annexes est élevé
    - Comparez ces chiffres avec vos objectifs pour ajuster vos stratégies de vente additionnelle
    """)


# ============================================================================
# SECTION 7: ANALYSE DES COÛTS
# ============================================================================

elif section == "📉 Analyse des coûts":
    st.header("📉 Analyse des coûts d'exploitation")
    
    kpis = calculate_overall_kpis(st.session_state.hotel_data)
    
    st.subheader("📊 Structure des coûts")
    
    costs = {
        "Hébergement": st.session_state.hotel_data["rooms_cost"],
        "Restauration": st.session_state.hotel_data["food_cost"] + st.session_state.hotel_data["beverage_cost"],
        "Payroll F&B": st.session_state.hotel_data["food_payroll"],
        "Spa": st.session_state.hotel_data["spa_cost"],
        "Administratifs": st.session_state.hotel_data["admin_costs"],
        "Marketing": st.session_state.hotel_data["marketing_costs"],
        "Énergie": st.session_state.hotel_data["energy_costs"],
        "Maintenance": st.session_state.hotel_data["maintenance_costs"],
    }
    
    fig = px.bar(x=list(costs.keys()), y=list(costs.values()), title="Coûts par catégorie",
                 color=list(costs.values()), color_continuous_scale="Reds")
    fig.update_layout(xaxis_tickangle=45, height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📈 Ratios de coûts")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Dept Cost %", f"{kpis['Total Dept Cost (%)']:.1f}%")
    col2.metric("Payroll Cost %", f"{kpis['Payroll Cost (%)']:.1f}%")
    col3.metric("Admin Cost %", f"{kpis['Admin Cost (%)']:.1f}%")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Marketing Cost %", f"{kpis['Marketing Cost (%)']:.1f}%")
    col2.metric("Energy Cost %", f"{kpis['Energy Cost (%)']:.1f}%")
    col3.metric("Maintenance Cost %", f"{kpis['Maintenance Cost (%)']:.1f}%")


# ============================================================================
# SECTION 8: RAPPORT COMPLET
# ============================================================================

else:
    st.header("📑 Rapport d'analyse complet")
    st.caption(f"Hôtel: {st.session_state.hotel_data['hotel_name']} - Période: {st.session_state.hotel_data['period']}")
    
    # Résumé exécutif
    kpis = calculate_overall_kpis(st.session_state.hotel_data)
    rooms = calculate_rooms_kpis(st.session_state.hotel_data)
    fandb = calculate_fandb_kpis(st.session_state.hotel_data)
    spa = calculate_spa_kpis(st.session_state.hotel_data)
    
    st.subheader("🎯 Résumé exécutif")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Taux d'occupation", f"{kpis['Occupancy (%)']:.1f}%")
    col2.metric("ADR", f"{kpis['ADR (€)']:.2f}€")
    col3.metric("RevPAR", f"{kpis['RevPAR (€)']:.2f}€")
    col4.metric("Marge GOP", f"{kpis['Gross Operating Profit (%)']:.1f}%")
    
    # Tableau de bord des KPIs
    st.subheader("📊 Tableau de bord complet")
    
    dashboard_data = {
        "Catégorie": ["Général", "Général", "Général", "Hébergement", "Hébergement", "Hébergement", "Restauration", "Restauration", "Spa", "Spa"],
        "KPI": ["TRevPAR", "GOP %", "EBITDA %", "Occupancy", "ADR", "RevPAR", "Marge F&B", "Food Cost %", "TRU", "ATR"],
        "Valeur": [
            f"{kpis['TRevPAR (€)']:.0f}€", f"{kpis['Gross Operating Profit (%)']:.1f}%", f"{kpis['EBITDA (%)']:.1f}%",
            f"{rooms['Occupancy (%)']:.0f}%", f"{rooms['ADR (€)']:.0f}€", f"{rooms['RevPAR (€)']:.0f}€",
            f"{fandb['Total F&B Profit (%)']:.0f}%", f"{fandb['Food Cost of Sales (%)']:.0f}%",
            f"{spa['Treatment Room Utilisation - TRU (%)']:.0f}%", f"{spa['Average Treatment Rate - ATR (€)']:.0f}€"
        ]
    }
    st.dataframe(pd.DataFrame(dashboard_data), use_container_width=True, hide_index=True)
    
    # Points forts et axes d'amélioration
    st.subheader("💡 Analyse et recommandations")
    
    strengths = []
    improvements = []
    
    if kpis["Occupancy (%)"] >= 65:
        strengths.append("✅ Taux d'occupation satisfaisant")
    else:
        improvements.append("⚠️ Améliorer le taux d'occupation (objectif >65%)")
    
    if kpis["Gross Operating Profit (%)"] >= 30:
        strengths.append("✅ Bonne profitabilité GOP")
    else:
        improvements.append("⚠️ Optimiser les coûts pour améliorer la marge GOP")
    
    if rooms["Rooms Dept Profit (%)"] >= 70:
        strengths.append("✅ Excellente marge sur l'hébergement")
    else:
        improvements.append("⚠️ Revoir les coûts du département hébergement")
    
    if fandb["Total F&B Profit (%)"] >= 25:
        strengths.append("✅ Bonne performance du département restauration")
    else:
        improvements.append("⚠️ Améliorer la rentabilité de la restauration")
    
    if spa["Treatment Room Utilisation - TRU (%)"] >= 60:
        strengths.append("✅ Bonne utilisation des installations spa")
    else:
        improvements.append("⚠️ Promouvoir le spa pour augmenter son utilisation")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Points forts**")
        for s in strengths:
            st.write(s)
    with col2:
        st.markdown("**Axes d'amélioration**")
        for i in improvements:
            st.write(i)
    
    # Export
    st.subheader("📥 Export des données")
    if st.button("Générer le rapport complet (CSV)"):
        report_data = {
            **kpis,
            **rooms,
            **fandb,
            **spa
        }
        df = pd.DataFrame([report_data]).T.reset_index()
        df.columns = ["Indicateur", "Valeur"]
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Télécharger le rapport CSV", csv, "hotel_kpi_report.csv", "text/csv")

st.markdown("---")
st.caption("Dashboard d'Analyse Financière Hôtelière - Interface universelle")
