import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Set Streamlit page configuration to use wide layout
st.set_page_config(layout="wide")

# Cache the data loading process
@st.cache_data
def load_data():
    return pd.read_csv('paskolos.csv', delimiter=";")

# Load the data (cached)
adresai_apj2 = load_data()

# Convert 'ja_reg_data' to datetime if it's not already and extract the year
@st.cache_data
def preprocess_data(data):
    data['ja_reg_data'] = pd.to_datetime(data['date'])
    data['year'] = data['ja_reg_data'].dt.year
    return data

adresai_apj2 = preprocess_data(adresai_apj2)


pattern = r'(?:[^;]*;){5}([^;]*);'
adresai_apj2['regex_lt_long_title'] = adresai_apj2['lt_long_title'].str.extract(pattern)

# Streamlit App
st.markdown("<h1 style='text-align: center; font-weight: bold;'>Paskolos pagal rezidentiškumą</h1>", unsafe_allow_html=True)


# Add slicers (filters) in the sidebar
st.sidebar.header("Filtrai")

@st.cache_data
def get_unique_values(data):
    years = data['year'].unique()
    form_list = data['regex_lt_long_title'].unique()
    return years, form_list

years, form_list = get_unique_values(adresai_apj2)

def multiselect_with_all(label, options, default):
    options_with_all = ["All"] + list(options)
    selected = st.multiselect(label, options_with_all, default=["All"])
    if "All" in selected:
        return options  # Return all options if "All" is selected
    else:
        return selected

# Date Range Filter for 'ja_reg_data' (Year-based)
with st.sidebar.expander("Pasirinkite metus", expanded=False):  # Collapsible expander
    selected_years = multiselect_with_all("Choose Year(s)", options=sorted(years), default=sorted(years))

# Multi-select for 'form_pavadinimas' (Form Type)
with st.sidebar.expander("Pasirinkite rezidentiškumą", expanded=False):
    selected_forms = multiselect_with_all("Choose Form Type(s)", options=form_list, default=form_list)


@st.cache_data
def filter_data(data, selected_years, selected_forms):
    if len(selected_years) > 0:
        data = data[data['year'].isin(selected_years)]
    if len(selected_forms) > 0:
        data = data[data['regex_lt_long_title'].isin(selected_forms)]
    return data

# Apply filters
filtered_data = filter_data(adresai_apj2, selected_years, selected_forms)

rez_sum = filtered_data.groupby(["regex_lt_long_title"])["value"].sum().sort_values(ascending=True)
year_counts = filtered_data.groupby(["year"])["value"].sum()

# Display the table and the graphs side by side
col1, col2 = st.columns([1.5, 3])

with col1:
    
    st.subheader("Rezidentiškumo pasiskirstymas pagal paskolų sumą")
    fig, ax = plt.subplots(figsize=(4, 2), dpi=350)
    sns.barplot(x=rez_sum.index, y=rez_sum.values, palette="Set2", ax=ax)
    ax.set_xlabel("Rezidentai", fontsize=5, fontweight='bold')
    ax.set_ylabel("Paskolų suma", fontsize=5, fontweight='bold')
    ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
    ax.tick_params(axis='x', labelsize=5, rotation=45)
    ax.tick_params(axis='y', labelsize=5)
    st.pyplot(fig)

with col2:


    st.subheader("Paskolų suma pagal metus")
    fig, ax = plt.subplots(figsize=(9, 2), dpi=350)
    sns.lineplot(x=year_counts.index, y=year_counts.values, ax=ax, marker='o', color='green')
    ax.set_xlabel("Metai", fontsize=5, fontweight='bold')
    ax.set_ylabel("Paskolų suma", fontsize=5, fontweight='bold')
    ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
    ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
    ax.set_xticks(ax.get_xticks())  # This ensures that ticks are auto-placed optimally.
    ax.set_xticklabels([int(tick) for tick in ax.get_xticks()])  # Formatting ticks to integers.
    ax.tick_params(axis='x', labelsize=5)
    ax.tick_params(axis='y', labelsize=5)
    st.pyplot(fig)













