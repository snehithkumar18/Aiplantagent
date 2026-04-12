import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def create_confusion_matrix():
    # Data from the table
    # Classes: Late Blight, Healthy, Scab, Early Blight, Bell Spot
    data = np.array([
        [94, 2, 0, 4, 0],
        [1, 98, 0, 0, 1],
        [0, 0, 95, 0, 5],
        [6, 0, 0, 93, 1],
        [0, 2, 3, 1, 94]
    ])
    labels = ['Tom Late Blight', 'Tom Healthy', 'Apple Scab', 'Pot Early Blight', 'Pep Bell Spot']
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(data, annot=True, fmt="d", cmap="Blues", xticklabels=labels, yticklabels=labels)
    plt.title('Figure 7: Confusion Matrix (Top 5 Classes)', pad=20, fontweight='bold')
    plt.ylabel('True Class', fontweight='bold')
    plt.xlabel('Predicted Class', fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig('fig7_confusion_matrix.png', dpi=300)
    plt.close()
    print("Generated fig7_confusion_matrix.png")

def create_ood_rejection():
    # Data from the table
    categories = ['Human Faces', 'Vehicles', 'Documents', 'Indoor Objects', 'Real Leaves']
    trr = [99.6, 98.8, 100.0, 98.4, 0] # Real leaves TRR is N/A conceptually, FRR is 1.2
    
    x = np.arange(len(categories))
    width = 0.6
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(x, trr, width, color=['skyblue', 'skyblue', 'skyblue', 'skyblue', 'salmon'])
    
    # Customizing the graph
    plt.ylabel('Rejection Rate (%)', fontweight='bold')
    plt.title('Figure 8: Out-of-Distribution Rejection Performance', pad=20, fontweight='bold')
    plt.xticks(x, categories, rotation=15)
    plt.ylim(0, 105)
    
    # Add labels on top of bars
    for i, bar in enumerate(bars):
        yval = bar.get_height()
        if i == 4:
            # For real leaves, we show FRR instead of TRR
            plt.text(bar.get_x() + bar.get_width()/2, 1.2 + 1, '1.2% FRR', ha='center', va='bottom', color='red', fontweight='bold')
            bar.set_height(1.2) # Visually show the FRR
        else:
            plt.text(bar.get_x() + bar.get_width()/2, yval + 1, f'{yval}% TRR', ha='center', va='bottom', color='blue', fontweight='bold')
            
    plt.tight_layout()
    plt.savefig('fig8_ood_rejection.png', dpi=300)
    plt.close()
    print("Generated fig8_ood_rejection.png")

def create_latency_breakdown():
    # Data from the table
    labels = [
        'Ingestion (3.5%)', 
        'YOLO Gate (10.3%)', 
        'MobileNetV2 (6.2%)', 
        'Weather Fetch (4.4%)', 
        'GROQ LLM (54.4%)', 
        'Translation (12.3%)', 
        'TTS Synthesis (8.8%)'
    ]
    sizes = [120, 350, 210, 150, 1850, 420, 300]
    explode = (0, 0, 0, 0, 0.1, 0, 0)  # Explode the LLM part

    plt.figure(figsize=(9, 7))
    colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
    plt.pie(sizes, explode=explode, labels=labels, autopct='', shadow=False, startangle=140, colors=colors)
    plt.title('Figure 9: End-to-End Latency Breakdown (~3400ms Total)', pad=20, fontweight='bold')
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    
    plt.tight_layout()
    plt.savefig('fig9_latency_breakdown.png', dpi=300)
    plt.close()
    print("Generated fig9_latency_breakdown.png")

if __name__ == "__main__":
    create_confusion_matrix()
    create_ood_rejection()
    create_latency_breakdown()
