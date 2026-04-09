# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from io import StringIO

st.set_page_config(page_title="Hotel Financial Dashboard", layout="wide", page_icon="🏨")

# 🎨 Thème & Configuration
st.title("🏨 Dashboard d'Analyse Financière Hôtelière")
st.caption("Méthodologie basée sur Jawabreh et al. (2017) - Analyse de sensibilité & ratios sectoriels")

# 📥 1. CHARGEMENT DES DONNÉES
st.sidebar.header("📥 Données")
uploaded = st.sidebar.file_uploader("Importer CSV (structure mensuelle)", type=["csv"])

if uploaded:
    df = pd.read_csv(uploaded)
else:
    # Données par défaut (exemple 12 mois)
    st.sidebar.info("Utilisation des données démo. Importez un CSV pour vos données réelles.")
    df = pd.DataFrame({
        "mois": range(1,13),
        "guests": [65,40,60,70,80,130,170,220,130,90,65,80],
        "accommodation_rev": [2242.5,2100,3870,4725,4200,9750,15300,19800,11700,5400,4875,4800],
        "accommodation_cost": [975,600,900,1050,1200,1950,2550,3300,1950,1350,975,1066.67],
        "fnb_rev": [1282.13,930,1350,1575,1860,3960.45,5668.65,11550,6825,1440.45,1537.58,1860],
        "fnb_cost": [483.96,715.38,450,525,600,975.11,1274.7,1650,975,675.21,487.52,885.71],
        "other_rev": [975,720,479.7,1050,1440,2340,1530,2399.1,975,2160,487.5,840],
        "other_cost": [390,240,359.78,420,480,630,1020,1319.51,630,1440,390,480],
        "fixed_admin": [3450/12]*12, # mensualisé pour l'exemple
        "fixed_general": [2500/12]*12,
        "energy_cost": [1.46]*12,
        "maintenance_cost": [1.56]*12,
        "promo_cost": [1.25]*12,
        "available_rooms": [600]*12,
        "occupied_rooms": [250,200,280,300,330,400,450,420,350,300,230,300]
    })

# Calculs de base
df["total_rev"] = df["accommodation_rev"] + df["fnb_rev"] + df["other_rev"]
df["total_cost_var"] = df["accommodation_cost"] + df["fnb_cost"] + df["other_cost"]
df["net_profit"] = df["total_rev"] - df["total_cost_var"] - (df["fixed_admin"] + df["fixed_general"] + df["energy_cost"] + df["maintenance_cost"] + df["promo_cost"])

# 📊 BENCHMARKS (Tableau 1 & 10 du PDF)
BENCHMARKS = {
    "rev_acc": (45, 50), "rev_fnb": (35, 40), "rev_other": (5, 10),
    "cost_acc": (15, 25), "cost_fnb": (65, 80), "cost_other": (40, 70),
    "indirect_ga": (5, 10), "indirect_promo": (5, 10), "indirect_energy": (4, 10), "indirect_maint": (3, 5)
}

def check_benchmark(val, rng):
    if val < rng[0]: return "⚠️ En dessous"
    elif val > rng[1]: return "🔴 Au-dessus"
    return "✅ Dans la norme"

# 🖥️ INTERFACE PRINCIPALE
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Vue d'ensemble", "🛏️ Occupation", "💳 Dépenses Clients", 
    "📈 Rentabilité", "💰 Coûts vs Benchmarks", "🎯 Analyse de Sensibilité"
])

# TAB 1: OVERVIEW
with tab1:
    st.header("📊 Indicateurs Clés (Moyenne Annuelle)")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Clients Total", f"{df['guests'].sum():,.0f}")
    col2.metric("CA Total", f"{df['total_rev'].sum():,.0f} JOD")
    col3.metric("Profit Net", f"{df['net_profit'].sum():,.0f} JOD")
    col4.metric("Marge Nette", f"{(df['net_profit'].sum()/df['total_rev'].sum()*100):.1f}%")
    
    st.line_chart(df.set_index("mois")[["total_rev", "net_profit"]], use_container_width=True)

# TAB 2: OCCUPATION
with tab2:
    st.header("🛏️ Taux d'Occupation")
    df["occ_rate"] = (df["occupied_rooms"] / df["available_rooms"]) * 100
    st.dataframe(df[["mois", "occupied_rooms", "available_rooms", "occ_rate"]].rename(columns={"occ_rate":"Taux (%)"}), use_container_width=True)
    st.bar_chart(df.set_index("mois")["occ_rate"], use_container_width=True)
    st.caption("📖 Formule : (Chambres occupées / Chambres disponibles) × 100")

# TAB 3: DEPENSES CLIENTS
with tab3:
    st.header("💳 Pouvoir d'Achat par Client")
    df["spend_global"] = df["total_rev"] / df["guests"]
    df["spend_acc"] = df["accommodation_rev"] / df["guests"]
    df["spend_fnb"] = df["fnb_rev"] / df["guests"]
    
    st.dataframe(df[["mois", "guests", "spend_global", "spend_acc", "spend_fnb"]].round(2), use_container_width=True)
    fig = px.line(df, x="mois", y=["spend_global", "spend_acc", "spend_fnb"], title="Évolution des dépenses moyennes/client")
    st.plotly_chart(fig, use_container_width=True)

# TAB 4: RENTABILITÉ ACTIVITÉS
with tab4:
    st.header("📈 Rentabilité par Activité")
    df["prof_acc"] = ((df["accommodation_rev"] - df["accommodation_cost"]) / df["accommodation_rev"]) * 100
    df["prof_fnb"] = ((df["fnb_rev"] - df["fnb_cost"]) / df["fnb_rev"]) * 100
    df["prof_other"] = ((df["other_rev"] - df["other_cost"]) / df["other_rev"]) * 100
    
    st.dataframe(df[["mois", "prof_acc", "prof_fnb", "prof_other"]].round(2).rename(columns={"prof_acc":"Hébergement %", "prof_fnb":"F&B %", "prof_other":"Autres %"}), use_container_width=True)
    fig = px.bar(df.melt(id_vars="mois", value_vars=["prof_acc", "prof_fnb", "prof_other"]), x="mois", y="value", color="variable", barmode="group")
    st.plotly_chart(fig, use_container_width=True)

# TAB 5: COÛTS vs BENCHMARKS
with tab5:
    st.header("💰 Analyse des Coûts (Comparaison aux standards jordaniens)")
    
    # Calculs ratios
    df["rat_acc_rev"] = (df["accommodation_rev"] / df["total_rev"])*100
    df["rat_fnb_rev"] = (df["fnb_rev"] / df["total_rev"])*100
    df["rat_other_rev"] = (df["other_rev"] / df["total_rev"])*100
    
    df["rat_acc_cost"] = (df["accommodation_cost"] / df["accommodation_rev"])*100
    df["rat_fnb_cost"] = (df["fnb_cost"] / df["fnb_rev"])*100
    df["rat_other_cost"] = (df["other_cost"] / df["other_rev"])*100
    
    df["ind_ga"] = (df["fixed_admin"] / df["total_rev"])*100
    df["ind_promo"] = (df["promo_cost"] / df["total_rev"])*100
    df["ind_energy"] = (df["energy_cost"] / df["total_rev"])*100
    df["ind_maint"] = (df["maintenance_cost"] / df["total_rev"])*100

    st.subheader("Structure des Revenus vs Normes")
    rev_df = pd.DataFrame({
        "Hébergement": df["rat_acc_rev"].mean(),
        "F&B": df["rat_fnb_rev"].mean(),
        "Autres": df["rat_other_rev"].mean()
    }, index=["Moyenne Hôtel"])
    st.dataframe(rev_df)
    st.caption("Normes : Héberg. 45-50% | F&B 35-40% | Autres 5-10%")

    st.subheader("Coûts Indirects vs Normes")
    ind_df = pd.DataFrame({
        "Admin/G&A": df["ind_ga"].mean(),
        "Promo": df["ind_promo"].mean(),
        "Énergie": df["ind_energy"].mean(),
        "Maintenance": df["ind_maint"].mean()
    }, index=["Moyenne Hôtel"])
    st.dataframe(ind_df)
    st.caption("Normes : G&A 5-10% | Promo 5-10% | Énergie 4-10% | Maint. 3-5%")

# TAB 6: SENSIBILITÉ (PROFIT MULTIPLIER)
with tab6:
    st.header("🎯 Analyse de Sensibilité des Bénéfices (Multiplicateur de Profit)")
    st.markdown("""
    📖 **Méthode de l'auteur** : On fait varier un facteur de contrôle de +X% (autres constants), on recalcule le profit net, puis :
    `Multiplicateur = (%Δ Profit Net) / (%Δ Facteur)`
    """)
    
    pct = st.slider("Variation testée (%)", 1, 20, 10)
    
    base_profit = df["net_profit"].sum()
    base_guests = df["guests"].sum()
    base_spend = df["total_rev"].sum() / base_guests
    base_var_cost_unit = (df["accommodation_cost"].sum() + df["fnb_cost"].sum() + df["other_cost"].sum()) / base_guests
    base_fixed = (df["fixed_admin"].sum() + df["fixed_general"].sum())
    
    # Simulation des 6 facteurs
    factors = {
        "Nombre de clients": lambda: (base_guests*(1+pct/100))*base_spend - (base_guests*(1+pct/100))*base_var_cost_unit - base_fixed,
        "Dépense moyenne/client": lambda: base_guests*(base_spend*(1+pct/100)) - base_guests*base_var_cost_unit - base_fixed,
        "Coûts variables/unité": lambda: base_guests*base_spend - base_guests*(base_var_cost_unit*(1+pct/100)) - base_fixed,
        "Frais fixes (Admin)": lambda: base_guests*base_spend - base_guests*base_var_cost_unit - base_fixed*(1+pct/100)
    }
    
    multipliers = []
    for name, calc in factors.items():
        new_profit = calc()
        delta_p = ((new_profit - base_profit) / base_profit) * 100
        mult = delta_p / pct
        multipliers.append({"Facteur": name, "Multiplicateur": round(mult, 3), "Impact %": round(delta_p, 2)})
        
    mult_df = pd.DataFrame(multipliers).sort_values("Multiplicateur", ascending=False)
    st.dataframe(mult_df, use_container_width=True)
    
    st.info(f"📌 **Facteur le plus sensible** : {mult_df.iloc[0]['Facteur']} (x{mult_df.iloc[0]['Multiplicateur']})")
    st.caption("Une augmentation de 1% de ce facteur entraîne une variation de ~{:.2f}% du profit net.".format(mult_df.iloc[0]['Multiplicateur']))

# 📋 RECOMMANDATIONS AUTOMATIQUES
st.sidebar.header("📋 Alertes & Recommandations")
if df["prof_acc"].mean() > 50:
    st.sidebar.success("✅ Hébergement très rentable. Priorité stratégique confirmée.")
else:
    st.sidebar.warning("⚠️ Rentabilité hébergement à optimiser (tarification, occupancy).")

if df["rat_fnb_cost"].mean() > 80:
    st.sidebar.error("🔴 Coûts F&B > 80%. Réviser approvisionnements & gaspillage.")
else:
    st.sidebar.success("✅ Maîtrise des coûts F&B conforme aux normes.")

if mult_df.iloc[0]["Facteur"] == "Dépense moyenne/client":
    st.sidebar.info("💡 Upselling & services premium recommandés (facteur #1 du multiplicateur).")
