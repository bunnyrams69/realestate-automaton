import docx
import os

doc = docx.Document(r"D:\Professional Training I template-1 (1).docx")

print("Checking inline shapes and images...")
images = []
for rel in doc.part.rels.values():
    if "image" in rel.target_ref:
        images.append((rel.target_ref, len(rel.target_part.blob)))

print(f"Total image parts: {len(images)}")
for img_ref, size in images:
    print(f"  Image: {img_ref}, Size: {size} bytes")
