import streamlit as st
import requests

CORRECTION_SERVICE_URL = "http://127.0.0.1:8002/corrections"

st.sidebar.title("Admin Settings")
admin_key = st.sidebar.text_input("Admin API Key", type="password", value="test-key-123")

headers = {
    "X-Correction-Service-Admin-Key": admin_key
}

st.title("Admin Review: Emergency Correction Queue")

# Fetch pending reports
try:
    response = requests.get(f"{CORRECTION_SERVICE_URL}/pending", headers=headers)
    response.raise_for_status()
    pending = response.json().get("pending_reports", [])
except Exception as e:
    st.error(f"Failed to connect to correction-service: {e}")
    pending = []

if not pending:
    st.success("No pending correction reports!")
else:
    st.write(f"Found {len(pending)} pending reports.")
    for report in pending:
        with st.expander(f"Report ID: {report['id']} - From: {report['reported_by']}"):
            st.write("**Reported Issue:**")
            st.info(report['reported_issue_text'])
            st.write(f"**Submitted At:** {report['created_at']}")
            
            with st.form(key=f"review_form_{report['id']}"):
                notes = st.text_area("Reviewer Notes", key=f"notes_{report['id']}")
                override_text = st.text_area("Approved Correction Text (Required if approving)", key=f"override_{report['id']}")
                
                col1, col2 = st.columns(2)
                approve_btn = col1.form_submit_button("Approve")
                reject_btn = col2.form_submit_button("Reject")
                
                if approve_btn:
                    if not override_text:
                        st.error("Correction Text is required to approve.")
                    else:
                        resp = requests.post(
                            f"{CORRECTION_SERVICE_URL}/review/{report['id']}", 
                            headers=headers,
                            json={
                                "status": "approved",
                                "reviewer_notes": notes,
                                "approved_correction_text": override_text
                            }
                        )
                        if resp.status_code == 200:
                            st.success("Approved successfully! Reload page to update.")
                        else:
                            st.error(f"Error: {resp.text}")
                            
                if reject_btn:
                    if not notes:
                        st.error("Notes (reason) are required to reject.")
                    else:
                        resp = requests.post(
                            f"{CORRECTION_SERVICE_URL}/review/{report['id']}", 
                            headers=headers,
                            json={
                                "status": "rejected",
                                "reviewer_notes": notes
                            }
                        )
                        if resp.status_code == 200:
                            st.success("Rejected successfully! Reload page to update.")
                        else:
                            st.error(f"Error: {resp.text}")
