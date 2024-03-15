import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import locale
import matplotlib.pyplot as plt

st.set_page_config(page_title="Challenge", page_icon=":soccer:", layout="wide")

# Carica i dati delle diverse tabelle
df = pd.read_excel("/Users/sallu/Desktop/df.xlsx")
df_no_filter = pd.read_excel("/Users/sallu/Desktop/no_filter.xlsx")
df_age = pd.read_excel("/Users/sallu/Desktop/age.xlsx")
df_value = pd.read_excel("/Users/sallu/Desktop/value.xlsx")
df_all = pd.read_excel("/Users/sallu/Desktop/all.xlsx")

# Elimina eventuali colonne non necessarie
df = df.drop('Unnamed: 0', axis=1, errors='ignore')
df_no_filter = df_no_filter.drop(['Unnamed: 0', 'cluster'], axis=1, errors='ignore')
df_age = df_age.drop(['Unnamed: 0', 'cluster'], axis=1, errors='ignore')
df_value = df_value.drop(['Unnamed: 0', 'cluster'], axis=1, errors='ignore')
df_all = df_all.drop(['Unnamed: 0', 'cluster'], axis=1, errors='ignore')


# Informazioni del giocatore
specific_player_name = "Francesco Acerbi"
specific_player_info = df[df['Player'] == specific_player_name].iloc[0]

# Colonna sinistra: Posizione e Età
with st.expander("Info sul giocatore", expanded=True):
    col1, col2, col3, col4= st.columns(4)
    with col1:
         st.subheader("Francesco Acerbi")
         st.image("/Users/sallu/Desktop/acerbi.png", width=200)

    with col2:
        st.write(f"**Posizione:** {specific_player_info['Pos']}")
        st.write(f"**Età:** {specific_player_info['Age']}")
        st.write(f"**Squadra:** {specific_player_info['Squad']}")
        st.write(f"**Nazione:** {specific_player_info['Nation']}")
    
    with col3:
        st.write(f"**Partite giocate su 90':** {specific_player_info['Playing Time 90s']}")
        st.write(f"**Goal:** {specific_player_info['Performance Gls']}")
        st.write(f"**Assist:** {specific_player_info['Performance Ast']}")
        st.write(f"**Intercettazioni:** {specific_player_info['Int']}")
    
    locale.setlocale(locale.LC_ALL, '')
    market_value = specific_player_info['market_value_in_eur']
    formatted_market_value = locale.format_string("%d", market_value, grouping=True)    

    with col4:
        st.write(f"**Salvataggi:** {specific_player_info['Clr']}")
        st.write(f"**% Duelli vinti:** {specific_player_info['Aerial Duels Won%']}")
        st.write(f"**% Passaggi completati:** {specific_player_info['Total Cmp%']}")
        st.write(f"**Valore di mercato:** €{formatted_market_value}")


def generate_scatter_plot(df, selected_players, specific_player_info, categories):
    # Preparazione dei dati
    selected_players_values = df[df['Player'].isin(selected_players)][categories].values
    specific_player_values = specific_player_info[categories].values
    
    # Creazione dello scatter plot
    fig, ax = plt.subplots(figsize=(10, 6))
    for player_values in selected_players_values:
        ax.scatter(categories, player_values)
    ax.scatter(categories, specific_player_values, label="Francesco Acerbi", marker='x')
    
    # Aggiunta di titoli e etichette
    ax.set_title('Confronto statistiche tra giocatori selezionati e Francesco Acerbi')
    ax.set_xlabel('Statistiche')
    ax.set_ylabel('Valore')
    ax.legend()
    ax.grid(True)
    
    # Ritorna il plot come oggetto Figure di Matplotlib
    return fig





def generate_radar_chart(df, selected_data, specific_player_info, categories):
    if not categories:
        st.warning("Seleziona almeno una categoria da considerare nel grafico radar.")
        return go.Figure()  # Restituisci un oggetto Figure vuoto
    
    fig_radar = make_subplots(rows=1, cols=1, specs=[[{'type': 'polar'}]])
    
    # Trova il valore massimo tra tutti i giocatori selezionati e il giocatore specifico
    max_values = []
    for _, player_row in selected_data.iterrows():
        player_name = player_row['Player']
        if player_name in df['Player'].values:
            player_values = df[df['Player'] == player_name][categories].values.flatten()
            max_values.append(max(player_values))
            
            fig_radar.add_trace(go.Scatterpolar(
                r=player_values,
                theta=categories,
                fill='toself',
                name=player_name,
                customdata=[f'{category}: {value}' for category, value in zip(categories, player_values)],
                hovertemplate='%{customdata}',
            ))
    
    # Aggiungi il giocatore specifico
    specific_player_values = specific_player_info[categories].values.flatten()
    max_values.append(max(specific_player_values))
    fig_radar.add_trace(go.Scatterpolar(
        r=specific_player_values,
        theta=categories,
        fill='toself',
        name=specific_player_name,
        customdata=[f'{category}: {value}' for category, value in zip(categories, specific_player_values)],
        hovertemplate='%{customdata}',
    ))

    max_value_selected_players = max(max_values)

    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max_value_selected_players],
            )
        ),
        showlegend=True,
        legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02,),
    )
    return fig_radar if max_values else None



# Multiselect per la selezione delle tabelle
table_selection = st.multiselect("Seleziona una o più variabili da considerare", ["Age", "Market Value"])


# Ottieni i dati della tabella selezionata
if not table_selection:
    selected_data = df_no_filter
elif "Age" in table_selection:
    selected_data = df_age
elif "Market Value" in table_selection:
    selected_data = df_value
if "Age" in table_selection and "Market Value" in table_selection:
    selected_data = df_all


# Visualizza la tabella selezionata
st.subheader("Top 5 giocatori simili")
st.dataframe(selected_data, hide_index=True, use_container_width=True)

with st.expander(" ",expanded=True):
    st.markdown(
        """
        <div style="text-align:center">
            <h3 style="margin-bottom:0">Significato statistiche</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.write(" ")  

    col_1, col_2, col_3= st.columns(3)
    with col_1:
        st.write(f"**Standard Gls:** {'Goal segnati'}")
        st.write(f"**Performance Ast:** {'Assist'}")
        st.write(f"**Standard SoT%:** {'Percentuale tiri nello specchio'}")
        st.write(f"**Total Cmp%:** {'Percentuale di passaggi completati'}")
    
    with col_2:
        st.write(f"**Short Cmp%:** {'Percentuale passaggi corti completati'}")
        st.write(f"**Long Cmp%:** {'Percentuale passaggi lunghi completati'}")
        st.write(f"**Tackles TklW:** {'Tackle vincenti'}")
        st.write(f"**Int:** {'Intercettazioni'}")

    with col_3:
        st.write(f"**Challenges Tkl%:** {'Percentuale di duelli vinti'}")
        st.write(f"**Clr:** {'Salvataggi'}")
        st.write(f"**Aerial Duels Won%:** {'Duelli aerei vinti'}")
    

# Multiselect per la selezione delle categorie
all_categories = ['Standard Gls','Performance Ast','Standard SoT%','Total Cmp%','Short Cmp%','Long Cmp%','Tackles TklW','Int','Challenges Tkl%','Clr','Aerial Duels Won%']
# Primo multiselect
selected_categories_1 = st.multiselect("Seleziona le categorie da considerare nel radar", all_categories, default=all_categories)

# Genera e visualizza il grafico radar
fig_radar = generate_radar_chart(df, selected_data, specific_player_info, selected_categories_1)
st.plotly_chart(fig_radar, use_container_width=True)

# Secondo multiselect
#selected_categories_2 = st.multiselect("Seleziona le categorie da considerare nel grafico 2", all_categories, default=all_categories)

# Genera e visualizza il grafico scatter
#fig_scatter = generate_scatter_plot(df, selected_data, specific_player_info, selected_categories_2)
#st.plotly_chart(fig_scatter, use_container_width=True)

