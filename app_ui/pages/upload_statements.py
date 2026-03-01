import os

import streamlit as st

from app_ui.data import AppData
from scripts.PDF_Stuff import FNBReadPDF, DiscoveryReadPDF
from scripts.ofx_reader import read_ofx_to_df
from scripts.db_manager import file_already_parsed, get_file_transactions, write_transactions
from scripts.bank_detector import detect_bank


def render(_: AppData) -> None:
    st.title("📄 Upload Bank Statements")

    st.info("Upload FNB, OFX or Discovery Bank statement PDFs to extract and categorize transactions.")

    uploaded_files = st.file_uploader("Choose files", type=["pdf", "ofx"], accept_multiple_files=True)

    if not uploaded_files:
        st.write("👆 Upload one or more PDF files to get started")
        return

    st.success(f"✅ {len(uploaded_files)} file(s) uploaded")

    for uploaded_file in uploaded_files:
        with st.expander(f"📄 {uploaded_file.name}"):
            st.write(f"**File size:** {uploaded_file.size / 1024:.2f} KB")

            temp_path = f"temp_{uploaded_file.name}"
            with open(temp_path, "wb") as file_handle:
                file_handle.write(uploaded_file.getbuffer())

            # allow user to override detection if needed
            bank_choice = st.selectbox("Bank (auto-detect)", options=["Auto", "FNB", "Discovery Bank", "unknown"], index=0)

            try:
                # Check if file already parsed and cached in DB
                if file_already_parsed(uploaded_file.name):
                    cached_txns = get_file_transactions(uploaded_file.name)
                    if cached_txns:
                        extracted_df = None
                        try:
                            import pandas as _pd

                            extracted_df = _pd.DataFrame(cached_txns, columns=["Year", "Month", "Date", "Type", "Details", "Amount"])  # type: ignore
                            st.info("📦 Loaded from database (previously parsed)")
                        except Exception as e:
                            st.warning(f"Could not load cached data: {e}")
                            extracted_df = None
                    else:
                        extracted_df = None
                else:
                    extracted_df = None
                
                # If no cached version, parse the file
                if extracted_df is None:
                    # OFX files
                    if uploaded_file.name.lower().endswith(".ofx"):
                        extracted_df = read_ofx_to_df(temp_path)
                        bank_id = "ofx"
                    else:
                        # PDF processing with bank detection and optional override
                        if bank_choice != "Auto":
                            bank_id = bank_choice
                        else:
                            bank_id = detect_bank(temp_path)

                        st.info(f"🏦 Bank detected: {bank_id}")

                        extracted_df = None
                        if bank_id == "FNB":
                            reader = FNBReadPDF(uploaded_file.name, temp_path)
                        elif bank_id == "Discovery Bank":
                            reader = DiscoveryReadPDF(uploaded_file.name, temp_path)
                        else:
                            # unknown: try discovery first, then fnb as fallback
                            extracted_df = None
                            try:
                                reader = DiscoveryReadPDF(uploaded_file.name, temp_path)
                            except Exception:
                                reader = None

                            if reader is None:
                                try:
                                    reader = FNBReadPDF(uploaded_file.name, temp_path)
                                except Exception:
                                    reader = None

                        if reader is None:
                            st.warning("Could not parse PDF with known readers. No transactions extracted.")
                            extracted_df = None
                        else:
                            extracted_df = reader.clean_data_to_df()
                    
                    # Store parsed transactions in DB for future requests
                    if extracted_df is not None and not extracted_df.empty:
                        try:
                            success = write_transactions(
                                transactions=extracted_df.values.tolist(),
                                filename=uploaded_file.name,
                                bank=bank_id,
                            )
                            if success:
                                st.success("💾 Transactions saved to database")
                        except Exception as e:
                            st.warning(f"Could not save to DB: {e}")

                if extracted_df is not None and not extracted_df.empty:
                    st.success(f"✅ Extracted {len(extracted_df)} transactions")
                    st.dataframe(extracted_df.head(20), use_container_width=True)

                    if st.button("Add to dataset", key=f"add_{uploaded_file.name}"):
                        st.success("Transactions added successfully!")
                else:
                    st.error("Failed to extract transactions from file")

            except Exception as error:
                st.error(f"Error processing file: {str(error)}")
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
