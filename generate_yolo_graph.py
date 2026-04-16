import matplotlib.pyplot as plt
import numpy as np
import os

def create_yolo_comparison_graph():
    # Data for YOLO comparison (Plant vs Non-Plant Detection)
    detectors = ['YOLOv8 (Proposed)', 'SSD (Single Shot)', 'Faster R-CNN', 'Classical (HOG+SVM)']
    accuracy = [99.2, 92.5, 95.8, 78.5]
    inference_time = [15, 35, 120, 60]  # in milliseconds

    # Plot Setup
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Bar width and positions
    bar_width = 0.35
    index = np.arange(len(detectors))

    # Bar Chart for Detection Accuracy
    bars1 = ax1.bar(index, accuracy, bar_width, label='Detection Accuracy (%)', color='#1f77b4') 
    ax1.set_ylabel('Detection Accuracy (%)', color='#1f77b4', fontweight='bold')
    ax1.set_ylim(70, 105)
    ax1.tick_params(axis='y', labelcolor='#1f77b4')
    ax1.set_title('Plant vs. Non-Plant Detection: Detector Comparison', pad=20, fontweight='bold', fontsize=14)
    ax1.set_xticks(index)
    ax1.set_xticklabels(detectors, fontweight='bold')

    # Line Chart for Inference Time
    ax2 = ax1.twinx()
    line1 = ax2.plot(index, inference_time, color='#d62728', marker='s', 
                     linewidth=2.5, markersize=10, label='Inference Time (ms)')
    ax2.set_ylabel('Inference Time (ms) - Lower is Better', color='#d62728', fontweight='bold')
    ax2.set_ylim(0, 150)
    ax2.tick_params(axis='y', labelcolor='#d62728')

    # Add legends
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc='upper right')

    # Add numeric labels to bars
    for bar in bars1:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2, yval + 1, 
                 f'{yval}%', ha='center', va='bottom', color='#1f77b4', fontweight='bold')

    # Add numeric labels to line markers
    for i, txt in enumerate(inference_time):
        ax2.annotate(f'{txt}ms', (index[i], inference_time[i] + 5), 
                     ha='center', va='bottom', color='#d62728', fontweight='bold')

    plt.tight_layout()
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    
    # Save the plot
    output_path = 'yolo_comparison_graph.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Graph successfully created and saved as: {os.path.abspath(output_path)}")

if __name__ == "__main__":
    create_yolo_comparison_graph()
