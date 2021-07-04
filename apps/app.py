
import streamlit as st
import pandas as pd


def explore(df):
    # DATA
    st.write('Data:')
    st.write(df)
    # SUMMARY
    df_types = pd.DataFrame(df.dtypes, columns=['Data Type'])
    numerical_cols = df_types[~df_types['Data Type'].isin(['object',
                   'bool'])].index.values
    df_types['Count'] = df.count()
    df_types['Unique Values'] = df.nunique()
    df_types['Min'] = df[numerical_cols].min()
    df_types['Max'] = df[numerical_cols].max()
    df_types['Average'] = df[numerical_cols].mean()
    df_types['Median'] = df[numerical_cols].median()
    df_types['St. Dev.'] = df[numerical_cols].std()
    st.write('Summary:')
    st.write(df_types)


def transform(df):
    # Select sample size
    frac = st.slider('Random sample (%)', 1, 100, 100)
    if frac < 100:
        df = df.sample(frac=frac/100)
    # Select columns
    cols = st.multiselect('Columns',
                        df.columns.tolist(),
                        df.columns.tolist())
    df = df[cols]
    return df


def get_df(file):
    # get extension and read file
    extension = file.name.split('.')[1]
    if extension.upper() == 'CSV':
        df = pd.read_csv(file)
    elif extension.upper() == 'XLSX':
        df = pd.read_excel(file, engine='openpyxl')
    elif extension.upper() == 'PICKLE':
        df = pd.read_pickle(file)
    return df


def main():
    st.title('Explore a dataset')
    st.write('A general purpose data exploration app')
    file = st.file_uploader("Upload file", type=['csv'
                                             ,'xlsx'
                                             ,'pickle'])
    if not file:
        st.write("Upload a .csv or .xlsx file to get started")
        return

    df = get_df(file)
    df = transform(df)

    explore()


main()

# streamlit run /Users/lucascarlson/Documents/Python/hello/apps/app.py
