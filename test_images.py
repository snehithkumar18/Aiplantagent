import os
import sys
sys.path.append('c:/Users/NEHITH/Documents/crop-ai-agent-repo')
from autogen_agents import detect_disease_hf

uploads = 'uploads'
with open('test_results.txt', 'w', encoding='utf-8') as f:
    if os.path.exists(uploads):
        for img in os.listdir(uploads):
            if img.endswith(('.png', '.jpg', '.jpeg')):
                path = os.path.join(uploads, img)
                res = detect_disease_hf(path)
                f.write(f'{img}: {res.get("disease")} ({res.get("confidence")})\n')
print("Testing complete. Check test_results.txt")
