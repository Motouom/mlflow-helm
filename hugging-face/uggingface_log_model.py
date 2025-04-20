import mlflow
import mlflow.transformers
from transformers import AutoModelForSequenceClassification, AutoTokenizer

# Load a pre-trained model and tokenizer
model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")

# Start MLflow run
inputs = tokenizer("Hello world!", return_tensors="pt")
pure_inputs = {k: v.tolist() for k, v in inputs.items()}  # Convert tensors to pure lists

with mlflow.start_run():
    mlflow.transformers.log_model(
        transformers_model={"model": model, "tokenizer": tokenizer},
        artifact_path="model",
        input_example={"inputs": pure_inputs}   # Use pure_inputs here
    )
    print("Model logged successfully!")
