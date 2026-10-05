from resume_parser import extract_resume_text

file_path = input("Enter the full path of your resume: ")

with open(file_path, "rb") as file:
    file_bytes = file.read()


class UploadedFile:
    def __init__(self, name, data):
        self.name = name
        self.data = data

    def getvalue(self):
        return self.data


uploaded_file = UploadedFile(
    file_path,
    file_bytes
)

text = extract_resume_text(uploaded_file)

print("\n--- EXTRACTED RESUME TEXT ---\n")
print(text)