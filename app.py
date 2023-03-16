import pandas as pd  # pip install pandas openpyxl
import plotly.express as px  # pip install plotly-express
import streamlit as st  # pip install streamlit
import base64
import textwrap
import xml.etree.ElementTree as ET
from st_aggrid import AgGrid
import numpy as np
from PIL import Image
import io


st.set_page_config(page_title="Dashboard Costi", page_icon=":bar_chart:", layout="wide")

# ---- LEGGI EXCEL ----
@st.cache
def get_data_from_excel():
    df = pd.read_excel(
        io="resu.xlsx",
        engine="openpyxl",
        sheet_name="Foglio1",
        
        usecols="C:V",
        nrows=2806,
    )

    return df
with open('ARC.svg', 'r') as f:
    svg_data = f.read()
def render_svg(svg, raggLC, filtro,filtroC):

    """Renders the given svg string."""

    # carica il file SVG come un oggetto ElementTree
    tree = ET.fromstring(svg)
    
    # cerca l'elemento SVG desiderato per ID
    
    if raggLC== filtroC:
        element_id = filtro  # sostituisci "my-rect" con il valore ID desiderato
        element = tree.find(".//*[@id='{}']".format(element_id))

        if element is not None:
            element.set("style", "fill: #004080;fill-opacity:0.7")

    # converte l'ElementTree modificato in una stringa SVG
        svg_string = ET.tostring(tree, encoding='unicode')
    else:
        svg_string = svg
    b64 = base64.b64encode(svg_string.encode('utf-8')).decode("utf-8")
    html = r'<img src="data:image/svg+xml;base64,%s" width=250 height=275/>' % b64


    
    
    
    st.write(html, unsafe_allow_html=True)

def render_svg_example():
    svg = svg_data
    render_svg(svg, raggLC,filtro, filtroC)




df = get_data_from_excel()

# ---- SIDEBAR ----
st.sidebar.header("Filtra i dati:")
agreeRLC = st.sidebar.checkbox('Attiva menù a discesa per Livelli')

if agreeRLC:
    raggLC = st.sidebar.selectbox(
        'Seleziona il livello da filtrare?',
        df["raggLC"].unique())
else:
    raggLC = st.sidebar.multiselect(
        "Selezione multipla Livelli:",
        options=df["raggLC"].unique(),
        default=df["raggLC"].unique()
)

raggLB = st.sidebar.multiselect(
    "Selezione Opera:",
    options=df["raggLB"].unique(),
    default=df["raggLB"].unique(),
)


agreeTC = st.sidebar.checkbox('Attiva menù a discesa per Tipologia Costruttiva')
if agreeTC:
    tip_cos = st.sidebar.selectbox(
        'Seleziona la Tipologia Costruttiva da filtrare?',
        df["tip_cos"].unique())
else:
    tip_cos = st.sidebar.multiselect(
        "Seleziona Tipologia Costruttiva:",
        options=df["tip_cos"].unique(),
        default=df["tip_cos"].unique()
)

df_selection = df.query(
    "raggLC == @raggLC & raggLB ==@raggLB & tip_cos == @tip_cos"
)

# ---- MAINPAGE ----
st.title(":bar_chart: Dashboard Costi")
st.markdown("##")

# TOP 
total_sales = int(df_selection["Total"].sum())
filtro= ''.join(df_selection["raggC"].unique())
filtroC= ''.join(df_selection["raggLC"].unique())
average_sale_by_transaction = round(df_selection["Total"].mean(), 2)

left_column, middle_column, right_column = st.columns(3)
with left_column:
    st.subheader("Costo Totale:")
    st.subheader(f"EUR € {total_sales:,}")
    #st.subheader(filtro)
with middle_column:
    st.subheader("Livello selezionato:")
    #if agreeRLC:
    #if __name__ == '__main__':
    render_svg_example()
        
st.markdown("""---""")

# ARTICOLI [BAR CHART]
sales_by_product_line = (
    df_selection.groupby(by=["Articolo"]).sum()[["Total"]].rename(columns={"Total": "Totale"}).sort_values(by="Totale")
)
fig_product_sales = px.bar(
    sales_by_product_line,
    x="Totale",
    y=sales_by_product_line.index,
    orientation="h",
    title="<b>Prezzi per Articolo</b>",
    color_discrete_sequence=["#0083B8"] * len(sales_by_product_line),
    template="plotly_white",
)
fig_product_sales.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False))
)

# LIVELLO [BAR CHART]
sales_by_hour = df_selection.groupby(by=["raggB"]).sum()[["Total"]].rename(columns={"Total": "Totale"}).rename_axis("Livello")
fig_hourly_sales = px.bar(
    sales_by_hour,
    x=sales_by_hour.index,
    y="Totale",
    title="<b>Prezzi per Livello</b>",
    color_discrete_sequence=["#0083B8"] * len(sales_by_hour),
    template="plotly_white",
)
fig_hourly_sales.update_layout(
    xaxis=dict(tickmode="linear"),
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=(dict(showgrid=False)),
)


left_column, right_column = st.columns(2)
left_column.plotly_chart(fig_hourly_sales, use_container_width=True)
right_column.plotly_chart(fig_product_sales, use_container_width=True)

#***************************************************************************************
st.subheader('Tabella Dati Costi:')
dfcol= df_selection.loc[:,['tip_cos','Articolo', 'raggA', 'raggLB', 'raggLC', 'Breve', 'Spec', 'Total']]
st.dataframe(dfcol)
#***************************************************************************************


#***************************************************************************************
Tasks=pd.read_csv('CRONO.csv')
Tasks['INIZIO'] = pd.to_datetime(Tasks['INIZIO'], format='%d/%m/%Y')#Tasks['INIZIO'].dt.strftime('%d%m%y%H%M%S')#.astype('datetime64')
Tasks['FINE'] = pd.to_datetime(Tasks['FINE'], format='%d/%m/%Y')#Tasks['FINE'].dt.strftime('%d%m%y%H%M%S')#.astype('datetime64')

#grid_response = AgGrid(
#    Tasks,
#    editable=True, 
#    height=300, 
#    width='100%',
#    )

#updated = grid_response['data']
df = pd.DataFrame(Tasks) 
#df = pd.DataFrame(updated) 
#Sezione interfaccia principale - 3
st.subheader('Visualizza il diagramma di Gantt per:')#<b>Prezzi per Livello</b>

Options = st.selectbox( "",['IMPORTO','DURATA'],index=0)#"Visualizza il diagramma di Gantt per:",
#if st.button('Generate Gantt Chart'): 
fig = px.timeline(
                df, 
                x_start="INIZIO", 
                x_end="FINE", 
                y="ATTIVITÀ",
                color=Options,
                hover_name="DESCRIZIONE ATTIVITÀ"
                )

fig.update_yaxes(autorange="reversed")          #se non specificato come 'reversed', le attività verranno elencate dal basso verso l'alto        

fig.update_layout(
                title='Diagramma di Gantt del piano di progetto',
                hoverlabel_bgcolor='#DAEEED',   #Cambia il colore di sfondo del tooltip di hover in un colore azzurro universale. Se non specificato, il colore di sfondo varierà in base al team o alla percentuale di completamento, a seconda della visualizzazione scelta dall'utente
                bargap=0.2,
                height=600,              
                xaxis_title="", 
                yaxis_title="",                   
                title_x=0.5,                    #Rendi il titolo centrato                     
                xaxis=dict(
                        tickfont_size=15,
                        tickangle = 270,
                        rangeslider_visible=True,
                        side ="top",            #Posiziona le etichette dell'asse delle x in alto al grafico
                        showgrid = True,
                        zeroline = True,
                        showline = True,
                        showticklabels = True,
                        tickformat="%x\n",      #Mostra le etichette degli assi in un formato specifico. 
                        )
            )

fig.update_xaxes(tickangle=0, tickfont=dict(family='Rockwell', color='blue', size=15))

st.plotly_chart(fig, use_container_width=True)  #Mostra il grafico di Plotly in Streamlit
st.subheader('Tabella Dati Tempi:')
grid_response = AgGrid(
    Tasks,
    editable=True, 
    height=300, 
    width='100%',
    )
#***************************************************************************************




# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)