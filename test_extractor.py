from app.ai.extractor import extract_patient_data


text = """
Բարև, ես Արսենն եմ։
Հեռախոսահամարս +37499960706։
Ատամս ցավում է։
Կուզեմ վաղը ժամը 15:00 գրանցվել։
"""

result = extract_patient_data(text)

print(result)