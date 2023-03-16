import pandas as pd  # pip install pandas openpyxl
import plotly.express as px  # pip install plotly-express
import streamlit as st  # pip install streamlit


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

average_sale_by_transaction = round(df_selection["Total"].mean(), 2)

left_column, middle_column, right_column = st.columns(3)
with left_column:
    st.subheader("Costo Totale:")
    st.subheader(f"EUR € {total_sales:,}")


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
dfcol= df_selection.loc[:,['tip_cos','Articolo', 'raggA', 'raggLB', 'raggLC', 'Breve', 'Spec', 'Total']]
st.dataframe(dfcol)
# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)