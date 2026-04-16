import os
import threading
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

_MODEL_LOCK = threading.Lock()
_MODEL = None
_PROCESSOR = None

def load_secondary_disease_model():
    """
    Download and load the secondary (ResNet-50) disease classifier from HuggingFace.
    Model: SanketJadhav/PlantDiseaseClassifier-Resnet50
    """
    global _MODEL, _PROCESSOR
    
    if _MODEL is not None:
        return _MODEL, _PROCESSOR

    with _MODEL_LOCK:
        if _MODEL is not None:
            return _MODEL, _PROCESSOR

        try:
            import torch
            import requests
            from transformers import AutoConfig, AutoModelForImageClassification
        except ImportError as e:
            msg = f"Essential libraries missing: {e}"
            logger.error(msg)
            raise ImportError(msg)

        repo_id = "SanketJadhav/PlantDiseaseClassifier-Resnet50"
        models_dir = os.path.join(os.path.dirname(__file__), "models", "disease_secondary")
        os.makedirs(models_dir, exist_ok=True)
        
        # Files needed for local loading
        files_to_download = {
            "config.json": f"https://huggingface.co/{repo_id}/resolve/main/config.json",
            "preprocessor_config.json": f"https://huggingface.co/{repo_id}/resolve/main/preprocessor_config.json",
            "pytorch_model.bin": f"https://huggingface.co/{repo_id}/resolve/main/pytorch_model.bin"
        }

        for filename, url in files_to_download.items():
            local_path = os.path.join(models_dir, filename)
            if not os.path.exists(local_path):
                logger.info("Downloading %s for secondary model...", filename)
                try:
                    r = requests.get(url, stream=True, timeout=120)
                    r.raise_for_status()
                    with open(local_path, "wb") as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                    logger.info("Downloaded %s successfully.", filename)
                except Exception as e:
                    logger.error("Failed to download %s: %s", filename, e)
                    raise e

        try:
            from torchvision import transforms
            _PROCESSOR = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406],
                                     [0.229, 0.224, 0.225])
            ])
            
            logger.info("Loading secondary disease model (ResNet-50) from config...")
            config = AutoConfig.from_pretrained(models_dir)
            _MODEL = AutoModelForImageClassification.from_config(config)
            
            weights_path = os.path.join(models_dir, "pytorch_model.bin")
            state_dict = torch.load(weights_path, map_location="cpu")
            _MODEL.load_state_dict(state_dict)
            _MODEL.eval()
            
            logger.info("Secondary disease model loaded successfully.")
            return _MODEL, _PROCESSOR
            
        except Exception as e:
            logger.exception("Failed to load secondary model info: %s", e)
            raise e

def predict_secondary(image_path: str) -> Tuple[str, float]:
    """
    Perform inference using the secondary local ResNet-50 model.
    """
    try:
        from PIL import Image
        import torch
        
        model, transform = load_secondary_disease_model()
        
        # Handle different image types
        if isinstance(image_path, str):
            img = Image.open(image_path).convert("RGB")
        else:
            # If it's already a PIL image or numpy array
            from PIL import Image as PILImage
            if isinstance(image_path, PILImage.Image):
                img = image_path.convert("RGB")
            else:
                import numpy as np
                arr = np.asarray(image_path)
                img = PILImage.fromarray(arr[:, :, :3][:, :, ::-1]).convert("RGB")

        # Preprocess
        inputs = transform(img).unsqueeze(0)
        
        # Inference
        with torch.no_grad():
            outputs = model(inputs)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=1)[0]
            idx = probs.argmax().item()
            conf = float(probs[idx])
            
            # Use model's internal label mapping if available
            label = model.config.id2label.get(idx, f"Class {idx}")
            
        return label, conf
        
    except Exception as e:
        logger.error("Secondary inference failed: %s", e)
        raise e
