from sentence_transformers import SentenceTransformer
from numpy.linalg import norm
import jsonlines

model = SentenceTransformer(R'jinaai/jina-embeddings-v2-base-zh', trust_remote_code=True)
cos_sim = lambda a,b: (a @ b.T) / (norm(a)*norm(b))

def evaluate_similarity(text1, text2):
    embeddings = model.encode([text1, text2])
    cosine_similarity = cos_sim(embeddings[0], embeddings[1])
    return cosine_similarity.item()

def is_description_valid(pic_name, description, similarity_threshold=0.4):
    invalid_keywords = [
        "无法为你提供",
        "不允许我",
        "不敬或冒犯",
        "无法解读",
        "内容被屏蔽",
    ]
    for keyword in invalid_keywords:
        if keyword in description or evaluate_similarity(keyword, description) > similarity_threshold:
            return False
    similarity_score = evaluate_similarity(pic_name, description)
    if similarity_score < similarity_threshold:
        return False
    return True
input_file = "/content/drive/MyDrive/ChineseBQB-gemini-1.5-pro-latest.jsonl"
output_file = "/content/drive/MyDrive/ChineseBQB-gemini-1.5-pro-latest_output.jsonl"
invalid_file = "/content/drive/MyDrive/ChineseBQB-gemini-1.5-pro-latest_invalid.jsonl"

with jsonlines.open(output_file, mode="w") as outfile, jsonlines.open(
    invalid_file, mode="w"
) as invalid_file:
    with jsonlines.open(input_file) as infile:
        for line in infile:
            pic_name = line["picName"]
            description = line["description"]
            if not is_description_valid(pic_name, description):
                invalid_file.write(line)
                continue
            outfile.write(line)
