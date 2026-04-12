import matplotlib.pyplot as plt
import matplotlib.patches as patches

def create_testing_diagram():
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('off')
    
    # Define blocks
    blocks = [
        {"text": "Test Image Dataset\n(Leaves + OOD Objects)", "pos": (0.4, 0.85), "color": "#e0e0e0", "width": 0.25},
        
        # Layer 1
        {"text": "Layer 1: Unit Testing\nYOLO Gatekeeper Validation\n(TRR & FRR Metrics)", "pos": (0.15, 0.6), "color": "#aec7e8", "width": 0.3},
        {"text": "Layer 1: Unit Testing\nMobileNetV2 Validation\n(Macro-F1 Score)", "pos": (0.6, 0.6), "color": "#ffbb78", "width": 0.3},
        
        # Layer 2
        {"text": "Layer 2: Integration Testing\nAPI Pipeline Execution\n(GROQ LLM + OpenWeatherMap)", "pos": (0.35, 0.35), "color": "#98df8a", "width": 0.35},
        
        # Layer 3
        {"text": "Layer 3: System Testing\nEnd-to-End Web Latency & TTS\n(P95 Latency Tracking)", "pos": (0.35, 0.1), "color": "#ff9896", "width": 0.35}
    ]
    
    # Draw blocks
    for b in blocks:
        x, y = b["pos"]
        width = b["width"]
        rect = patches.FancyBboxPatch((x, y), width, 0.15, boxstyle="round,pad=0.03", 
                                      linewidth=1.5, edgecolor="black", facecolor=b["color"])
        ax.add_patch(rect)
        ax.text(x + width/2, y + 0.075, b["text"], ha='center', va='center', fontsize=10, fontweight='bold', wrap=True)

    # Draw arrows
    arrows = [
        # From Dataset to Layer 1
        ((0.525, 0.85), (0.3, 0.75)), 
        ((0.525, 0.85), (0.75, 0.75)),
        
        # From Layer 1 to Layer 2
        ((0.3, 0.6), (0.525, 0.5)),
        ((0.75, 0.6), (0.525, 0.5)),
        
        # From Layer 2 to Layer 3
        ((0.525, 0.35), (0.525, 0.25))
    ]
    
    for start, end in arrows:
        ax.annotate('', xy=end, xytext=start, arrowprops=dict(facecolor='black', width=2, headwidth=8))

    plt.title('Figure 6: Multi-Layered Testing and Evaluation Framework', fontweight='bold', pad=20)
    
    output_path = 'fig6_testing_framework.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Generated {output_path}")

if __name__ == "__main__":
    create_testing_diagram()
