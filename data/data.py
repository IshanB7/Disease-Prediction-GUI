import pandas as pd

disease_to_drug = {
    'Urinary tract infection': 'UTI',
    '(vertigo) Paroymsal  Positional Vertigo': 'Vertigo'
}

drug_to_disease = {
    'Rheumatoid Arthritis': 'Arthritis',
    'GERD (Heartburn)': 'GERD',
    'Colds & Flu': 'Common cold',
    'Allergies': 'Allergy'
}

columns_to_keep = ['drug_name', 'medical_condition', 'rx_otc', 'medical_condition_url', 'drug_link']

# used to compare unique disease names across both datasets
def check():
    diseases = pd.read_csv("./raw/DiseaseAndSymptoms.csv")
    drugs = pd.read_csv("./raw/drugs_for_common_treatments.csv")
    unique_disease = diseases['Disease'].unique()
    df1 = pd.DataFrame(unique_disease)

    unique_drugs = drugs['medical_condition'].unique()
    df2 = pd.DataFrame(unique_drugs)

    df1.to_csv('./disease.csv', index=False)
    df2.to_csv('./condition.csv', index=False)

# make changes based on observations
def clean(path_from = './raw', path_to = './clean'):

    diseases = pd.read_csv(f"{path_from}/DiseaseAndSymptoms.csv")
    drugs = pd.read_csv(f"{path_from}/drugs_for_common_treatments.csv")

    # drop irrelevant columns and rename a column for consistency
    drugs = drugs[columns_to_keep]
    drugs = drugs.rename(columns={'medical_condition': 'Disease'})

    # rename some diseases in both datasets so that the disease name is consistent
    diseases['Disease'] = diseases['Disease'].replace(disease_to_drug)
    diseases = diseases.map(lambda x: x.strip() if isinstance(x, str) else x)
    diseases = diseases.replace('dischromic _patches', 'dischromic_patches')
    drugs['Disease'] = drugs['Disease'].replace(drug_to_disease)

    # drop drugs that are prescription only or do not correspond to a disease
    drugs = drugs[drugs['rx_otc'] != 'Rx']
    drugs = drugs[drugs['Disease'].isin(diseases['Disease'])]

    diseases.to_csv(f'{path_to}/diseases.csv', index=False)
    drugs.to_csv(f'{path_to}/drugs.csv', index=False)

    precautions = pd.read_csv(f'{path_from}/DiseasePrecaution.csv')
    precautions['Disease'] = precautions['Disease'].replace(disease_to_drug)
    precautions.to_csv(f'{path_to}/precautions.csv', index=False)
    
# probability server that will be used by the app
def make_probability_table(path = './clean', validation_split = 0.4):
    diseases = pd.read_csv(f'{path}/diseases.csv')

    unique_diseases = diseases['Disease'].unique().tolist()
    unique_symptoms = diseases.drop(columns=['Disease'])
    unique_symptoms = pd.unique(unique_symptoms.values.flatten())
    unique_symptoms = unique_symptoms[~pd.isna(unique_symptoms)]
    unique_symptoms = unique_symptoms.tolist()

    val_diseases = pd.DataFrame(columns=diseases.columns)
    probability_table = {disease: {} for disease in unique_diseases}

    for disease in unique_diseases:
        disease_data = diseases[diseases['Disease'] == disease]

        # get some amount of validation cases for each disease enumerated
        val_count = int(len(disease_data) * validation_split)
        disease_data = disease_data.sample(frac=1).reset_index(drop=True)
        val_disease_data = disease_data[:val_count]
        val_diseases = pd.concat([val_diseases, val_disease_data], ignore_index=True)

        # use the non-validation cases to learn probability
        disease_data = disease_data[val_count:]
        total_disease_count = float(len(disease_data))

        disease_data = disease_data.drop(columns=['Disease'])
        disease_data = disease_data.values.flatten().tolist()

        # counts the number of times a symptom appears for a disease
        counts = pd.Series(disease_data).value_counts()

        for symptom in unique_symptoms:
            try:
                probability = counts[symptom]/total_disease_count
            except:
                probability = 0
            probability_table[disease][symptom] = probability

    # write the probability table to file
    probability_df = pd.DataFrame(probability_table).T
    probability_df.reset_index(inplace=True)
    probability_df.rename(columns={'index' : 'Disease'}, inplace=True)
    probability_df.set_index('Disease', inplace=True)
    probability_df.to_csv(f'{path}/probabilities.csv')

    # write validation cases to file
    val_diseases.set_index('Disease', inplace=True)
    val_diseases.to_csv(f'{path}/tests.csv')
    

def count_lowest():
    df = pd.read_csv('./raw/drugs_for_common_treatments.csv')
    unique_diseases = df['medical_condition'].unique()
    print(len(unique_diseases))

# clean()
# make_probability_table()