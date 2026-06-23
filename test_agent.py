from app.ai.agent import process_message


text = """
Բարև, ես Արսենն եմ։
Հեռախոսահամարս +37499960706։
Ատամս ցավում է։
Կուզեմ վաղը ժամը 15:00 գրանցվել։
"""

result = process_message(text)

print(result)