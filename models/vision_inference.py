import os
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image

class ChartAnomalyDetector:
    def __init__(self, model_path=None):
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        
        # Determine model path
        if model_path is None:
            base_dir = os.path.dirname(__file__)
            model_path = os.path.join(base_dir, 'chart_anomaly_cnn.pth')
            
        self.model_path = model_path
        self.class_names = ['anomalous', 'healthy'] # Based on alphabetical order of folders during ImageFolder
        self.model = self._load_model()
        
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

    def _load_model(self):
        try:
            model = models.resnet18(weights=None)
            num_ftrs = model.fc.in_features
            model.fc = nn.Linear(num_ftrs, 2)
            
            if os.path.exists(self.model_path):
                model.load_state_dict(torch.load(self.model_path, map_location=self.device))
                model = model.to(self.device)
                model.eval()
                return model
            else:
                print(f"Warning: Model weights not found at {self.model_path}. Returning untrained model.")
                return None
        except Exception as e:
            print(f"Error loading model: {e}")
            return None

    def analyze_chart(self, image_path: str) -> dict:
        if self.model is None:
            return {"error": "Model not loaded. Train the model first."}
            
        try:
            image = Image.open(image_path).convert('RGB')
            input_tensor = self.transform(image)
            input_batch = input_tensor.unsqueeze(0).to(self.device)

            with torch.no_grad():
                output = self.model(input_batch)
                probabilities = torch.nn.functional.softmax(output[0], dim=0)
                
            prob_dict = {self.class_names[i]: float(probabilities[i]) for i in range(len(self.class_names))}
            
            # Predict the class with highest probability
            predicted_class = self.class_names[torch.argmax(probabilities).item()]
            confidence = prob_dict[predicted_class]
            
            return {
                "status": "success",
                "prediction": predicted_class,
                "confidence": confidence,
                "probabilities": prob_dict
            }
        except Exception as e:
            return {"error": str(e)}

if __name__ == "__main__":
    # Test script if run directly
    detector = ChartAnomalyDetector()
    print("Detector initialized.")
