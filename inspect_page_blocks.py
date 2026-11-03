import pymupdf

pdf = pymupdf.open("Professional_Training_I_Real_Estate_AI_Automation_Report.pdf")

print("--- Inspecting Page 1 Blocks ---")
p1 = pdf[0]
for b in p1.get_text("blocks"):
    text = b[4].strip().replace("\n", " ")
    if text:
        print(f"bbox: ({b[0]:.1f}, {b[1]:.1f}, {b[2]:.1f}, {b[3]:.1f}) | align x={b[0]:.1f}-{b[2]:.1f} | text: {text[:60]}")

print("\n--- Inspecting Page 2 Blocks ---")
p2 = pdf[1]
for b in p2.get_text("blocks"):
    text = b[4].strip().replace("\n", " ")
    if text:
        print(f"bbox: ({b[0]:.1f}, {b[1]:.1f}, {b[2]:.1f}, {b[3]:.1f}) | align x={b[0]:.1f}-{b[2]:.1f} | text: {text[:60]}")
