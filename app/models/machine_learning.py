import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

class MLModel:
    def __init__(self, model_name: str):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)

    def predict(self, text: str):
        inputs = self.tokenizer(text, return_tensors="pt")
        outputs = self.model(**inputs)
        predictions = torch.argmax(outputs.logits, dim=1)
        return predictions.item()  # Returns the predicted class
