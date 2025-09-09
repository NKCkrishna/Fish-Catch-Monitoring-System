import streamlit as st
from supabase_client import get_client
from datetime import datetime
import pandas as pd
import plotly.express as px

# Initialize Supabase client
supabase = get_client()

# Set up the Streamlit page
st.set_page_config(page_title="Fish Catching Monitoring", page_icon="🎣", layout="centered")
# Add background image using CSS
st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1507525428034-b723cf961d3e");
        background-attachment: fixed;
        background-size: cover;
    }

    h1, h2, h3, h4, h5, h6, p, label, .css-10trblm, .css-1d391kg, .css-1cpxqw2 {
        color: black !important;
        font-size: 24px !important;
        font-weight: 600;
    }

    /* Optional: make input fields slightly transparent with black text */
    .stTextInput>div>div>input,
    .stNumberInput>div>div>input,
    .stTextArea>div>textarea {
        background-color: rgba(255, 255, 255, 0.8) !important;
        color: black !important;
        font-size: 18px !important;
    }

    /* Adjust button styling too if needed */
    .stButton>button {
        font-size: 18px !important;
        font-weight: bold;
        color: black !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)
# Display title
st.markdown("# 🎣 Fish Catching Monitoring System")

# Sidebar menu
menu = ["Add Catch", "View Catches", "Update Catch", "Delete Catch", "Analytics"]
choice = st.sidebar.selectbox("Menu", menu)

# Helper: Get next custom_id
def get_next_id():
    data = supabase.table("fish_catches").select("custom_id").order("custom_id", desc=True).limit(1).execute().data
    if not data or data[0]['custom_id'] is None:
        return "C01"  # Start from C01 if table is empty or null
    last_id = data[0]['custom_id']
    number = int(last_id[1:]) + 1
    return f"C{number:02d}"

# Add Catch
if choice == "Add Catch":
    st.subheader("➕ Add a New Catch Record")
    
    # Input fields
    fisher = st.text_input("Fisher Name")
    species = st.text_input("Fish Species")
    weight = st.number_input("Weight (kg)", min_value=0.0)
    location = st.text_input("Location")
    timestamp = st.date_input("Date of Catch", datetime.now())
    
    # Submit button
    if st.button("Submit"):
        custom_id = get_next_id()
        data = {
            "custom_id": custom_id,
            "fisher_name": fisher,
            "species": species,
            "weight": weight,
            "location": location,
            "timestamp": str(timestamp),
        }

        response = supabase.table("fish_catches").insert(data).execute()

        if response.data:
            st.success(f"Catch record {custom_id} added successfully!")
        elif response.error:
            st.error(f"Failed to add catch record: {response.error['message']}")
        else:
            st.error("Unknown error occurred.")

# View Catches
elif choice == "View Catches":
    st.subheader("📜 Catch History")
    result = supabase.table("fish_catches").select("*").order("timestamp", desc=True).execute()
    df = pd.DataFrame(result.data)

    if not df.empty:
        df = df[["custom_id", "fisher_name", "species", "weight", "location", "timestamp"]]
        df.columns = ["ID", "Fisher", "Species", "Weight (kg)", "Location", "Date"]
        st.dataframe(df.style.set_properties(**{
            'background-color': '#111',
            'color': 'white',
            'border-color': 'gray'
        }))
    else:
        st.info("No catch records found.")

# Update Catch
elif choice == "Update Catch":
    st.subheader("✏️ Update a Catch Record")
    records = supabase.table("fish_catches").select("custom_id").execute().data
    ids = [r["custom_id"] for r in records]
    selected_id = st.selectbox("Select ID to update", ids)

    if selected_id:
        record = supabase.table("fish_catches").select("*").eq("custom_id", selected_id).execute().data[0]
        fisher = st.text_input("Fisher Name", record["fisher_name"])
        species = st.text_input("Fish Species", record["species"])
        weight = st.number_input("Weight (kg)", min_value=0.0, value=float(record["weight"]))
        location = st.text_input("Location", record["location"])
        timestamp = st.date_input("Date of Catch", datetime.strptime(record["timestamp"][:10], "%Y-%m-%d"))

        if st.button("Update"):
            update_data = {
                "fisher_name": fisher,
                "species": species,
                "weight": weight,
                "location": location,
                "timestamp": str(timestamp),
            }
            response = supabase.table("fish_catches").update(update_data).eq("custom_id", selected_id).execute()

            if response.data:
                st.success("Record updated successfully.")
            elif response.error:
                st.error(f"Failed to update record: {response.error['message']}")
            else:
                st.error("Unknown error occurred.")

# Delete Catch
elif choice == "Delete Catch":
    st.subheader("❌ Delete a Catch Record")
    records = supabase.table("fish_catches").select("custom_id").execute().data
    ids = [r["custom_id"] for r in records]
    selected_id = st.selectbox("Select ID to delete", ids)

    if st.button("Delete"):
        response = supabase.table("fish_catches").delete().eq("custom_id", selected_id).execute()

        if response.data:
            st.success(f"Catch record {selected_id} deleted successfully.")
        elif response.error:
            st.error(f"Failed to delete record: {response.error['message']}")
        else:
            st.error("Unknown error occurred.")

# Analytics
elif choice == "Analytics":
    st.subheader("📊 Catch Analytics")
    data = supabase.table("fish_catches").select("*").execute().data
    if data:
        df = pd.DataFrame(data)

        # Prepare metric values
        total_catches = df.shape[0]
        total_weight = f"{df['weight'].sum():.2f} kg"
        most_caught_species = df["species"].value_counts().idxmax() if "species" in df.columns else "N/A"

        # Display custom metrics
        st.markdown(f"""
            <style>
            .metric-container {{
                display: flex;
                gap: 40px;
                margin-bottom: 30px;
                flex-wrap: wrap;
            }}

            .metric-box {{
                background-color: rgba(255, 255, 255, 0.8);
                padding: 15px 25px;
                border-radius: 12px;
                box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
                color: black;
                font-size: 20px;
                font-weight: bold;
                width: 260px;
                text-align: center;
            }}

            .metric-title {{
                font-size: 16px;
                font-weight: normal;
                margin-bottom: 6px;
            }}

            .chart-container {{
                background-color: rgba(255, 255, 255, 0.8);
                padding: 20px;
                border-radius: 12px;
                margin-top: 20px;
                box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
            }}

            .chart-title {{
                font-size: 22px;
                font-weight: 600;
                color: black;
                margin-bottom: 10px;
            }}
            </style>

            <div class="metric-container">
                <div class="metric-box">
                    <div class="metric-title">🎣 Total Catches</div>
                    <div>{total_catches}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-title">⚖️ Total Weight</div>
                    <div>{total_weight}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-title">🏆 Most Caught Species</div>
                    <div>{most_caught_species}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if "species" in df.columns:
            species_count = df["species"].value_counts().reset_index()
            species_count.columns = ["species", "count"]
            fig_species = px.bar(
                species_count,
                x="species",
                y="count",
                text="count",
                color_discrete_sequence=["#4B9CD3"]
            )
            fig_species.update_layout(
                plot_bgcolor='rgba(255,255,255,0.8)',
                paper_bgcolor='rgba(255,255,255,0.8)',
                font_color='black',
                showlegend=False,
                margin=dict(t=30, l=20, r=20, b=40),
                xaxis=dict(title=None, tickfont=dict(color='black', size=12)),
                yaxis=dict(title=None, tickfont=dict(color='black', size=12), showgrid=False)
            )
            fig_species.update_traces(textposition="outside")
            st.markdown('<div class="chart-container"><div class="chart-title">🐟 Catches per Species</div>', unsafe_allow_html=True)
            st.plotly_chart(fig_species, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Bar chart 2 – Total Weight by Fisher using Plotly
        if "fisher_name" in df.columns:
            fisher_group = df.groupby("fisher_name")["weight"].sum().reset_index().sort_values(by="weight", ascending=False)
            fig_fisher = px.bar(
                fisher_group,
                x="fisher_name",
                y="weight",
                text="weight",
                color_discrete_sequence=["#4B9CD3"]
            )
            fig_fisher.update_layout(
                plot_bgcolor='rgba(255,255,255,0.8)',
                paper_bgcolor='rgba(255,255,255,0.8)',
                font_color='black',
                showlegend=False,
                margin=dict(t=30, l=20, r=20, b=40),
                xaxis=dict(title=None, tickfont=dict(color='black', size=12)),
                yaxis=dict(title=None, tickfont=dict(color='black', size=12), showgrid=False)
            )
            fig_fisher.update_traces(textposition="outside")
            st.markdown('<div class="chart-container"><div class="chart-title">👤 Total Weight by Fisher</div>', unsafe_allow_html=True)
            st.plotly_chart(fig_fisher, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.warning("No data to analyze.")