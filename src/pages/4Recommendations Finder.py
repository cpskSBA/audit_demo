import pandas as pd
import streamlit as st


#@st.cache_data
df= pd.read_csv("src/pages/GAO_for streamlit.csv").drop_duplicates(subset=['Case No','Recommendation','Agency Affected']).drop(columns="Unnamed: 0")
#df = pd.read_csv("pages/GAO_for streamlit.csv").drop_duplicates(subset=['Case No','Recommendation','Agency Affected']).drop(columns="Unnamed: 0")

df['Sub Topics']=df['Sub Topics'].astype(str)

def apply_filters(df):

    filtered_df=df.copy()

    selected_agency = st.sidebar.multiselect('Filter by Agency', options=sorted(filtered_df['Agency Affected'].dropna().unique()))
    
    if selected_agency:
        filtered_df=filtered_df[filtered_df['Agency Affected'].isin(selected_agency)]

    selected_agency_type = st.sidebar.multiselect('Filter by Agency Type', options=sorted(filtered_df['Agency Type'].dropna().unique()))
    if selected_agency_type:
        filtered_df=filtered_df[filtered_df['Agency Type'].isin(selected_agency_type)]

    selected_main_topic = st.sidebar.multiselect('Filter by Main Topic', options=sorted(filtered_df['Main Topic'].dropna().unique()))
    if selected_main_topic:
        filtered_df=filtered_df[filtered_df['Main Topic'].isin(selected_main_topic)]

    all_sub_topics= df['Sub Topics'].dropna().str.split(",").explode().str.strip().unique()
    selected_sub_topics = st.sidebar.multiselect('Filter by Sub Topics',options=sorted(all_sub_topics))
    if selected_sub_topics:
         filtered_df=filtered_df[filtered_df['Sub Topics'].str.contains('|'.join(selected_sub_topics),case=False,na=False)]

    
    all_audit_type= df['Audit Type'].dropna().str.split(",").explode().str.strip().unique()
    selected_audit_type = st.sidebar.multiselect('Filter by Audit Type',options=sorted(all_audit_type))
    if selected_audit_type:
         filtered_df=filtered_df[filtered_df['Audit Type'].str.contains('|'.join(selected_audit_type),case=False,na=False)]

    selected_risk_level = st.sidebar.multiselect('Filter by Risk Level', options=sorted(filtered_df['Risk Level'].dropna().unique()))
    if selected_risk_level:
        filtered_df=filtered_df[filtered_df['Risk Level'].isin(selected_risk_level)]

    return filtered_df


df_filtered = apply_filters(df)

for index,row in df_filtered.iterrows():
    st.text_area(f"{row['Case No']} - {row['Title']}", row["Recommendation"],height=150)

#df_filtered=df_filtered[['Case No','Title','Recommendation']]

#st.dataframe(df_filtered,hide_index=True)

