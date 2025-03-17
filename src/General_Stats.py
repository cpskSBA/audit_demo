#search-ms:displayname=Search%20Results%20in%20Local&crumb=location:C%3A%5CUsers%5Ccpsolerkanchumarthy%5CAppData%5CLocal\Git

import pandas as pd
import streamlit as st
import ast 
import matplotlib.pyplot as plt

page_title= "GAO Recommendations Analysis"
st.set_page_config(
    page_title=page_title,
    page_icon="https://www.sba.gov/brand/assets/sba/img/pages/logo/logo.svg",
    layout="wide",
    initial_sidebar_state="expanded")

hide_streamlit_style = """
             <style>
             footer {visibility: hidden;}
             </style>
             """

st.markdown(hide_streamlit_style, unsafe_allow_html=True)
st.header(page_title)

#@st.cache_data
#df0 = pd.read_csv(r"C:\Users\cpsolerkanchumarthy\OneDrive - U.S. Small Business Administration\Desktop\repositories\audit_demo\src\GAO_for streamlit.csv").drop_duplicates(subset=['Case No','Recommendation','Agency Affected']).drop(columns="Unnamed: 0")
df0 = pd.read_csv("src/GAO_for streamlit.csv").drop_duplicates(subset=['Case No','Recommendation','Agency Affected']).drop(columns="Unnamed: 0")

df0=df0.sort_values(by='Agency Type',ascending=False)

df=df0[~df0['Year'].isin([2008,2025])]
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

#def data_aggregations(df):
unique_cases = df_filtered.groupby('Year')['Case No'].nunique().reset_index(name='Total # of Audits')
unique_recommendations=df_filtered['Year'].value_counts(dropna=True).reset_index().rename(columns={"count":"Total # of Recommendations"})
avg_unique_agencies=df_filtered.groupby(['Year','Case No'])['Agency Affected'].nunique().groupby('Year').mean().round(0).reset_index(name='Avg. # of Agencies Involved')
avg_unique_recommendation=df_filtered.groupby(['Year','Case No']).size().groupby('Year').mean().round(0).reset_index(name='Avg. # of Recommendations')
status_counts=df_filtered.groupby(['Year','Case No', 'Status']).size().unstack(fill_value=0)
status_counts=status_counts.groupby('Year').sum().reset_index().rename(columns={"Closed – Implemented":"Closed Impl.","Closed – Not Implemented":"Closed Not Impl.","Open – Partially Addressed":"Open Part. Addressed", "Closed – No Longer Valid":"Closed NLV"})
status_counts.columns=['Year'] + [f'{col} Recommendations' for col in status_counts.columns[1:]]


#Dataset
final_df = (unique_cases
            .merge(unique_recommendations, on="Year",how='left')
            .merge(avg_unique_agencies, on ='Year',how='left')
            .merge(avg_unique_recommendation, on='Year',how='left')
            .merge(status_counts, on='Year',how='left'))#.set_index("Year")

expected_chart_columns =['Closed Impl. Recommendations','Closed Not Impl. Recommendations','Open Recommendations']
for col in expected_chart_columns:
    if col not in final_df.columns:
        final_df[col]=0

final_df['Year'] = final_df['Year'].astype(str)
#graph
col1,col2=st.columns(2)
with col1:
    st.line_chart(
    final_df,
    x='Year',
    y=["Total # of Audits", "Total # of Recommendations"],
    color=["#FF0000","#0000FF"])

with col2:
    st.bar_chart(
    final_df,
    x='Year',
    y=["Closed Impl. Recommendations","Closed Not Impl. Recommendations", "Open Recommendations"],
    color=["#FF0000","#0000FF","#000080"],
    x_label='Year', 
    y_label=["Count"],
    use_container_width=True)

final_df=final_df.set_index('Year')
st.dataframe(final_df,use_container_width=True)

# if 'Open Recommendations' not in df_filtered.columns and 'Closed Impl. Recommendations' not in df_filtered.columns:
#         st.warning("No Open or Closed Recommendations Found for Selected Filters.")
#         st.stop()


csv = final_df.to_csv(index=False).encode('utf-8')
st.download_button("Download Data", data=csv, file_name="recommendation_stats.csv", mime="text/csv",
                               help='Click here to download the data as a CSV file')

