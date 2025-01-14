import pandas as pd
import numpy as np
from flask import Flask, jsonify, request
from flask_cors import CORS
from data import data

# load all data
data.clean('./data/raw', './data/clean')
data.make_probability_table('./data/clean')
probabilities = pd.read_csv('./data/clean/probabilities.csv', index_col=0)
precautions = pd.read_csv('./data/clean/precautions.csv', index_col=0)
drugs = pd.read_csv('./data/clean/drugs.csv', index_col=1)
P_disease = 1/probabilities.shape[0]

def predict(symptoms, for_graph=False):
    predictions = {}

    # get P(symptom | disease) for all symptom-disease pairs
    for disease in probabilities.index:
        likelihood = 1
        for symptom in symptoms:
            likelihood *= probabilities.loc[disease, symptom]

        predictions[disease] = likelihood * P_disease

    # divide all predictions by sum of probability to get likeliness
    P_total = sum(predictions.values())
    if P_total != 0:
        for disease in predictions:
            predictions[disease] /= P_total

    # return top 5 predictions if its intended for website
    if for_graph:
        top_5_predictions = sorted(predictions.items(), key=lambda x: x[1], reverse=True)[:5] if P_total != 0 else []
        return top_5_predictions

    # return top prediction, to test on validation dataset
    return max(predictions, key=predictions.get)

def accuracy():
    tests = pd.read_csv('./data/clean/tests.csv')
    labels = np.array(tests['Disease'].tolist())
    tests.drop(columns=['Disease'], inplace=True)
    
    symptoms = tests.apply(lambda row: row.dropna().tolist(), axis=1)
    predictions = np.array([predict(each_list) for each_list in symptoms])

    return np.mean(labels == predictions)

# SERVER CODE

server = Flask(__name__)
CORS(server)

# frontend tells server to remake the probability table
# changes P(symptom | disease) by a few %, but does not have impact on most likely class
@server.route('/remake', methods=['GET'])
def remake_probability_table():
    data.make_probability_table('./data/clean')
    probabilities = pd.read_csv('./data/clean/probabilities.csv', index_col=0)
    return jsonify({"message": "done"})

# return list of all symptoms for multi-select in frontend
@server.route('/symptoms', methods=['GET'])
def get_symptoms():
    symptoms = probabilities.columns.tolist()
    return jsonify(symptoms)

# get disease data, name, link, drugs, precautions, links to drug sites
@server.route('/disease', methods=['GET'])
def get_disease():
    disease = request.args.get('name')
    
    disease_precautions = precautions.loc[disease].dropna().tolist()

    # disease may not exist in drugs dataset
    # supported diseases are: [Acne, Allergy, GERD, Migraine, Psoriasis, Arthritis, UTI]
    try:
        load_data = drugs.loc[disease]
        disease_link = load_data['medical_condition_url'].iloc[0]
        disease_drugs = load_data['drug_name'].tolist()
        disease_drug_links = load_data['drug_link'].tolist()
    except:
        disease_link = ""
        disease_drugs = []
        disease_drug_links = []

    disease_data = {}
    disease_data['name'] = disease
    disease_data['precautions'] = disease_precautions
    disease_data['link'] = disease_link
    disease_data['drugs'] = disease_drugs
    disease_data['drug_links'] = disease_drug_links
    
    return jsonify(disease_data)

# @server.route('/accuracy', methods=['GET'])
# def get_accuracy():
#     print("a")

# return predictions to frontend
@server.route('/predict', methods=['POST'])
def make_prediction():
    symptoms = request.json
    predictions = predict(symptoms, for_graph=True)
    return jsonify(predictions)

# run server
if __name__ == "__main__":
    server.run()