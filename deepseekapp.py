
**Facteurs controlants identifies:**
1. Nombre de clients
2. Pouvoir de depense moyen par client
3. Couts des materiaux (variables)
4. Salaires variables
5. Frais administratifs
6. Frais generaux
""")

change_percent = st.slider("Pourcentage de variation des facteurs (%)", min_value=1, max_value=30, value=10) / 100

results, base_net_income = calculate_profit_sensitivity(
    data["guests"], data["avg_spending"], data["var_material"], 
    data["var_wages"], data["admin_exp"], data["general_exp"], 
    change_percent
)

st.subheader(f"💰 Benefice net initial: {base_net_income:,.2f} JOD")

# Tableau des resultats
df_results = pd.DataFrame([
    {
        "Facteur controlant": factor,
        "Nouvelle valeur": res["new_value"],
        "Nouveau benefice net (JOD)": f"{res['net_income']:,.2f}",
        "Variation du benefice (%)": f"{res['change_ratio']*100:.2f}%",
        "Multiplicateur de profit": f"{res['multiplier']:.3f}"
    }
    for factor, res in results.items()
])

st.dataframe(df_results, use_container_width=True)

# Classement des facteurs (Table 4 du document)
st.subheader("📊 Classement des facteurs controlants selon leur impact")

ranking = sorted(
    [(factor, res["multiplier"]) for factor, res in results.items()],
    key=lambda x: x[1],
    reverse=True
)

ranking_df = pd.DataFrame(ranking, columns=["Facteur controlant", "Multiplicateur de profit"])
ranking_df.index = range(1, len(ranking_df) + 1)
ranking_df.index.name = "Rang"

st.dataframe(ranking_df, use_container_width=True)

# Graphique
fig = px.bar(
    ranking_df, 
    x="Facteur controlant", 
    y="Multiplicateur de profit",
    title="Multiplicateur de profit par facteur controlant",
    color="Multiplicateur de profit",
    color_continuous_scale="Viridis"
)
st.plotly_chart(fig, use_container_width=True)

st.info("""
**Interpretation selon l'etude:**
- Un multiplicateur eleve (>1) indique une forte sensibilite du profit a ce facteur
- Le pouvoir de depense du client (3.945x) est le facteur le plus influent
- L'hotel est qualifie de 'sensible aux revenus'
""")


# ============================================================================
# SECTION 2: TAUX D'OCCUPATION
# ============================================================================

elif section == "2. Taux d'Occupation":
st.header("🏠 Taux d'Occupation")
st.markdown("""
**Formules selon le document:**

- **Taux d'occupation des chambres** = (Nombre de chambres occupees / Nombre de chambres disponibles) * 100%
- **Taux d'occupation des lits** = (Nombre de lits occupes / Nombre de lits disponibles) * 100%
- **Taux d'occupation des suites** = (Nombre de suites occupees / Nombre de suites disponibles) * 100%
- **Taux d'occupation du restaurant** = (Nombre de repas servis / Capacite en sieges) * 100%
""")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Donnees d'entree")
    available_rooms = st.number_input("Chambres disponibles", value=data["available_rooms"], min_value=1)
    occupied_rooms = st.number_input("Chambres occupees", value=data["occupied_rooms"], min_value=0)
    available_beds = st.number_input("Lits disponibles", value=data["available_beds"], min_value=1)
    occupied_beds = st.number_input("Lits occupes", value=data["occupied_beds"], min_value=0)
    
with col2:
    available_suites = st.number_input("Suites disponibles", value=data["available_suites"], min_value=1)
    occupied_suites = st.number_input("Suites occupees", value=data["occupied_suites"], min_value=0)
    seats_capacity = st.number_input("Capacite restaurant (sieges)", value=data["seats_capacity"], min_value=1)
    meals_served = st.number_input("Repas servis", value=data["meals_served"], min_value=0)

occupancy_rates = calculate_occupancy_rates(
    occupied_rooms, available_rooms,
    occupied_beds, available_beds,
    occupied_suites, available_suites,
    meals_served, seats_capacity
)

st.subheader("📊 Resultats des taux d'occupation")

# Affichage des metriques
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

# Donnees mensuelles de l'etude (Table 5)
st.subheader("📅 Donnees mensuelles - Hotel Al Zaitonia (reference)")
monthly_data = {
    "Mois": ["Jan", "Fev", "Mar", "Avr", "Mai", "Juin", "Juil", "Aou", "Sep", "Oct", "Nov", "Dec"],
    "Chambres occupees": [250, 200, 280, 300, 330, 400, 450, 420, 350, 300, 230, 300],
    "Taux d'occupation (%)": [42, 33, 47, 50, 55, 67, 75, 70, 58, 50, 38, 50]
}
monthly_df = pd.DataFrame(monthly_data)

fig_monthly = px.line(
    monthly_df, 
    x="Mois", 
    y="Taux d'occupation (%)",
    title="Evolution mensuelle du taux d'occupation (Hotel Al Zaitonia - 2003)",
    markers=True
)
fig_monthly.add_hline(y=monthly_df["Taux d'occupation (%)"].mean(), line_dash="dash", 
                      annotation_text=f"Moyenne: {monthly_df['Taux d occupation (%)'].mean():.1f}%")
st.plotly_chart(fig_monthly, use_container_width=True)

st.caption("Source: Table 5 du document - Hotel Al Zaitonia, chambres disponibles mensuelles: 600")


# ============================================================================
# SECTION 3: DEPENSES DES CLIENTS
# ============================================================================

elif section == "3. Depenses des Clients":
st.header("💰 Taux de Depense des Clients")
st.markdown("""
**Formules selon le document:**

- **Depense moyenne generale** = Revenu total / Nombre de clients
- **Depense moyenne hebergement** = Revenu hebergement / Nombre de clients
- **Depense moyenne repas et boissons** = Revenu repas / Nombre de clients
- **Depense moyenne autres services** = Revenu autres services / Nombre de clients
- **Depense moyenne par repas** = Revenu repas / Nombre de repas
- **Duree moyenne du sejour** = Nombre total de nuits / Nombre de clients
""")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Revenus")
    total_revenue = st.number_input("Revenu total (JOD)", value=data["total_revenue"], min_value=0.0)
    accommodation_revenue = st.number_input("Revenu hebergement (JOD)", value=data["accommodation_revenue"], min_value=0.0)
    food_revenue = st.number_input("Revenu repas et boissons (JOD)", value=data["food_revenue"], min_value=0.0)
    other_revenue = st.number_input("Revenu autres services (JOD)", value=data["other_revenue"], min_value=0.0)
    
with col2:
    st.subheader("Autres donnees")
    num_guests = st.number_input("Nombre de clients", value=data["num_guests"], min_value=1)
    num_meals = st.number_input("Nombre de repas servis", value=data["num_meals"], min_value=0)
    total_nights = st.number_input("Nombre total de nuits", value=data["total_nights"], min_value=0)

spending_rates = calculate_guest_spending_rates(
    total_revenue, num_guests, accommodation_revenue, food_revenue, 
    other_revenue, num_meals, total_nights
)

st.subheader("📊 Resultats des depenses moyennes")

spending_df = pd.DataFrame([
    {"Indicateur": k, "Valeur (JOD)": v if "JOD" in k else v}
    for k, v in spending_rates.items()
])
st.dataframe(spending_df, use_container_width=True)

# Graphique des repartitions (Figure 2 du document)
st.subheader("🏗️ Structure des depenses par service")

composition = {
    "Hebergement": accommodation_revenue,
    "Repas et boissons": food_revenue,
    "Autres services": other_revenue
}

fig = px.pie(
    values=list(composition.values()),
    names=list(composition.keys()),
    title="Repartition du revenu par service",
    color_discrete_sequence=px.colors.sequential.Blues_r
)
st.plotly_chart(fig, use_container_width=True)

# Donnees mensuelles de l'etude (Table 6)
st.subheader("📅 Donnees mensuelles de reference - Hotel Al Zaitonia")
monthly_spending = {
    "Mois": ["Jan", "Fev", "Mar", "Avr", "Mai", "Juin", "Juil", "Aou", "Sep", "Oct", "Nov", "Dec"],
    "Depense moyenne (JOD)": [69.2, 93.75, 95, 105, 93.75, 123.46, 132.35, 153.4, 150, 90, 106.15, 93.75]
}
monthly_df = pd.DataFrame(monthly_spending)

fig_monthly = px.line(
    monthly_df,
    x="Mois",
    y="Depense moyenne (JOD)",
    title="Depense moyenne mensuelle par client",
    markers=True
)
fig_monthly.add_hline(y=monthly_df["Depense moyenne (JOD)"].mean(), 
                      line_dash="dash", 
                      annotation_text=f"Moyenne: {monthly_df['Depense moyenne (JOD)'].mean():.1f} JOD")
st.plotly_chart(fig_monthly, use_container_width=True)

st.caption("Source: Table 6 du document - Hotel Al Zaitonia 2003")


# ============================================================================
# SECTION 4: RENTABILITE PAR ACTIVITE
# ============================================================================

elif section == "4. Rentabilite par Activite":
st.header("📊 Rentabilite par Activite Hoteliere")
st.markdown("""
**Formules selon le document:**

- **Rentabilite hebergement** = (Revenu hebergement - Couts hebergement) / Couts hebergement * 100%
- **Rentabilite repas et boissons** = (Revenu repas - Couts repas) / Couts repas * 100%
- **Rentabilite autres services** = (Revenu autres - Couts autres) / Couts autres * 100%
""")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Hebergement")
    acc_rev = st.number_input("Revenu hebergement (JOD)", value=data["accommodation_revenue"], min_value=0.0)
    acc_cost = st.number_input("Couts hebergement (JOD)", value=data["accommodation_costs"], min_value=0.0)
    
    st.subheader("Repas et boissons")
    food_rev = st.number_input("Revenu repas (JOD)", value=data["food_revenue"], min_value=0.0)
    food_cost = st.number_input("Couts repas (JOD)", value=data["food_costs"], min_value=0.0)
    
with col2:
    st.subheader("Autres services")
    other_rev = st.number_input("Revenu autres services (JOD)", value=data["other_revenue"], min_value=0.0)
    other_cost = st.number_input("Couts autres services (JOD)", value=data["other_costs"], min_value=0.0)

profitability = calculate_activity_profitability(
    acc_rev, acc_cost, food_rev, food_cost, other_rev, other_cost
)

st.subheader("📈 Resultats de rentabilite")

col_prof1, col_prof2, col_prof3 = st.columns(3)
col_prof1.metric("Rentabilite Hebergement", f"{profitability['Rentabilite hebergement (%)']:.1f}%")
col_prof2.metric("Rentabilite Repas", f"{profitability['Rentabilite repas et boissons (%)']:.1f}%")
col_prof3.metric("Rentabilite Autres services", f"{profitability['Rentabilite autres services (%)']:.1f}%")

# Graphique
profit_rates = {
    "Hebergement": profitability['Rentabilite hebergement (%)'],
    "Repas et boissons": profitability['Rentabilite repas et boissons (%)'],
    "Autres services": profitability['Rentabilite autres services (%)']
}

fig = px.bar(
    x=list(profit_rates.keys()),
    y=list(profit_rates.values()),
    title="Taux de rentabilite par activite",
    labels={"x": "Activite", "y": "Taux de rentabilite (%)"},
    color=list(profit_rates.values()),
    color_continuous_scale="Greens"
)
st.plotly_chart(fig, use_container_width=True)

# Donnees mensuelles de l'etude (Table 7)
st.subheader("📅 Rentabilite mensuelle par activite - Hotel Al Zaitonia")
monthly_profit = {
    "Mois": ["Jan", "Fev", "Mar", "Avr", "Mai", "Juin", "Juil", "Aou", "Sep", "Oct", "Nov", "Dec"],
    "Hebergement (%)": [49.84, 56.00, 67.90, 64.29, 56.00, 60.75, 68.00, 58.67, 60.00, 60.00, 70.65, 64.00],
    "Repas (%)": [28.49, 24.80, 23.69, 21.43, 24.80, 24.68, 25.20, 34.22, 35.00, 16.00, 22.28, 24.80],
    "Autres (%)": [22, 19, 8, 14, 19, 15, 7, 7, 5, 24, 7, 11]
}
monthly_df = pd.DataFrame(monthly_profit)

fig_monthly = px.line(
    monthly_df,
    x="Mois",
    y=["Hebergement (%)", "Repas (%)", "Autres (%)"],
    title="Evolution mensuelle de la rentabilite par activite",
    markers=True
)
st.plotly_chart(fig_monthly, use_container_width=True)

st.caption("Source: Table 7 du document - Hotel Al Zaitonia 2003")


# ============================================================================
# SECTION 5: TAUX DE COUTS D'EXPLOITATION
# ============================================================================

elif section == "5. Taux de Couts d'Exploitation":
st.header("📉 Taux de Couts d'Exploitation")
st.markdown("""
**Couts directs (Formules):**
- Taux couts directs hebergement = Couts hebergement / Revenu hebergement * 100%
- Taux couts directs repas = Couts repas / Revenu repas * 100%
- Taux couts directs autres = Couts autres / Revenu autres * 100%

**Couts indirects (Formules):**
- Taux de promotion = Couts promotion / Revenu total * 100%
- Taux d'energie = Couts energie / Revenu total * 100%
- Taux de maintenance = Couts maintenance / Revenu total * 100%
- Taux administratif = Couts administratifs / Revenu total * 100%
""")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Couts directs")
    acc_rev = st.number_input("Revenu hebergement (JOD)", value=data["accommodation_revenue"], min_value=0.0, key="dir_acc_rev")
    acc_cost = st.number_input("Couts hebergement (JOD)", value=data["accommodation_costs"], min_value=0.0, key="dir_acc_cost")
    food_rev = st.number_input("Revenu repas (JOD)", value=data["food_revenue"], min_value=0.0, key="dir_food_rev")
    food_cost = st.number_input("Couts repas (JOD)", value=data["food_costs"], min_value=0.0, key="dir_food_cost")
    other_rev = st.number_input("Revenu autres (JOD)", value=data["other_revenue"], min_value=0.0, key="dir_other_rev")
    other_cost = st.number_input("Couts autres (JOD)", value=data["other_costs"], min_value=0.0, key="dir_other_cost")
    
with col2:
    st.subheader("Couts indirects")
    total_revenue = st.number_input("Revenu total (JOD)", value=data["total_revenue"], min_value=0.0, key="ind_total")
    sales_promo = st.number_input("Couts de promotion (JOD)", value=data["sales_promotion_costs"], min_value=0.0)
    energy_costs = st.number_input("Couts energie (JOD)", value=data["energy_costs"], min_value=0.0)
    maintenance_costs = st.number_input("Couts maintenance (JOD)", value=data["maintenance_costs"], min_value=0.0)
    admin_costs = st.number_input("Couts administratifs (JOD)", value=data["admin_costs"], min_value=0.0)

cost_rates = calculate_cost_rates(
    acc_cost, acc_rev, food_cost, food_rev, other_cost, other_rev,
    sales_promo, total_revenue, energy_costs, maintenance_costs, admin_costs
)

st.subheader("📊 Resultats des taux de couts")

cost_df = pd.DataFrame([
    {"Type de cout": k, "Taux (%)": f"{v:.2f}%"}
    for k, v in cost_rates.items()
])
st.dataframe(cost_df, use_container_width=True)

# Graphique
fig = make_subplots(rows=2, cols=1, subplot_titles=("Couts directs", "Couts indirects"))

direct_costs = {k: v for k, v in cost_rates.items() if "Couts directs" in k}
indirect_costs = {k: v for k, v in cost_rates.items() if "Couts directs" not in k}

fig.add_trace(
    go.Bar(x=list(direct_costs.keys()), y=list(direct_costs.values()), name="Couts directs", marker_color="coral"),
    row=1, col=1
)
fig.add_trace(
    go.Bar(x=list(indirect_costs.keys()), y=list(indirect_costs.values()), name="Couts indirects", marker_color="lightblue"),
    row=2, col=1
)

fig.update_layout(height=600, showlegend=False, title_text="Analyse des couts d'exploitation")
fig.update_xaxes(tickangle=45)
st.plotly_chart(fig, use_container_width=True)

# Donnees mensuelles (Table 9, 11)
st.subheader("📅 Evolution mensuelle des couts - Hotel Al Zaitonia")

monthly_direct = {
    "Mois": ["Jan", "Fev", "Mar", "Avr", "Mai", "Juin", "Juil", "Aou", "Sep", "Oct", "Nov", "Dec"],
    "Hebergement (%)": [43.48, 28.57, 23.26, 22.22, 28.57, 20.00, 16.67, 16.67, 16.67, 25.00, 20.00, 22.22],
    "Repas (%)": [37.75, 76.92, 33.33, 33.33, 32.26, 24.62, 22.49, 14.29, 14.29, 46.88, 31.71, 47.62],
    "Autres (%)": [40.00, 33.33, 75.00, 40.00, 33.33, 26.92, 66.67, 55.00, 64.62, 66.67, 80.00, 57.14]
}
monthly_df = pd.DataFrame(monthly_direct)

fig_monthly = px.line(
    monthly_df,
    x="Mois",
    y=["Hebergement (%)", "Repas (%)", "Autres (%)"],
    title="Taux de couts directs mensuels par activite",
    markers=True
)
st.plotly_chart(fig_monthly, use_container_width=True)

st.caption("Source: Table 9 (couts directs) et Table 11 (couts indirects) du document")


# ============================================================================
# SECTION 6: COMPARAISON AVEC LES NORMES SECTORIELLES
# ============================================================================

elif section == "6. Comparaison avec les Normes Sectorielles":
st.header("🏆 Comparaison avec les Normes Sectorielles Jordaniennes")
st.markdown("""
**Normes standards pour les hotels en Jordanie (Source: Ministere du Tourisme / Table 1 du document)**

Ces normes permettent d'identifier les ecarts et les axes d'amelioration.
""")

# Tableau des normes
st.subheader("📋 Normes standards pour l'hotellerie jordanienne")

standards_df = pd.DataFrame([
    {"Categorie": "Revenus - Hebergement", "Min": "45%", "Max": "50%"},
    {"Categorie": "Revenus - Repas et boissons", "Min": "35%", "Max": "40%"},
    {"Categorie": "Revenus - Autres services", "Min": "5%", "Max": "10%"},
    {"Categorie": "Couts directs - Hebergement", "Min": "15%", "Max": "25%"},
    {"Categorie": "Couts directs - Repas", "Min": "65%", "Max": "80%"},
    {"Categorie": "Couts directs - Autres", "Min": "40%", "Max": "70%"},
    {"Categorie": "Couts indirects - Administratifs", "Min": "5%", "Max": "10%"},
    {"Categorie": "Couts indirects - Promotion", "Min": "5%", "Max": "10%"},
    {"Categorie": "Couts indirects - Energie", "Min": "4%", "Max": "10%"},
    {"Categorie": "Couts indirects - Maintenance", "Min": "3%", "Max": "5%"}
], index=range(1, 11))
st.dataframe(standards_df, use_container_width=True)

# Donnees de l'hotel Al Zaitonia pour comparaison
st.subheader("📊 Comparaison avec les performances de l'Hotel Al Zaitonia")

# Calcul des ratios de l'hotel
total_rev = data["total_revenue"]
hotel_revenue_pct = {
    "Hebergement": (data["accommodation_revenue"] / total_rev) * 100 if total_rev > 0 else 0,
    "Repas et boissons": (data["food_revenue"] / total_rev) * 100 if total_rev > 0 else 0,
    "Autres services": (data["other_revenue"] / total_rev) * 100 if total_rev > 0 else 0
}

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Structure des revenus**")
    revenue_df = pd.DataFrame([
        {"Source": k, "Hotel Al Zaitonia (%)": round(v, 2), 
         "Norme min": INDUSTRY_STANDARDS["Revenue Elements"][k]["min"], 
         "Norme max": INDUSTRY_STANDARDS["Revenue Elements"][k]["max"], 
         "Conforme": "✅" if INDUSTRY_STANDARDS["Revenue Elements"][k]["min"] <= v <= INDUSTRY_STANDARDS["Revenue Elements"][k]["max"] else "⚠️"}
        for k, v in hotel_revenue_pct.items()
    ])
    st.dataframe(revenue_df, use_container_width=True)
    
with col2:
    st.markdown("**Couts indirects**")
    hotel_indirect = {
        "Administratifs et generaux": (data["admin_costs"] / total_rev) * 100 if total_rev > 0 else 0,
        "Promotion": (data["sales_promotion_costs"] / total_rev) * 100 if total_rev > 0 else 0,
        "Energie et eclairage": (data["energy_costs"] / total_rev) * 100 if total_rev > 0 else 0,
        "Maintenance et reparation": (data["maintenance_costs"] / total_rev) * 100 if total_rev > 0 else 0
    }
    
    indirect_df = pd.DataFrame([
        {"Source": k, "Hotel Al Zaitonia (%)": round(v, 2), 
         "Norme min": INDUSTRY_STANDARDS["Indirect Costs"][k]["min"],
         "Norme max": INDUSTRY_STANDARDS["Indirect Costs"][k]["max"], 
         "Conforme": "✅" if INDUSTRY_STANDARDS["Indirect Costs"][k]["min"] <= v <= INDUSTRY_STANDARDS["Indirect Costs"][k]["max"] else "⚠️"}
        for k, v in hotel_indirect.items()
    ])
    st.dataframe(indirect_df, use_container_width=True)

# Graphique de comparaison
st.subheader("📈 Ecarts par rapport aux normes")

fig = make_subplots(rows=2, cols=2, subplot_titles=("Revenus", "Couts indirects"))

# Revenus
rev_names = list(hotel_revenue_pct.keys())
rev_hotel = list(hotel_revenue_pct.values())
rev_min = [INDUSTRY_STANDARDS["Revenue Elements"][k]["min"] for k in rev_names]
rev_max = [INDUSTRY_STANDARDS["Revenue Elements"][k]["max"] for k in rev_names]

fig.add_trace(go.Bar(name="Hotel Al Zaitonia", x=rev_names, y=rev_hotel, marker_color="blue"), row=1, col=1)
fig.add_trace(go.Bar(name="Norme min", x=rev_names, y=rev_min, marker_color="lightgray"), row=1, col=1)
fig.add_trace(go.Bar(name="Norme max", x=rev_names, y=rev_max, marker_color="darkgray"), row=1, col=1)

# Couts indirects
ind_names = list(hotel_indirect.keys())
ind_hotel = list(hotel_indirect.values())
ind_min = [INDUSTRY_STANDARDS["Indirect Costs"][k]["min"] for k in ind_names]
ind_max = [INDUSTRY_STANDARDS["Indirect Costs"][k]["max"] for k in ind_names]

fig.add_trace(go.Bar(name="Hotel Al Zaitonia", x=ind_names, y=ind_hotel, marker_color="coral"), row=2, col=1)
fig.add_trace(go.Bar(name="Norme min", x=ind_names, y=ind_min, marker_color="lightgray"), row=2, col=1)
fig.add_trace(go.Bar(name="Norme max", x=ind_names, y=ind_max, marker_color="darkgray"), row=2, col=1)

fig.update_layout(height=600, showlegend=True, barmode='group')
st.plotly_chart(fig, use_container_width=True)

st.info("""
**Interpretation des ecarts selon l'etude:**
- Les revenus d'hebergement sont superieurs a la norme (bon indicateur)
- Les couts administratifs sont tres eleves par rapport a la norme
- Les couts de promotion sont trop faibles
- Les couts d'energie et maintenance sont inferieurs aux normes
""")


# ============================================================================
# SECTION 7: RAPPORT COMPLET
# ============================================================================

else:  # Rapport complet
st.header("📑 Rapport d'Analyse Financiere Complet")
st.markdown("""
**Methodologie:** Analyse financiere appliquee au secteur hotelier selon Jawabreh et al. (2017)

**Cas d'etude:** Hotel Al Zaitonia - 3 etoiles, Aqaba, Jordanie
""")

# Execution de toutes les analyses
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
st.subheader("🎯 Indicateurs Cles de Performance (KPI)")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Benefice net annuel", f"{base_net_income:,.0f} JOD")
col2.metric("Taux d'occupation", f"{occupancy['Taux d occupation chambres']:.1f}%")
col3.metric("Depense moyenne/client", f"{spending['Depense moyenne generale (JOD)']:.1f} JOD")
col4.metric("Rentabilite hebergement", f"{profitability['Rentabilite hebergement (%)']:.1f}%")

# Classement des facteurs de sensibilite
st.subheader("🔍 Classement des facteurs controlants (Multiplicateurs de profit)")
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
    "Taux d'occupation": occupancy['Taux d occupation chambres'],
    "Depense/client": spending['Depense moyenne generale (JOD)'] / 200 * 100,
    "Rentabilite hebergement": profitability['Rentabilite hebergement (%)'],
    "Rentabilite repas": profitability['Rentabilite repas et boissons (%)'],
    "Conformite couts hebergement": max(0, 100 - costs['Couts directs - Hebergement (%)'])
}

fig = go.Figure(data=go.Scatterpolar(
    r=list(radar_data.values()),
    theta=list(radar_data.keys()),
    fill='toself',
    marker_color='blue'
))
fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False)
st.plotly_chart(fig, use_container_width=True)

# Resume et recommandations
st.subheader("📝 Resume et Recommandations (selon l'etude)")

st.markdown("""
**Principaux resultats:**

1. **Facteurs controlants des revenus:** Le pouvoir de depense moyen par client est le facteur le plus influent sur la rentabilite, suivi du nombre de clients

2. **Rentabilite par activite:** L'hebergement represente l'activite la plus rentable

3. **Structure des couts:** Les couts variables et fixes affectent directement la rentabilite et necessitent une planification continue

**Recommandations de l'auteur:**
- Accorder plus d'attention aux facteurs lies aux revenus (pouvoir de depense des clients)
- Augmenter les budgets de promotion (actuellement inferieurs aux normes sectorielles)
- Mettre en place un systeme de suivi mensuel des ecarts par rapport aux normes
- Developper une identite distinctive pour le secteur hotelier jordanien
""")

# Tableau recapitulatif des formules
with st.expander("📚 Voir toutes les formules utilisees"):
    st.markdown("""
    ### Formules d'Analyse Financiere Hoteliere
    
    **Analyse de sensibilite du profit:**
    - Multiplicateur de profit = (Δ% Benefice net) / (Δ% Facteur controlant)
    
    **Taux d'occupation:**
    - Taux occupation chambres = (Chambres occupees / Chambres disponibles) * 100%
    - Taux occupation lits = (Lits occupes / Lits disponibles) * 100%
    - Taux occupation restaurant = (Repas servis / Capacite sieges) * 100%
    
    **Taux de depense des clients:**
    - Depense moyenne generale = Revenu total / Nombre de clients
    - Depense moyenne hebergement = Revenu hebergement / Nombre de clients
    - Duree moyenne sejour = Nombre total de nuits / Nombre de clients
    
    **Taux de rentabilite:**
    - Rentabilite activite = (Revenu - Cout) / Cout * 100%
    
    **Taux de couts:**
    - Taux cout direct = Cout activite / Revenu activite * 100%
    - Taux cout indirect = Cout indirect / Revenu total * 100%
    """)

st.markdown("---")
st.caption("🏨 Dashboard d'Analyse Financiere Hoteliere | Base sur Jawabreh et al. (2017) - International Journal of Economics and Financial Issues")
