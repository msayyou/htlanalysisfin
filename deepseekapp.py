
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
        "Nouvelle valeur": round(res["new_value"], 2),
        "Nouveau bénéfice net (JOD)": f"{res['net_income']:,.2f}",
        "Variation du bénéfice (%)": f"{res['change_ratio']*100:.2f}%",
        "Multiplicateur de profit": f"{res['multiplier']:.3f}"
    }
    for factor, res in results.items()
])

st.dataframe(df_results, use_container_width=True)

# Classement des facteurs
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
- Le pouvoir de dépense du client est le facteur le plus influent
- L'hôtel est qualifié de 'sensible aux revenus'
""")


# ============================================================================
# SECTION 3: TAUX D'OCCUPATION
# ============================================================================

elif section == "3. Taux d'Occupation":
st.header("🏠 Taux d'Occupation")
st.markdown("""
**Formules selon le document:**

- **Taux d'occupation des chambres** = (Nombre de chambres occupées / Nombre de chambres disponibles) × 100%
- **Taux d'occupation des lits** = (Nombre de lits occupés / Nombre de lits disponibles) × 100%
- **Taux d'occupation des suites** = (Nombre de suites occupées / Nombre de suites disponibles) × 100%
- **Taux d'occupation du restaurant** = (Nombre de repas servis / Capacité en sièges) × 100%
""")

available_rooms = st.number_input("Chambres disponibles", value=data["available_rooms"], min_value=1)
occupied_rooms = st.number_input("Chambres occupées", value=data["occupied_rooms"], min_value=0)
available_beds = st.number_input("Lits disponibles", value=800, min_value=1)
occupied_beds = st.number_input("Lits occupés", value=430, min_value=0)
available_suites = st.number_input("Suites disponibles", value=100, min_value=1)
occupied_suites = st.number_input("Suites occupées", value=54, min_value=0)
seats_capacity = st.number_input("Capacité restaurant (sièges)", value=data["seats_available"], min_value=1)
meals_served = st.number_input("Repas servis", value=data["num_meals"], min_value=0)

occupancy_rate = (occupied_rooms / available_rooms) * 100 if available_rooms > 0 else 0
bed_rate = (occupied_beds / available_beds) * 100 if available_beds > 0 else 0
suite_rate = (occupied_suites / available_suites) * 100 if available_suites > 0 else 0
restaurant_rate = (meals_served / seats_capacity) * 100 if seats_capacity > 0 else 0

st.subheader("📊 Résultats des taux d'occupation")

cols = st.columns(4)
cols[0].metric("Taux d'occupation chambres", f"{occupancy_rate:.1f}%")
cols[1].metric("Taux d'occupation lits", f"{bed_rate:.1f}%")
cols[2].metric("Taux d'occupation suites", f"{suite_rate:.1f}%")
cols[3].metric("Taux d'occupation restaurant", f"{restaurant_rate:.1f}%")

# Graphique
fig = px.bar(
    x=["Chambres", "Lits", "Suites", "Restaurant"],
    y=[occupancy_rate, bed_rate, suite_rate, restaurant_rate],
    title="Taux d'occupation",
    labels={"x": "Indicateur", "y": "Taux (%)"},
    color=[occupancy_rate, bed_rate, suite_rate, restaurant_rate],
    color_continuous_scale="Blues"
)
st.plotly_chart(fig, use_container_width=True)

# Données mensuelles de l'étude
st.subheader("📅 Évolution mensuelle - Hôtel Al Zaitonia")
monthly_data = {
    "Mois": ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Aoû", "Sep", "Oct", "Nov", "Déc"],
    "Taux d'occupation (%)": [42, 33, 47, 50, 55, 67, 75, 70, 58, 50, 38, 50]
}
monthly_df = pd.DataFrame(monthly_data)

fig_monthly = px.line(
    monthly_df, 
    x="Mois", 
    y="Taux d'occupation (%)",
    title="Évolution mensuelle du taux d'occupation",
    markers=True
)
fig_monthly.add_hline(y=monthly_df["Taux d'occupation (%)"].mean(), line_dash="dash", 
                      annotation_text=f"Moyenne: {monthly_df['Taux d occupation (%)'].mean():.1f}%")
st.plotly_chart(fig_monthly, use_container_width=True)

st.caption("Source: Table 5 du document - Hôtel Al Zaitonia")


# ============================================================================
# SECTION 4: DÉPARTEMENT HÉBERGEMENT
# ============================================================================

elif section == "4. Département Hébergement":
st.header("🛏️ Département Hébergement - KPIs Spécifiques")
st.markdown("""
**KPIs du département Hébergement selon Fáilte Ireland**

Les trois KPIs principaux à suivre sont: **ADR** (Average Daily Rate), **Occupancy** et **RevPAR** (Revenue per Available Room).
""")

rooms_kpis = calculate_rooms_kpis(data)

# KPIs principaux
st.subheader("🎯 KPIs Principaux")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Occupancy", f"{rooms_kpis['Occupancy (%)']:.1f}%")
with col2:
    st.metric("ADR", f"{rooms_kpis['ADR (€)']:.2f} €")
with col3:
    st.metric("RevPAR", f"{rooms_kpis['RevPAR (€)']:.2f} €")

st.info(f"Vérification: RevPAR = Occupancy × ADR = {rooms_kpis['Occupancy (%)']:.1f}% × {rooms_kpis['ADR (€)']:.2f}€ = {rooms_kpis['RevPAR (Occupancy x ADR)']:.2f}€")

# KPIs de profitabilité et coûts
st.subheader("📊 Profitabilité et Coûts")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Profit Dept Hébergement", f"{rooms_kpis['Total Rooms Dept Profit (%)']:.1f}%")
with col2:
    st.metric("Commissions", f"{rooms_kpis['Commissions (%)']:.1f}%")
with col3:
    st.metric("Payroll Cost", f"{rooms_kpis['Rooms Payroll Cost (%)']:.1f}%")
with col4:
    st.metric("Cost per occupied Room", f"{rooms_kpis['Cost per occupied Room (€)']:.2f} €")

# Graphiques
st.subheader("📈 Analyse détaillée")

fig = make_subplots(rows=1, cols=2, subplot_titles=("Structure des coûts hébergement", "Performance mensuelle"))

# Structure des coûts
cost_structure = {
    "Payroll": rooms_kpis['Rooms Payroll Cost (%)'],
    "Commissions": rooms_kpis['Commissions (%)'],
    "Autres coûts": rooms_kpis['Other Rooms Dept Cost (%)']
}
fig.add_trace(
    go.Pie(labels=list(cost_structure.keys()), values=list(cost_structure.values()), hole=0.3),
    row=1, col=1
)

# Performance mensuelle simulée
months = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Aoû", "Sep", "Oct", "Nov", "Déc"]
revpar_values = [45, 38, 52, 58, 65, 80, 92, 85, 68, 58, 42, 55]

fig.add_trace(
    go.Scatter(x=months, y=revpar_values, mode='lines+markers', name='RevPAR', line=dict(color='blue')),
    row=1, col=2
)
fig.add_hline(y=sum(revpar_values)/len(revpar_values), line_dash="dash", 
              annotation_text=f"Moyenne: {sum(revpar_values)/len(revpar_values):.0f}€", row=1, col=2)

fig.update_layout(height=500, showlegend=False)
st.plotly_chart(fig, use_container_width=True)

# Tableau récapitulatif
st.subheader("📋 Détail des KPIs Hébergement")
rooms_df = pd.DataFrame([
    {"KPI": k, "Valeur": f"{v:.2f}" + ("%" if "%" in k else " €" if "€" in k else "") 
     for k, v in rooms_kpis.items()}
]).T.reset_index()
rooms_df.columns = ["KPI", "Valeur"]
st.dataframe(rooms_df, use_container_width=True, hide_index=True)


# ============================================================================
# SECTION 5: DÉPARTEMENT RESTAURATION (F&B)
# ============================================================================

elif section == "5. Département Restauration (F&B)":
st.header("🍽️ Département Restauration (F&B) - KPIs Spécifiques")
st.markdown("""
**KPIs du département Restauration selon Fáilte Ireland**

Les KPIs les plus courants sont les marges brutes et la dépense moyenne par client.
""")

fandb_kpis = calculate_fandb_kpis(data)

# KPIs principaux
st.subheader("🎯 KPIs de Revenus")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("F&B Revenue POR", f"{fandb_kpis['F&B Revenue POR (€)']:.2f} €")
with col2:
    st.metric("F&B Revenue PAR", f"{fandb_kpis['F&B Revenue PAR (€)']:.2f} €")
with col3:
    st.metric("Average Spend per Cover", f"{fandb_kpis['Average Spend per Cover (€)']:.2f} €")
with col4:
    st.metric("Breakfast sit down rate", f"{fandb_kpis['Breakfast sit down rate (%)']:.1f}%")

# Marges
st.subheader("📈 Marges Brutes")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Gross Food Margin", f"{fandb_kpis['Gross Food Margin (%)']:.1f}%")
with col2:
    st.metric("Gross Beverage Margin", f"{fandb_kpis['Gross Beverage Margin (%)']:.1f}%")
with col3:
    st.metric("Total F&B Dept Profit", f"{fandb_kpis['Total F&B Dept Profit (%)']:.1f}%")

# Efficacité opérationnelle
st.subheader("⚙️ KPIs d'Efficacité Opérationnelle")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Table Turn Rate", f"{fandb_kpis['Table Turn Rate']:.1f} tours")
    st.caption("Nombre de services par table")
with col2:
    st.metric("Revenue per wait staff", f"{fandb_kpis['F&B Revenue per wait staff (€)']:.0f} €")
    st.caption("Productivité du personnel")
with col3:
    st.metric("Revenue per available seat/hour", f"{fandb_kpis['Revenue per available seat per hour (€)']:.2f} €")
    st.caption("Rendement par siège")

# Graphique des marges
st.subheader("📊 Analyse des marges F&B")

fig = make_subplots(rows=1, cols=2, subplot_titles=("Structure du coût des ventes", "Performance par service"))

# Coût des ventes
cogs_structure = {
    "Food Cost %": fandb_kpis['Food Cost of Sales (%)'],
    "Beverage Cost %": fandb_kpis['Beverage Cost of Sales (%)'],
    "Marge brute": 100 - fandb_kpis['Total F&B Cost of Sales (%)']
}
fig.add_trace(
    go.Bar(x=list(cogs_structure.keys()), y=list(cogs_structure.values()), 
           marker_color=["#FF6B6B", "#4ECDC4", "#45B7D1"]),
    row=1, col=1
)

# Performance par service
service_performance = {
    "Petit-déjeuner": 18,
    "Déjeuner": 22,
    "Dîner": 35
}
fig.add_trace(
    go.Bar(x=list(service_performance.keys()), y=list(service_performance.values()),
           marker_color="#F18F01"),
    row=1, col=2
)

fig.update_layout(height=500, showlegend=False)
st.plotly_chart(fig, use_container_width=True)

# Tableau complet
st.subheader("📋 Détail des KPIs Restauration")
fandb_df = pd.DataFrame([
    {"KPI": k, "Valeur": f"{v:.2f}" + ("%" if "%" in k else " €" if "€" in k else "") 
     for k, v in fandb_kpis.items()}
]).T.reset_index()
fandb_df.columns = ["KPI", "Valeur"]
st.dataframe(fandb_df, use_container_width=True, hide_index=True)


# ============================================================================
# SECTION 6: DÉPARTEMENT SPA & LOISIRS
# ============================================================================

elif section == "6. Département Spa & Loisirs":
st.header("💆 Département Spa & Loisirs - KPIs Spécifiques")
st.markdown("""
**KPIs du département Spa et Centre de Loisirs selon Fáilte Ireland**

Ces indicateurs permettent de mesurer la performance des activités annexes de l'hôtel.
""")

spa_kpis = calculate_spa_kpis(data)

# KPIs Spa
st.subheader("🧖 KPIs du Spa")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Treatment Room Utilisation", f"{spa_kpis['Treatment Room Utilisation (TRU) (%)']:.1f}%")
with col2:
    st.metric("Average Treatment Rate", f"{spa_kpis['Average Treatment Rate (ATR) (€)']:.2f} €")
with col3:
    st.metric("Revenue Per Available Treatment Room", f"{spa_kpis['Revenue Per Available Treatment Room (€)']:.2f} €")
with col4:
    st.metric("Average Spend per Spa Customer", f"{spa_kpis['Average Spend per Spa Customer (€)']:.2f} €")

# KPIs de capture clientèle
st.subheader("📊 KPIs de Capture Clientèle")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Guest Capture Rate", f"{spa_kpis['Guest Capture Rate (%)']:.1f}%")
    st.caption("% des clients hôtel utilisant le spa")
with col2:
    st.metric("Retail Capture Rate", f"{spa_kpis['Retail Capture Rate (%)']:.1f}%")
    st.caption("% des clients spa achetant en boutique")
with col3:
    st.metric("Spa Revenue POR", f"{spa_kpis['Spa Revenue POR (€)']:.2f} €")
    st.caption("Revenu spa par chambre occupée")

# KPIs Centre de Loisirs
st.subheader("🏋️ KPIs du Centre de Loisirs")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Revenue per Member", f"{spa_kpis['Revenue per Member (€)']:.2f} €")
with col2:
    st.metric("Revenue per square metre", f"{spa_kpis['Revenue per square metre (€)']:.2f} €")
with col3:
    st.metric("Average revenue per class", f"{spa_kpis['Average revenue per class (€)']:.2f} €")

# KPIs de coûts
st.subheader("📉 KPIs de Coûts - Spa & Loisirs")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Cost of Sales", f"{spa_kpis['Cost of Sales (%)']:.1f}%")
with col2:
    st.metric("Payroll Cost", f"{spa_kpis['Spa and Leisure Payroll Cost (%)']:.1f}%")
with col3:
    st.metric("Therapist Utilisation", f"{spa_kpis['Therapist Utilisation (%)']:.1f}%")
with col4:
    st.metric("Total Dept Cost", f"{spa_kpis['Total Spa/Leisure Dept Cost (%)']:.1f}%")

# Graphiques
st.subheader("📈 Visualisation des KPIs Spa")

fig = make_subplots(rows=1, cols=2, subplot_titles=("Utilisation et rendement", "Structure des coûts"))

# Utilisation et rendement
utilisation_data = {
    "TRU": spa_kpis['Treatment Room Utilisation (TRU) (%)'],
    "ATR": spa_kpis['Average Treatment Rate (ATR) (€)'] / 10,
    "RevPATR": spa_kpis['Revenue Per Available Treatment Room (€)'] / 10
}
fig.add_trace(
    go.Bar(x=list(utilisation_data.keys()), y=list(utilisation_data.values()),
           marker_color=["#2E86AB", "#A23B72", "#F18F01"]),
    row=1, col=1
)

# Structure des coûts
cost_structure = {
    "Cost of Sales": spa_kpis['Cost of Sales (%)'],
    "Payroll": spa_kpis['Spa and Leisure Payroll Cost (%)'],
    "Autres": spa_kpis['Other Spa/Leisure Dept Cost (%)']
}
fig.add_trace(
    go.Pie(labels=list(cost_structure.keys()), values=list(cost_structure.values()), hole=0.3),
    row=1, col=2
)

fig.update_layout(height=500, showlegend=False)
st.plotly_chart(fig, use_container_width=True)

# Tableau complet
st.subheader("📋 Détail des KPIs Spa & Loisirs")
spa_df = pd.DataFrame([
    {"KPI": k, "Valeur": f"{v:.2f}" + ("%" if "%" in k else " €" if "€" in k else "") 
     for k, v in spa_kpis.items()}
]).T.reset_index()
spa_df.columns = ["KPI", "Valeur"]
st.dataframe(spa_df, use_container_width=True, hide_index=True)


# ============================================================================
# SECTION 7: DÉPENSES DES CLIENTS
# ============================================================================

elif section == "7. Dépenses des Clients":
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

total_revenue = st.number_input("Revenu total (JOD)", value=data["total_revenue"], min_value=0.0)
accommodation_revenue = st.number_input("Revenu hébergement (JOD)", value=data["accommodation_revenue"], min_value=0.0)
food_revenue = st.number_input("Revenu repas et boissons (JOD)", value=data["food_revenue"], min_value=0.0)
other_revenue = st.number_input("Revenu autres services (JOD)", value=data["other_revenue"], min_value=0.0)
num_guests = st.number_input("Nombre de clients", value=data["num_guests"], min_value=1)
num_meals = st.number_input("Nombre de repas servis", value=data["num_meals"], min_value=0)
total_nights = st.number_input("Nombre total de nuits", value=data["total_nights"], min_value=0)

avg_spending_general = total_revenue / num_guests if num_guests > 0 else 0
avg_spending_accommodation = accommodation_revenue / num_guests if num_guests > 0 else 0
avg_spending_food = food_revenue / num_guests if num_guests > 0 else 0
avg_spending_other = other_revenue / num_guests if num_guests > 0 else 0
avg_spending_per_meal = food_revenue / num_meals if num_meals > 0 else 0
avg_stay_duration = total_nights / num_guests if num_guests > 0 else 0

st.subheader("📊 Résultats des dépenses moyennes")

col1, col2, col3 = st.columns(3)
col1.metric("Dépense moyenne générale", f"{avg_spending_general:.2f} JOD")
col2.metric("Dépense moyenne hébergement", f"{avg_spending_accommodation:.2f} JOD")
col3.metric("Dépense moyenne repas", f"{avg_spending_food:.2f} JOD")

col1, col2, col3 = st.columns(3)
col1.metric("Dépense moyenne autres services", f"{avg_spending_other:.2f} JOD")
col2.metric("Dépense moyenne par repas", f"{avg_spending_per_meal:.2f} JOD")
col3.metric("Durée moyenne du séjour", f"{avg_stay_duration:.1f} nuits")

# Graphique
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

# Données mensuelles
st.subheader("📅 Évolution mensuelle de la dépense moyenne")
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
# SECTION 8: RENTABILITÉ PAR ACTIVITÉ
# ============================================================================

elif section == "8. Rentabilité par Activité":
st.header("📊 Rentabilité par Activité Hôtelière")
st.markdown("""
**Formules selon le document:**

- **Rentabilité hébergement** = (Revenu hébergement - Coûts hébergement) / Coûts hébergement × 100%
- **Rentabilité repas et boissons** = (Revenu repas - Coûts repas) / Coûts repas × 100%
- **Rentabilité autres services** = (Revenu autres - Coûts autres) / Coûts autres × 100%
""")

acc_rev = st.number_input("Revenu hébergement (JOD)", value=data["accommodation_revenue"], min_value=0.0)
acc_cost = st.number_input("Coûts hébergement (JOD)", value=data["accommodation_costs"], min_value=0.0)
food_rev = st.number_input("Revenu repas (JOD)", value=data["food_revenue"], min_value=0.0)
food_cost = st.number_input("Coûts repas (JOD)", value=data["food_costs"], min_value=0.0)
other_rev = st.number_input("Revenu autres services (JOD)", value=data["other_revenue"], min_value=0.0)
other_cost = st.number_input("Coûts autres services (JOD)", value=data["other_costs"], min_value=0.0)

acc_profit = acc_rev - acc_cost
food_profit = food_rev - food_cost
other_profit = other_rev - other_cost

acc_rentability = (acc_profit / acc_cost) * 100 if acc_cost > 0 else 0
food_rentability = (food_profit / food_cost) * 100 if food_cost > 0 else 0
other_rentability = (other_profit / other_cost) * 100 if other_cost > 0 else 0

st.subheader("📈 Résultats de rentabilité")

col1, col2, col3 = st.columns(3)
col1.metric("Rentabilité Hébergement", f"{acc_rentability:.1f}%", delta=f"{acc_profit:,.0f} JOD")
col2.metric("Rentabilité Repas", f"{food_rentability:.1f}%", delta=f"{food_profit:,.0f} JOD")
col3.metric("Rentabilité Autres services", f"{other_rentability:.1f}%", delta=f"{other_profit:,.0f} JOD")

# Graphique
profit_rates = {
    "Hébergement": acc_rentability,
    "Repas et boissons": food_rentability,
    "Autres services": other_rentability
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

st.caption("Source: Table 7 du document - Hôtel Al Zaitonia 2003")


# ============================================================================
# SECTION 9: TAUX DE COÛTS D'EXPLOITATION
# ============================================================================

elif section == "9. Taux de Coûts d'Exploitation":
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

total_revenue = st.number_input("Revenu total (JOD)", value=data["total_revenue"], min_value=0.0)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Coûts directs")
    acc_cost = st.number_input("Coûts hébergement (JOD)", value=data["accommodation_costs"], min_value=0.0)
    acc_rev = st.number_input("Revenu hébergement (JOD)", value=data["accommodation_revenue"], min_value=0.0)
    food_cost = st.number_input("Coûts repas (JOD)", value=data["food_costs"], min_value=0.0)
    food_rev = st.number_input("Revenu repas (JOD)", value=data["food_revenue"], min_value=0.0)
    other_cost = st.number_input("Coûts autres (JOD)", value=data["other_costs"], min_value=0.0)
    other_rev = st.number_input("Revenu autres (JOD)", value=data["other_revenue"], min_value=0.0)
    
with col2:
    st.subheader("Coûts indirects")
    sales_promo = st.number_input("Coûts de promotion (JOD)", value=data["sales_promotion_costs"], min_value=0.0)
    energy_costs = st.number_input("Coûts énergie (JOD)", value=data["energy_costs"], min_value=0.0)
    maintenance_costs = st.number_input("Coûts maintenance (JOD)", value=data["maintenance_costs"], min_value=0.0)
    admin_costs = st.number_input("Coûts administratifs (JOD)", value=data["admin_costs"], min_value=0.0)

direct_acc_rate = (acc_cost / acc_rev) * 100 if acc_rev > 0 else 0
direct_food_rate = (food_cost / food_rev) * 100 if food_rev > 0 else 0
direct_other_rate = (other_cost / other_rev) * 100 if other_rev > 0 else 0

promo_rate = (sales_promo / total_revenue) * 100 if total_revenue > 0 else 0
energy_rate = (energy_costs / total_revenue) * 100 if total_revenue > 0 else 0
maintenance_rate = (maintenance_costs / total_revenue) * 100 if total_revenue > 0 else 0
admin_rate = (admin_costs / total_revenue) * 100 if total_revenue > 0 else 0

st.subheader("📊 Résultats des taux de coûts")

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Coûts directs**")
    st.metric("Hébergement", f"{direct_acc_rate:.1f}%")
    st.metric("Repas et boissons", f"{direct_food_rate:.1f}%")
    st.metric("Autres services", f"{direct_other_rate:.1f}%")
with col2:
    st.markdown("**Coûts indirects**")
    st.metric("Administratifs et généraux", f"{admin_rate:.1f}%")
    st.metric("Promotion", f"{promo_rate:.1f}%")
    st.metric("Énergie et éclairage", f"{energy_rate:.1f}%")
    st.metric("Maintenance et réparation", f"{maintenance_rate:.1f}%")

# Graphique
fig = make_subplots(rows=1, cols=2, subplot_titles=("Coûts directs", "Coûts indirects"))

fig.add_trace(
    go.Bar(x=["Hébergement", "Restauration", "Autres"], 
           y=[direct_acc_rate, direct_food_rate, direct_other_rate],
           marker_color="coral"),
    row=1, col=1
)

fig.add_trace(
    go.Bar(x=["Administratifs", "Promotion", "Énergie", "Maintenance"],
           y=[admin_rate, promo_rate, energy_rate, maintenance_rate],
           marker_color="lightblue"),
    row=1, col=2
)

fig.update_layout(height=500, showlegend=False)
st.plotly_chart(fig, use_container_width=True)

st.caption("Source: Table 9 et Table 11 du document")


# ============================================================================
# SECTION 10: COMPARAISON AVEC LES NORMES SECTORIELLES
# ============================================================================

elif section == "10. Comparaison avec les Normes Sectorielles":
st.header("🏆 Comparaison avec les Normes Sectorielles")
st.markdown("""
**Normes standards pour les hôtels en Jordanie (Source: Ministère du Tourisme)**

Ces normes permettent d'identifier les écarts et les axes d'amélioration.
""")

# Tableau des normes
st.subheader("📋 Normes standards pour l'hôtellerie")

standards_df = pd.DataFrame([
    {"Catégorie": "Revenus - Hébergement", "Min": "45%", "Max": "50%", "Hôtel": f"{data['accommodation_revenue']/data['total_revenue']*100:.1f}%" if data['total_revenue'] > 0 else "N/A"},
    {"Catégorie": "Revenus - Repas et boissons", "Min": "35%", "Max": "40%", "Hôtel": f"{data['food_revenue']/data['total_revenue']*100:.1f}%" if data['total_revenue'] > 0 else "N/A"},
    {"Catégorie": "Revenus - Autres services", "Min": "5%", "Max": "10%", "Hôtel": f"{data['other_revenue']/data['total_revenue']*100:.1f}%" if data['total_revenue'] > 0 else "N/A"},
    {"Catégorie": "Coûts directs - Hébergement", "Min": "15%", "Max": "25%", "Hôtel": f"{data['accommodation_costs']/data['accommodation_revenue']*100:.1f}%" if data['accommodation_revenue'] > 0 else "N/A"},
    {"Catégorie": "Coûts directs - Repas", "Min": "65%", "Max": "80%", "Hôtel": f"{data['food_costs']/data['food_revenue']*100:.1f}%" if data['food_revenue'] > 0 else "N/A"},
    {"Catégorie": "Coûts indirects - Administratifs", "Min": "5%", "Max": "10%", "Hôtel": f"{data['admin_costs']/data['total_revenue']*100:.1f}%" if data['total_revenue'] > 0 else "N/A"},
], index=range(1, 7))
st.dataframe(standards_df, use_container_width=True)

# Graphique de comparaison
st.subheader("📈 Analyse des écarts")

categories = ["Hébergement", "Restauration", "Autres services"]
hotel_values = [
    data['accommodation_revenue']/data['total_revenue']*100 if data['total_revenue'] > 0 else 0,
    data['food_revenue']/data['total_revenue']*100 if data['total_revenue'] > 0 else 0,
    data['other_revenue']/data['total_revenue']*100 if data['total_revenue'] > 0 else 0
]
norm_min = [45, 35, 5]
norm_max = [50, 40, 10]

fig = go.Figure()
fig.add_trace(go.Bar(name="Hôtel", x=categories, y=hotel_values, marker_color="blue"))
fig.add_trace(go.Bar(name="Norme min", x=categories, y=norm_min, marker_color="lightgray"))
fig.add_trace(go.Bar(name="Norme max", x=categories, y=norm_max, marker_color="darkgray"))

fig.update_layout(title="Comparaison de la structure des revenus", barmode='group', height=500)
st.plotly_chart(fig, use_container_width=True)

st.info("""
**Interprétation des écarts:**
- Les revenus d'hébergement sont généralement supérieurs à la norme (bon indicateur)
- Les coûts administratifs sont souvent élevés par rapport à la norme
- Les coûts de promotion sont parfois trop faibles
""")


# ============================================================================
# SECTION 11: RAPPORT COMPLET
# ============================================================================

else:  # Rapport complet
st.header("📑 Rapport d'Analyse Financière Complet")
st.markdown("""
**Méthodologie:** Analyse financière appliquée au secteur hôtelier selon Jawabreh et al. (2017)
et enrichie avec les KPIs de Fáilte Ireland.

**Cas d'étude:** Hôtel Al Zaitonia - 3 étoiles, Aqaba, Jordanie
""")

# Calcul de tous les KPIs
kpis = calculate_hotel_kpis(data)
rooms_kpis = calculate_rooms_kpis(data)
fandb_kpis = calculate_fandb_kpis(data)
spa_kpis = calculate_spa_kpis(data)

# Scorecard
st.subheader("🎯 Tableau de bord stratégique")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Occupancy", f"{kpis['Occupancy (%)']:.1f}%")
    st.metric("ADR", f"{kpis['ADR (€)']:.2f}€")
with col2:
    st.metric("RevPAR", f"{kpis['RevPAR (€)']:.2f}€")
    st.metric("TRevPAR", f"{kpis['TRevPAR (€)']:.2f}€")
with col3:
    st.metric("GOP %", f"{kpis['Gross Operating Profit (%)']:.1f}%")
    st.metric("EBITDA %", f"{kpis['EBITDA (%)']:.1f}%")
with col4:
    st.metric("F&B Margin", f"{fandb_kpis['Gross Food Margin (%)']:.1f}%")
    st.metric("Spa TRU", f"{spa_kpis['Treatment Room Utilisation (TRU) (%)']:.1f}%")

# Classement des facteurs de sensibilité
sensitivity_results, base_net_income = calculate_profit_sensitivity(
    data["guests"], data["avg_spending"], data["var_material"], 
    data["var_wages"], data["admin_exp"], data["general_exp"], 0.10
)

st.subheader("🔍 Top 3 des leviers de profitabilité")
ranking = sorted(
    [(factor, res["multiplier"]) for factor, res in sensitivity_results.items()],
    key=lambda x: x[1],
    reverse=True
)[:3]

for i, (factor, multiplier) in enumerate(ranking, 1):
    st.markdown(f"**{i}. {factor}** : Multiplicateur = {multiplier:.2f}x")

# Recommandations
st.subheader("📝 Recommandations stratégiques")

recommendations = []
if kpis['Occupancy (%)'] < 65:
    recommendations.append("🔴 **Améliorer l'occupation** : Mettre en place des offres promotionnelles hors saison")
if kpis['Gross Operating Profit (%)'] < 30:
    recommendations.append("🟡 **Optimiser la profitabilité** : Réduire les coûts fixes et variables")
if fandb_kpis['Gross Food Margin (%)'] < 60:
    recommendations.append("🟡 **Améliorer la marge F&B** : Revoir les prix et optimiser les achats")
if spa_kpis['Treatment Room Utilisation (TRU) (%)'] < 60:
    recommendations.append("🟡 **Augmenter l'occupation du spa** : Promouvoir les forfaits et réservations")
if len(recommendations) == 0:
    recommendations.append("✅ **Performance satisfaisante** - Maintenir les efforts actuels")

for rec in recommendations:
    st.markdown(rec)

# Graphique radar
st.subheader("📊 Indicateurs de performance - Vue radar")

radar_data = {
    "Occupancy": kpis['Occupancy (%)'],
    "ADR (normalisé)": min(100, kpis['ADR (€)'] / 2),
    "GOP %": kpis['Gross Operating Profit (%)'],
    "F&B Margin": fandb_kpis['Gross Food Margin (%)'],
    "Spa TRU": spa_kpis['Treatment Room Utilisation (TRU) (%)']
}

fig = go.Figure(data=go.Scatterpolar(
    r=list(radar_data.values()),
    theta=list(radar_data.keys()),
    fill='toself',
    marker_color='blue'
))
fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), 
                  showlegend=False, height=500)
st.plotly_chart(fig, use_container_width=True)

# Tableau récapitulatif des formules
with st.expander("📚 Voir toutes les formules utilisées"):
    st.markdown("""
    ### Formules d'Analyse Financière Hôtelière
    
    **KPIs Globaux:**
    - Occupancy = (Chambres occupées / Chambres disponibles) × 100%
    - ADR = Revenu hébergement / Chambres occupées
    - RevPAR = Revenu hébergement / Chambres disponibles = Occupancy × ADR
    - TRevPAR = Revenu total / Chambres disponibles
    - TRevPOR = Revenu total / Chambres occupées
    - GOP % = (Revenu total - Coûts d'exploitation) / Revenu total × 100%
    - EBITDA % = EBITDA / Revenu total × 100%
    
    **KPIs Restauration:**
    - Gross Food Margin = (Revenu food - COGS food) / Revenu food × 100%
    - Average Spend per Cover = Revenu F&B / Nombre de couverts
    - Table Turn Rate = Nombre de tables servies / Nombre de tables disponibles
    - Breakfast sit down rate = Petit-déjeuners servis / Nuits client × 100%
    
    **KPIs Spa:**
    - TRU = Heures de traitement vendues / Heures disponibles × 100%
    - ATR = Revenu traitements / Nombre de traitements
    - Guest Capture Rate = Clients spa / Clients hôtel × 100%
    - Therapist Utilisation = Heures prestées / Heures disponibles × 100%
    
    **Analyse de sensibilité:**
    - Multiplicateur de profit = (Δ% Bénéfice net) / (Δ% Facteur contrôlant)
    """)

st.markdown("---")
st.caption("🏨 Dashboard d'Analyse Financière Hôtelière | Basé sur Jawabreh et al. (2017) et Fáilte Ireland KPI Framework")
