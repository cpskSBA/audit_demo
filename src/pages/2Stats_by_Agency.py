import pandas as pd
import streamlit as st
import plotly.express as px

df = pd.read_csv("../src/GAO_for streamlit.csv").drop_duplicates(subset=['Case No','Recommendation','Agency Affected']).drop(columns="Unnamed: 0")
df['Sub Topics']=df['Sub Topics'].astype(str)
df=df[~df['Year'].isin([2008,2025])]

def apply_filters(df):

    filtered_df=df.copy()

    #filtered_df['Year']=pd.to_numeric(filtered_df['Year'], errors="coarse")
    min_year,max_year=int(filtered_df['Year'].min()),int(filtered_df['Year'].max())

    selected_year = st.sidebar.slider('Select Year Range',min_value=min_year, max_value=max_year, value=(min_year,max_year))
    filtered_df= filtered_df[(filtered_df['Year']>= selected_year[0])& (filtered_df['Year'] <=selected_year[1])]


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
unique_cases = df_filtered.groupby('Agency Affected')['Case No'].nunique().reset_index(name='Total # of Audits')
unique_recommendations=df_filtered['Agency Affected'].value_counts(dropna=True).reset_index().rename(columns={"count":"Total # of Recommendations"})
avg_unique_recommendation=df_filtered.groupby(['Agency Affected','Case No']).size().groupby('Agency Affected').mean().round(0).reset_index(name='Avg. # of Recommendations')
status_counts=df_filtered.groupby(['Agency Affected','Case No', 'Status']).size().unstack(fill_value=0)
status_counts=status_counts.groupby('Agency Affected').sum().reset_index().rename(columns={"Closed – Implemented":"Closed Impl.","Closed – Not Implemented":"Closed Not Impl.","Open – Partially Addressed":"Open Part. Addressed", "Closed – No Longer Valid":"Closed NLV"})
status_counts.columns=['Agency Affected'] + [f'{col} Recommendations' for col in status_counts.columns[1:]]

final_df = (unique_cases
            .merge(unique_recommendations, on="Agency Affected",how='left')
            .merge(avg_unique_recommendation, on='Agency Affected',how='left')
            .merge(status_counts, on='Agency Affected',how='left')).sort_values(by="Total # of Audits",ascending=False)

final_df_top=final_df[['Agency Affected','Total # of Audits','Total # of Recommendations']].head(10)
final_df_top['Agency Affected'] = final_df_top['Agency Affected'].str.replace("DEPARTMENT","DEPT")


st.subheader("Top Audited Agencies")

fig1 = px.bar(
    final_df_top.sort_values('Total # of Audits', ascending=True),y='Agency Affected', x='Total # of Audits',orientation='h')
st.plotly_chart(fig1, use_container_width=True)

st.dataframe(final_df,use_container_width=True,hide_index=True)
