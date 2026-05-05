import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import api_client
import time

st.set_page_config(
    page_title="Fraud Analyst Portal",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern, professional look
st.markdown("""
<style>
    .reportview-container .main .block-container{
        padding-top: 2rem;
    }
    .metric-container {
        background-color: #1e1e1e;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: 1px solid #333;
    }
    h1, h2, h3 {
        color: #4A90E2;
        font-family: 'Inter', sans-serif;
    }
    .stButton>button {
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar for Navigation
page = st.sidebar.radio("Navigation", ["Dashboard", "New Evaluation", "Batch Evaluation", "User Guide"])

st.title("🛡️ Credit Card Fraud Risk System")

if page == "User Guide":
    st.header("📖 User Guide")
    st.markdown("""
    Welcome to the **Fraud Analyst Portal**. This tool allows you to evaluate credit card transactions for potential fraud in real-time or in bulk batches.
    
    ### 1. Dashboard
    - **Overview:** View high-level metrics of all processed transactions.
    - **Charts:** Analyze the distribution of risk levels and the correlation between transaction amounts and risk scores.
    - **Data Table:** See a historical log of recent transactions.
    - **Clear History:** As an admin, you have the ability to clear the transaction history database if necessary.
    
    ### 2. New Evaluation
    - Evaluate a single transaction in real-time.
    - Enter the User ID, Amount, Currency (including USD, EUR, INR, etc.), and Merchant details.
    - The system's ML model will return a Risk Level (Low, Medium, High) and the reasons for its decision.
    
    ### 3. Batch Evaluation
    - Ideal for end-of-day processing or bulk testing.
    - You can generate a test CSV using the `generate_test_data.py` script provided in the project root.
    - Upload the CSV file, and the system will process all rows simultaneously, displaying the aggregated results in a color-coded table.
    """)
    
elif page == "New Evaluation":
    st.header("📝 Evaluate New Transaction")
    st.markdown("Enter transaction details below to run them through the risk scoring model.")
    
    with st.form("evaluation_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            user_id = st.text_input("User ID", placeholder="e.g. user_12345")
            amount = st.number_input("Transaction Amount", min_value=0.0, value=50.0, step=10.0)
            currency = st.selectbox("Currency", ["USD", "EUR", "GBP", "JPY", "INR"])
            
        with col2:
            merchant_category = st.selectbox("Merchant Category", [
                "Retail", "Groceries", "Electronics", "Travel", "Crypto", "Gambling", "Restaurant", "Wire Transfer", "Other"
            ])
            merchant_location = st.text_input("Merchant Location", placeholder="e.g. New York, USA or Country_X")
            
        submitted = st.form_submit_button("Evaluate Risk", use_container_width=True)
        
        if submitted:
            if not user_id or not merchant_location:
                st.error("Please fill in all required fields.")
            else:
                with st.spinner("Analyzing transaction patterns..."):
                    tx_data = {
                        "user_id": user_id,
                        "amount": amount,
                        "currency": currency,
                        "merchant_category": merchant_category,
                        "merchant_location": merchant_location
                    }
                    try:
                        result = api_client.evaluate_transaction(tx_data)
                        score_data = result["score"]
                        
                        st.subheader("Evaluation Results")
                        
                        res_col1, res_col2 = st.columns(2)
                        risk_level = score_data["risk_level"]
                        risk_color = "green" if risk_level == "Low" else "orange" if risk_level == "Medium" else "red"
                        
                        with res_col1:
                            st.metric(label="Risk Score", value=f"{score_data['score'] * 100:.1f}%", delta_color="inverse")
                            st.markdown(f"**Risk Level:** <span style='color:{risk_color}; font-size: 20px; font-weight: bold;'>{risk_level}</span>", unsafe_allow_html=True)
                            
                        with res_col2:
                            st.markdown("**Risk Factors Identified:**")
                            for reason in score_data["reasons"]:
                                st.markdown(f"- {reason}")
                                
                    except Exception as e:
                        st.error(f"Error communicating with backend: {e}")

elif page == "Batch Evaluation":
    st.header("📂 Batch Transaction Evaluation")
    st.markdown("Upload a CSV file containing multiple transactions to evaluate them simultaneously.")
    
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        if st.button("Evaluate Batch", use_container_width=True):
            with st.spinner("Processing batch file..."):
                try:
                    file_content = uploaded_file.getvalue()
                    results = api_client.evaluate_batch(file_content, uploaded_file.name)
                    
                    st.toast(f"Successfully processed {len(results)} transactions!", icon='✅')
                    
                    flat_results = []
                    for item in results:
                        tx = item["transaction"]
                        sc = item["score"]
                        flat_results.append({
                            "User ID": tx.get("user_id"),
                            "Amount": tx.get("amount"),
                            "Currency": tx.get("currency", "USD"),
                            "Category": tx.get("merchant_category"),
                            "Location": tx.get("merchant_location"),
                            "Risk Level": sc.get("risk_level"),
                            "Score (%)": round(sc.get("score", 0) * 100, 1)
                        })
                        
                    results_df = pd.DataFrame(flat_results)
                    
                    def color_risk(val):
                        color = '#ff4b4b' if val == 'High' else '#ffa500' if val == 'Medium' else '#00cc66'
                        return f'color: {color}; font-weight: bold;'
                        
                    # st.dataframe(results_df.style.applymap(color_risk, subset=['Risk Level']), use_container_width=True)
                    st.dataframe(results_df.style.map(color_risk, subset=['Risk Level']), use_container_width=True)
                    
                except Exception as e:
                    st.error(f"Failed to process batch: {e}")

elif page == "Dashboard":
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        st.header("📊 Transaction Monitoring Dashboard")
    with col2:
        with st.expander("⚠️ Admin Actions"):
            if st.button("Clear History", type="primary"):
                try:
                    api_client.clear_transactions()
                    st.toast("Transaction history cleared.", icon="🗑️")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to clear history: {e}")
    
    try:
        transactions_data = api_client.get_transactions()
        if not transactions_data:
            st.info("No transactions evaluated yet. Go to 'New Evaluation' or upload a Batch to get started.")
        else:
            flat_data = []
            for item in transactions_data:
                tx = item["transaction"]
                sc = item["score"]
                flat_data.append({
                    "Transaction ID": tx.get("id"),
                    "Time": tx.get("timestamp"),
                    "User": tx.get("user_id"),
                    "Amount": tx.get("amount"),
                    "Category": tx.get("merchant_category"),
                    "Location": tx.get("merchant_location"),
                    "Risk Score": sc.get("score"),
                    "Risk Level": sc.get("risk_level")
                })
            
            df = pd.DataFrame(flat_data)
            df['Time'] = pd.to_datetime(df['Time'])
            
            # Key Metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Transactions", len(df))
            with col2:
                high_risk = len(df[df["Risk Level"] == "High"])
                st.metric("High Risk Transactions", high_risk)
            with col3:
                avg_score = df["Risk Score"].mean() * 100
                st.metric("Average Risk Score", f"{avg_score:.1f}%")
                
            st.divider()
            
            # Charts
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                st.subheader("Risk Level Distribution")
                fig_pie = px.pie(df, names="Risk Level", title="Transactions by Risk Level", 
                               color="Risk Level",
                               color_discrete_map={'Low':'#00cc66', 'Medium':'#ffa500', 'High':'#ff4b4b'})
                st.plotly_chart(fig_pie, use_container_width=True)
                
            with chart_col2:
                st.subheader("Risk Score vs Amount")
                fig_scatter = px.scatter(df, x="Amount", y="Risk Score", color="Risk Level",
                                       hover_data=["Category", "Location"],
                                       title="Transaction Amount vs Risk Score",
                                       color_discrete_map={'Low':'#00cc66', 'Medium':'#ffa500', 'High':'#ff4b4b'})
                st.plotly_chart(fig_scatter, use_container_width=True)
                
            st.divider()
            st.subheader("Recent Transactions Log")
            st.dataframe(df.sort_values(by="Time", ascending=False), use_container_width=True)
            
    except Exception as e:
         st.error(f"Error fetching dashboard data. Is the backend running? ({e})")
