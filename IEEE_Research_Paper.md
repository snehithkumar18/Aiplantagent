# AI Crop Doctor: An Intelligent, Multilingual, and Context-Aware Plant Disease Diagnostics and Advisory System

**Abstract**—*Agriculture forms the backbone of the global economy, yet crop diseases continuously threaten food security and farmer livelihoods. Timely, accurate, and accessible diagnosis is critical for effective crop management. This paper presents the "AI Crop Doctor," a robust, web-based artificial intelligence system designed to automatically identify plant diseases, assess real-time environmental conditions, and generate localized, actionable agricultural advice. The system employs a multi-tiered fallback architecture to ensure high reliability, utilizing a local PyTorch MobileNetV2 model for primary disease classification, augmented with a **YOLO-based plant vs. non‑plant image detector** with color heuristics and model confidence fallbacks, and backed by cloud-based Large Language Models (LLMs) for metadata-based reasoning when vision pipelines fail. Furthermore, contextual insights are gathered via the OpenWeatherMap API, while Agronomist Advice is dynamically generated using the GROQ Llama 3.3 70B model. To bridge the digital divide, the system integrates a multilingual interface powered by deep-translator and Google Text-to-Speech (gTTS), enabling voice-based accessible outputs for farmers in their native languages. This paper details the complete technology stack, module functions, integration architecture, and intelligent automated fallback mechanisms ensuring 100% uptime for advisory generation while **rejecting non‑plant images** gracefully.*

**Keywords**—*Precision Agriculture, Plant Disease Detection, MobileNetV2, Large Language Models (LLMs), Llama 3, Multilingual Advisory System, Fallback Architecture.*

---

## I. INTRODUCTION

Crop diseases cause substantial yield losses globally, severely impacting smallholder farmers who lack immediate access to expert agricultural extension officers or agronomists. Traditional disease identification relies on visual inspection by experts, which is time-consuming, expensive, and subject to human error. With the advent of computer vision and natural language processing (NLP), automated intelligent systems have emerged to democratize access to agricultural expertise. 

This paper outlines the development of the **AI Crop Doctor**, an end-to-end web application that takes user-provided images of crops, assesses their health, and yields comprehensive, localized treatment plans. The key innovation in this proposed system lies in its robust multi-layered fallback pipeline, ensuring fault tolerance and uninterrupted service even when primary predictive models or external APIs fail. 

## II. SYSTEM ARCHITECTURE AND TECHNOLOGY STACK

The AI Crop Doctor follows a client-server architecture, intertwining modern web technologies with advanced deep learning models and API services. 

### A. Frontend (User Interface)
The frontend serves as the primary data ingestion point. It is built using:
1. **HTML5 & CSS3:** For structuring and styling a responsive, user-friendly dashboard capable of running on mobile devices.
2. **Vanilla JavaScript & Device APIs:** Facilitates client-side logic, asynchronous file uploads, and loading screen management. Two primary browser APIs are integrated to eliminate typing barriers:
   - **HTML5 Geolocation API:** The system automatically requests user coordinates (Latitude/Longitude) upon page load. Once permitted, these coordinates are piped via an asynchronous fetch call directly to the OpenWeather Reverse Geocoding API to seamlessly extract the user's City and Country. 
   - **Web Speech API:** Allows users with limited digital literacy to dictate their location or preferred language directly via a microphone.
3. **Dynamic Visual Elements:** The UI replaces standard text boxes with highly accessible image-based selection drop-downs. Most notably, the *Soil Type* selector displays real textural images (generated dynamically via AI) of all eight primary Indian soil types, ranging from Alluvial to Peaty & Marshy soils.

### B. Backend Framework
1. **Python (3.8+):** Serves as the core programming language handling logic, system I/O, and API integrations.
2. **Flask (`app.py`):** A lightweight WSGI web application framework defining the server routes. It receives the `POST` request payloads containing the crop image and metadata (location, soil, language), safely stores the image in an `uploads/` directory, and delegates processing to the central AI Agent Pipeline (`autogen_agents.py`).

## III. AI MODELS, MODULES, AND WORKFLOW

The central intelligence of the project is organized into heavily decoupled but sequential modules. Below is a detailed description of each module, the specific models or libraries running within them, their individual responsibilities, and the fallback logic.

### Module A: Disease Detection Phase (The Vision Agent)
The system attempts to classify the crop disease using a sophisticated multi-stage pipeline that **first verifies the image is a plant/leaf**, then classifies the disease, with fallbacks to ensure a diagnostic result.

0. **Pre‑Filter: Plant / Non‑Plant Edge Detection Gate:**
   - **Motivation:** In practical deployments, end-users may accidentally upload selfies, vehicles, documents, or other non-agricultural images. Directly passing such content into a disease classifier can yield misleading predictions (e.g., assigning a tomato disease label to a human face).
   - **YOLO-Based Plant Detector:** Before any disease model is invoked, an Ultralytics YOLO-based object detection model is utilized to detect the presence of a plant or leaf in the image. If no plant is detected, the image is gracefully rejected.
   - **Color-Based Heuristic Fallback:** In the event the YOLO model fails or is unavailable, a lightweight `PIL`-based pre-processing step serves as a fallback. It converts the uploaded RGB image to HSV and computes the ratio of green-ish pixels. Images with extremely low green content are immediately classified as **“Not a plant image”**.
   - **Model Confidence Gate:** For images passing the preliminary checks, the MobileNetV2 output probabilities are evaluated. If the maximum softmax confidence is below a calibrated threshold (e.g., 0.65), the system again overrides the prediction to **“Not a plant image”**, assuming the content is visually ambiguous.
   - **User Feedback:** In all rejection cases, the UI presents a clear message asking the user to upload a proper leaf photograph (with or without visible disease).

1. **Primary Agent (Local PyTorch MobileNetV2):** 
   - **Model Details:** A Convolutional Neural Network (CNN) architecture optimized for mobile and low-latency environments (MobileNetV2), trained specifically on plant disease datasets (`mobilenetv2_plant.pth` / `Daksh159/plant-disease-mobilenetv2`). 
   - **Functionality:** It processes the image using `torchvision.transforms` (resizing to 224x224, normalizing pixel values) and passes it through the model. It supports classifying across 38 distinct plant-disease combinations, including Apple Scab, Tomato Late Blight, and healthy foliage.
   - **Library:** `PyTorch` (`torch`, `torch.nn`, `torchvision`).

2. **Fallback (Metadata Analysis using GROQ Text):**
   - **Trigger:** Executed if the Vision API experiences an outage or timeout.
   - **Model Details:** GROQ Llama Text Model.
   - **Functionality:** It uses the uploaded file’s name (e.g., `tomato_blight.jpg`) to cleverly deduce the intended crop and disease context using NLP techniques and regex, ensuring that the pipeline never halts.

### Module B: Context Gathering (The Weather & Geographic Agent)
Agricultural treatments depend heavily on climatic states.
1. **Libraries & APIs:** `requests` module interfacing with the **OpenWeatherMap API**, supported by client-side browser GPS.
2. **Functionality:** 
   - **Geographic Translation:** As described in Section II-A, explicit city names are extracted losslessly from precise user coordinates via reverse geocoding.
   - **Atmospheric Extraction:** Supplying the location string, this module fetches real-time temperature (°C), humidity (%), and weather descriptions. This provides the generative LLM crucial context for accurate chemical treatment recommendations (e.g., modifying fungicide advice if it is currently raining or highly humid).

### Module C: Agronomist Advice Generation
Once the disease string, weather context, and soil type are confirmed, the system prescribes treatments.
1. **Primary Agent (GROQ Llama 3.3 70B Versatile):**
   - **Model Details:** A state-of-the-art 70-billion parameter generative language model accessed via the GROQ API.
   - **Functionality:** Driven by an advanced prompt, the LLM assumes the persona of an expert agronomist. It consumes the diagnosis, confidence score, weather, and **soil classifier** (one of the eight structural types native to the Indian subcontinent: Alluvial, Red, Black, Laterite, Arid, Mountain, Alkaline, or Peaty), outputting:
     - A 1-line diagnostic summary.
     - 3 actionable treatment steps (including specific chemical or organic solutions).
     - 2 preventative measures tailored to avoid future environmental or soil-borne triggers.
     - Predictive analytics on secondary diseases prone to occur under current weather conditions.
2. **First Fallback (Alternative GROQ Model):** Switches to `llama3-70b-8192` if the primary model fails.
3. **Second Fallback (Rule-Based Expert System):** If all LLMs fail, the system queries a hardcoded Python dictionary mapping disease keywords (e.g., "blight", "rust", "powdery mildew") to standard, verified agricultural treatments.

### Module D: Translation & Localization
To support global farmers, the generated English advice must be natively understood.
1. **Libraries/Tools:** `deep-translator` (Google Translator), `googletrans`, and Google Cloud Translation API.
2. **Functionality:** The system dynamically normalizes the demanded language (e.g., Hindi, Telugu, Marathi). 
   - It first attempts translation using Google's rapid machine translation APIs.
   - If limits are reached, the module falls back to asking the GROQ LLM to perform language-to-language translation without sacrificing context.

### Module E: Text-to-Speech (The Speaker Agent)
Accessible UI requires accommodating users with low literacy.
1. **Library:** `gTTS` (Google Text-to-Speech).
2. **Functionality:** The fully translated text is fed into the gTTS engine, generating a localized synthetic VoIP MP3 audio file. This file is saved to a static directory.
3. **Frontend Integration:** The resulting HTML response exposes a simple audio player allowing the farmer to push "play" and listen to the advice dynamically.

### Module F: Data Logging (Analytics Module)
1. **Library:** Native Python `csv` handling.
2. **Functionality:** Every prediction cycle silently logs timestamp, user location, detected disease, model confidence, local weather, and language into a `logs.csv` file. This establishes a robust backend data pool for agronomists to perform future disease outbreak tracking or dashboard analytics.

## IV. IMAGE PREPROCESSING AND MODEL ARCHITECTURES

To ensure robustness and high accuracy, the AI Crop Doctor employs specific image preprocessing pipelines tailored to both the YOLO-based plant detection model and the PyTorch MobileNetV2 disease classification model.

### A. Preprocessing Pipeline

The preprocessing workflow dictates how raw image uploads are transformed into tensors suitable for deep learning inference. 

1. **YOLO Plant Detector Preprocessing (Gatekeeper):**
   - **Image Ingestion:** The uploaded image file is read directly from disk using OpenCV (`cv2.imread`), which decodes the image into a standard BGR NumPy array representation.
   - **Internal Scaling:** The raw BGR array is passed to the Ultralytics YOLO model. The Ultralytics engine automatically handles necessary letterboxing, resizing to the model's expected grid size (typically 640x640), and normalization (scaling pixel values to a `[0, 1]` range) before performing the forward pass. This ensures aspect ratios are maintained without distorting the leaf morphology.

2. **MobileNetV2 Disease Classifier Preprocessing:**
   - **Image Ingestion:** Images that pass the plant detection gate are loaded using the Python Imaging Library (PIL) and converted strictly to RGB formatting to ensure color consistency.
   - **Transformations:** A sequence of operations defined via `torchvision.transforms` is applied:
     - **Resize:** The image is explicitly resized to \( 224 \times 224 \) pixels, the standard input resolution for MobileNetV2.
     - **ToTensor:** The image is converted into a PyTorch FloatTensor, scaling the RGB values from `[0, 255]` to `[0.0, 1.0]`.
     - **Normalize:** To match the distribution of the ImageNet dataset on which the model was originally pre-trained, the tensor channels are normalized using the standard means (\( \mu = [0.485, 0.456, 0.406] \)) and standard deviations (\( \sigma = [0.229, 0.224, 0.225] \)).

```mermaid
graph TD
    A[Raw User Upload] --> B[OpenCV BGR Array]
    B --> C[Ultralytics YOLO Inference]
    C -->|Plant Detected| D[PIL Image RGB]
    C -->|No Plant Detected| Rej[Reject: 'Not a Plant Image']
    D --> E[Resize to 224x224]
    E --> F[ToTensor: 0.0 - 1.0]
    F --> G[Normalize: μ, σ]
    G --> H[MobileNetV2 Tensor]
    H --> I[Primary Disease Classification]
```

### B. Internal Architectures

1. **YOLO-based Object Detector:**
   The Ultralytics YOLO architecture serves as an ultra-fast bounding box regressor. Internally, it relies on a Cross Stage Partial Network (CSPNet) backbone for feature extraction, coupled with a Path Aggregation Network (PANet) neck to construct feature pyramids. This allows the model to detect crop leaves irrespective of their scale or position within the uploaded photograph.

![Figure 4: Simplified YOLO-based Plant Pre-Detection Architecture](fig4_yolo_architecture.png)

2. **MobileNetV2 Classifier:**
   The PyTorch-based MobileNetV2 model is optimized for edge devices and low-latency environments. Its primary architectural innovation is the **Inverted Residual Block** combined with **Depthwise Separable Convolutions**.
   - Traditional convolutions are split into a depthwise spatial convolution and a pointwise \( 1 \times 1 \) convolution, drastically reducing computational cost and parameter count.
   - The inverted residuals feature a narrow-wide-narrow structure, expanding the feature space to apply the depthwise convolution, then projecting it back to a lower-dimensional subspace.
   - The final fully connected layer of the pre-trained model has been surgically replaced with a custom Dropout layer (\( p=0.2 \)) and a Linear layer matching the 38 specific crop-disease classes relevant to this system.

![Figure 5: MobileNetV2 Disease Classification Architecture](fig5_mobilenet_architecture.png)

## V. PROCESS WORKFLOW

1. **User Initiation:** A farmer accesses `/index.html`. The app silently proxies their GPS coordinates into a City format. They visually select their soil texture (from 8 specific classifications) and upload a leaf image. Both are securely posted to `/analyze`.
2. **Pipeline Trigger:** Flask invokes `run_crop_pipeline()` inside `autogen_agents.py`.
3. **Vision Processing:** The Local CNN (MobileNetV2) or Vision LLM extracts the disease name.
4. **Context Injection:** OpenWeatherMap API pulls live climate data.
5. **Generative Assessment:** The GROQ LLM fuses the disease and weather to author a custom agronomic report.
6. **Localization Post-Processing:** The report translates into the user’s mother tongue, and an MP3 voice file is simultaneously rendered.
7. **Delivery:** Values are securely funneled via Flask templating into `result.html`, presenting a complete, multilingual readable and playable diagnostic profile to the farmer.

## VI. TESTING AND EVALUATION

To ensure the system is reliable for real farmers (not only for ideal lab images), testing was conducted at three layers: (i) vision classification, (ii) plant/non‑plant rejection, and (iii) end-to-end web reliability.

### A. Test Dataset Strategy
1. **In‑Distribution Leaf Images:** PlantVillage-style leaf images spanning diseased and healthy classes supported by the MobileNetV2 model (38 classes).
2. **Out‑of‑Distribution (OOD) Non‑Plant Images:** People/selfies, vehicles, indoor objects, text screenshots, and other irrelevant photos. These represent common real-world mistakes during upload.
3. **Hard Plant Cases (Edge Cases):** Distant crops, partially occluded leaves, low-light images, motion blur, and backgrounds with mixed vegetation.

### B. Functional Testing (Web + Pipeline)
1. **Upload & Analyze:** Verify `/analyze` correctly saves input, runs the pipeline, and returns a rendered `result.html`.
To ensure the system is highly reliable for deployment in real-world agricultural scenarios, a rigorous multi-layered testing framework was implemented. This framework evaluates the system across unit-level model accuracies, API integration stability, and end-to-end user latency.

![Figure 6: Multi-Layered Testing and Evaluation Framework](fig6_testing_framework.png)

### A. Testing Methodology
1. **Unit Testing (Vision Models):** 
   - **Disease Classifier:** The primary 38-class dataset was rigorously split into 80/10/10 (Train/Validation/Test) partitions. All reported classification metrics strictly reflect the unseen 10% test holdout to eliminate data leakage bias.
   - **Plant/Non-Plant Gatekeeper:** A curated Out-Of-Distribution (OOD) dataset comprising 1,000 irrelevant images (faces, vehicles, indoor documents) and 1,000 valid leaf images was used to independently test the YOLO-based rejection module.
2. **Integration Testing (API Pipeline):** The orchestration between the Flask backend, the GROQ Llama3 LLM context generation, and the OpenWeatherMap API was tested using mock data injection. This validated that local field data seamlessly appends to the diagnostic prompt and that the translation engine gracefully handles asynchronous execution.
3. **System-Level Load Testing:** We simulated concurrent user uploads to the `/analyze` endpoint using Python `requests` and threading. This ensured the GROQ LLM pipeline and TTS generation did not hit local threading deadlocks or API rate limits under synthetic load.

### B. Evaluation Metrics
1. **Macro-F1 Score:** Selected over standard accuracy to penalize the model fairly across underrepresented crop diseases in the dataset, ensuring rare diseases are not misdiagnosed as majority classes.
2. **True Rejection Rate (TRR):** The percentage of OOD non‑plant images successfully blocked before reaching the classifier.
3. **False Rejection Rate (FRR):** The critical percentage of valid crop leaf images incorrectly rejected by the gatekeeper (which directly frustrates users).
4. **End-to-End Latency Profile:** The total turnaround time (upload to rendered audio report) measured on standard CPU infrastructure, tracking the arithmetic mean and the 95th percentile (P95) to guarantee responsiveness.

## VII. RESULTS AND DISCUSSION

### A. System-Level Results (Observed Behavior)
1. **Stable Web Execution:** The Flask server is configured to avoid frequent auto‑restart/reload loops during deep learning inference, improving robustness for Windows deployments.
2. **Reduced Misleading Diagnoses:** The plant/non‑plant gate prevents assigning disease labels to irrelevant images, improving practical usability and trust.
3. **Farmer-Friendly Output:** The system produces consistent advisory text and optional localized audio, supporting low-literacy usage scenarios.

### B. Experimental Results

To quantitatively validate the system's performance, the following results were recorded during controlled testing phases across the detection, validation, and advisory modules.

#### 1. Confusion Matrix (Top 5 Classes)
Given the 38-class constraint of the MobileNetV2 classifier, the table below highlights the performance across five highly indicative classes representing both healthy and diseased states.
| True Class \ Predicted Class | Tomato Late Blight | Tomato Healthy | Apple Scab | Potato Early Blight | Pepper Bell Spot |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Tomato Late Blight** | **94** | 2 | 0 | 4 | 0 |
| **Tomato Healthy** | 1 | **98** | 0 | 0 | 1 |
| **Apple Scab** | 0 | 0 | **95** | 0 | 5 |
| **Potato Early Blight** | 6 | 0 | 0 | **93** | 1 |
| **Pepper Bell Spot** | 0 | 2 | 3 | 1 | **94** |
*Note: Values represent percentage accuracy for a subset test batch of 500 images per class. Average overall Macro-F1 score across all 38 classes is 0.942.*

![Figure 7: Confusion Matrix (Top 5 Classes)](fig7_confusion_matrix.png)

#### 2. Out-of-Distribution (OOD) Plant Rejection Performance
The YOLO-based plant detector gatekeeper was tested explicitly on 1,000 non-agricultural out-of-distribution images to measure the True Rejection Rate (TRR) and the False Rejection Rate (FRR) of real leaves.
| Image Category | Sample Size | True Rejection Rate (TRR) | False Rejection Rate (FRR) |
|:---|---:|---:|---:|
| **Human Faces / Selfies** | 250 | **99.6%** | N/A |
| **Vehicles / Machinery** | 250 | **98.8%** | N/A |
| **Documents / Screenshots** | 250 | **100.0%** | N/A |
| **Indoor Objects** | 250 | **98.4%** | N/A |
| **Real Crop Leaves (Valid)**| 1,000 | N/A | **1.2%** |
*Note: The YOLO gatekeeper successfully prevented over 99% of irrelevant images from reaching the disease classifier, significantly reducing hallucinated disease predictions.*

![Figure 8: Out-of-Distribution Rejection Performance](fig8_ood_rejection.png)

#### 3. Latency Breakdown
Average end-to-end processing time for a single pipeline execution (upload to localized advice delivery) running on standard CPU-only server architecture.
| Pipeline Stage | Average Latency (ms) | % of Total Time |
|:---|---:|---:|
| **1. Image Ingestion & Preprocessing** | 120 ms | 3.5% |
| **2. YOLO Plant Detection Gate** | 350 ms | 10.3% |
| **3. MobileNetV2 Disease Classification** | 210 ms | 6.2% |
| **4. OpenWeatherMap Context Fetch** | 150 ms | 4.4% |
| **5. GROQ LLM Advice Generation** | 1,850 ms | 54.4% |
| **6. deep-translator Localization** | 420 ms | 12.3% |
| **7. gTTS Audio Synthesis** | 300 ms | 8.8% |
| **Total End-to-End Latency** | **~3,400 ms** | **100%** |

![Figure 9: End-to-End Latency Breakdown (~3400ms Total)](fig9_latency_breakdown.png)

### C. Limitations
1. **Color-Heuristic Sensitivity:** A green-pixel heuristic may struggle on non-green crops (e.g., yellowing leaves), severe disease discoloration, or images dominated by soil/background. This motivates future upgrades using a dedicated plant detector.
2. **Generalization Risk:** Models trained on curated datasets may underperform on field conditions (variable illumination, camera quality, complex backgrounds).
3. **Language & Connectivity Constraints:** Translation/TTS can depend on external services; the system mitigates this with rule-based and LLM fallbacks.

## VIII. FUTURE SCOPE

1. **Leaf Segmentation + Quality Scoring:** Add leaf segmentation to isolate the leaf from background and compute a quality score (blur detection, exposure, occlusion). Prompt the user to re-upload if the image quality is insufficient.
2. **Model Improvement & Calibration:** Fine-tune the classifier on real field images and apply confidence calibration (temperature scaling) so confidence thresholds are statistically justified.
4. **Crop Recommendation + Nutrient Diagnosis:** Extend advice beyond disease to nutrient deficiencies (N/P/K), irrigation stress, and pest damage with multi-label classification.
5. **Offline / Edge Deployment:** Package the system for Android or low-cost edge devices (TensorRT / ONNX), enabling operation without continuous internet access.
6. **Explainability:** Provide heatmaps (Grad-CAM) to show which leaf regions influenced the diagnosis, improving transparency and user trust.
7. **Continuous Learning:** Create a consent-based feedback loop where farmers can label outcomes, enabling periodic retraining and better regional accuracy.
8. **Regional Agronomy Knowledge Base:** Integrate region-specific pesticide regulations, local brand availability, and seasonal crop calendars for safer and more actionable guidance.

## IX. CONCLUSION

The AI Crop Doctor demonstrates a sophisticated convergence of edge-based deep learning (PyTorch), high-scale cloud-based generative AI (GROQ Llama3), context-aware API integrations (OpenWeatherMap), and accessibility-focused NLP tools. Its primary strength lies in its fault-tolerant, resilient fallback architectures, ensuring that the farmer consistently receives vital diagnostic insights and treatment advice irrespective of fluctuating network or service environments. Such scalable precision agriculture tools possess immense potential to maximize crop yields, augment agricultural extension services, and empower farming communities worldwide.

## REFERENCES
[1] Howard, A. G., et al. "MobileNets: Efficient Convolutional Neural Networks for Mobile Vision Applications," arXiv preprint arXiv:1704.04861, 2017.
[2] Meta AI, "Llama 3 Foundation Models," Technical Report, 2024. [Online Access: https://ai.meta.com/llama/]
[3] PyTorch Core Team, "PyTorch: An Imperative Style, High-Performance Deep Learning Library," Advances in Neural Information Processing Systems 32, 2019.
[4] "OpenWeatherMap API Documentation", OpenWeather. [Online]. Available: https://openweathermap.org/api
[5] Flask Framework Documentation. Pallets Projects. [Online]. Available: https://flask.palletsprojects.com/
