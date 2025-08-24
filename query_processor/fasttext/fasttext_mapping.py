# from query_processor.config import config
#
# import fasttext
# import numpy as np
# from sklearn.metrics.pairwise import cosine_similarity
# from unidecode import unidecode
# import re
#
from util.schemas import PostAnalysisResult
from collections import Counter
import json

from query_processor.config import config
#
# ft = fasttext.load_model(config.FASTTEXT.PATH)
#
# EKMAN_SEEDS = {
#     "alegria": ["felicidad","satisfaccion","bienestar","entusiasmo","gratitud","gozo","contento","alegre","animado"],
#     "tristeza": ["pena","desanimo","soledad","melancolia","decepcion","afliccion","triste","abatido"],
#     "ira": ["enojo","frustracion","rabia","irritacion","resentimiento","bronca","enfado"],
#     "miedo": ["temor","ansiedad","inseguridad","preocupacion","panico","susto","nervioso"],
#     "sorpresa": ["asombro","sorpresa","desconcierto","inesperado","perplejidad"],
#     "asco": ["rechazo","repulsion","desagrado","aversion","asco","nausea"]
# }
# EMOS = list(EKMAN_SEEDS.keys())
#
# # --- Utilidades ---
# def norm(s: str) -> str:
#     s = (s or "").strip().lower()
#     s = unidecode(s)
#     # Conservo 'x' y '@' para tratarlas antes de eliminarlas
#     s = re.sub(r"[^\w\s@x]", " ", s)
#     s = re.sub(r"(.)\1{2,}", r"\1", s)  # "muuuy" -> "muy"
#     s = re.sub(r"\s+", " ", s).strip()
#     return s
#
# def inclusive_variants(token: str):
#     """
#     Genera variantes simples para inclusivo.
#       - amigx/@ -> amigo, amiga
#       - opcionalmente palabra terminada en 'e' -> o/a (p.ej. contente -> contento/contanta; útil en algunos casos)
#     """
#     vs = {token}
#
#     # amigx / amig@ -> amigo / amiga
#     if re.search(r"(x|@)\b", token):
#         vs.add(re.sub(r"(x|@)\b", "o", token))
#         vs.add(re.sub(r"(x|@)\b", "a", token))
#
#     # forma con 'e' al final -> probar o/a
#     if re.search(r"e\b", token):
#         vs.add(re.sub(r"e\b", "o", token))
#         vs.add(re.sub(r"e\b", "a", token))
#
#     return list(vs)
#
# def vec(token: str) -> np.ndarray:
#     return ft.get_sentence_vector(token)
#
# # Prototipos por emoción (promedio de seeds)
# EMO_VECS = {emo: np.mean([vec(w) for w in words], axis=0) for emo, words in EKMAN_SEEDS.items()}
# EMO_MAT = np.vstack([EMO_VECS[e] for e in EMOS])  # (6 x 300)
#
# def best_vector(token: str) -> np.ndarray:
#     """
#     Elige la mejor variante inclusiva evaluando su máxima similitud contra los centroides.
#     Si ninguna mejora, usa el original. Mantiene el cálculo en una sola pasada simple.
#     """
#     candidates = inclusive_variants(token)
#     best_v = None
#     best_sim = -1.0
#     for ct in candidates:
#         v = vec(ct).reshape(1, -1)
#         m = float(np.max(cosine_similarity(v, EMO_MAT)[0]))
#         if m > best_sim:
#             best_sim, best_v = m, v
#     return best_v.reshape(-1)
#
# def map_word(word: str, threshold: float = config.FASTTEXT.THRESHOLD, debug: bool = False):
#     w = norm(word)
#     wv = best_vector(w).reshape(1, -1)
#     sims = cosine_similarity(wv, EMO_MAT)[0]
#     j = int(np.argmax(sims))
#     if debug:
#         print({emo: float(s) for emo, s in zip(EMOS, sims)})
#     return (EMOS[j], float(sims[j])) if sims[j] >= threshold else ("neutral", float(sims[j]))

with open("fasttext/mapping.json", "r", encoding="utf-8") as f:
    fixed_mapping = json.load(f)

def map_affective_states_to_emotions(affective_states):
    """Maps the result of the emotional analysis to a fixed set of emotions."""
    emotions=[]
    if len(affective_states) == 0:
        return ["neutral"]
    for state in affective_states.keys():
        for key, mapped_list in fixed_mapping.items():
            genderless_state = f"{state[:-1]}x"
            if state in mapped_list or genderless_state in mapped_list:
                emotions.append(key)
    counts = Counter(emotions)
    max_count = max(counts.values())
    most_common = [k for k, v in counts.items() if v == max_count]
    return most_common

def map_to_ekman_fasttext(result_list: list[PostAnalysisResult]):
    """Return normalized summary of affective states and mapped emotions."""
    for result in result_list:
        result["dominant_emotions"] = map_affective_states_to_emotions(result["affective_states"])
