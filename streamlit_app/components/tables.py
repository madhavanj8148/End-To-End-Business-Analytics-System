"""
Interactive Table & CSV Download Component
"""

import streamlit as st
import pandas as pd

def render_interactive_table(df: pd.DataFrame, title: str, filename: str, key: str = None):
    """
    Renders a searchable dataframe with a CSV download button.
    """
    st.markdown(f"### 📋 {title}")

    # Search filter
    search_query = st.text_input("🔍 Search table", key=f"search_{key or title}")
    if search_query:
        mask = df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)
        filtered_df = df[mask]
    else:
        filtered_df = df

    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"📥 Download {title} (CSV)",
        data=csv_data,
        file_name=f"{filename}.csv",
        mime="text/csv",
        key=f"dl_{key or title}"
    )
