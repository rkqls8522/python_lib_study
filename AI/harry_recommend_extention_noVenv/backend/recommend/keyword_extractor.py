import time
import yake

def extract_keywords_yake(text):
    start_time = time.time()
    kw_extractor = yake.KeywordExtractor(lan="en", n=1, top=10, dedupLim=0.3)
    keywords = kw_extractor.extract_keywords(text)
    sorted_keywords = sorted(keywords, key=lambda x: x[1])
    top_keywords = [kw for kw, score in sorted_keywords[:4]]
    elapsed_time = time.time() - start_time
    return top_keywords, elapsed_time
