import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Configuration de l'expertise
st.set_page_config(page_title="Audit & Valorisation Hôtelière", layout="wide")

# --- FONCTIONS DE CALCUL D'EXPERTISE ---
def calculate_valuation(gop_annuel, cap_rate):
    """Calcule la valeur de l'hôtel par la méthode de capitalisation."""
    return gop_annuel / (cap_rate / 100)

def calculate_breakeven(fixes, ca_total, variables):
    """Calcule le point mort en CA."""
    marge_cv = (ca_total - variables) / ca_total if ca_total > 0 else 0
    return fixes / marge_cv if marge_cv > 0 else 0

# --- INTERFACE ---
st.title("🏛️ Hotel Asset Management & Appraisal Tool")
st.markdown("---")

# --- COLONNE DE GAUCHE : INPUTS AUDIT ---
with st.sidebar:
    st.header("📥 Données d'Audit (Inputs)")
    
    with st.expander("Capacité & Occupation", expanded=True):
        nb_cles = st.number_input("Nombre de clés", value=150)
        jours_ouvres = 365
        occ_rate = st.slider("Taux d'occupation annuel (%)", 0.0, 100.0, 68.0)
        adr = st.number_input("ADR (Prix Moyen HT) (€)", value=185.0)

    with st.expander("Structure des Revenus (Annexes)", expanded=False):
        fb_per_guest = st.number_input("Revenu F&B par client (€)", value=45.0)
        autres_rev_fixe = st.number_input("Autres revenus annuels (€)", value=50000)

    with st.expander("Analyse des Coûts (OPEX)", expanded=True):
        labor_cost_ratio = st.slider("Ratio Masse Salariale / CA (%)", 20.0, 50.0, 32.0)
        variable_costs_ratio = st.slider("Coûts variables / CA (%)", 10.0, 30.0, 15.0)
        fixed_costs_annuels = st.number_input("Charges Fixes Annuelles (€)", value=850000)

    with st.expander("Paramètres de Valorisation", expanded=True):
        cap_rate = st.select_slider("Taux de Capitalisation (Yield) %", options=[4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0], value=6.0)

# --- MOTEUR DE CALCUL ---
chambres_vendues = (nb_cles * jours_ouvres) * (occ_rate / 100)
rev_chambres = chambres_vendues * adr
rev_fb = chambres_vendues * fb_per_guest # Hypothèse 1 client/chambre pour simuler
ca_total = rev_chambres + rev_fb + autres_rev_fixe

masse_salariale = ca_total * (labor_cost_ratio / 100)
couts_variables = ca_total * (variable_costs_ratio / 100)
total_opex = masse_salariale + couts_variables + fixed_costs_annuels

gop = ca_total - total_opex
gop_margin = (gop / ca_total) * 100
valeur_venale = calculate_valuation(gop, cap_rate)
point_mort = calculate_breakeven(fixed_costs_annuels, ca_total, (masse_salariale + couts_variables))

# --- AFFICHAGE EXPERT ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("RevPAR", f"{(rev_chambres / (nb_cles * 365)):.2f} €")
col2.metric("GOP Final", f"{gop:,.0f} €")
col3.metric("Marge de GOP", f"{gop_margin:.1f} %")
col4.metric("Valeur Estimée (Asset Value)", f"{valeur_venale:,.0f} €", delta=f"Cap Rate: {cap_rate}%", delta_color="normal")

st.markdown("---")

# --- GRAPHIQUE : ANALYSE DU POINT MORT (BREAK-EVEN) ---
st.subheader("📈 Analyse de Rentabilité et Sensibilité")
c_plot1, c_plot2 = st.columns([2, 1])

with c_plot1:
    # Simulation pour graphique de point mort
    ca_range = np.linspace(point_mort * 0.5, ca_total * 1.5, 10)
    charges_fixes_line = [fixed_costs_annuels] * 10
    total_costs_line = charges_fixes_line + (ca_range * ((masse_salariale + couts_variables) / ca_total))
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ca_range, y=ca_range, name='Chiffre d\'Affaires', line=dict(color='green', dash='dot')))
    fig.add_trace(go.Scatter(x=ca_range, y=total_costs_line, name='Coûts Totaux', fill='tonexty', line=dict(color='red')))
    fig.add_vline(x=point_mort, line_dash="dash", line_color="orange", annotation_text="POINT MORT")
    fig.update_layout(title="Modèle de Rentabilité (Break-even Analysis)", xaxis_title="Chiffre d'Affaires (€)", yaxis_title="Montant (€)")
    st.plotly_chart(fig, use_container_width=True)

with c_plot2:
    st.write("### 📝 Conclusions de l'Expert")
    if gop_margin < 25:
        st.error("Alerte : Sous-performance opérationnelle. La marge de GOP est inférieure aux standards du marché (30-40%).")
    elif gop_margin > 40:
        st.success("Performance Exceptionnelle : L'actif génère un flux de trésorerie supérieur à la moyenne sectorielle.")
    
    st.info(f"""
    - **Seuil de rentabilité :** {point_mort:,.0f} € de CA.
    - **Valeur par chambre :** {valeur_venale / nb_cles:,.0f} € / clé.
    - **Sensibilité :** Une hausse de 1% du Cap Rate réduirait la valeur de l'actif de {(calculate_valuation(gop, cap_rate) - calculate_valuation(gop, cap_rate+1)):,.0f} €.
    """)

# --- TABLEAU DE RÉSUMÉ USALI ---
st.subheader("📋 Compte de Résultat Simplifié (Format USALI)")
data_pnl = {
    "Postes": ["Revenus Logement", "Revenus Restauration", "Autres Revenus", "TOTAL REVENUS", "Masse Salariale", "Autres Charges Variables", "Charges Fixes", "GOP (Profit Brut d'Exploitation)"],
    "Montant (€)": [rev_chambres, rev_fb, autres_rev_fixe, ca_total, -masse_salariale, -couts_variables, -fixed_costs_annuels, gop],
    "% du CA": [(rev_chambres/ca_total)*100, (rev_fb/ca_total)*100, (autres_rev_fixe/ca_total)*100, 100, -labor_cost_ratio, -variable_costs_ratio, -(fixed_costs_annuels/ca_total)*100, gop_margin]
}
st.table(pd.DataFrame(data_pnl))
