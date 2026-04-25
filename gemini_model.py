import google.generativeai as genai
genai.configure(api_key="AIzaSyA7vz2reDYv10VHFdEgNS3xUhpgSQ9ucxI")
for m in genai.list_models():
    print(m.name)