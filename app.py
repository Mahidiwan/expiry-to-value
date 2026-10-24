import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
from db import get_connection

st.set_page_config(
    page_title="Expiry-to-Value",
    page_icon="🥬",
    layout="wide"
)

# ---------------- PAGE DESIGN ----------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root {
  --forest: #174c36; --forest-deep: #103b2a; --leaf: #2f855a;
  --mint: #d9f99d; --mint-pale: #f0fdf4; --ivory: #fbfaf5;
  --ink: #1d3027; --muted: #647568; --line: #dce8dc;
  --amber: #b7791f; --coral: #c2413b;
}
.stApp { background: var(--ivory); color: var(--ink); font-family: 'DM Sans', sans-serif; }
[data-testid="stHeader"] { background: rgba(251,250,245,.94); }
.block-container { padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1480px; }
h1,h2,h3,h4 { font-family: 'Manrope', sans-serif !important; color: var(--forest) !important; letter-spacing: -.035em; }
p, label, .stMarkdown { color: var(--ink); }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #e6f4e7 0%, #f3f8ed 100%); border-right: 1px solid #d3e5d2; }
[data-testid="stSidebar"] > div:first-child { padding-top: 1.25rem; }
[data-testid="stSidebar"] * { color: var(--forest); }
[data-testid="stSidebar"] [data-testid="stRadio"] label { border-radius: 10px; padding: .42rem .55rem; }
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover { background: #d9f0d8; }
/* Cohesive, light form controls across every page */
.stSelectbox [data-baseweb="select"] > div,
.stMultiSelect [data-baseweb="select"] > div,
[data-testid="stNumberInput"] input,
[data-testid="stTextInput"] input,
[data-testid="stDateInput"] input,
[data-testid="stTimeInput"] input,
[data-testid="stTextArea"] textarea,
[data-baseweb="input"] > div,
[data-baseweb="textarea"] > div {
  background: #ffffff !important;
  color: var(--ink) !important;
  border: 1px solid #cbdccb !important;
  border-radius: 11px !important;
  box-shadow: 0 1px 2px rgba(23,76,54,.025) !important;
}
.stSelectbox [data-baseweb="select"] > div:hover,
.stMultiSelect [data-baseweb="select"] > div:hover,
[data-testid="stNumberInput"] input:hover,
[data-testid="stTextInput"] input:hover,
[data-testid="stDateInput"] input:hover,
[data-testid="stTextArea"] textarea:hover {
  border-color: #83b795 !important;
}
.stSelectbox [data-baseweb="select"] > div:focus-within,
.stMultiSelect [data-baseweb="select"] > div:focus-within,
[data-testid="stNumberInput"] input:focus,
[data-testid="stTextInput"] input:focus,
[data-testid="stDateInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
  border-color: var(--leaf) !important;
  box-shadow: 0 0 0 2px rgba(47,133,90,.14) !important;
}
[data-testid="stNumberInput"] button {
  background: #edf6ed !important;
  color: var(--forest) !important;
  border-color: #d4e5d4 !important;
}
[data-baseweb="popover"] [role="listbox"],
[data-baseweb="menu"] { background: #fff !important; border: 1px solid var(--line) !important; }
[data-baseweb="popover"] [role="option"] { color: var(--ink) !important; }
.stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] > button {
  background: var(--forest); color: white; border: 1px solid var(--forest);
  border-radius: 10px; font-weight: 700; padding: .55rem 1rem; transition: all .18s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover {
  background: var(--leaf); color: white; border-color: var(--leaf); transform: translateY(-1px);
}
div[data-testid="stMetric"] { background: #fff; border: 1px solid var(--line); padding: 1rem; border-radius: 16px; box-shadow: 0 4px 16px rgba(23,76,54,.04); }
[data-testid="stDataFrame"], [data-testid="stTable"] { border: 1px solid var(--line); border-radius: 12px; overflow: hidden; }
hr { border-color: var(--line) !important; }
.main-title { font-family: 'Manrope',sans-serif; font-size: clamp(2.1rem,4vw,3.2rem); line-height: 1.08; font-weight: 800; letter-spacing: -.055em; color: var(--forest); margin-bottom: .45rem; }
.sub-title { color: var(--muted); font-size: 1.02rem; margin-bottom: 1.25rem; }
.etv-eyebrow { color: var(--leaf); font-size: .74rem; text-transform: uppercase; font-weight: 800; letter-spacing: .16em; margin-bottom: .55rem; }
.etv-intro { color: var(--muted); font-size: 1rem; margin-top: -.25rem; margin-bottom: 1.35rem; }
.etv-card { min-height: 145px; padding: 1.1rem; border-radius: 17px; border: 1px solid var(--line); background: #fff; box-shadow: 0 5px 18px rgba(23,76,54,.045); border-top: 4px solid var(--accent, #2f855a); }
.etv-card-label { display:flex; gap:.5rem; align-items:center; color:var(--muted); font-size:.88rem; font-weight:700; }
.etv-card-value { color:var(--forest); font-size:clamp(1.5rem,2.2vw,2rem); font-weight:800; letter-spacing:-.04em; margin-top:.75rem; }
.etv-card-note { color:var(--muted); font-size:.8rem; margin-top:.25rem; }
.hero-panel { background-image: linear-gradient(90deg, rgba(12,48,31,.94) 0%, rgba(18,62,43,.86) 48%, rgba(18,62,43,.46) 100%), url("https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=1800&q=85"); background-position: center, center 48%; background-size: cover; color: #fff; padding: clamp(1.4rem,4vw,3.2rem); border-radius: 26px; position:relative; overflow:hidden; box-shadow: 0 14px 32px rgba(23,76,54,.12); }
.hero-panel h1, .hero-panel h2, .hero-panel p { color:#fff !important; }
.hero-kicker { color:#d9f99d; text-transform:uppercase; font-size:.75rem; font-weight:800; letter-spacing:.16em; }
.hero-copy { color:#e5f3e8 !important; font-size:1.05rem; max-width:720px; line-height:1.7; }
.feature-tile { background:#fff; border:1px solid var(--line); border-radius:17px; padding:1.15rem; height:100%; }
.feature-icon { color:var(--leaf); font-size:1.35rem; font-weight:800; }
.feature-title { color:var(--forest); font-size:1.02rem; font-weight:800; margin:.4rem 0; }
.feature-copy { color:var(--muted); font-size:.9rem; line-height:1.55; }
.step-num { display:inline-block; padding:.35rem .65rem; border-radius:9px; background:#e1f5df; color:var(--forest); font-weight:800; }
@media (max-width:760px) { .etv-card { min-height:125px; padding:.85rem; } .etv-card-value { font-size:1.5rem; } .hero-panel { border-radius:18px; } }
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="main-title">Expiry-to-Value<span style="color:#84a85a">.</span></div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="sub-title">A smarter way to manage fresh inventory, protect value, and reduce avoidable food waste.</div>',
    unsafe_allow_html=True
)


# ---------------- DATABASE FUNCTIONS ----------------

def get_connection_safe():
    return get_connection()


def load_data(query, params=None):
    connection = None
    try:
        connection = get_connection_safe()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        rows = cursor.fetchall()
        cursor.close()
        return pd.DataFrame(rows)
    finally:
        if connection is not None and connection.is_connected():
            connection.close()


def execute_query(query, params=None):
    connection = None
    try:
        connection = get_connection_safe()
        cursor = connection.cursor()
        cursor.execute(query, params or ())
        connection.commit()
        cursor.close()
        return True, "Operation completed successfully."
    except Exception as e:
        if connection is not None:
            connection.rollback()
        return False, str(e)
    finally:
        if connection is not None and connection.is_connected():
            connection.close()


def get_columns(table_name):
    df = load_data(
        """
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = %s
        """,
        (table_name,)
    )
    return df["COLUMN_NAME"].tolist() if not df.empty else []


def find_column(columns, possible_names):
    lower_columns = {c.lower(): c for c in columns}
    for name in possible_names:
        if name.lower() in lower_columns:
            return lower_columns[name.lower()]
    return None


def get_inventory_data():
    batch_cols = get_columns("inventory_batch")
    product_cols = get_columns("product")
    store_cols = get_columns("store")

    batch_id = find_column(batch_cols, ["batch_id", "inventory_batch_id"])
    batch_product_id = find_column(batch_cols, ["product_id"])
    batch_store_id = find_column(batch_cols, ["store_id"])
    quantity_col = find_column(
        batch_cols, ["quantity_available", "quantity", "available_quantity"]
    )
    expiry_col = find_column(batch_cols, ["expiry_date", "expiration_date"])
    product_id = find_column(product_cols, ["product_id"])
    product_name = find_column(product_cols, ["product_name", "name"])
    store_id = find_column(store_cols, ["store_id"])
    store_name = find_column(store_cols, ["store_name", "name"])
    batch_cost_col = find_column(batch_cols, ["unit_cost", "cost_price"])
    product_price_col = find_column(
        product_cols, ["selling_price", "unit_price", "price", "cost_price"]
    )

    required = [
        batch_id, batch_product_id, batch_store_id, quantity_col,
        expiry_col, product_id, product_name, store_id, store_name
    ]
    if any(col is None for col in required):
        raise ValueError(
            "Some required columns could not be found. "
            "Check the column names in inventory_batch, product and store."
        )

    # Inventory-at-risk is valued at batch purchase cost where available.
    # Fall back to the product selling price only for schemas without batch cost.
    if batch_cost_col:
        price_expression = f"COALESCE(b.`{batch_cost_col}`, 0)"
    elif product_price_col:
        price_expression = f"COALESCE(p.`{product_price_col}`, 0)"
    else:
        price_expression = "0"

    query = f"""
        SELECT
            b.`{batch_id}` AS batch_id,
            p.`{product_name}` AS product_name,
            s.`{store_name}` AS store_name,
            b.`{quantity_col}` AS quantity_available,
            b.`{expiry_col}` AS expiry_date,
            {price_expression} AS unit_price,
            (b.`{quantity_col}` * {price_expression}) AS inventory_value,
            DATEDIFF(b.`{expiry_col}`, CURDATE()) AS days_to_expiry,
            CASE
                WHEN b.`{expiry_col}` < CURDATE() THEN 'EXPIRED'
                WHEN DATEDIFF(b.`{expiry_col}`, CURDATE()) <= 3 THEN 'CRITICAL'
                WHEN DATEDIFF(b.`{expiry_col}`, CURDATE()) <= 7 THEN 'WARNING'
                ELSE 'SAFE'
            END AS expiry_status
        FROM inventory_batch b
        JOIN product p
            ON b.`{batch_product_id}` = p.`{product_id}`
        JOIN store s
            ON b.`{batch_store_id}` = s.`{store_id}`
        WHERE b.`{quantity_col}` > 0
        ORDER BY b.`{expiry_col}` ASC
    """
    return load_data(query)


# ---------------- SIDEBAR ----------------

st.sidebar.markdown("## 🥬 Expiry-to-Value")
st.sidebar.caption("Perishable inventory • less waste")
st.sidebar.title("Navigation")
page_options = [
    "Home",
    "Dashboard",
    "Inventory Management",
    "Stock Movement",
    "SQL Reports",
    "About Project"
]
if "etv_requested_page" in st.session_state:
    st.session_state["etv_page_choice"] = st.session_state.pop("etv_requested_page")
page = st.sidebar.radio(
    "Choose a page",
    page_options,
    key="etv_page_choice"
)


# ---------------- HOME / LANDING PAGE ----------------

if page == "Home":
    st.markdown("""
    <section class="hero-panel">
      <div class="hero-kicker">Smarter stock. Less waste.</div>
      <h1 style="font-size:clamp(2.2rem,5vw,4rem);line-height:1.03;margin:.8rem 0 1rem;">
        Turn expiring inventory<br>into an opportunity.
      </h1>
      <p class="hero-copy">
        Expiry-to-Value helps store teams spot at-risk stock earlier, take informed action,
        and make every batch count — from receiving inventory to recording its final movement.
      </p>
    </section>
    """, unsafe_allow_html=True)
    st.write("")
    cta1, cta2, cta3 = st.columns([1.15, 1.15, 3])
    with cta1:
        if st.button("Open dashboard", use_container_width=True, type="primary"):
            st.session_state["etv_requested_page"] = "Dashboard"
            st.rerun()
    with cta2:
        if st.button("Add inventory", use_container_width=True):
            st.session_state["etv_requested_page"] = "Inventory Management"
            st.rerun()
    st.write("")
    st.markdown("### Your inventory, with more clarity")
    st.markdown("Use expiry-aware workflows to prioritize urgent batches, track stock movement, and export reports for follow-up.")
    feature_cols = st.columns(3, gap="medium")
    features = [
        ("01", "Smart expiry tracking", "Classify active batches as expired, critical, warning, or safe using the expiry date stored in MySQL."),
        ("02", "Inventory visibility", "Search and filter by product, store, and expiry status to find the stock that needs attention."),
        ("03", "Actionable reporting", "Record sold, donated, and discarded quantities, then export report results as CSV.")
    ]
    for col, (num, title, copy) in zip(feature_cols, features):
        with col:
            st.markdown(f'<div class="feature-tile"><div class="feature-icon">{num}</div><div class="feature-title">{title}</div><div class="feature-copy">{copy}</div></div>', unsafe_allow_html=True)
    st.write("")
    st.markdown("### How it works")
    step_cols = st.columns(4, gap="small")
    steps = [
        ("1", "Receive", "Add a batch with supplier, store, quantity, cost, and expiry date."),
        ("2", "Monitor", "Review expiry status and inventory value from the live database."),
        ("3", "Act", "Record sales, donations, or discards so available stock stays accurate."),
        ("4", "Learn", "Use SQL reports and CSV exports to support operational decisions.")
    ]
    for col, (num, title, copy) in zip(step_cols, steps):
        with col:
            st.markdown(f'<div class="feature-tile"><span class="step-num">{num}</span><div class="feature-title">{title}</div><div class="feature-copy">{copy}</div></div>', unsafe_allow_html=True)
    st.write("")
    st.markdown("### Live inventory snapshot")
    try:
        home_df = get_inventory_data()
        if home_df.empty:
            st.info("Your inventory is empty or has no available stock yet. Add a batch to start tracking expiry risk.")
        else:
            active_units = int(pd.to_numeric(home_df["quantity_available"], errors="coerce").fillna(0).sum())
            expiring = int(home_df["expiry_status"].isin(["EXPIRED", "CRITICAL", "WARNING"]).sum())
            expired = int((home_df["expiry_status"] == "EXPIRED").sum())
            at_risk_value = float(home_df.loc[home_df["expiry_status"].isin(["EXPIRED", "CRITICAL", "WARNING"]), "inventory_value"].sum())
            live_metrics = st.columns(4)
            for col, label, value, note in zip(
                live_metrics,
                ["Available units", "Batches needing attention", "Expired batches", "At-risk stock value"],
                [f"{active_units:,}", f"{expiring:,}", f"{expired:,}", f"₹{at_risk_value:,.2f}"],
                ["Across active batches", "Expired or due within 7 days", "Expiry date has passed", "Estimated cost value"]
            ):
                with col:
                    st.markdown(f'<div class="etv-card"><div class="etv-card-label">{label}</div><div class="etv-card-value">{value}</div><div class="etv-card-note">{note}</div></div>', unsafe_allow_html=True)
            st.caption("Metrics above are calculated from the connected MySQL inventory, not sample figures.")
    except Exception:
        st.info("Connect to MySQL to display live inventory impact metrics.")
    st.write("")
    st.markdown('<div class="feature-tile"><div class="feature-title">Built around a practical goal</div><div class="feature-copy">Reduce avoidable waste by making expiry risk visible early. Discount recommendations, customer-facing discounted listings, and sustainability totals can be added as a next step when the related business rules and campaign workflow are confirmed.</div></div>', unsafe_allow_html=True)

# ---------------- DASHBOARD ----------------

elif page == "Dashboard":
    st.markdown('<div class="etv-eyebrow">OVERVIEW</div>', unsafe_allow_html=True)
    st.header("Inventory overview")
    st.markdown(
        '<div class="etv-intro">A live snapshot of stock health, expiry exposure and recoverable inventory value.</div>',
        unsafe_allow_html=True
    )

    try:
        df = get_inventory_data()

        # Visible diagnostics and useful empty-state message
        if df.empty:
            st.info(
                "No active inventory batches were found. "
                "Add inventory from the Inventory Management page."
            )
        else:
            st.subheader("🔎 Find inventory")
            filter_col1, filter_col2, filter_col3 = st.columns([2, 2, 1.5])
            with filter_col1:
                search_text = st.text_input("Search product or batch ID", placeholder="e.g. Milk or 12")
            with filter_col2:
                store_options = ["All stores"] + sorted(df["store_name"].dropna().astype(str).unique().tolist())
                selected_store = st.selectbox("store", store_options)
            with filter_col3:
                status_options = ["All statuses"] + [x for x in ["EXPIRED", "CRITICAL", "WARNING", "SAFE"] if x in df["expiry_status"].values]
                selected_status = st.selectbox("Expiry status", status_options)
            if search_text.strip():
                term = search_text.strip().lower()
                df = df[df["product_name"].astype(str).str.lower().str.contains(term, na=False) | df["batch_id"].astype(str).str.lower().str.contains(term, na=False)]
            if selected_store != "All stores":
                df = df[df["store_name"].astype(str) == selected_store]
            if selected_status != "All statuses":
                df = df[df["expiry_status"] == selected_status]
            st.download_button("⬇️ Export filtered inventory (CSV)", data=df.to_csv(index=False).encode("utf-8-sig"), file_name="expiry_to_value_inventory.csv", mime="text/csv")
            if df.empty:
                st.warning("No inventory matches those search and filter choices. Clear a filter and try again.")
                st.stop()
            else:
                expiring_soon = int(df["expiry_status"].isin(["EXPIRED", "CRITICAL", "WARNING"]).sum())
                if expiring_soon:
                    st.warning(f"⚠️ Expiry alert: {expiring_soon} batch(es) in the current view are expired or expiring within 7 days. Review the attention table below.")
                else:
                    st.success("🌿 No expiry-risk batches in the current view.")
            total_batches = len(df)
            critical = int(df["expiry_status"].isin(["EXPIRED", "CRITICAL"]).sum())
            warning = int((df["expiry_status"] == "WARNING").sum())
            at_risk_value = float(
                df.loc[
                    df["expiry_status"].isin(["EXPIRED", "CRITICAL", "WARNING"]),
                    "inventory_value"
                ].sum()
            )

            # Styled HTML metric cards; values are still calculated from live MySQL data.
            metric_cards = [
                ("📦", "Active batches", f"{total_batches:,}", "Batches with stock available", "#34d399"),
                ("🔴", "Critical / expired", f"{critical:,}", "Needs immediate attention", "#fb7185"),
                ("🟠", "Warning", f"{warning:,}", "Expiring within 4–7 days", "#fbbf24"),
                ("💰", "Value at risk", f"₹{at_risk_value:,.2f}", "Estimated value of at-risk stock", "#60a5fa"),
            ]
            metric_columns = st.columns(4, gap="medium")
            for column, (icon, label, value, note, accent) in zip(metric_columns, metric_cards):
                with column:
                    st.markdown(
                        f"""
                        <div class="etv-card" style="--accent:{accent}">
                            <div class="etv-card-label"><span>{icon}</span><span>{label}</span></div>
                            <div class="etv-card-value">{value}</div>
                            <div class="etv-card-note">{note}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
            st.divider()
            st.subheader("📈 Inventory Expiry Status")
            st.caption("Explore how your active batches and inventory value are distributed by expiry status.")

            status_counts = (
                df["expiry_status"]
                .value_counts()
                .rename_axis("Status")
                .reset_index(name="Batches")
            )

            left, right = st.columns(2)

            with left:
                fig = px.pie(
                    status_counts,
                    names="Status",
                    values="Batches",
                    title="Batches by Expiry Status",
                    hole=0.35,
                    color="Status",
                    color_discrete_map={
                        "EXPIRED": "#f43f5e",
                        "CRITICAL": "#fb7185",
                        "WARNING": "#fbbf24",
                        "SAFE": "#34d399"
                    }
                )
                fig.update_layout(
                    template="plotly_white",
                    paper_bgcolor="#ffffff",
                    plot_bgcolor="#ffffff",
                    margin=dict(l=12, r=12, t=60, b=12),
                    legend_title_text="Expiry status"
                )
                st.plotly_chart(fig, use_container_width=True)

            with right:
                value_by_status = (
                    df.groupby("expiry_status", as_index=False)["inventory_value"]
                    .sum()
                )
                fig = px.bar(
                    value_by_status,
                    x="expiry_status",
                    y="inventory_value",
                    title="Inventory Value by Expiry Status",
                    labels={
                        "expiry_status": "Expiry Status",
                        "inventory_value": "Inventory Value (₹)"
                    },
                    color="expiry_status",
                    color_discrete_map={
                        "EXPIRED": "#f43f5e",
                        "CRITICAL": "#fb7185",
                        "WARNING": "#fbbf24",
                        "SAFE": "#34d399"
                    }
                )
                fig.update_layout(
                    template="plotly_white",
                    paper_bgcolor="#ffffff",
                    plot_bgcolor="#ffffff",
                    margin=dict(l=12, r=12, t=60, b=12),
                    showlegend=False,
                    yaxis_title="Inventory value (₹)",
                    xaxis_title=""
                )
                st.plotly_chart(fig, use_container_width=True)

            st.subheader("⚠️ Inventory Requiring Attention")
            risky = df[df["expiry_status"].isin(
                ["EXPIRED", "CRITICAL", "WARNING"]
            )].copy()

            if risky.empty:
                st.success("No batches currently require expiry attention.")
            else:
                st.dataframe(
                    risky[
                        [
                            "batch_id", "product_name", "store_name",
                            "quantity_available", "expiry_date",
                            "days_to_expiry", "inventory_value",
                            "expiry_status"
                        ]
                    ],
                    use_container_width=True,
                    hide_index=True
                )

            st.subheader("Recent stock activity")
            try:
                recent_activity = load_data("""
                    SELECT sm.movement_id, sm.movement_type, sm.quantity,
                           sm.movement_date, sm.notes, p.product_name,
                           b.batch_code
                    FROM stock_movement sm
                    JOIN inventory_batch b ON sm.batch_id = b.batch_id
                    JOIN product p ON b.product_id = p.product_id
                    ORDER BY sm.movement_date DESC
                    LIMIT 8
                """)
                if recent_activity.empty:
                    st.caption("No stock movements have been recorded yet.")
                else:
                    st.dataframe(recent_activity, use_container_width=True, hide_index=True)
            except Exception:
                st.caption("Recent activity is unavailable. Check the stock_movement table schema.")

            with st.expander("View all active inventory"):
                st.dataframe(df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error("The dashboard could not load data from MySQL.")
        st.code(str(e))
        st.info(
            "Check that MySQL is running, db.py connects to "
            "expiry_to_value, and the required tables contain the expected columns."
        )


# ---------------- INVENTORY MANAGEMENT ----------------

elif page == "Inventory Management":
    st.header("Inventory management")

    try:
        product_df = load_data(
            "SELECT product_id, product_name FROM product ORDER BY product_name"
        )
        store_df = load_data(
            "SELECT store_id, store_name FROM store ORDER BY store_name"
        )
        supplier_df = load_data(
            "SELECT supplier_id, supplier_name FROM supplier ORDER BY supplier_name"
        )

        if product_df.empty or store_df.empty or supplier_df.empty:
            st.warning("Add products, stores, and suppliers to the database first.")
        else:
            with st.form("add_inventory_form"):
                st.subheader("Add an Inventory Batch")

                product_choice = st.selectbox(
                    "product",
                    product_df.to_dict("records"),
                    format_func=lambda x: x["product_name"]
                )
                supplier_choice = st.selectbox(
                    "supplier",
                    supplier_df.to_dict("records"),
                    format_func=lambda x: x["supplier_name"]
                )
                store_choice = st.selectbox(
                    "store",
                    store_df.to_dict("records"),
                    format_func=lambda x: x["store_name"]
                )
                quantity = st.number_input(
                    "Quantity Received / Available", min_value=1, step=1
                )
                batch_code = st.text_input(
                    "Batch Code",
                    placeholder="e.g. MIL-W02"
                )
                received_date = st.date_input(
                    "Received Date", value=date.today()
                )
                expiry_date = st.date_input(
                    "Expiry Date", value=date.today()
                )
                unit_cost = st.number_input(
                    "Unit Cost (₹)", min_value=0.0, step=0.5, format="%.2f"
                )

                submitted = st.form_submit_button("Add Batch")

                if submitted:
                    if not batch_code.strip():
                        st.error("Please enter a batch code.")
                    elif expiry_date < received_date:
                        st.error("Expiry date cannot be before the received date.")
                    else:
                        ok, message = execute_query(
                            """
                            INSERT INTO inventory_batch
                                (product_id, supplier_id, store_id, batch_code,
                                 received_date, expiry_date, quantity_received,
                                 quantity_available, unit_cost)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """,
                            (
                                product_choice["product_id"],
                                supplier_choice["supplier_id"],
                                store_choice["store_id"],
                                batch_code.strip(),
                                received_date,
                                expiry_date,
                                int(quantity),
                                int(quantity),
                                float(unit_cost)
                            )
                        )

                        if ok:
                            st.success("Inventory batch added successfully.")
                            st.rerun()
                        else:
                            st.error(message)

        st.subheader("Current Inventory")
        inventory_df = get_inventory_data()
        st.dataframe(inventory_df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error("Could not load inventory management.")
        st.code(str(e))


# ---------------- STOCK MOVEMENT ----------------

elif page == "Stock Movement":
    st.header("Stock movement")
    st.write("Record stock that was sold, donated or discarded.")

    try:
        batch_df = get_inventory_data()
        employee_df = load_data(
            "SELECT * FROM employee"
        )

        if batch_df.empty:
            st.warning("No active batches are available for stock movement.")
        elif employee_df.empty:
            st.warning("No employees are available in the database.")
        else:
            employee_cols = get_columns("employee")
            employee_id_col = find_column(
                employee_cols, ["employee_id", "emp_id"]
            )
            employee_name_col = find_column(
                employee_cols, ["employee_name", "name", "full_name"]
            )
            employee_store_col = find_column(employee_cols, ["store_id"])

            movement_cols = get_columns("stock_movement")
            movement_batch_col = find_column(
                movement_cols, ["batch_id", "inventory_batch_id"]
            )
            movement_employee_col = find_column(
                movement_cols, ["employee_id", "emp_id"]
            )
            movement_type_col = find_column(
                movement_cols, ["movement_type", "movement"]
            )
            movement_quantity_col = find_column(
                movement_cols, ["quantity", "quantity_moved"]
            )
            movement_date_col = find_column(
                movement_cols, ["movement_date", "movement_datetime", "date"]
            )
            movement_notes_col = find_column(
                movement_cols, ["notes", "remarks", "description"]
            )

            required = [
                employee_id_col, movement_batch_col,
                movement_employee_col, movement_type_col,
                movement_quantity_col
            ]
            if any(col is None for col in required):
                st.warning(
                    "The stock_movement or employee table uses different column names. "
                    "See the error-free inventory page, and check your table schema."
                )
            else:
                if employee_name_col is None:
                    employee_df["display_name"] = (
                        employee_df[employee_id_col].astype(str)
                    )
                    employee_name_col = "display_name"

                with st.form("movement_form"):
                    selected_batch = st.selectbox(
                        "Inventory Batch",
                        batch_df.to_dict("records"),
                        format_func=lambda x:
                            f'Batch {x["batch_id"]} - {x["product_name"]} '
                            f'(available: {x["quantity_available"]})'
                    )
                    selected_employee = st.selectbox(
                        "employee",
                        employee_df.to_dict("records"),
                        format_func=lambda x: str(x[employee_name_col])
                    )
                    movement_type = st.selectbox(
                        "Movement Type", ["SOLD", "DONATED", "DISCARDED"]
                    )
                    movement_quantity = st.number_input(
                        "Quantity", min_value=1, step=1
                    )
                    notes = st.text_input("Notes (optional)")
                    submitted = st.form_submit_button("Record Movement")

                    if submitted:
                        available = int(selected_batch["quantity_available"])

                        if int(movement_quantity) > available:
                            st.error(
                                f"Only {available} units are available in this batch."
                            )
                        else:
                            connection = None
                            try:
                                connection = get_connection_safe()
                                cursor = connection.cursor()

                                update_quantity_col = find_column(
                                    get_columns("inventory_batch"),
                                    ["quantity_available", "quantity", "available_quantity"]
                                )
                                batch_id_col = find_column(
                                    get_columns("inventory_batch"),
                                    ["batch_id", "inventory_batch_id"]
                                )

                                cursor.execute(
                                    f"""
                                    UPDATE inventory_batch
                                    SET `{update_quantity_col}` =
                                        `{update_quantity_col}` - %s
                                    WHERE `{batch_id_col}` = %s
                                      AND `{update_quantity_col}` >= %s
                                    """,
                                    (
                                        int(movement_quantity),
                                        selected_batch["batch_id"],
                                        int(movement_quantity)
                                    )
                                )

                                if cursor.rowcount != 1:
                                    raise ValueError(
                                        "Stock could not be updated. "
                                        "Refresh the page and try again."
                                    )

                                insert_cols = [
                                    movement_batch_col,
                                    movement_employee_col,
                                    movement_type_col,
                                    movement_quantity_col
                                ]
                                insert_values = [
                                    selected_batch["batch_id"],
                                    selected_employee[employee_id_col],
                                    movement_type,
                                    int(movement_quantity)
                                ]

                                if movement_date_col:
                                    insert_cols.append(movement_date_col)
                                    insert_values.append(date.today())

                                if movement_notes_col:
                                    insert_cols.append(movement_notes_col)
                                    insert_values.append(notes)

                                col_sql = ", ".join(
                                    f"`{col}`" for col in insert_cols
                                )
                                placeholders = ", ".join(
                                    ["%s"] * len(insert_values)
                                )

                                cursor.execute(
                                    f"INSERT INTO stock_movement ({col_sql}) "
                                    f"VALUES ({placeholders})",
                                    tuple(insert_values)
                                )

                                connection.commit()
                                st.success("Stock movement recorded successfully.")
                                st.rerun()

                            except Exception as e:
                                if connection:
                                    connection.rollback()
                                st.error("Movement could not be recorded.")
                                st.code(str(e))
                            finally:
                                if connection and connection.is_connected():
                                    connection.close()

        st.subheader("Stock Movement History")
        history = load_data("SELECT * FROM stock_movement ORDER BY 1 DESC")
        st.dataframe(history, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error("Could not load stock movement information.")
        st.code(str(e))


# ---------------- SQL REPORTS ----------------

elif page == "SQL Reports":
    st.header("SQL reports")
    st.write("Run reports using SQL queries on the project database.")

    reports = {
        "Inventory at Risk": """
            SELECT b.batch_id, p.product_name, s.store_name,
                   b.quantity_available, b.expiry_date,
                   DATEDIFF(b.expiry_date, CURDATE()) AS days_to_expiry
            FROM inventory_batch b
            JOIN product p ON b.product_id = p.product_id
            JOIN store s ON b.store_id = s.store_id
            WHERE b.quantity_available > 0
              AND b.expiry_date <= DATE_ADD(CURDATE(), INTERVAL 7 DAY)
            ORDER BY b.expiry_date
        """,
        "Inventory Value by store": """
            SELECT s.store_name,
                   SUM(b.quantity_available * COALESCE(b.unit_cost, 0))
                       AS inventory_value
            FROM inventory_batch b
            JOIN product p ON b.product_id = p.product_id
            JOIN store s ON b.store_id = s.store_id
            GROUP BY s.store_id, s.store_name
            ORDER BY inventory_value DESC
        """,
        "Stock by product": """
            SELECT p.product_name,
                   SUM(b.quantity_available) AS total_quantity
            FROM product p
            LEFT JOIN inventory_batch b ON p.product_id = b.product_id
            GROUP BY p.product_id, p.product_name
            ORDER BY total_quantity DESC
        """,
        "supplier Summary": """
            SELECT * FROM supplier
        """,
        "Stock Movement Summary": """
            SELECT * FROM stock_movement
        """
    }

    selected_report = st.selectbox("Select a report", list(reports.keys()))

    if st.button("Run Report"):
        try:
            report_df = load_data(reports[selected_report])
            st.success(f"Report loaded: {len(report_df)} rows.")
            st.dataframe(report_df, use_container_width=True, hide_index=True)
            st.download_button(
                "⬇️ Download report as CSV",
                data=report_df.to_csv(index=False).encode("utf-8-sig"),
                file_name=selected_report.lower().replace(" ", "_") + ".csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error("This report could not be executed.")
            st.code(str(e))


# ---------------- ABOUT PROJECT ----------------

elif page == "About Project":
    st.header("About Expiry-to-Value")

    st.markdown("""
    ### Project Objective
    Expiry-to-Value helps stores manage perishable products and reduce waste
    by identifying stock that is close to expiry.

    ### Main Features
    - Inventory tracking by product, store and batch.
    - Expiry-risk classification.
    - Inventory value-at-risk estimation.
    - Recording sold, donated and discarded stock.
    - SQL-based reports for inventory and stock movement.

    ### Database
    The project uses MySQL and relational tables for stores, products,
    suppliers, employees, inventory batches, stock movements and discount campaigns.

    ### Technology Stack
    - Python
    - Streamlit
    - MySQL
    - Pandas
    - Plotly
    """)

st.divider()
st.caption("Expiry-to-Value | Smart Perishable Inventory and Value Recovery Management System")
