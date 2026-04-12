import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os

def create_yolo_diagram():
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('off')
    
    # Define blocks
    blocks = [
        {"text": "Input Device/UI\nRaw Image (640x640)", "pos": (0.1, 0.8), "color": "#e0e0e0"},
        {"text": "CSPNet Backbone\n(Feature Extraction)", "pos": (0.1, 0.5), "color": "#aec7e8"},
        {"text": "PANet Neck\n(Feature Aggregation)", "pos": (0.5, 0.5), "color": "#ffbb78"},
        {"text": "YOLO Head\n(BBox & Class Preds)", "pos": (0.5, 0.2), "color": "#98df8a"},
        {"text": "Non-Maximum\nSuppression (NMS)", "pos": (0.8, 0.2), "color": "#ff9896"},
        {"text": "Output Validation\nPlant vs Non-Plant", "pos": (0.8, 0.5), "color": "#c5b0d5"}
    ]
    
    # Draw blocks
    for i, b in enumerate(blocks):
        x, y = b["pos"]
        rect = patches.FancyBboxPatch((x, y), 0.15, 0.15, boxstyle="round,pad=0.02", 
                                      linewidth=1.5, edgecolor="black", facecolor=b["color"])
        ax.add_patch(rect)
        ax.text(x + 0.075, y + 0.075, b["text"], ha='center', va='center', fontsize=9, fontweight='bold', wrap=True)

    # Draw arrows
    arrows = [
        ((0.175, 0.8), (0.175, 0.65)),
        ((0.25, 0.575), (0.5, 0.575)),
        ((0.575, 0.5), (0.575, 0.35)),
        ((0.65, 0.275), (0.8, 0.275)),
        ((0.875, 0.35), (0.875, 0.5))
    ]
    
    for start, end in arrows:
        ax.annotate('', xy=end, xytext=start, arrowprops=dict(facecolor='black', width=2, headwidth=8))

    plt.title('Figure 4: Simplified YOLO-based Plant Pre-Detection Architecture', fontweight='bold', pad=20)
    
    output_path = 'fig4_yolo_architecture.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Generated {output_path}")

def create_mobilenet_diagram():
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.axis('off')
    
    # Define blocks
    blocks = [
        {"text": "Input Leaf Image\n(224x224 RGB)", "pos": (0.1, 0.7), "color": "#e0e0e0"},
        {"text": "Initial 3x3 Conv\n(Feature Abstraction)", "pos": (0.3, 0.7), "color": "#aec7e8"},
        {"text": "Inverted Residuals\n(Bottleneck Blocks)", "pos": (0.5, 0.7), "color": "#ffbb78"},
        {"text": "Global Avg Pool\n(1280-D Vector)", "pos": (0.7, 0.7), "color": "#98df8a"},
        {"text": "Linear Classifier\n(38 Disease Classes)", "pos": (0.9, 0.7), "color": "#ff9896"},
        
        # Detail Block
        {"text": "Bottleneck Block Detail:\n1. 1x1 Expansion (Increase Dims)\n2. 3x3 Depthwise Conv (Spatial)\n3. 1x1 Projection (Linear/Decrease Dims)", 
         "pos": (0.5, 0.2), "color": "#f7b6d2", "width": 0.3}
    ]
    
    # Draw blocks
    for i, b in enumerate(blocks):
        x, y = b["pos"]
        width = b.get("width", 0.15)
        rect = patches.FancyBboxPatch((x, y), width, 0.15, boxstyle="round,pad=0.03", 
                                      linewidth=1.5, edgecolor="black", facecolor=b["color"])
        ax.add_patch(rect)
        ax.text(x + width/2, y + 0.075, b["text"], ha='center', va='center', fontsize=9, fontweight='bold', wrap=True)

    # Draw arrows
    arrows = [
        ((0.25, 0.775), (0.3, 0.775)),
        ((0.45, 0.775), (0.5, 0.775)),
        ((0.65, 0.775), (0.7, 0.775)),
        ((0.85, 0.775), (0.9, 0.775)),
        
        # To detail block
        ((0.575, 0.7), (0.575, 0.35))
    ]
    
    for i, (start, end) in enumerate(arrows):
        style = '--' if i == 4 else '-'
        ax.annotate('', xy=end, xytext=start, arrowprops=dict(facecolor='black', width=2, headwidth=8, linestyle=style))

    plt.title('Figure 5: MobileNetV2 Disease Classification Architecture', fontweight='bold', pad=20)
    
    output_path = 'fig5_mobilenet_architecture.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Generated {output_path}")

if __name__ == "__main__":
    create_yolo_diagram()
    create_mobilenet_diagram()
