import docx

doc = docx.Document(r"D:\Professional Training I template-1 (1).docx")

print("Mapping paragraphs:")
for i, p in enumerate(doc.paragraphs):
    txt = p.text.strip()
    if txt:
        if any(keyword in txt.upper() for keyword in [
            'TITLE', 'PROFESSIONAL TRAINING', 'BONAFIDE', 'DECLARATION', 
            'ACKNOWLEDGEMENT', 'TRAINING CERTIFICATE', 'ABSTRACT', 
            'TABLE OF CONTENTS', 'LIST OF FIGURES', 'LIST OF TABLES', 
            'CHAPTER 1', 'CHAPTER 2', 'CHAPTER 3', 'CHAPTER 4', 'REFERENCES'
        ]):
            print(f"P{i:03d}: [{p.style.name}] {txt[:70]}")
