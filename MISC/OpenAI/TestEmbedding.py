import pandas as pd
import numpy as np
import openai
#https://www.youtube.com/watch?v=ocxq84ocYi0
from openai.embeddings_utils import get_embedding, cosine_similarity

df = pd.read_csv('TWSearchV4.csv')
df['embedding'] = df.embedding.apply(eval).apply(np.array)
print(df)
print("Above is the dataset")
# data_description = "bot commissions and final design"
 
# data_description = "rsa"

# data_description = "ebill"
# data_description = "Get me a solar quote"
# data_description = "i want a quote"
# data_description = "why should i pick trinity solar over anything else?"
# data_description = "how can i save money with trinity solar?"
# data_description = "how can i work for trinity solar?"
# data_description = "who should i pick for solar?"
# data_description = "i want to work for trinity"
# data_description = "I want a sales job in New haven"
data_description = "human resource"
# data_description = "i want to work for trinity"
# data_description = "Show me rsa bots"
# data_description = "show me ebill completed process detail identifiers"
# data_description = "show me bot_Commission_And_Final_Design"
# data_description = "how many rsa bots are there"
# def search_reviews(df, data_description, n=3, pprint=True):
#     embedding = get_embedding(data_description)
#     df['similarities'] = df.embedding.apply(lambda x: cosine_similarity(x, embedding))
#     res = df.sort_values('similarities', ascending=False).head(3)
#     return res

def search_data(df, data_description, n=1, pprint=True):
    product_embedding = get_embedding(
        data_description,
        engine="text-embedding-ada-002"
        # engine="gpt-3.5-turbo"
        # engine="text-similarity-davinci-001"
        # engine="text-davinci-003"
    )
    df["similarity"] = df.embedding.apply(lambda x: cosine_similarity(x, product_embedding))
    df = df.sort_values("similarity", ascending=False)

    print(df['similarity'].head(n).to_string(header=False, index=False))

    results = (
        df.sort_values("similarity", ascending=False)
        .head(1)
        .combined.str.replace("Title: ", "")
        .str.replace("; Content:", ": ")
    )
    if pprint:
        for r in results:
            print(r[:200])
            print()
    return results

print("------------------------------------ANSWER BELOW-------------------------------------")
results = search_data(df, data_description, n=1)
# print(res)