import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils import fetch_coin_history, fetch_current_price, COINS
from cycles import get_cycle_data, get_current_cycle_progress, HALVING_DATES
from dca import calculate_dca
from prediction import generate_fan_chart_data
from languages import TRANSLATIONS

# Page Config
st.set_page_config(
    page_title="Crypto Cycle Analysis",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for "Professional" look and Fixed Top-Right Nav
st.markdown("""
<style>
    .metric-card {
        background-color: #0e1117;
        border: 1px solid #262730;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .stProgress > div > div > div > div {
        background-color: #f63366;
    }
    
    /* Fixed Top Right Language Switcher */
    /* Select the first stHorizontalBlock in the main area (which contains our flags) */
    /* Note: We use a specific structure selector. This is a bit hacky but works for now. */
    /* Strategy: The flags are in the first columns block. We will target the buttons inside it. */
    
    /* Target the container of the buttons to fix it to top right */
    /* We use the sibling selector to find the div immediately after our anchor span */
    /* The anchor span is inserted just before the columns */
    div:has(span#lang-nav-anchor) + div {
        position: fixed !important;
        top: 2.5rem !important; /* Move up slightly */
        right: 4.5rem !important; /* Move left to avoid 3-dots menu */
        width: auto !important;
        z-index: 999990 !important;
        background-color: rgba(14, 17, 23, 0.8) !important;
        border-radius: 15px !important;
        padding: 5px !important;
        gap: 0.5rem !important;
        backdrop-filter: blur(5px);
    }
    
    /* Adjust spacing within the columns */
    div:has(span#lang-nav-anchor) + div > div {
        width: auto !important;
        flex: 0 1 auto !important;
        min-width: 0 !important;
    }

    /* Style the Buttons to look like Icons */
    div:has(span#lang-nav-anchor) + div button {
        border: none !important;
        background: transparent !important;
        padding: 0px 5px !important;
        font-size: 1.2rem !important;
        line-height: 1 !important;
        min-height: 0px !important;
        height: auto !important;
        box-shadow: none !important;
        transition: all 0.3s ease !important;
    }
    
    /* Ensure no background/border on hover/focus/active */
    div:has(span#lang-nav-anchor) + div button:hover,
    div:has(span#lang-nav-anchor) + div button:focus,
    div:has(span#lang-nav-anchor) + div button:active {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: inherit !important;
    }
    
    /* Unselected State (Secondary) -> Dimmed */
    div:has(span#lang-nav-anchor) + div button[kind="secondary"] {
        opacity: 0.3 !important;
        filter: grayscale(100%) !important;
        transform: scale(0.9);
    }
    
    /* Selected State (Primary) -> Bright & Glow */
    div:has(span#lang-nav-anchor) + div button[kind="primary"] {
        opacity: 1.0 !important;
        filter: grayscale(0%) !important;
        transform: scale(1.2);
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
    }
    
    /* Hover Effect */
    div:has(span#lang-nav-anchor) + div button:hover {
        opacity: 1.0 !important;
        transform: scale(1.1);
    }

</style>
""", unsafe_allow_html=True)

# --- Top Right Language Selector ---
# Use columns to position the language selector at the top right
# We use a single block here, CSS will move it to fixed position
# col_spacer is removed as it's not needed for fixed positioning

# Inject Anchor for CSS positioning
st.markdown('<span id="lang-nav-anchor"></span>', unsafe_allow_html=True)

# Language Selector (Icons Only)
# Define available languages and their flags
langs = ["🇬🇧", "🇨🇳", "🇯🇵"]

# Determine current language first to set button types
if 'language' not in st.session_state:
    st.session_state['language'] = "🇬🇧"
current_lang = st.session_state['language']

# Create columns for flags (Compact)
# Use a unique key for the container to target if needed, though :has is used above
c1, c2, c3 = st.columns([1, 1, 1])

def set_lang(l):
    st.session_state['language'] = l
    st.rerun()

with c1:
    # Use type="primary" for selected, "secondary" for unselected
    btn_type = "primary" if current_lang == "🇬🇧" else "secondary"
    if st.button("🇬🇧", key="lang_en", type=btn_type):
        set_lang("🇬🇧")
        
with c2:
    btn_type = "primary" if current_lang == "🇨🇳" else "secondary"
    if st.button("🇨🇳", key="lang_cn", type=btn_type):
        set_lang("🇨🇳")
        
with c3:
    btn_type = "primary" if current_lang == "🇯🇵" else "secondary"
    if st.button("🇯🇵", key="lang_jp", type=btn_type):
        set_lang("🇯🇵")

t = TRANSLATIONS[current_lang] # Get current translation dictionary

# --- Sidebar ---

st.sidebar.title(t["sidebar_title"])

# Coin Selector
# Use radio as requested by user (No dropdowns)
selected_coin = st.sidebar.radio(t["select_asset"], list(COINS.keys()))

# API Key Input
# Default to Auto source, hide selection
selected_source = "Auto"
api_key = None # Settings removed per user request

# with st.sidebar.expander(t["settings"]):
#     api_key = st.text_input(t["api_key_label"], type="password", help=t["api_key_help"])

# Navigation
page_options = list(t["nav_options"].keys())
# Mapping display name to key
page_map = {v: k for k, v in t["nav_options"].items()}

# Determine current page index to maintain state
current_page_canonical = st.session_state.get('current_page_canonical', 'Dashboard')

# t["nav_options"] is {Canonical: Display}
nav_display_values = list(t["nav_options"].values())
nav_canonical_keys = list(t["nav_options"].keys())

try:
    default_index = nav_canonical_keys.index(current_page_canonical)
except ValueError:
    default_index = 0

# Use radio for Navigation for better visibility
page_display = st.sidebar.radio(t["nav_label"], nav_display_values, index=default_index)

# Update current page in session state
# Map back from Display to Canonical
selected_canonical = next((k for k, v in t["nav_options"].items() if v == page_display), "Dashboard")
st.session_state['current_page_canonical'] = selected_canonical

page = selected_canonical

st.sidebar.markdown("---")
# st.sidebar.markdown(t["data_source"])
    
    # Display Current Source
    # if selected_source != "Auto":
    #    st.sidebar.caption(f"Source: {selected_source} (Forced)")
    # elif api_key:
    #    st.sidebar.caption(t["source_coingecko"])
    # else:
    #    # In Auto mode without key, it tries Binance then Yahoo
    #    st.sidebar.caption(f"Source: Binance / Yahoo (Auto)")
    
    # Remove old static captions
    # st.sidebar.caption("v1.3.0 (Binance Added)")

# Fetch Data
with st.spinner(t["fetch_data"].format(coin=selected_coin)):
    df, source_used = fetch_coin_history(selected_coin, api_key, selected_source)
    current_price_data = fetch_current_price(selected_coin, api_key)

if df.empty or not current_price_data:
    st.error(t["load_error"].format(coin=selected_coin))
    st.stop()

# --- Sidebar Footer: Data Source & Author ---
st.sidebar.markdown(t["data_source"])
st.sidebar.info("Binance, Yahoo, CoinGecko")

st.sidebar.markdown("### About Author")

# Try to load local logo
import os
logo_path = "jw_logo.png"
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, width=120)
else:
    st.sidebar.markdown("🦁 **JW**") # Fallback emoji if no image

st.sidebar.markdown("[@JW_CryptoBeggar](https://x.com/JW_CryptoBeggar)")

# --- Page: Dashboard ---
if page == "Dashboard":
    st.title(t["dash_title"].format(coin=selected_coin))
    
    # Top Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    price = current_price_data['usd']
    change_24h = current_price_data['usd_24h_change']
    
    with col1:
        st.metric(t["current_price"], f"${price:,.2f}", f"{change_24h:.2f}%")
        
    progress = get_current_cycle_progress()
    
    with col2:
        st.metric(t["days_since_halving"], f"{progress['days_passed']} Days")
        
    with col3:
        st.metric(t["cycle_progress"], f"{progress['progress_pct']:.1f}%")
        
    with col4:
        next_halving_est = progress['halving_date'] + pd.Timedelta(days=1460) # Rough estimate
        st.metric(t["next_halving"], next_halving_est.strftime("%Y-%m-%d"))

    # Cycle Progress Bar
    st.markdown(t["progress_bar_title"])
    st.progress(progress['progress_pct'] / 100)
    
    # Recent Price Chart
    st.markdown(t["recent_price_title"])
    last_30_days = df.tail(30)
    fig = px.line(last_30_days, x=last_30_days.index, y="price", title=t["chart_price_title"].format(coin=selected_coin))
    fig.update_layout(xaxis_title="Date", yaxis_title="Price (USD)", dragmode="pan")
    st.plotly_chart(fig, use_container_width=True)

# --- Page: Cycle Analysis ---
elif page == "Cycle Analysis":
    st.title(t["cycle_title"].format(coin=selected_coin))
    st.info(t["cycle_info"])
    
    cycles = get_cycle_data(df)
    
    # 1. Full History with Halvings
    st.markdown(t["full_history_title"])
    
    # Log/Linear Toggle
    # Default to Linear as per user request
    scale_type = st.radio("Scale Type", [t["linear_scale_label"], t["log_scale_label"]], horizontal=True, label_visibility="collapsed")
    use_log = (scale_type == t["log_scale_label"])
    
    fig_full = px.line(df, x=df.index, y="price", log_y=use_log, title=t["full_history_chart"].format(coin=selected_coin))
    
    # Add vertical lines for halvings
    # Only show halvings that are within or slightly before the data range to avoid huge empty spaces
    min_date = df.index.min()
    max_date = df.index.max()
    
    # Buffer: Allow halving lines 1 year before data starts to show context, but not 10 years
    buffer_date = min_date - pd.Timedelta(days=365)
    
    for cycle_num, date_str in HALVING_DATES.items():
        h_date = pd.to_datetime(date_str)
        if h_date >= buffer_date:
            fig_full.add_vline(x=h_date, line_width=1, line_dash="dash", line_color="orange")
            # Only add text if it's within the visible range or close to it
            if h_date >= min_date:
                fig_full.add_annotation(x=h_date, y=df['price'].min(), text=f"BTC Halving {cycle_num}", showarrow=False, textangle=-90)
    
    # Adjust Y-axis range to fit data tightly (User Request)
    y_min_val = df['price'].min()
    y_max_val = df['price'].max()
    
    if use_log:
        # Log scale range (log10 units)
        # Add slight padding (e.g. 5% of the log range)
        range_min = np.log10(y_min_val)
        range_max = np.log10(y_max_val)
        log_padding = (range_max - range_min) * 0.05
        fig_full.update_layout(yaxis_range=[range_min - log_padding, range_max + log_padding])
    else:
        # Linear scale range
        # Add 5% padding
        padding = (y_max_val - y_min_val) * 0.05
        fig_full.update_layout(yaxis_range=[y_min_val - padding, y_max_val + padding])

    fig_full.update_layout(yaxis_tickprefix="$", dragmode="pan")
    st.plotly_chart(fig_full, use_container_width=True)
    
    # 2. Cycle Comparison (Overlay)
    st.markdown(t["overlay_title"])
    st.markdown(t["overlay_desc"])
    
    fig_overlay = go.Figure()
    
    colors = {0: "purple", 1: "gray", 2: "blue", 3: "green", 4: "red"}
    
    for cycle_num, data in cycles.items():
        cycle_df = data["data"]
        # Use absolute prices instead of normalized
        if not cycle_df.empty:
            
            fig_overlay.add_trace(go.Scatter(
                x=cycle_df["days_since_halving"],
                y=cycle_df["price"],
                mode='lines',
                name=f"Cycle {cycle_num} ({data['start_date'].year})",
                line=dict(color=colors.get(cycle_num, "black"), width=2 if cycle_num == 4 else 1)
            ))
            
    fig_overlay.update_layout(
        title=t["overlay_chart"],
        xaxis_title="Days Since Halving",
        yaxis_title="Price (USD)",
        yaxis_type="log",
        hovermode="x unified",
        dragmode="pan"
    )
    st.plotly_chart(fig_overlay, use_container_width=True)
    
    # Cycle Stats Table
    st.markdown(t["stats_title"])
    stats_data = []
    for c_num, data in cycles.items():
        # Use actual_start_date if available (handling empty cycles)
        s_date = data.get("actual_start_date")
        if pd.isna(s_date):
            s_date = data["start_date"]
            
        stats_data.append({
            t["col_cycle"]: c_num,
            t["col_start_date"]: s_date.strftime("%Y-%m-%d"),
            t["col_high"]: f"${data['high']:,.2f}" if not pd.isna(data['high']) else "N/A",
            t["col_days_high"]: data["high_days"] if data["high_days"] is not None else "N/A",
            t["col_low"]: f"${data['low']:,.2f}" if not pd.isna(data['low']) else "N/A"
        })
    st.dataframe(pd.DataFrame(stats_data), hide_index=True, use_container_width=True)

# --- Page: Price Prediction ---
elif page == "Price Prediction":
    st.title(t["pred_title"].format(coin=selected_coin))
    st.warning(t["pred_disclaimer"])
    
    cycles = get_cycle_data(df)
    fan_data = generate_fan_chart_data(df, cycles)
    
    if fan_data.empty:
        st.error(t["pred_error"])
    else:
        st.markdown(t["fan_title"])
        st.markdown(t["fan_desc"])
        
        fig_fan = go.Figure()
        
        # Historical Data (Current Cycle)
        current_cycle_df = cycles[4]['data']
        fig_fan.add_trace(go.Scatter(
            x=current_cycle_df.index,
            y=current_cycle_df['price'],
            mode='lines',
            name=t["legend_actual"],
            line=dict(color='#007bff', width=3)
        ))
        
        # Fan Chart Areas
        # 1. Max to Median (Upper zone)
        fig_fan.add_trace(go.Scatter(
            x=fan_data.index,
            y=fan_data['max_price'],
            mode='lines',
            line=dict(width=0),
            showlegend=False
        ))
        
        fig_fan.add_trace(go.Scatter(
            x=fan_data.index,
            y=fan_data['median_price'],
            mode='lines',
            fill='tonexty',
            fillcolor='rgba(0, 255, 0, 0.1)',
            line=dict(color='green', dash='dash'),
            name=t["legend_median"]
        ))
        
        # 2. Median to Min (Lower zone)
        fig_fan.add_trace(go.Scatter(
            x=fan_data.index,
            y=fan_data['min_price'],
            mode='lines',
            fill='tonexty',
            fillcolor='rgba(255, 0, 0, 0.1)',
            line=dict(width=0),
            name=t["legend_range"]
        ))
        
        fig_fan.update_layout(
            title=t["fan_chart_title"].format(coin=selected_coin),
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            yaxis_type="log",
            hovermode="x unified",
            dragmode="pan"
        )
        
        st.plotly_chart(fig_fan, use_container_width=True)
        
        st.markdown(t["levels_title"])
        last_proj = fan_data.iloc[-1]
        c1, c2, c3 = st.columns(3)
        c1.metric(t["metric_low"], f"${last_proj['min_price']:,.2f}")
        c2.metric(t["metric_median"], f"${last_proj['median_price']:,.2f}")
        c3.metric(t["metric_high"], f"${last_proj['max_price']:,.2f}")


# --- Page: DCA Calculator ---
elif page == "DCA Calculator":
    st.title(t["dca_title"].format(coin=selected_coin))
    st.markdown(t["dca_desc"].format(coin=selected_coin))
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader(t["dca_params"])
        amount = st.number_input(t["input_amount"], min_value=10, value=500, step=50)
        
        # Default start date logic: Try to get start of cycle 3, else first date
        default_start = pd.to_datetime("2020-05-11")
        if df.index[0] > default_start:
            default_start = df.index[0]
            
        start_date = st.date_input(t["input_start"], default_start)
        end_date = st.date_input(t["input_end"], pd.Timestamp.now())
        
        if st.button(t["btn_run"]):
            res = calculate_dca(df, amount, "Monthly", start_date, end_date)
            
            if res:
                st.session_state['dca_result'] = res
            else:
                st.error(t["dca_error"])

    with col2:
        if 'dca_result' in st.session_state:
            res = st.session_state['dca_result']
            
            # Summary Metrics
            m1, m2, m3 = st.columns(3)
            m1.metric(t["metric_invested"], f"${res['total_invested']:,.0f}")
            m2.metric(t["metric_value"], f"${res['final_value']:,.0f}")
            m3.metric(t["metric_roi"], f"{res['roi']:.2f}%", delta_color="normal")
            
            st.metric(t["metric_drawdown"], f"{res['max_drawdown']:.2f}%")
            
            # Chart
            history_df = res['history']
            fig_dca = go.Figure()
            fig_dca.add_trace(go.Scatter(x=history_df.index, y=history_df['value'], mode='lines', name=t["metric_value"], fill='tozeroy'))
            fig_dca.add_trace(go.Scatter(x=history_df.index, y=history_df['invested'], mode='lines', name=t["metric_invested"], line=dict(dash='dash')))
            
            fig_dca.update_layout(title=t["dca_chart_title"], xaxis_title="Date", yaxis_title="Value (USD)", dragmode="pan")
            st.plotly_chart(fig_dca, use_container_width=True)
            
            st.success(t["dca_success"])
