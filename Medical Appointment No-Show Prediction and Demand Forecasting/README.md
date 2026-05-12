This project was built for the CER clinic (University of Vale do Itajaí, Brazil) which serves 13 cities and has a no-show rate of around 31.8%. The goal is to help the clinic predict which patients are likely to miss their appointments and also forecast how many appointments to expect on a given day.

There are three machine learning models built here. The first one is a classification model that takes patient details like age, health conditions, weather, and appointment info and predicts whether the patient will show up or not. The second one is a demand forecasting model that predicts the number of appointments expected per day for the whole clinic, and also another model broken down by specialty like physiotherapy, psychotherapy, and speech therapy.
All models are deployed in a Streamlit web app where clinic staff can enter patient details to get a no-show risk score, select a date range to see forecasted appointment volumes, and explore key data insights like no-show rates by specialty and the impact of SMS reminders.
Also the third model was used, just to improve accuracy of overall demand forecasting.

