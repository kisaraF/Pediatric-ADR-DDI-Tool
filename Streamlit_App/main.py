import streamlit as st
import pandas as pd
import json
from typing import List
import matplotlib.pyplot as plt
import re
import os

# --- Load Mined Rules and Outcome Severity Data ---
@st.cache_data
def load_data():
    base_path = os.path.dirname(__file__)
    with open(os.path.join(base_path, "mined_rules_items.json"), "r") as f:
        rules = json.load(f)
    outcome_df = pd.read_csv(os.path.join(base_path, "outc_dis_pivot.csv"))
    return rules, outcome_df

rules, outcome_df = load_data()

# --- UI: Inputs ---
st.title("Pediatric ADR-DDI Assessment")

col1, col2 = st.columns(2)
with col1:
    age = st.selectbox("Age Category", ["Child", "Teenager", "Preschooler", "Toddler", "Infant", "Neonate"])
    weight = st.selectbox("Weight", ["Below 5 kg", "5-10 kg", "10-20 kg", "20-40 kg", "40-60 kg", "Above 60 kg"])
with col2:
    sex = st.selectbox("Sex", ["M", "F"])
    country = st.selectbox("Country", [
        "DE",
        "CA",
        "BR",
        "AU",
        "US",
        "MX",
        "FR",
        "JP",
        "ES",
        "RU",
        "CN",
        "GR",
        "IE",
        "PK",
        "GB",
        "CL",
        "CO",
        "RO",
        "IQ",
        "KR",
        "IT",
        "TN",
        "IN",
        "DZ",
        "BE",
        "PR",
        "SA",
        "LV",
        "TR",
        "CZ",
        "PT",
        "NO",
        "DK",
        "AR",
        "UZ",
        "RS",
        "TW",
        "EG",
        "BD",
        "KZ",
        "KG",
        "SE",
        "PL",
        "AE",
        "LB",
        "NL",
        "AT",
        "KE",
        "CH",
        "SY",
        "MG",
        "UY",
        "ZA",
        "TH",
        "IL",
        "MY",
        "NG",
        "SK",
        "PE",
        "KW",
        "HR",
        "UG",
        "UA",
        "EC",
        "BT",
        "PG",
        "NZ",
        "HU",
        "CR",
        "NP",
        "HN",
        "HK",
        "CG",
        "AZ",
        "AF",
        "VN",
        "BA",
        "FI",
        "BG",
        "TJ",
        "SI",
        "PA",
        "PH",
        "LU",
        "ID",
        "GT",
        "GY",
        "MZ",
        "BH",
        "MD",
        "DO",
        "EU",
        "EE",
        "CI",
        "ME",
        "HT",
        "LT",
        "SZ",
        "MA",
        "ZM",
        "AD",
        "GE",
        "UM",
        "IR",
        "JO",
        "TZ",
        "BY",
        "CY",
        "MW",
        "ZW",
        "LK",
        "A1",
        "MT",
        "OM",
        "ET",
        "PY",
        "QA",
        "SS",
        "SG",
        "IS",
        "BO",
        "VE",
        "KP",
        "MK",
        "BJ",
        "PS",
        "ER",
        "RW",
        "VU",
        "SD",
        "NI",
        "GH",
        "TT",
        "SV",
        "BF",
        "AL",
        "AM",
        "BW",
        "nan",
        "MM",
        "JM",
        "XK",
        "GN",
        "RE",
        "CU",
        "TG",
        "NE",
        "CM",
        "TM",
        "ML",
        "TL",
        "CF",
        "CW",
        "GF",
        "LY"
    ])

prescriptions = st.text_area("Prescription Medicines (comma-separated)").strip()



def clean_prescription_name(name: str) -> str:
    """
    Cleans a single prescription drug name for standardized matching:
    - Lowercases
    - Removes punctuations
    - Replaces spaces with underscores
    """
    name = name.lower().strip()
    name = re.sub(r'[^\w\s]', '', name) # Remove punctuation
    name = re.sub(r'\s+', '_', name) # Replace whitespace with underscore
    return name


if st.button("Submit"):
    if prescriptions:
        # --- Create input itemset ---
        input_items = [
            f"demo_age_bin_{age.lower()}",
            f"demo_sex_{sex.lower()}",
            f"demo_origin_{country.lower()}"
            #f"demo_weight_{weight.lower()}"
        ] + [f"drug_{clean_prescription_name(d)}" for d in prescriptions.split(",") if d.strip()]


        input_set = set(input_items) #Making a set to make sure data is not duplicated

        #segregate into drug and demographics seperately for filtering
        manda_demo_set = []
        manda_drug_set = []

        for i in input_set:
            if i.startswith('demo_age_bin_'):
                manda_demo_set.append(i)
            if i.startswith('demo_sex_'):
                manda_demo_set.append(i)
            if i.startswith('demo_origin_'):
                manda_demo_set.append(i)
            if i.startswith('drug_'):
                manda_drug_set.append(i)
        #for testing purposes
        # print(manda_demo_set) 
        # print(manda_drug_set)

        # --- Find matching rules ---
        matched_rows = []
        for i, row in outcome_df.iterrows():
            rule_set = set(eval(row['items_str']))
            if all(attr in rule_set for attr in manda_demo_set) and any(drug in rule_set for drug in manda_drug_set):
                matched_rows.append(row)
                # print('Found a match') #For testing purposes
        
        if matched_rows:
            matched_df = pd.DataFrame(matched_rows)

            case_count = matched_df['outc_ho'].sum() + matched_df['outc_ot'].sum() + matched_df['outc_ri'].sum() 
            + matched_df['outc_ds'].sum() + matched_df['outc_lt'].sum()

            display_out = f'''
{len(matched_df)} similar patterns have been identified.

Found {case_count} outcome cases reported.

'''
            st.divider() 
            st.header('Results')
            st.success(display_out)

            #Extracting reactions specific to the case
            reaction_ls = []
            for i, r in matched_df.iterrows():
                item_set= r['items_str'].split("'")
                # print(item_set)
                for item in item_set:
                    # print(item)
                    if item.startswith('reaction_'):
                        reaction_ls.append(item)

            
            reactions_rec_intrm = [i.replace('_', ' ').title() for i in list(set(','.join(','.join(reaction_ls).split('reaction_')).split(','))) if len(i) > 0 and i != ',']
            # print(reactions_rec_intrm) #For testing

            st.subheader('Reactions Reported')
            for reaction in reactions_rec_intrm:
                st.markdown(f"- {reaction}")


            # --- Show severity breakdown ---
            outcome_cols = ['outc_ds', 'outc_ho', 'outc_lt', 'outc_ot', 'outc_ri']
            severity_labels = {
                'outc_ds': 'Disability',
                'outc_ho': 'Hospitalization',
                'outc_lt': 'Life-Threatening',
                'outc_ot': 'Other Serious',
                'outc_ri': 'Required Intervention to Prevent Permanent Impairment/Damage'
            }

            counts = matched_df[outcome_cols].sum()

            non_zero_counts = counts[counts > 0]
            labels = [severity_labels[col] for col in non_zero_counts.index]

            if not non_zero_counts.empty:
                st.subheader("Outcome Severity Breakdown")
                fig, ax = plt.subplots()
                ax.pie(non_zero_counts, labels=labels, autopct='%1.1f%%', startangle=140)
                ax.axis('equal')
                st.pyplot(fig)
            else:
                st.info("No severity outcomes found for the matched cases.")

            st.markdown('#### Important:')
            st.info(
    "In the analyzed dataset of Adverse Drug Reaction (ADR) cases, "
    "whenever the demographic and drug conditions specified in a rule were present, "
    "the associated reactions and outcomes were also observed in **at least 90%** of those cases.\n\n"
    "**Note:** This represents a statistical correlation observed in historical data. "
    "It does **not** imply a causal relationship or guarantee future outcomes."
)

        else:
            st.warning("No similar cases found in the dataset.")
    else:
        st.error("Please input at least one prescription drug.")
