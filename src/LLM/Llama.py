from groq import Groq

input_path = "../../image_samples/page/NL-HaNA_2.10.50_71_0006.xml"
description_path = "information_description.txt"

with open(input_path, "r") as f:
    input_file = f.read()

with open(description_path, "r") as f:
    description_file = f.read()

client = Groq()
completion = client.chat.completions.create(
    model="llama-3.1-70b-versatile",
    messages=[
        {
            "role": "user",
            "content": "From xml file"
            + input_path
            + "read the value  and extract the information metioned in this following file"
            + description_file
            + ".\
                  Do not give me the code, just extract these informations. \
                  Just extract the information based on the csv file. \
                  If you cannot find the answer, just say infomration do not match.",
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
