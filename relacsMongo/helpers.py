import numpy as np
import pandas as pd 
import json
import math
from io import StringIO 

#COLUMNS = ['Temperature (K)', 'Magnetic Field (Oe)', "AC X' (emu/Oe)", "AC X'' (emu/Oe)", "AC Frequency (Hz)"]
COLUMNS = ['Temperature', 'MagneticField', 'ChiPrime', 'ChiBis', 'Frequency']
NEW_COLUMNS = {'Temperature': 'Temperature (K)', 'MagneticField': 'Magnetic Field (Oe)', 'ChiPrime': "AC X' (emu/Oe)", 'ChiBis': "AC X'' (emu/Oe)", 'Frequency': "AC Frequency (Hz)"}

def mergeLists(list1, list2):
    return list(np.unique(list1, list2))

def get_data_from_csv(measurements_csv):
    
    data_file = StringIO(measurements_csv)
    data = pd.read_csv(data_file)
    data = data.sort_values(NEW_COLUMNS['Temperature'])
    columns_swapped = {value:key for key, value in NEW_COLUMNS.items()}
    data = data.rename(columns=columns_swapped)
    data = data[COLUMNS]
    return data
   
def calculate_additional_measurements(data, molar_mass, probe_mass):
    
    data["ChiPrimeMol"] = data["ChiPrime"] * molar_mass/probe_mass
    data["ChiBisMol"] = data["ChiBis"] * molar_mass/probe_mass
    data["Omega"] = 2 * data["Frequency"] * np.pi
    data["OmegaLog"] = np.log10(data["Omega"])
    data["FrequencyLog"] = np.log10(data["Frequency"])

    data = data.sort_values('Temperature')

    return data

def clusterize(data, field_epsilon, tmp_epsilon):
    fields = cluster(data, "MagneticField", field_epsilon)
    for i in list(range(0, len(fields))):
            fields[i] = cluster(fields[i], "Temperature", tmp_epsilon)
    return fields

def cluster(data, by, epsilon, reindex=False):
    sorted_data = data.sort_values(by=by).copy()
    min_value = sorted_data[by].min()
    results = []
    df = pd.DataFrame(columns=data.columns)

    for _, row in sorted_data.iterrows():
            if row[by] <= min_value + epsilon:
                df.loc[-1] = row
                df.index = df.index + 1
            else:
                results.append(df)
                df = pd.DataFrame(columns=data.columns)
                min_value = row[by]
                df.loc[-1] = row
                df.index = df.index +1
        
    results.append(df)

    if reindex:
        i:int
        for i in range(0, len(results)):
            results[i] = results[i].sort_values(by, ascending=False).reset_index(drop=True)

        # i: int
    for i in range(0, len(results)):
            results[i] = results[i].sort_values("Omega")
    
    return results

def measurize(measurement, file_name, field_epsilon, tmp_epsilon):
    accuracy_temp: float = math.log10(tmp_epsilon)
    if(tmp_epsilon >= 1):
        accuracy_temp = 0
    else:
        accuracy_temp = abs(math.floor(accuracy_temp) + 1)

    accuracy_field: float = math.log10(field_epsilon)
    if(tmp_epsilon >= 1):
        accuracy_field = 0
    else:
        accuracy_field = abs(math.floor(accuracy_field) + 1)
        
    temp = round((measurement["Temperature"].max() + measurement["Temperature"].min())/2, accuracy_temp)
    field = round((measurement["MagneticField"].max() + measurement["MagneticField"].min())/2, accuracy_field)

    if '.' in file_name:
        file_name = file_name.split('.')[0]

    name = f"T: {temp}K H: {field}Oe {file_name}"
    length = len(measurement["Frequency"])
    measurement["Hidden"] = pd.Series(np.zeros(length), index=measurement.index)
    
    return {'name': name, 'df': measurement, 'temp': temp, 'field': field}
    return Measurement(name, df, temp, field, compound, collection)  

def getMeasurement(document, measurement_id):
        for measurement in document['measurements']:
             if measurement['name'] == measurement_id:
                  return measurement
             
        return None
             
        