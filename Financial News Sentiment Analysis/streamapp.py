import streamlit as st
import torch
import pandas as pd
from transformers import BertTokenizer, BertForSequenceClassification

st.set_page_config(
    page_title="Financial News Sentiment Prediction",
    layout="wide"
)

st.title("Financial News Sentiment Prediction")
st.write("Enter a financial news headline or tweet below.")

# Load Tokenizer
tokenizer = BertTokenizer.from_pretrained("bert_tokenizer")

# Load Model
model = BertForSequenceClassification.from_pretrained(
    "bert-base-uncased",
    num_labels=3
)
model.load_state_dict(
    torch.load(
        "bert_model.pth",
        map_location=torch.device("cpu")
    )
)

model.eval()

# Label Mapping
label_map = {
    0: "Bearish",
    1: "Bullish",
    2: "Neutral"
}

# User Input
news = st.text_area("Enter Financial News", height=150)

# Prediction
if st.button("Predict Sentiment"):
    if news.strip() == "":
        st.warning("Please enter some financial news.")
    else:
        inputs = tokenizer(
            news,
            truncation=True,
            padding=True,
            max_length=25,
            return_tensors="pt"
        )
        with torch.no_grad():
            outputs = model(input_ids=inputs["input_ids"], attention_mask=inputs["attention_mask"])
            probabilities = torch.softmax(outputs.logits, dim=1)
            prediction = torch.argmax(probabilities, dim=1).item()

        predicted_label = label_map[prediction]
        if prediction == 0:  # this is for the result colour grid just to make it visually understandable
            st.error(f"Predicted Sentiment: {predicted_label}")

        elif prediction == 1:
            st.success(f"Predicted Sentiment: {predicted_label}")

        else:
            st.info(f"Predicted Sentiment: {predicted_label}")

        st.subheader("Prediction Probabilities")
        prob_df = pd.DataFrame(
            {"Probability": probabilities.squeeze().numpy()}, index=["Bearish", "Bullish", "Neutral"]
        )
        st.bar_chart(prob_df)
