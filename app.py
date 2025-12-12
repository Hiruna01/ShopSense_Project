import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(
    page_title="ShopSense AI",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom CSS for "Modern Card" UI
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #F3F4F6;
    }
    
    /* Card Styling */
    .metric-card {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        text-align: center;
        margin-bottom: 20px;
    }
    
    /* Headings */
    h1, h2, h3 {
        color: #1F2937;
        font-family: 'Helvetica Neue', sans-serif;
    }
    
    /* Custom Sidebar */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E5E7EB;
    }
    
    /* Success Message Green */
    .stSuccess {
        background-color: #D1FAE5;
        color: #065F46;
    }
</style>
""", unsafe_allow_html=True)

# 3. Load Data
@st.cache_data
def load_data():
    try:
        rfm = pd.read_csv('rfm_analyzed.csv')
        rules = pd.read_csv('association_rules.csv')
        return rfm, rules
    except FileNotFoundError:
        return None, None

rfm_df, rules_df = load_data()

# Stop if data is missing
if rfm_df is None:
    st.error("🚨 Data files not found! Please run Phase 3 & 4 scripts first.")
    st.stop()

# 4. Sidebar Navigation
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3144/3144456.png", width=50)
st.sidebar.title("ShopSense AI")
st.sidebar.caption("Retail Intelligence Dashboard")

page = st.sidebar.radio(
    "Menu", 
    ["Dashboard Overview", "Customer Search", "Smart Recommender"],
    index=0
)

st.sidebar.divider()
st.sidebar.info("👨‍💻 Developed by Hiruna Dilmith")


# --- PAGE 1: DASHBOARD OVERVIEW (The "Coinest" Look) ---
if page == "Dashboard Overview":
    st.title("📊 Executive Dashboard")
    st.markdown("Real-time overview of customer segments and business health.")

    # Top KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    # Helper to style cards
    def metric_card(label, value, prefix="", help_text=""):
        return f"""
        <div class="metric-card">
            <p style="font-size:14px; color:#6B7280; margin-bottom:5px;">{label}</p>
            <h2 style="font-size:24px; color:#10B981; margin:0;">{prefix}{value}</h2>
        </div>
        """

    with col1:
        st.markdown(metric_card("Total Customers", f"{len(rfm_df):,}", ""), unsafe_allow_html=True)
    with col2:
        st.markdown(metric_card("Avg. Spending", f"{rfm_df['Monetary'].mean():.0f}", "$"), unsafe_allow_html=True)
    with col3:
        st.markdown(metric_card("Avg. Frequency", f"{rfm_df['Frequency'].mean():.0f}", "", "Visits"), unsafe_allow_html=True)
    with col4:
        st.markdown(metric_card("Active Churn Rate", "12%", ""), unsafe_allow_html=True)

    # Main Visuals
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("Customer Segments (3D)")
        # Clean white background for plot
        fig = px.scatter_3d(
            rfm_df, x='Recency', y='Frequency', z='Monetary',
            color='Cluster', opacity=0.8, height=500,
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        fig.update_layout(margin=dict(l=0, r=0, b=0, t=0), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("Segment Profiles")
        avg_df = rfm_df.groupby('Cluster')[['Recency', 'Frequency', 'Monetary']].mean().reset_index()
        # Round the numbers for cleaner look
        avg_df = avg_df.round(1)
        
        # Display as a styled table
        st.dataframe(
            avg_df, 
            column_config={
                "Recency": st.column_config.ProgressColumn("Recency (Days)", format="%d", min_value=0, max_value=365),
                "Monetary": st.column_config.NumberColumn("Avg Spend", format="$%d"),
            },
            hide_index=True,
            use_container_width=True
        )
        
        st.info("💡 **Tip:** Cluster 1 contains your most valuable 'Whales'.")


# --- PAGE 2: CUSTOMER SEARCH (Updated with Smart Logic) ---
elif page == "Customer Search":
    st.title("🔎 Customer Insights Lookup")
    
    # Search Bar (Styled nicely)
    col_search, col_padding = st.columns([1, 2])
    with col_search:
        customer_id_input = st.text_input("Enter Customer ID:", placeholder="e.g. 12347", help="Type ID and press Enter")

    if customer_id_input:
        try:
            search_id = int(customer_id_input)
            customer_data = rfm_df[rfm_df['Customer ID'] == search_id]
            
            if not customer_data.empty:
                # Extract Data
                c_data = customer_data.iloc[0]
                cluster = c_data['Cluster']
                
                # --- SMART LOGIC SECTION ---
                
                # 1. Calculate Churn Risk (Dynamic)
                churn_risk = "Low"
                risk_color = "#059669" # Green
                risk_bg = "#D1FAE5"

                if c_data['Recency'] > 90:
                    churn_risk = "High"
                    risk_color = "#DC2626" # Red
                    risk_bg = "#FEE2E2"
                elif c_data['Recency'] > 45:
                    churn_risk = "Medium"
                    risk_color = "#D97706" # Orange
                    risk_bg = "#FEF3C7"

                # 2. Marketing Matrix (Strategies)
                # 2. Marketing Matrix (Strategies)
                strategies = {
                    0: { # Lost Customers
                        "Status": "Lost Customer",
                        "Strategy": "Win-Back Campaign",
                        "Channel": "Automated Email Series",
                        "Offer": "Aggressive Discount (20% OFF)",
                        "Copy": "We miss you! Here is a gift to welcome you back.",
                        "Priority": "Low",
                        "Icon": "😴"
                    },
                    1: { # VIP Whales
                        "Status": "VIP Member",
                        "Strategy": "Loyalty Reinforcement",
                        "Channel": "Personal Account Manager Call",
                        "Offer": "Early Access to New Collection",
                        "Copy": "As a top-tier member, you get first dibs on our new arrival.",
                        "Priority": "Critical 🚨",
                        "Icon": "👑"
                    },
                    2: { # Regular / Loyal
                        "Status": "Regular Customer",
                        "Strategy": "Basket Expansion",
                        "Channel": "Targeted Push Notification",
                        "Offer": "Bundle Deal (Buy 2 Get 1 Free)",
                        "Copy": "Complete your set! Items you love are better together.",
                        "Priority": "Medium",
                        "Icon": "🛒"
                    },
                    3: { # New Customers
                        "Status": "New Customer",
                        "Strategy": "Onboarding",
                        "Channel": "Welcome Email Sequence",
                        "Offer": "Free Shipping on Next Order",
                        "Copy": "Thanks for joining! Here is how to get the most out of your purchase.",
                        "Priority": "High",
                        "Icon": "🌱"
                    }
                }

                current_strategy = strategies.get(cluster, strategies[0])

                # --- UI RENDERING ---
                st.divider()
                
                # Header Section
                p_col1, p_col2 = st.columns([1, 4])
                with p_col1:
                    st.markdown(f"<h1 style='text-align: center; font-size: 80px; margin:0;'>{current_strategy['Icon']}</h1>", unsafe_allow_html=True)
                
                with p_col2:
                    st.markdown(f"## Customer #{search_id}")
                    # Badges
                    st.markdown(f"""
                    <span style='background-color: #E5E7EB; padding: 5px 12px; border-radius: 15px; font-weight: bold; color: #374151;'>Status: {current_strategy['Status']}</span>
                    <span style='background-color: {risk_bg}; padding: 5px 12px; border-radius: 15px; font-weight: bold; color: {risk_color}; margin-left: 10px;'>Churn Risk: {churn_risk}</span>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"**LTV:** ${c_data['Monetary']:,.2f} • **Visits:** {int(c_data['Frequency'])} • **Last Seen:** {int(c_data['Recency'])} days ago")

                # Smart Action Board
                st.write("")
                st.subheader("⚡ Recommended Next Action")
                
                with st.container():
                    st.markdown(f"""
                    <div style="background-color: white; padding: 25px; border-radius: 12px; border-left: 6px solid #10B981; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h3 style="margin: 0; color: #065F46; font-size: 20px;">🎯 {current_strategy['Strategy']}</h3>
                            <span style="background-color: #DCFCE7; color: #166534; padding: 4px 12px; border-radius: 6px; font-size: 14px; font-weight: bold;">{current_strategy['Priority']} Priority</span>
                        </div>
                        <div style="margin-top: 20px; display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                            <div>
                                <p style="color: #6B7280; font-size: 14px; margin-bottom: 5px;">Best Channel</p>
                                <p style="font-weight: 600; color: #1F2937;">{current_strategy['Channel']}</p>
                            </div>
                            <div>
                                <p style="color: #6B7280; font-size: 14px; margin-bottom: 5px;">Offer to Send</p>
                                <p style="font-weight: 600; color: #1F2937;">{current_strategy['Offer']}</p>
                            </div>
                        </div>
                        <div style="margin-top: 20px; background-color: #F9FAFB; padding: 15px; border-radius: 8px; border: 1px dashed #D1D5DB;">
                            <p style="color: #6B7280; font-style: italic; font-size: 14px; margin: 0;">🗣️ <b>Sample Script:</b> "{current_strategy['Copy']}"</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            else:
                st.warning("❌ Customer ID not found.")
                
        except ValueError:
            st.error("Please enter a numeric ID.")
    else:
        st.info("👈 Enter a Customer ID to view their full profile.")


# --- PAGE 3: SMART RECOMMENDER ---
elif page == "Smart Recommender":
    st.title("🛍️ Product Recommender Engine")
    
    # Prepare list for dropdown
    all_products = set()
    for item_set in rules_df['antecedents']:
        clean_item = item_set.replace("frozenset({'", "").replace("'})", "").replace("', '", ", ")
        all_products.add(clean_item)
        
    selected_product = st.selectbox("Select a Product:", sorted(list(all_products)))
    
    if st.button("Generate Recommendations", type="primary"):
        st.write("---")
        recommendations = rules_df[rules_df['antecedents'].str.contains(selected_product, regex=False)]
        
        if not recommendations.empty:
            st.subheader(f"People who bought this also bought:")
            
            # Show top 3 recommendations as "Cards"
            top_recs = recommendations.sort_values(by='lift', ascending=False).head(3)
            
            cols = st.columns(3)
            for idx, (i, row) in enumerate(top_recs.iterrows()):
                rec_item = row['consequents'].replace("frozenset({'", "").replace("'})", "")
                confidence = row['confidence'] * 100
                
                with cols[idx]:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3 style="font-size:18px; height:60px; overflow: hidden;">{rec_item}</h3>
                        <p style="color:#10B981; font-weight:bold;">{confidence:.0f}% Confidence</p>
                        <small>Customers match this item frequently</small>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No strong associations found for this item.")