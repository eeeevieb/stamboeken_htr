from groq import Groq

input_path = 'image_samples/page/NL-HaNA_2.10.50_71_0006.csv'
description_path = 'information_description.txt'

with open(input_path, 'r') as f:
    input_file = f.read()

with open(description_path, 'r') as f:
    description_file = f.read()

client = Groq()
completion = client.chat.completions.create(
    model="llama3-8b-8192",
    messages=[
        {
            "role": "user",
            "content": "From this csv file"+ input_path +"take the column 'TextEquiv Text' and extract the information metioned in this following file"+ description_file + ". Do not give me the code, just extract these informations "
        }
    ],
    temperature=1,
    max_tokens=1024,
    top_p=1,
    stream=True,
    stop=None,
)

for chunk in completion:
    print(chunk.choices[0].delta.content or "", end="")