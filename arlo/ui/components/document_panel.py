import streamlit as st
from arlo.ui.client import ArloAPIClient

def render_document_panel(project_id: int):
    """
    Renders the document management panel inside the Project Detail screen.
    Allows listing, uploading, and deleting documents.
    """
    client = ArloAPIClient()
    st.markdown("### 📁 Project Knowledge Base")
    st.caption("Upload project requirement docs, spec sheets, reference notes, or meeting minutes to enrich Arlo's context.")

    # 1. Document Upload Form
    with st.expander("📤 Upload New Document", expanded=False):
        uploaded_file = st.file_uploader("Choose a file (PDF, TXT, MD, DOCX)", type=["pdf", "txt", "md", "docx"], key=f"uploader_{project_id}")
        doc_type = st.selectbox(
            "Document Type",
            options=["requirement", "meeting notes", "report", "reference"],
            key=f"doc_type_{project_id}"
        )
        
        if uploaded_file is not None:
            if st.button("Index Document", key=f"btn_upload_{project_id}", type="primary"):
                try:
                    file_content = uploaded_file.read()
                    with st.spinner("Parsing text and index chunk embeddings..."):
                        client.upload_document(
                            project_id=project_id,
                            doc_type=doc_type,
                            filename=uploaded_file.name,
                            file_content=file_content
                        )
                    st.success(f"Indexed {uploaded_file.name} successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Upload failed: {e}")

    st.divider()

    # 2. Document List
    try:
        docs = client.list_documents(project_id)
    except Exception as e:
        st.error(f"Failed to fetch documents: {e}")
        return

    if not docs:
        st.info("No documents uploaded to this project's Knowledge Base yet.")
        return

    st.markdown(f"**Indexed Documents ({len(docs)})**")
    for doc in docs:
        col1, col2, col3, col4 = st.columns([4, 2, 2, 1])
        with col1:
            st.markdown(f"📄 **{doc['filename']}**")
            st.caption(f"Type: {doc['doc_type'].title()} | Uploaded: {doc['uploaded_at'][:16]}")
        with col2:
            size_kb = doc['filesize_bytes'] / 1024
            st.metric("File Size", f"{size_kb:.1f} KB")
        with col3:
            st.metric("Vector Chunks", f"{doc['chunk_count']} chunks")
        with col4:
            st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
            if st.button("🗑️", key=f"del_doc_{doc['id']}", help="Delete from database and vector index"):
                try:
                    client.delete_document(project_id, doc["id"])
                    st.toast(f"Deleted {doc['filename']}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to delete document: {e}")
        st.divider()
