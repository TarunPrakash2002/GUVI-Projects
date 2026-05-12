import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib
import os
from datetime import date, timedelta

st.set_page_config(page_title="Medical Appointment System", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "model")


@st.cache_resource
def load_models():
    no_show_model = joblib.load(os.path.join(MODEL_DIR, "no_show_model.pkl"))
    no_show_features = joblib.load(os.path.join(MODEL_DIR, "no_show_features.pkl"))
    demand_model = joblib.load(os.path.join(MODEL_DIR, "demand_model.pkl"))
    demand_features = joblib.load(os.path.join(MODEL_DIR, "demand_feature_cols.pkl"))
    specialty_model = joblib.load(os.path.join(MODEL_DIR, "specialty_model.pkl"))
    specialty_features = joblib.load(os.path.join(MODEL_DIR, "specialty_model_features.pkl"))
    specialty_mapping = joblib.load(os.path.join(MODEL_DIR, "specialty_mapping.pkl"))
    feature_defaults = joblib.load(os.path.join(MODEL_DIR, "demand_feature_defaults.pkl"))
    return (no_show_model, no_show_features, demand_model, demand_features,
            specialty_model, specialty_features, specialty_mapping, feature_defaults)


@st.cache_data
def load_history():
    demand_hist = pd.read_csv(os.path.join(MODEL_DIR, "demand_history.csv"))
    demand_hist['date'] = pd.to_datetime(demand_hist['date'])
    spec_hist = pd.read_csv(os.path.join(MODEL_DIR, "specialty_history.csv"))
    spec_hist['date'] = pd.to_datetime(spec_hist['date'])
    return demand_hist, spec_hist


@st.cache_data
def load_raw_data():
    path = os.path.join(BASE_DIR, "Datasets", "cleaned_dataset.csv")
    df = pd.read_csv(path)
    df['appointment_date_continuous'] = pd.to_datetime(df['appointment_date_continuous'])
    return df


(no_show_model, no_show_features, demand_model, demand_features,
 specialty_model, specialty_features, specialty_mapping, feature_defaults) = load_models()

demand_hist, spec_hist = load_history()
df_raw = load_raw_data()

name_to_code = {v: k for k, v in specialty_mapping.items()}
specialties = ['psychotherapy', 'speech therapy', 'physiotherapy',
               'occupational therapy', 'pedagogo', 'enf']


def forecast_future(model, features, history_df, start_date, end_date, extra={}):
    future_dates = []
    current = start_date
    while current <= end_date:
        if current.weekday() < 5:
            future_dates.append(current)
        current += timedelta(days=1)

    if len(future_dates) == 0:
        return None

    hist = history_df.copy().sort_values('date').reset_index(drop=True)
    results = []

    for fdate in future_dates:
        last = hist.iloc[-1]

        row = {
            'avg_temp': float(last.get('avg_temp', 22.0)),
            'avg_rain': float(last.get('avg_rain', 0.0)),
            'rainy_day_before': 0,
            'pct_elderly': float(last.get('pct_elderly', 0.2)),
            'pct_hypertension': float(last.get('pct_hypertension', 0.3)),
            'pct_diabetes': float(last.get('pct_diabetes', 0.1)),
            'pct_sms': float(last.get('pct_sms', 0.3)),
            'day_of_week': fdate.weekday(),
            'month': fdate.month,
            'year': fdate.year,
            'is_weekend': 0,
            'lag_1': float(hist.iloc[-1]['total_appointments']),
            'lag_7': float(hist.iloc[-7]['total_appointments']) if len(hist) >= 7 else float(last['total_appointments']),
            'lag_14': float(hist.iloc[-14]['total_appointments']) if len(hist) >= 14 else float(last['total_appointments']),
        }

        for k, v in extra.items():
            row[k] = v

        for f in features:
            if f not in row:
                row[f] = feature_defaults.get(f, 0)

        input_df = pd.DataFrame([row])[features]
        pred = float(model.predict(input_df)[0])
        pred = max(0, pred)

        results.append({'date': fdate, 'predicted_appointments': round(pred)})

        new_row = pd.DataFrame([{
            'date': pd.Timestamp(fdate),
            'total_appointments': pred,
            'avg_temp': row['avg_temp'],
            'avg_rain': row['avg_rain'],
            'rainy_day_before': 0,
            'pct_elderly': row['pct_elderly'],
            'pct_hypertension': row['pct_hypertension'],
            'pct_diabetes': row['pct_diabetes'],
            'pct_sms': row['pct_sms'],
            'day_of_week': fdate.weekday(),
            'month': fdate.month,
            'year': fdate.year,
            'is_weekend': 0,
            'lag_1': pred,
            'lag_7': row['lag_7'],
            'lag_14': row['lag_14'],
        }])
        hist = pd.concat([hist, new_row], ignore_index=True)

    return pd.DataFrame(results)


st.title("Medical Appointment No-Show & Demand Forecasting")
st.divider()

tab1, tab2, tab3, tab4 = st.tabs([
    "No-Show Prediction",
    "Overall Demand Forecast",
    "Specialty Demand Forecast",
    "Data Insights"
])

with tab1:  # No Show Prediction
    st.header("No-Show Risk Prediction")
    st.write("Enter patient details to predict if the patient will miss their appointment.")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Patient Info")
        age = st.slider("Age", min_value=0, max_value=120, value=35)
        under_12 = 1 if age < 12 else 0
        over_60 = 1 if age > 60 else 0
        age_missing = 0

        gender = st.radio("Gender", ["Male", "Female", "Other"])
        gender_M = 1 if gender == "Male" else 0
        gender_I = 1 if gender == "Other" else 0

        needs_companion = st.radio("Needs companion?", ["No", "Yes"])
        patient_needs_companion = 1 if needs_companion == "Yes" else 0

    with col2:
        st.subheader("Health Conditions")
        st.write("Check all that apply:")
        hipertension = 1 if st.checkbox("Hypertension") else 0
        diabetes = 1 if st.checkbox("Diabetes") else 0
        alcoholism = 1 if st.checkbox("Alcoholism") else 0
        handcap = 1 if st.checkbox("Handicap") else 0
        scholarship = 1 if st.checkbox("Government Scholarship") else 0
        disability_intellectual = 1 if st.checkbox("Intellectual Disability") else 0
        disability_motor = 1 if st.checkbox("Motor Disability") else 0
        sms_received = 1 if st.checkbox("SMS Reminder Sent") else 0

    with col3:
        st.subheader("Appointment & Weather")
        appointment_time = st.slider("Appointment Hour", min_value=6, max_value=22, value=10)
        shift = st.radio("Shift", ["Morning", "Afternoon"])
        appointment_shift = 0 if shift == "Morning" else 1

        rainy_yesterday = st.radio("Was yesterday rainy?", ["No", "Yes"])
        rainy_day_before = 1 if rainy_yesterday == "Yes" else 0

        storm_yesterday = st.radio("Storm yesterday?", ["No", "Yes"])
        storm_day_before = 1 if storm_yesterday == "Yes" else 0

        weather_today = st.radio("Weather today", ["No Rain", "Weak Rain", "Moderate Rain"])
        rain_no_rain = 1 if weather_today == "No Rain" else 0
        rain_weak = 1 if weather_today == "Weak Rain" else 0
        rain_moderate = 1 if weather_today == "Moderate Rain" else 0

        heat_today = st.radio("Temperature today", ["Mild", "Warm", "Heavy Warm", "Heavy Cold"])
        heat_mild = 1 if heat_today == "Mild" else 0
        heat_warm = 1 if heat_today == "Warm" else 0
        heat_heavy_warm = 1 if heat_today == "Heavy Warm" else 0
        heat_heavy_cold = 1 if heat_today == "Heavy Cold" else 0

        avg_temp = 15.0 if heat_today == "Heavy Cold" else 22.0 if heat_today == "Mild" else 27.0 if heat_today == "Warm" else 32.0
        max_temp = avg_temp + 4
        avg_rain = 0.0 if weather_today == "No Rain" else 5.0 if weather_today == "Weak Rain" else 15.0
        max_rain = avg_rain * 1.5

    st.divider()

    if st.button("Predict No-Show Risk"):
        input_data = {
            'appointment_time': appointment_time,
            'appointment_shift': appointment_shift,
            'age': age,
            'under_12_years_old': under_12,
            'over_60_years_old': over_60,
            'patient_needs_companion': patient_needs_companion,
            'average_temp_day': avg_temp,
            'average_rain_day': avg_rain,
            'max_temp_day': max_temp,
            'max_rain_day': max_rain,
            'rainy_day_before': rainy_day_before,
            'storm_day_before': storm_day_before,
            'Hipertension': hipertension,
            'Diabetes': diabetes,
            'Alcoholism': alcoholism,
            'Handcap': handcap,
            'Scholarship': scholarship,
            'SMS_received': sms_received,
            'age_missing': age_missing,
            'gender_I': gender_I,
            'gender_M': gender_M,
            'disability_intellectual': disability_intellectual,
            'disability_motor': disability_motor,
            'heat_heavy_cold': heat_heavy_cold,
            'heat_heavy_warm': heat_heavy_warm,
            'heat_mild': heat_mild,
            'heat_warm': heat_warm,
            'rain_moderate': rain_moderate,
            'rain_no_rain': rain_no_rain,
            'rain_weak': rain_weak,
        }

        input_df = pd.DataFrame([input_data])
        for f in no_show_features:
            if f not in input_df.columns:
                input_df[f] = 0
        input_df = input_df[no_show_features]

        with st.spinner("Predicting..."):
            prob = no_show_model.predict_proba(input_df)[0][1]
            pred = no_show_model.predict(input_df)[0]

        st.divider()
        if pred == 1:
            st.error(f"High No-Show Risk — Probability: {prob*100:.1f}%")
            st.write("Recommendation: Send SMS reminder and consider a follow-up call.")
        else:
            st.success(f"Likely to Attend — No-Show Probability: {prob*100:.1f}%")
            st.write("Recommendation: Standard confirmation is sufficient.")

        st.progress(float(prob))


with tab2:  # Overall Demand Forecast
    st.header("Overall Clinic Demand Forecast")
    st.write("Select a date range to forecast total daily appointments for the whole clinic.")

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=date(2021, 2, 1))
    with col2:
        end_date = st.date_input("End Date", value=date(2021, 3, 31))

    if st.button("Generate Forecast"):
        if start_date >= end_date:
            st.error("End date must be after start date")
        elif (end_date - start_date).days > 365:
            st.error("Please select a range of less than 1 year")
        else:
            with st.spinner("Forecasting..."):
                results = forecast_future(demand_model, demand_features, demand_hist, start_date, end_date)

            if results is not None and len(results) > 0:
                col1, col2, col3 = st.columns(3)
                col1.metric("Average Per Day", round(results['predicted_appointments'].mean()))
                col2.metric("Peak Day", int(results['predicted_appointments'].max()))
                col3.metric("Total Appointments", int(results['predicted_appointments'].sum()))

                st.divider()

                plt.figure(figsize=(12, 4))
                plt.plot(results['date'], results['predicted_appointments'], marker='o', markersize=3)
                plt.title('Predicted Daily Appointments - Full Clinic')
                plt.xlabel('Date')
                plt.ylabel('Appointments')
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(plt)

                st.divider()
                st.subheader("Daily Forecast Table")
                st.dataframe(results, use_container_width=True)
            else:
                st.warning("No weekdays found in selected date range")


with tab3:  # Specialty Demand Forecast
    st.header("Specialty Demand Forecast")
    st.write("Select a specialty and date range to forecast daily appointments.")

    col1, col2, col3 = st.columns(3)
    with col1:
        selected_specialty = st.selectbox("Select Specialty", specialties)
    with col2:
        sp_start = st.date_input("Start Date", value=date(2021, 2, 1), key="sp_start")
    with col3:
        sp_end = st.date_input("End Date", value=date(2021, 3, 31), key="sp_end")

    if st.button("Forecast Specialty Demand"):
        if sp_start >= sp_end:
            st.error("End date must be after start date")
        elif (sp_end - sp_start).days > 365:
            st.error("Please select a range of less than 1 year")
        else:
            with st.spinner("Forecasting..."):
                spec_code = name_to_code.get(selected_specialty, 0)
                spec_h = spec_hist[spec_hist['specialty'] == selected_specialty].copy()
                spec_h = spec_h.sort_values('date').reset_index(drop=True)

                if len(spec_h) < 14:
                    st.error("Not enough data for this specialty")
                else:
                    results_sp = forecast_future(
                        specialty_model, specialty_features,
                        spec_h, sp_start, sp_end,
                        extra={'specialty_encoded': spec_code}
                    )

                    if results_sp is not None and len(results_sp) > 0:
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Average Per Day", round(results_sp['predicted_appointments'].mean()))
                        col2.metric("Peak Day", int(results_sp['predicted_appointments'].max()))
                        col3.metric("Total Appointments", int(results_sp['predicted_appointments'].sum()))

                        st.divider()

                        plt.figure(figsize=(12, 4))
                        plt.plot(results_sp['date'], results_sp['predicted_appointments'], marker='o', markersize=3, color='darkorange')
                        plt.title('Predicted Daily Appointments - ' + selected_specialty)
                        plt.xlabel('Date')
                        plt.ylabel('Appointments')
                        plt.xticks(rotation=45)
                        plt.tight_layout()
                        st.pyplot(plt)

                        st.divider()
                        st.subheader("Daily Forecast - " + selected_specialty)
                        st.dataframe(results_sp, use_container_width=True)
                    else:
                        st.warning("No weekdays found in selected date range")


with tab4:  # Data Insights - Visualisations for all info

    st.header("Data Insights")
    st.write("Key patterns found in the dataset.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("No-Show Rate by Specialty")
        spec_ns = df_raw.groupby('specialty')['no_show'].mean() * 100
        spec_ns = spec_ns.sort_values(ascending=False).head(8)
        plt.figure(figsize=(8, 4))
        plt.barh(spec_ns.index, spec_ns.values, color='steelblue')
        plt.xlabel('No-Show Rate %')
        plt.title('No-Show Rate by Specialty')
        st.pyplot(plt)

    with col2:
        st.subheader("Appointments by Day of Week")
        df_raw['dow'] = df_raw['appointment_date_continuous'].dt.dayofweek
        dow_counts = df_raw.groupby('dow').size()
        dow_labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        plt.figure(figsize=(8, 4))
        plt.bar([dow_labels[i] for i in dow_counts.index], dow_counts.values, color='darkorange')
        plt.ylabel('Total Appointments')
        plt.title('Appointments by Day of Week')
        st.pyplot(plt)

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Weather Impact on No-Shows")
        weather_data = {
            'No Rain': df_raw[df_raw['rain_no_rain'] == 1]['no_show'].mean() * 100,
            'Rainy Day': df_raw[df_raw['rain_no_rain'] == 0]['no_show'].mean() * 100,
            'Storm Before': df_raw[df_raw['storm_day_before'] == 1]['no_show'].mean() * 100,
        }
        plt.figure(figsize=(8, 4))
        plt.bar(weather_data.keys(), weather_data.values(), color=['steelblue', 'crimson', 'purple'])
        plt.ylabel('No-Show Rate %')
        plt.title('No-Show Rate by Weather')
        st.pyplot(plt)

    with col4:
        st.subheader("SMS Reminder Impact")
        sms_ns = df_raw.groupby('SMS_received')['no_show'].mean() * 100
        values = [sms_ns.get(0, 0), sms_ns.get(1, 0)]
        plt.figure(figsize=(8, 4))
        plt.bar(['No SMS', 'SMS Sent'], values, color=['crimson', 'steelblue'])
        plt.ylabel('No-Show Rate %')
        plt.title('SMS Impact on No-Show Rate')
        for i, v in enumerate(values):
            plt.text(i, v + 0.3, f'{v:.1f}%', ha='center', fontsize=11)
        st.pyplot(plt)

    st.divider()
    st.subheader("Monthly Appointment Volume")
    df_raw['month'] = df_raw['appointment_date_continuous'].dt.to_period('M')
    monthly_counts = df_raw.groupby('month').size()
    plt.figure(figsize=(14, 4))
    plt.plot(range(len(monthly_counts)), monthly_counts.values, marker='o', color='steelblue', linewidth=2)
    plt.xticks(range(len(monthly_counts)), [str(m) for m in monthly_counts.index], rotation=45)
    plt.title('Monthly Appointment Volume')
    plt.ylabel('Total Appointments')
    plt.tight_layout()
    st.pyplot(plt)

    st.divider()
    st.subheader("Key Findings")
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.write("**Top No-Show Factors:**")
        st.write("- Appointment time of day")
        st.write("- Age of patient")
        st.write("- SMS reminder status")
        st.write("- Patient health conditions")
        st.write("- Weather on appointment day")

    with col_b:
        st.write("**Demand Patterns:**")
        st.write("- Monday has highest demand")
        st.write("- Demand drops in winter")
        st.write("- Psychotherapy has highest volume")
        st.write("- Weekends have near-zero appointments")
        st.write("- Weather affects daily attendance")

    with col_c:
        st.write("**Recommendations:**")
        st.write("- Send SMS to high-risk patients")
        st.write("- Schedule more staff on Mondays")
        st.write("- Use forecast for weekly planning")
        st.write("- Target elderly with reminders")
        st.write("- Monitor weather impact")