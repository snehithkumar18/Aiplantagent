import sys
sys.path.append('c:/Users/NEHITH/Documents/crop-ai-agent-repo')
import torch
import torchvision
from torchvision import models, transforms
from PIL import Image

weights = models.ResNet18_Weights.DEFAULT
model = models.resnet18(weights=weights)
model.eval()

tf = weights.transforms()
categories = weights.meta["categories"]

def is_plant_resnet(image_path):
    img = Image.open(image_path).convert("RGB")
    x = tf(img).unsqueeze(0)
    with torch.no_grad():
        preds = model(x)
        probs = torch.softmax(preds, dim=1)[0]
        top_prob, top_idx = torch.topk(probs, 3)
    
    classes = [categories[idx] for idx in top_idx]
    
    # We can write a simple heuristic or pass these to LLM
    return classes

print("Girl 1:", is_plant_resnet("uploads/ChatGPT_Image_Mar_13_2026_06_16_03_PM.png"))
print("Girl 2:", is_plant_resnet("uploads/ChatGPT_Image_Mar_13_2026_06_43_39_PM.png"))
print("Cat:", is_plant_resnet("uploads/cat.jpg"))
print("Apple rust:", is_plant_resnet("uploads/Screenshot_2026-03-01_003551.png"))
print("Tomato blight:", is_plant_resnet("uploads/Screenshot_2026-03-01_003447.png"))
