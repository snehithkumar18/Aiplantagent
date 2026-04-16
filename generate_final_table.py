import matplotlib.pyplot as plt
import pandas as pd
import os

def create_final_comparison_table():
    # Final curated data for the comparison table
    data = {
        "Feature / Capability": [
            "System Architecture",
            "Input Validation",
            "Diagnostic Precision",
            "Environmental Intel",
            "User Accessibility",
            "Reasoning Engine",
            "Result Delivery",
            "System Reliability"
        ],
        "Traditional Systems": [
            "Single-Model (Flat)",
            "None (Accepts anything)",
            "Full Image Processing",
            "Static / Ignored",
            "Text/English Only",
            "Hardcoded Labels",
            "Disease Name Only",
            "Internet Dependent"
        ],
        "AI Crop Doctor (Proposed)": [
            "Multi-Agent Tiered Resilience",
            "YOLOv8 Plant Gatekeeper",
            "Adaptive ROI Cropping",
            "Real-time Weather Fusion",
            "Multilingual + TTS Audio",
            "Generative LLM Reasoning",
            "4-Pillar Actionable Report",
            "Fault-Tolerant Fallback Logic"
        ]
    }

    df = pd.DataFrame(data)

    # Plot Setup
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.axis('off')

    # Create the table
    table = ax.table(cellText=df.values, 
                     colLabels=df.columns, 
                     cellLoc='left', 
                     loc='center',
                     colColours=['#1a5d1a', '#4a4a4a', '#1a5d1a'], # Dark green for proposed
                     cellColours=[['#f2f2f2']*3]*len(df))

    # Styling the table
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.2, 2.5) # Increase row height

    # Header styling
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_text_props(weight='bold', color='white', fontsize=12)
            cell.set_edgecolor('white')
            if col == 2: # Highlight our system
                cell.set_facecolor('#2d8a2d')
        else:
            cell.set_edgecolor('#d1d1d1')
            if col == 2: # Highlight our system column
                cell.set_text_props(weight='bold', color='#1a5d1a')
                cell.set_facecolor('#e8f5e8')

    plt.title('Comparative Analysis: Traditional Solutions vs. AI Crop Doctor Agent', 
              fontsize=16, fontweight='bold', pad=30, color='#1a5d1a')

    # Add a subtitle or footer
    plt.figtext(0.5, 0.05, "* The proposed system utilizes a tiered reliability architecture with generative reasoning and multi-modal accessibility.", 
                ha="center", fontsize=10, style='italic', color='#666666')

    # Save the plot to a NEW filename
    output_path = 'final_comparison_clean.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight', transparent=False)
    plt.close()
    print(f"Final Comparison table image created: {os.path.abspath(output_path)}")

if __name__ == "__main__":
    create_final_comparison_table()
