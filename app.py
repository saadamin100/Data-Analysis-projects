import pandas as pd
import os
import streamlit as st
from io import StringIO, BytesIO

class MainCleaner:
    
    def __init__(self, uploaded_file):
        self.df = pd.DataFrame()
        self.load_data(uploaded_file)

    def load_data(self, uploaded_file):
        try:
            if uploaded_file.name.endswith('.csv'):
                self.df = pd.read_csv(uploaded_file)
                st.success(f"[LOAD] File loaded successfully: {uploaded_file.name}")
            elif uploaded_file.name.endswith('.xlsx'):
                self.df = pd.read_excel(uploaded_file)
                st.success(f"[LOAD] File loaded successfully: {uploaded_file.name}")
            else:
                st.error("[ERROR] Unsupported file type. Please use CSV or XLSX.")
                self.df = pd.DataFrame()
        except Exception as e:
            st.error(f"[ERROR] An unexpected error occurred during loading: {e}")

    def initial_set(self):
        st.header("1️⃣ Initial Data Audit")
        st.subheader("Column Information (d-types and Null Counts):")
        buf = StringIO()
        self.df.info(buf=buf)
        st.text(buf.getvalue())
        
        st.subheader("First 5 Rows:")
        st.dataframe(self.df.head())
        st.info(f"Data Size: **{len(self.df)}** rows and **{len(self.df.columns)}** columns.")

    def missingvalues_analysis(self, strategy='median'):
        st.header("2️⃣ Handling Missing Values (Imputation)")
        
        numeric_cols = self.df.select_dtypes(include=['number']).columns
        object_cols = self.df.select_dtypes(include=['object']).columns
        
        st.markdown("---")
        
        for col in numeric_cols:
            missing_count = self.df[col].isnull().sum()
            if missing_count > 0:
                missing_percent = (missing_count / len(self.df)) * 100
                median_val = self.df[col].median()
                self.df[col].fillna(median_val, inplace=True)
                st.success(f"**[FILLED]** `{col}`: {missing_count} values **({missing_percent:.2f}%)** filled with **Median**.")
        
        for col in object_cols:
            missing_count = self.df[col].isnull().sum()
            if missing_count > 0:
                mode_val = self.df[col].mode()[0]
                self.df[col].fillna(mode_val, inplace=True)
                st.success(f"**[FILLED]** `{col}`: {missing_count} values filled with **Mode**.")
        
        if self.df.isnull().sum().sum() == 0:
            st.info("All missing values have been handled.")
        
        return self.df

    def standardize_suggestion(self):
        st.header("3️⃣ Text Standardization & Duplicate Removal")
        object_cols = self.df.select_dtypes(include=['object']).columns
        
        if object_cols.empty:
            st.warning("[INFO] No text (object) columns found for standardization.")
            
        for col in object_cols:
            self.df[col] = self.df[col].astype(str).str.lower().str.strip()
            
        st.success("All text columns converted to **lowercase** and **leading/trailing spaces removed**.")
        
        return self.df

    def auto_cleaning(self):
        before = len(self.df)
        self.df.drop_duplicates(inplace=True)
        after = len(self.df)
        
        if before - after > 0:
            st.warning(f"**{before - after}** duplicate rows removed. Remaining rows: **{after}**")
        else:
            st.info("[INFO] No duplicate rows found.")
        
        return self.df

    def categorized_standardization(self):
        st.header("4️⃣ Categorical Column Analysis")
        object_cols = self.df.select_dtypes(include=['object']).columns
        total_rows = len(self.df)
        
        for col in object_cols:
            unique = self.df[col].nunique()
            st.markdown(f"* Column **`{col}`** has **{unique}** unique values (out of {total_rows} rows).")
            
            if unique <= 20 and unique > 1:
                st.markdown("  * [SUGGESTION] This column may need **Manual Mapping** (e.g., 'tv' -> 'television').")
            elif unique == total_rows:
                st.markdown("  * [NOTE] High unique count, likely an ID or descriptive text.")
    
    def categorized_checker(self, column_name, map_input):
        if not map_input or '->' not in map_input:
            st.error("[SKIP] No valid mapping rules provided.")
            return self.df
        
        st.header(f"5️⃣ Applying Manual Mapping on '{column_name}'")
        manual_map = {}
        original_unique = self.df[column_name].nunique()
        
        try:
            for item in map_input.split(','):
                if '->' in item:
                    old_value, new_value = item.split('->') 
                    manual_map[old_value.strip().lower()] = new_value.strip().lower()
            
            self.df[column_name] = self.df[column_name].replace(manual_map)
            
            new_unique_count = self.df[column_name].nunique()
            
            st.success(f"Mapping applied successfully. Unique values reduced from **{original_unique}** to **{new_unique_count}**.")
            
        except Exception as e:
            st.error(f"[ERROR] Mapping failed. Check format. Error: {e}")
            
        return self.df

def main():
    st.set_page_config(page_title="Data Cleaner App", layout="wide")
    st.title("💡 Automated Data Cleaner with Streamlit")
    st.markdown("Upload your CSV or XLSX file to begin the data cleaning process.")
    st.markdown("---")

    uploaded_file = st.file_uploader("Choose a CSV or XLSX file", type=['csv', 'xlsx'])

    if uploaded_file is not None:
        
        cleaner = MainCleaner(uploaded_file)
        
        if not cleaner.df.empty:
            
            st.session_state['cleaner'] = cleaner
            
            cleaner.initial_set()
            
            cleaner.missingvalues_analysis()
            
            cleaner.standardize_suggestion()
            cleaner.auto_cleaning()
            
            cleaner.categorized_standardization()
            
            st.markdown("---")
            st.header("Manual Category Mapping")
            object_cols = cleaner.df.select_dtypes(include=['object']).columns.tolist()
            
            if object_cols:
                st.text(f"Available text columns: {object_cols}")
                
                col_to_map = st.selectbox(
                    "Select column for mapping (or skip):", 
                    ['skip'] + object_cols
                )
                
                if col_to_map != 'skip':
                    st.markdown("**Mapping format:** `old_value->new_value`, separated by comma.")
                    st.caption("Example: `tv->television, pc->computer`")
                    map_rules = st.text_input(
                        "Enter mapping rules:", 
                        key='map_input'
                    )
                    
                    if st.button('Apply Manual Mapping'):
                        cleaner.categorized_checker(
                            column_name=col_to_map, 
                            map_input=map_rules
                        )
                        st.session_state['cleaner'] = cleaner # Update state
            
            st.markdown("---")
            st.header("✅ Final Cleaned Data Preview")
            st.dataframe(cleaner.df.head())

            @st.cache_data
            def convert_df_to_csv(df):

                return df.to_csv(index=False).encode('utf-8')

            csv_data = convert_df_to_csv(cleaner.df)
            output_filename = "clean_" + os.path.basename(uploaded_file.name).replace(".xlsx", ".csv")

            st.download_button(
                label="Download Cleaned CSV File",
                data=csv_data,
                file_name=output_filename,
                mime='text/csv',
                help="Click to download the final cleaned dataset."
            )
            
        else:
            st.error("Process terminated: Data could not be loaded.")

if __name__ == "__main__":
    main()