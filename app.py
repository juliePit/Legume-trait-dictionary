import streamlit as st
import pandas as pd

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Trait Dictionary", layout="wide")
st.title("🫛 Legume Trait Dictionary")

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("Classeur1.xlsx", sheet_name="Feuil1")
    return df

df = load_data()

# -----------------------------
# CLEAN COLUMN NAMES
# -----------------------------
df.columns = [c.strip() for c in df.columns]

# -----------------------------
# IDENTIFY SPECIES COLUMNS
# -----------------------------
species_cols = [
    "Lentil", "Pea", "Common bean", "Soybean",
    "Faba bean", "Lucerne", "Chickpea",
    "Sainfoin", "Red clover", "White clover", "Annual clover", "lupin", "Vetches", "Lotus"
]

grain_species = ["Lentil", "Pea", "Common bean", "Soybean", "Faba bean", "Chickpea", "lupin"]
forage_species = ["Lucerne", "Sainfoin", "Red clover", "White clover", "Annual clover", ]

# -----------------------------
# FILTERS
# -----------------------------
st.sidebar.header("Filters")

search = st.sidebar.text_input("Search trait")

category_filter = st.sidebar.selectbox(
    "Trait Class",
    ["All"] + sorted(df["Class"].dropna().unique().tolist())
)

biology_filter = st.sidebar.selectbox(
"Trait Category",
["All"] + sorted(df["Biology Sub-classs"].dropna().unique().tolist())
)

species_filter = st.sidebar.selectbox(
    "Species",
    ["All"] + species_cols
)


# -----------------------------
# APPLY FILTERS
# -----------------------------
filtered_df = df.copy()

# Search filter
if search:
    filtered_df = filtered_df[
        filtered_df["Trait name"].str.contains(search, case=False, na=False)
    ]

# Category filter
if category_filter != "All":
    filtered_df = filtered_df[
        filtered_df["Class"] == category_filter
    ]
# Biology subclass filter
if biology_filter != "All":
    filtered_df = filtered_df[
        filtered_df["Biology Sub-classs"] == biology_filter
    ]
# ✅ NEW: Species filter
if species_filter != "All":
    filtered_df = filtered_df[
        filtered_df[species_filter].notna()
    ]

# -----------------------------
# GROUP BY TRAIT
# -----------------------------

grouped = filtered_df.groupby("Trait name")





# -----------------------------
# DISPLAY
# -----------------------------
for trait, group in grouped:

    st.markdown("---")

    # -------------------------
    # HEADER
    # -------------------------
    col1, col2 = st.columns([3, 1])

    trait_class = group["Class"].iloc[0]

    # -------------------------
    # TRAIT ABBREVIATION
    # -------------------------
    abbr_series = group["Trait abbr."].dropna()
    abbr = abbr_series.iloc[0] if not abbr_series.empty else ""

    # -------------------------
    # HEADER WITH ABBR
    # -------------------------
    with col1:
        if abbr:
            st.header(f"{trait} ({abbr})")
        else:
            st.header(trait)

    with col2:
        st.write(f"**{trait_class}**")

    # -------------------------
    # TRAIT DESCRIPTION
    # -------------------------
    desc_series = group["Trait description"].dropna()
    description = desc_series.iloc[0] if not desc_series.empty else ""

    if description:
        st.markdown(f"*{description}*")
    else:
        st.caption("No description available")

    # -------------------------
    # SPECIES
    # -------------------------
    species_present = [
        col for col in species_cols
        if col in group.columns and group[col].notna().any()
    ]

    grain_present = [s for s in species_present if s in grain_species]
    forage_present = [s for s in species_present if s in forage_species]

    st.subheader("Species")

    if grain_present:
        st.success("Grain: " + ", ".join(grain_present))
    if forage_present:
        st.info("Forage: " + ", ".join(forage_present))

    # -------------------------
    # METHODS
    # -------------------------
    st.subheader("Methods")
    
    method_groups = group.groupby("Method name")
    
    for method, mgroup in method_groups:
    
        with st.expander(f"📘 {method}"):
    
            # Method description
            m_desc_series = mgroup["Method description"].dropna()
            m_description = (
                m_desc_series.iloc[0]
                if not m_desc_series.empty
                else "No description available."
            )
    
            st.write("**Description**")
            st.write(m_description)
    
            # ---------------------
            # SCALES
            # ---------------------
            scales = mgroup["Scale name"].dropna().unique()
    
            if len(scales) > 0:
                st.write("**Available scales:**")
                for s in scales:
                    st.write(f"- {s}")
            else:
                st.write("No scale specified")
    
            # ---------------------
            # SCALE DETAILS
            # ---------------------
            scale_class = mgroup["scale class"].dropna()
    
            if (
                not scale_class.empty
                and scale_class.iloc[0] in ["Ordinal", "Nominal"]
            ):
    
                scale_rows = []
    
                row = mgroup.iloc[0]
    
                for i in range(1, 10):
    
                    code_col = f"Level {i} code"
                    label_col = f"Level {i} label"
    
                    if (
                        pd.notna(row.get(code_col))
                        and pd.notna(row.get(label_col))
                    ):
                        scale_rows.append(
                            {
                                "Code": row[code_col],
                                "Meaning": row[label_col],
                            }
                        )
    
                if scale_rows:
                    st.write("**Scale details**")
                    st.dataframe(
                        pd.DataFrame(scale_rows),
                        hide_index=True,
                        use_container_width=True,
                    )
    
            # ---------------------
            # VARIABLES
            # ---------------------
            var_names = mgroup["Var_name"].dropna().unique()
    
            if len(var_names) > 0:
                with st.expander("Show variable names"):
                    for v in var_names:
                        st.write(f"- {v}")
