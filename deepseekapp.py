
**Facteurs contrôlants identifiés:**
1. Nombre de clients
2. Pouvoir de dépense moyen par client
3. Coûts des matériaux (variables)
4. Salaires variables
5. Frais administratifs
6. Frais généraux
""")

change_percent = st.slider("Pourcentage de variation des facteurs (%)", min_value=1, max_value=30, value=10) / 100

results, base_net_income = calculate_profit_sensitivity(
    data["guests"], data["avg_spending"], data["var_material"], 
    data["var_wages"], data["admin_exp"], data["general_exp"], 
    change_percent
)

st.subheader(f"💰 Bénéfice net initial: {base_net_income:,.2f} JOD")

# Tableau des résultats
df_results = pd.DataFrame([
    {
        "Facteur contrôlant": factor,
        "Nouvelle valeur": res["new_value"],
        "Nouveau bénéfice net (JOD)": f"{res['net_income']:,.2f}",
        "Variation du bénéfice (%)": f"{res['change_ratio']*100:.2f}%",
        "Multiplicateur de profit": f"{res['multiplier']:.3f}"
    }
    for factor, res in results.items()
])

st.dataframe(df_results, use_container_width=True)

# Classement des facteurs (Table 4 du document)
st.subheader("📊 Classement des facteurs contrôlants selon leur impact")

ranking = sorted(
    [(factor, res["multiplier"]) for factor, res in results.items()],
    key=lambda x: x[1],
    reverse=True
)

ranking_df = pd.DataFrame(ranking, columns=["Facteur contrôlant", "Multiplicateur de profit"])
ranking_df.index = range(1, len(ranking_df) + 1)
ranking_df.index.name = "Rang"

st.dataframe(ranking_df, use_container_width=True)

# Graphique
fig = px.bar(
    ranking_df, 
    x="Facteur contrôlant", 
    y="Multiplicateur de profit",
    title="Multiplicateur de profit par facteur contrôlant",
    color="Multiplicateur de profit",
    color_continuous_scale="Viridis"
)
st.plotly_chart(fig, use_container_width=True)

st.info("""
**Interprétation selon l'étude:**
- Un multiplicateur élevé (>1) indique une forte sensibilité du profit à ce facteur
- Le pouvoir de dépense du client (3.945x) est le facteur le plus influent
- L'hôtel est qualifié de 'sensible aux revenus'
""")

# ============================================================================
# SECTION 2: TAUX D'OCCUPATION
# ============================================================================

elif section == "2. Taux d'Occupation":
st.header("🏠 Taux d'Occupation")
st.markdown("""
**Formules selon le document:**

- **Taux d'occupation des chambres** = (Nombre de chambres occupées / Nombre de chambres disponibles) × 100%
- **Taux d'occupation des lits** = (Nombre de lits occupés / Nombre de lits disponibles) × 100%
- **Taux d'occupation des suites** = (Nombre de suites occupées / Nombre de suites disponibles) × 100%
- **Taux d'occupation du restaurant** = (Nombre de repas servis / Capacité en sièges) × 100%
""")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Données d'entrée")
    available_rooms = st.number_input("Chambres disponibles", value=600, min_value=1)
    occupied_rooms = st.number_input("Chambres occupées", value=322, min_value=0)
    available_beds = st.number_input("Lits disponibles", value=800, min_value=1)
    occupied_beds = st.number_input("Lits occupés", value=430, min_value=0)
    
with col2:
    available_suites = st.number_input("Suites disponibles", value=100, min_value=1)
    occupied_suites = st.number_input("Suites occupées", value=54, min_value=0)
    seats_capacity = st.number_input("Capacité restaurant (sièges)", value=200, min_value=1)
    meals_served = st.number_input("Repas servis", value=1500, min_value=0)

occupancy_rates = calculate_occupancy_rates(
    occupied_rooms, available_rooms,
    occupied_beds, available_beds,
    occupied_suites, available_suites,
    meals_served, seats_capacity
)

st.subheader("📊 Résultats des taux d'occupation")

# Affichage des métriques
cols = st.columns(4)
for i, (name, value) in enumerate(occupancy_rates.items()):
    cols[i].metric(name, f"{value:.1f}%")

# Graphique
fig = px.bar(
    x=list(occupancy_rates.keys()),
    y=list(occupancy_rates.values()),
    title="Taux d'occupation",
    labels={"x": "Indicateur", "y": "Taux (%)"},
    color=list(occupancy_rates.values()),
    color_continuous_scale="Blues"
)
st.plotly_chart(fig, use_container_width=True)

# Données mensuelles de l'étude (Table 5)
st.subheader("📅 Données mensuelles - Hôtel Al Zaitonia (référence)")
monthly_data = {
    "Mois": ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Aoû", "Sep", "Oct", "Nov", "Déc"],
    "Chambres occupées": [250, 200, 280, 300, 330, 400, 450, 420, 350, 300, 230, 300],
    "Taux d'occupation (%)": [42, 33, 47, 50, 55, 67, 75, 70, 58, 50, 38, 50]
}
monthly_df = pd.DataFrame(monthly_data)

fig_monthly = px.line(
    monthly_df, 
    x="Mois", 
    y="Taux d'occupation (%)",
    title="Évolution mensuelle du taux d'occupation (Hôtel Al Zaitonia - 2003)",
    markers=True
)
fig_monthly.add_hline(y=monthly_df["Taux d'occupation (%)"].mean(), line_dash="dash", 
                      annotation_text=f"Moyenne: {monthly_df['Taux d'occupation (%)'].mean():.1f}%")
st.plotly_chart(fig_monthly, use_container_width=True)

st.caption("Source: Table 5 du document - Hôtel Al Zaitonia, chambres disponibles mensuelles: 600")

# ============================================================================
# SECTION 3: DÉPENSES DES CLIENTS
# ============================================================================

elif section == "3. Dépenses des Clients":
st.header("💰 Taux de Dépense des Clients")
st.markdown("""
**Formules selon le document:**

- **Dépense moyenne générale** = Revenu total / Nombre de clients
- **Dépense moyenne hébergement** = Revenu hébergement / Nombre de clients
- **Dépense moyenne repas et boissons** = Revenu repas / Nombre de clients
- **Dépense moyenne autres services** = Revenu autres services / Nombre de clients
- **Dépense moyenne par repas** = Revenu repas / Nombre de repas
- **Durée moyenne du séjour** = Nombre total de nuits / Nombre de clients
""")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Revenus")
    total_revenue = st.number_input("Revenu total (JOD)", value=144000.0, min_value=0.0)
    accommodation_revenue = st.number_input("Revenu hébergement (JOD)", value=88762.5, min_value=0.0)
    food_revenue = st.number_input("Revenu repas et boissons (JOD)", value=39839.25, min_value=0.0)
    other_revenue = st.number_input("Revenu autres services (JOD)", value=15396.3, min_value=0.0)
    
with col2:
    st.subheader("Autres données")
    num_guests = st.number_input("Nombre de clients", value=1200, min_value=1)
    num_meals = st.number_input("Nombre de repas servis", value=2500, min_value=0)
    total_nights = st.number_input("Nombre total de nuits", value=3600, min_value=0)

spending_rates = calculate_guest_spending_rates(
    total_revenue, num_guests, accommodation_revenue, food_revenue, 
    other_revenue, num_meals, total_nights
)

st.subheader("📊 Résultats des dépenses moyennes")

spending_df = pd.DataFrame([
    {"Indicateur": k, "Valeur (JOD)": v if "JOD" in k else v}
    for k, v in spending_rates.items()
])
st.dataframe(spending_df, use_container_width=True)

# Graphique des répartitions (Figure 2 du document)
st.subheader("🏗️ Structure des dépenses par service")

composition = {
    "Hébergement": accommodation_revenue,
    "Repas et boissons": food_revenue,
    "Autres services": other_revenue
}

fig = px.pie(
    values=list(composition.values()),
    names=list(composition.keys()),
    title="Répartition du revenu par service",
    color_discrete_sequence=px.colors.sequential.Blues_r
)
st.plotly_chart(fig, use_container_width=True)

# Données mensuelles de l'étude (Table 6)
st.subheader("📅 Données mensuelles de référence - Hôtel Al Zaitonia")
monthly_spending = {
    "Mois": ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Aoû", "Sep", "Oct", "Nov", "Déc"],
    "Dépense moyenne (JOD)": [69.2, 93.75, 95, 105, 93.75, 123.46, 132.35, 153.4, 150, 90, 106.15, 93.75]
}
monthly_df = pd.DataFrame(monthly_spending)

fig_monthly = px.line(
    monthly_df,
    x="Mois",
    y="Dépense moyenne (JOD)",
    title="Dépense moyenne mensuelle par client",
    markers=True
)
fig_monthly.add_hline(y=monthly_df["Dépense moyenne (JOD)"].mean(), 
                      line_dash="dash", 
                      annotation_text=f"Moyenne: {monthly_df['Dépense moyenne (JOD)'].mean():.1f} JOD")
st.plotly_chart(fig_monthly, use_container_width=True)

st.caption("Source: Table 6 du document - Hôtel Al Zaitonia 2003")

# ============================================================================
# SECTION 4: RENTABILITÉ PAR ACTIVITÉ
# ============================================================================

elif section == "4. Rentabilité par Activité":
st.header("📊 Rentabilité par Activité Hôtelière")
st.markdown("""
**Formules selon le document:**

- **Rentabilité hébergement** = (Revenu hébergement - Coûts hébergement) / Coûts hébergement × 100%
- **Rentabilité repas et boissons** = (Revenu repas - Coûts repas) / Coûts repas × 100%
- **Rentabilité autres services** = (Revenu autres - Coûts autres) / Coûts autres × 100%
""")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Hébergement")
    acc_rev = st.number_input("Revenu hébergement (JOD)", value=88762.5, min_value=0.0)
    acc_cost = st.number_input("Coûts hébergement (JOD)", value=15396.3, min_value=0.0)
    
    st.subheader("Repas et boissons")
    food_rev = st.number_input("Revenu repas (JOD)", value=39839.25, min_value=0.0)
    food_cost = st.number_input("Coûts repas (JOD)", value=15396.3, min_value=0.0)
    
with col2:
    st.subheader("Autres services")
    other_rev = st.number_input("Revenu autres services (JOD)", value=15396.3, min_value=0.0)
    other_cost = st.number_input("Coûts autres services (JOD)", value=15396.3, min_value=0.0)

profitability = calculate_activity_profitability(
    acc_rev, acc_cost, food_rev, food_cost, other_rev, other_cost
)

st.subheader("📈 Résultats de rentabilité")

col_prof1, col_prof2, col_prof3 = st.columns(3)
col_prof1.metric("Rentabilité Hébergement", f"{profitability['Rentabilité hébergement (%)']:.1f}%")
col_prof2.metric("Rentabilité Repas", f"{profitability['Rentabilité repas et boissons (%)']:.1f}%")
col_prof3.metric("Rentabilité Autres services", f"{profitability['Rentabilité autres services (%)']:.1f}%")

# Graphique
profit_rates = {
    "Hébergement": profitability['Rentabilité hébergement (%)'],
    "Repas et boissons": profitability['Rentabilité repas et boissons (%)'],
    "Autres services": profitability['Rentabilité autres services (%)']
}

fig = px.bar(
    x=list(profit_rates.keys()),
    y=list(profit_rates.values()),
    title="Taux de rentabilité par activité",
    labels={"x": "Activité", "y": "Taux de rentabilité (%)"},
    color=list(profit_rates.values()),
    color_continuous_scale="Greens"
)
st.plotly_chart(fig, use_container_width=True)

# Données mensuelles de l'étude (Table 7)
st.subheader("📅 Rentabilité mensuelle par activité - Hôtel Al Zaitonia")
monthly_profit = {
    "Mois": ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Aoû", "Sep", "Oct", "Nov", "Déc"],
    "Hébergement (%)": [49.84, 56.00, 67.90, 64.29, 56.00, 60.75, 68.00, 58.67, 60.00, 60.00, 70.65, 64.00],
    "Repas (%)": [28.49, 24.80, 23.69, 21.43, 24.80, 24.68, 25.20, 34.22, 35.00, 16.00, 22.28, 24.80],
    "Autres (%)": [22, 19, 8, 14, 19, 15, 7, 7, 5, 24, 7, 11]
}
monthly_df = pd.DataFrame(monthly_profit)

fig_monthly = px.line(
    monthly_df,
    x="Mois",
    y=["Hébergement (%)", "Repas (%)", "Autres (%)"],
    title="Évolution mensuelle de la rentabilité par activité",
    markers=True
)
st.plotly_chart(fig_monthly, use_container_width=True)

st.caption("Source: Table 7 du document - Hôtel Al Zaitonia 2003")

# ============================================================================
# SECTION 5: TAUX DE COÛTS D'EXPLOITATION
# ============================================================================

elif section == "5. Taux de Coûts d'Exploitation":
st.header("📉 Taux de Coûts d'Exploitation")
st.markdown("""
**Coûts directs (Formules):**
- Taux coûts directs hébergement = Coûts hébergement / Revenu hébergement × 100%
- Taux coûts directs repas = Coûts repas / Revenu repas × 100%
- Taux coûts directs autres = Coûts autres / Revenu autres × 100%

**Coûts indirects (Formules):**
- Taux de promotion = Coûts promotion / Revenu total × 100%
- Taux d'énergie = Coûts énergie / Revenu total × 100%
- Taux de maintenance = Coûts maintenance / Revenu total × 100%
- Taux administratif = Coûts administratifs / Revenu total × 100%
""")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Coûts directs")
    acc_rev = st.number_input("Revenu hébergement (JOD)", value=88762.5, min_value=0.0, key="dir_acc_rev")
    acc_cost = st.number_input("Coûts hébergement (JOD)", value=15396.3, min_value=0.0, key="dir_acc_cost")
    food_rev = st.number_input("Revenu repas (JOD)", value=39839.25, min_value=0.0, key="dir_food_rev")
    food_cost = st.number_input("Coûts repas (JOD)", value=15396.3, min_value=0.0, key="dir_food_cost")
    other_rev = st.number_input("Revenu autres (JOD)", value=15396.3, min_value=0.0, key="dir_other_rev")
    other_cost = st.number_input("Coûts autres (JOD)", value=15396.3, min_value=0.0, key="dir_other_cost")
    
with col2:
    st.subheader("Coûts indirects")
    total_revenue = st.number_input("Revenu total (JOD)", value=144000.0, min_value=0.0, key="ind_total")
    sales_promo = st.number_input("Coûts de promotion (JOD)", value=2000.0, min_value=0.0)
    energy_costs = st.number_input("Coûts énergie (JOD)", value=3000.0, min_value=0.0)
    maintenance_costs = st.number_input("Coûts maintenance (JOD)", value=2500.0, min_value=0.0)
    admin_costs = st.number_input("Coûts administratifs (JOD)", value=34500.0, min_value=0.0)

cost_rates = calculate_cost_rates(
    acc_cost, acc_rev, food_cost, food_rev, other_cost, other_rev,
    sales_promo, total_revenue, energy_costs, maintenance_costs, admin_costs
)

st.subheader("📊 Résultats des taux de coûts")

cost_df = pd.DataFrame([
    {"Type de coût": k, "Taux (%)": f"{v:.2f}%"}
    for k, v in cost_rates.items()
])
st.dataframe(cost_df, use_container_width=True)

# Graphique
fig = make_subplots(rows=2, cols=1, subplot_titles=("Coûts directs", "Coûts indirects"))

direct_costs = {k: v for k, v in cost_rates.items() if "Coûts directs" in k}
indirect_costs = {k: v for k, v in cost_rates.items() if "Coûts directs" not in k}

fig.add_trace(
    go.Bar(x=list(direct_costs.keys()), y=list(direct_costs.values()), name="Coûts directs", marker_color="coral"),
    row=1, col=1
)
fig.add_trace(
    go.Bar(x=list(indirect_costs.keys()), y=list(indirect_costs.values()), name="Coûts indirects", marker_color="lightblue"),
    row=2, col=1
)

fig.update_layout(height=600, showlegend=False, title_text="Analyse des coûts d'exploitation")
fig.update_xaxes(tickangle=45)
st.plotly_chart(fig, use_container_width=True)

# Données mensuelles (Table 9, 11)
st.subheader("📅 Évolution mensuelle des coûts - Hôtel Al Zaitonia")

monthly_direct = {
    "Mois": ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Aoû", "Sep", "Oct", "Nov", "Déc"],
    "Hébergement (%)": [43.48, 28.57, 23.26, 22.22, 28.57, 20.00, 16.67, 16.67, 16.67, 25.00, 20.00, 22.22],
    "Repas (%)": [37.75, 76.92, 33.33, 33.33, 32.26, 24.62, 22.49, 14.29, 14.29, 46.88, 31.71, 47.62],
    "Autres (%)": [40.00, 33.33, 75.00, 40.00, 33.33, 26.92, 66.67, 55.00, 64.62, 66.67, 80.00, 57.14]
}
monthly_df = pd.DataFrame(monthly_direct)

fig_monthly = px.line(
    monthly_df,
    x="Mois",
    y=["Hébergement (%)", "Repas (%)", "Autres (%)"],
    title="Taux de coûts directs mensuels par activité",
    markers=True
)
st.plotly_chart(fig_monthly, use_container_width=True)

st.caption("Source: Table 9 (coûts directs) et Table 11 (coûts indirects) du document")

# ============================================================================
# SECTION 6: COMPARAISON AVEC LES NORMES SECTORIELLES
# ============================================================================

elif section == "6. Comparaison avec les Normes Sectorielles":
st.header("🏆 Comparaison avec les Normes Sectorielles Jordaniennes")
st.markdown("""
**Normes standards pour les hôtels en Jordanie (Source: Ministère du Tourisme / Table 1 du document)**

Ces normes permettent d'identifier les écarts et les axes d'amélioration.
""")

# Tableau des normes
st.subheader("📋 Normes standards pour l'hôtellerie jordanienne")

standards_df = pd.DataFrame([
    {"Catégorie": "Revenus - Hébergement", "Min": "45%", "Max": "50%"},
    {"Catégorie": "Revenus - Repas et boissons", "Min": "35%", "Max": "40%"},
    {"Catégorie": "Revenus - Autres services", "Min": "5%", "Max": "10%"},
    {"Catégorie": "Coûts directs - Hébergement", "Min": "15%", "Max": "25%"},
    {"Catégorie": "Coûts directs - Repas", "Min": "65%", "Max": "80%"},
    {"Catégorie": "Coûts directs - Autres", "Min": "40%", "Max": "70%"},
    {"Catégorie": "Coûts indirects - Administratifs", "Min": "5%", "Max": "10%"},
    {"Catégorie": "Coûts indirects - Promotion", "Min": "5%", "Max": "10%"},
    {"Catégorie": "Coûts indirects - Énergie", "Min": "4%", "Max": "10%"},
    {"Catégorie": "Coûts indirects - Maintenance", "Min": "3%", "Max": "5%"}
], index=range(1, 11))
st.dataframe(standards_df, use_container_width=True)

# Données de l'hôtel Al Zaitonia pour comparaison
st.subheader("📊 Comparaison avec les performances de l'Hôtel Al Zaitonia")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Structure des revenus**")
    hotel_revenue = {
        "Hébergement": 61.67,
        "Repas et boissons": 26.07,
        "Autres services": 12.26
    }
    
    revenue_df = pd.DataFrame([
        {"Source": k, "Hôtel Al Zaitonia (%)": v, "Norme min": INDUSTRY_STANDARDS["Revenue Elements"][k]["min"], 
         "Norme max": INDUSTRY_STANDARDS["Revenue Elements"][k]["max"], "Conforme": "✅" if INDUSTRY_STANDARDS["Revenue Elements"][k]["min"] <= v <= INDUSTRY_STANDARDS["Revenue Elements"][k]["max"] else "⚠️"}
        for k, v in hotel_revenue.items()
    ])
    st.dataframe(revenue_df, use_container_width=True)
    
with col2:
    st.markdown("**Coûts indirects**")
    hotel_indirect = {
        "Administratifs et généraux": 41.67,
        "Promotion": 1.4,
        "Énergie et éclairage": 2.2,
        "Maintenance et réparation": 1.25
    }
    
    # Note: La moyenne pour les coûts administratifs de l'hôtel est de 41.67% selon Table 11
    indirect_df = pd.DataFrame([
        {"Source": k, "Hôtel Al Zaitonia (%)": v, "Norme min": INDUSTRY_STANDARDS["Indirect Costs"][k]["min"],
         "Norme max": INDUSTRY_STANDARDS["Indirect Costs"][k]["max"], "Conforme": "✅" if INDUSTRY_STANDARDS["Indirect Costs"][k]["min"] <= v <= INDUSTRY_STANDARDS["Indirect Costs"][k]["max"] else "⚠️"}
        for k, v in hotel_indirect.items()
    ])
    st.dataframe(indirect_df, use_container_width=True)

# Graphique de comparaison
st.subheader("📈 Écarts par rapport aux normes")

fig = make_subplots(rows=2, cols=2, subplot_titles=("Revenus", "Coûts directs", "Coûts indirects", "Analyse"))

# Revenus
rev_names = list(hotel_revenue.keys())
rev_hotel = list(hotel_revenue.values())
rev_min = [INDUSTRY_STANDARDS["Revenue Elements"][k]["min"] for k in rev_names]
rev_max = [INDUSTRY_STANDARDS["Revenue Elements"][k]["max"] for k in rev_names]

fig.add_trace(go.Bar(name="Hôtel Al Zaitonia", x=rev_names, y=rev_hotel, marker_color="blue"), row=1, col=1)
fig.add_trace(go.Bar(name="Norme min", x=rev_names, y=rev_min, marker_color="lightgray"), row=1, col=1)
fig.add_trace(go.Bar(name="Norme max", x=rev_names, y=rev_max, marker_color="darkgray"), row=1, col=1)

# Coûts indirects
ind_names = list(hotel_indirect.keys())
ind_hotel = list(hotel_indirect.values())
ind_min = [INDUSTRY_STANDARDS["Indirect Costs"][k]["min"] for k in ind_names]
ind_max = [INDUSTRY_STANDARDS["Indirect Costs"][k]["max"] for k in ind_names]

fig.add_trace(go.Bar(name="Hôtel Al Zaitonia", x=ind_names, y=ind_hotel, marker_color="coral"), row=2, col=1)
fig.add_trace(go.Bar(name="Norme min", x=ind_names, y=ind_min, marker_color="lightgray"), row=2, col=1)
fig.add_trace(go.Bar(name="Norme max", x=ind_names, y=ind_max, marker_color="darkgray"), row=2, col=1)

fig.update_layout(height=600, showlegend=True, barmode='group')
st.plotly_chart(fig, use_container_width=True)

st.info("""
**Interprétation des écarts selon l'étude:**
- Les revenus d'hébergement sont supérieurs à la norme (bon indicateur)
- Les coûts administratifs sont très élevés par rapport à la norme (41.67% vs 5-10%)
- Les coûts de promotion sont trop faibles (1.4% vs 5-10%)
- Les coûts d'énergie et maintenance sont inférieurs aux normes
""")

# ============================================================================
# SECTION 7: RAPPORT COMPLET
# ============================================================================

else:  # Rapport complet
st.header("📑 Rapport d'Analyse Financière Complet")
st.markdown("""
**Méthodologie:** Analyse financière appliquée au secteur hôtelier selon Jawabreh et al. (2017)

**Cas d'étude:** Hôtel Al Zaitonia - 3 étoiles, Aqaba, Jordanie
""")

# Exécution de toutes les analyses
change_percent = 0.10
sensitivity_results, base_net_income = calculate_profit_sensitivity(
    data["guests"], data["avg_spending"], data["var_material"], 
    data["var_wages"], data["admin_exp"], data["general_exp"], 
    change_percent
)

occupancy = calculate_occupancy_rates(
    data["occupied_rooms"], data["available_rooms"],
    data["occupied_beds"], data["available_beds"],
    data["occupied_suites"], data["available_suites"],
    data["meals_served"], data["seats_capacity"]
)

spending = calculate_guest_spending_rates(
    data["total_revenue"], data["num_guests"],
    data["accommodation_revenue"], data["food_revenue"],
    data["other_revenue"], data["num_meals"], data["total_nights"]
)

profitability = calculate_activity_profitability(
    data["accommodation_revenue"], data["accommodation_costs"],
    data["food_revenue"], data["food_costs"],
    data["other_revenue"], data["other_costs"]
)

costs = calculate_cost_rates(
    data["accommodation_costs"], data["accommodation_revenue"],
    data["food_costs"], data["food_revenue"],
    data["other_costs"], data["other_revenue"],
    data["sales_promotion_costs"], data["total_revenue"],
    data["energy_costs"], data["maintenance_costs"],
    data["admin_costs"]
)

# Affichage des KPI principaux
st.subheader("🎯 Indicateurs Clés de Performance (KPI)")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Bénéfice net annuel", f"{base_net_income:,.0f} JOD")
col2.metric("Taux d'occupation", f"{occupancy['Taux d\'occupation chambres']:.1f}%")
col3.metric("Dépense moyenne/client", f"{spending['Dépense moyenne générale (JOD)']:.1f} JOD")
col4.metric("Rentabilité hébergement", f"{profitability['Rentabilité hébergement (%)']:.1f}%")

# Classement des facteurs de sensibilité
st.subheader("🔍 Classement des facteurs contrôlants (Multiplicateurs de profit)")
ranking = sorted(
    [(factor, res["multiplier"]) for factor, res in sensitivity_results.items()],
    key=lambda x: x[1],
    reverse=True
)
ranking_df = pd.DataFrame(ranking[:6], columns=["Facteur", "Multiplicateur"])
st.dataframe(ranking_df, use_container_width=True)

# Graphique radar des indicateurs
st.subheader("📊 Indicateurs de performance")

radar_data = {
    "Taux d'occupation": occupancy['Taux d\'occupation chambres'],
    "Dépense/client": spending['Dépense moyenne générale (JOD)'] / 200 * 100,  # normalisé
    "Rentabilité hébergement": profitability['Rentabilité hébergement (%)'],
    "Rentabilité repas": profitability['Rentabilité repas et boissons (%)'],
    "Conformité coûts directs hébergement": max(0, 100 - costs['Coûts directs - Hébergement (%)'])
}

fig = go.Figure(data=go.Scatterpolar(
    r=list(radar_data.values()),
    theta=list(radar_data.keys()),
    fill='toself',
    marker_color='blue'
))
fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False)
st.plotly_chart(fig, use_container_width=True)

# Résumé et recommandations
st.subheader("📝 Résumé et Recommandations (selon l'étude)")

st.markdown("""
**Principaux résultats:**

1. **Facteurs contrôlants des revenus:** Le pouvoir de dépense moyen par client (multiplicateur 3.945x) est le facteur le plus influent sur la rentabilité, suivi du nombre de clients (2.63x)

2. **Rentabilité par activité:** L'hébergement représente l'activité la plus rentable (taux moyen de 61% dans l'étude)

3. **Structure des coûts:** Les coûts variables et fixes affectent directement la rentabilité et nécessitent une planification continue

**Recommandations de l'auteur:**
- Accorder plus d'attention aux facteurs liés aux revenus (pouvoir de dépense des clients)
- Augmenter les budgets de promotion (actuellement inférieurs aux normes sectorielles)
- Mettre en place un système de suivi mensuel des écarts par rapport aux normes
- Développer une identité distinctive pour le secteur hôtelier jordanien
""")

# Tableau récapitulatif des formules
with st.expander("📚 Voir toutes les formules utilisées"):
    st.markdown("""
    ### Formules d'Analyse Financière Hôtelière
    
    **Analyse de sensibilité du profit:**
    - Multiplicateur de profit = (Δ% Bénéfice net) / (Δ% Facteur contrôlant)
    
    **Taux d'occupation:**
    - Taux occupation chambres = (Chambres occupées / Chambres disponibles) × 100%
    - Taux occupation lits = (Lits occupés / Lits disponibles) × 100%
    - Taux occupation restaurant = (Repas servis / Capacité sièges) × 100%
    
    **Taux de dépense des clients:**
    - Dépense moyenne générale = Revenu total / Nombre de clients
    - Dépense moyenne hébergement = Revenu hébergement / Nombre de clients
    - Durée moyenne séjour = Nombre total de nuits / Nombre de clients
    
    **Taux de rentabilité:**
    - Rentabilité activité = (Revenu - Coût) / Coût × 100%
    
    **Taux de coûts:**
    - Taux coût direct = Coût activité / Revenu activité × 100%
    - Taux coût indirect = Coût indirect / Revenu total × 100%
    """)

st.markdown("---")
st.caption("🏨 Dashboard d'Analyse Financière Hôtelière | Basé sur Jawabreh et al. (2017) - International Journal of Economics and Financial Issues")
