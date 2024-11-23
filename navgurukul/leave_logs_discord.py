import frappe
import requests
from frappe.utils import nowdate
from datetime import datetime

def send_leave_logs_to_discord():
    # Campus-to-Discord channel mapping
    campus_channel_map = {
        "Jashpur": "https://discord.com/api/webhooks/1308019257589891094/WRXKqZ9I7_W6rrjy-mURqHjn7PFS_dUi069Xr_C8dmE7nFEyAvcVaI5Ua3A58jTXyP4T",
        "Pune": "https://discord.com/api/webhooks/1308019257589891094/WRXKqZ9I7_W6rrjy-mURqHjn7PFS_dUi069Xr_C8dmE7nFEyAvcVaI5Ua3A58jTXyP4T",
        "Kishanganj": "https://discord.com/api/webhooks/1308018388466929774/utGga8WoFiz2BARH8_heEjFjVCW93s0dse2j1SGjd8eIHdE-XPEHFcOF-7TPMz1UR6kG",
        "Banglore":"https://discord.com/api/webhooks/1308018012141649961/h-eqwot-nf-XRxlX-KWaFdsG_9jX-hNXkf5rCE7x6hhvC4EMGvMCcjxGPfwQLpxDhVZ0",
        "Sarjapur":"https://discord.com/api/webhooks/1308016767372754956/yc9bFZulhChX61W2qegvtEZz_L4nQfLKAIyevRN0amACdsEALEW7u9BbYj6sLTCUkfSM",
        "Raipur":"https://discord.com/api/webhooks/1289606437902745683/03I1Y0k2osf6BMQZUKXj0b1zU2WyjKwU6677vYcoMa9FzUFjXCehI0Mn9H8EQNOxJruG",
        "Dantewada":"https://discord.com/api/webhooks/1308018875463630889/ZJlXwR6xZ4Dyq4L3b-PhAup0jiKvx_dAFu3a4PbNZah2tPMhO3IvAklDGLxkXEOSyVD8",
        "Udaipur":"https://discord.com/api/webhooks/1308019551820058624/_pO3loqreU75a929A1ti7n_kwpGoEjeshfXKTY7y-Wgc5VrJrhV0pUCK_RaQ43FZTpHv",
        "Dharamshala":"https://discord.com/api/webhooks/1308019712294129756/LrwwG_8RUf16t7aYimjgwhEeaQQRLCaFSE4DgZFLgmD4bVAEdRJw21kBL0kqP3CwF-BZ",
        "Himachal Campus":"https://discord.com/api/webhooks/1308019945585770497/Gidtn7QFXWWUlPteBaF7eL1WwX-8YZBm2OI2hBPwl_Ka7CwRyqQzM2L7NnN5rq_d0KMF",
    }
    
    # Get today's date in DD/MM/YYYY format
    today_date = datetime.strptime(nowdate(), '%Y-%m-%d').strftime('%d/%m/%Y')
    
    # Fetch leave data from Leave Application
    leaves = frappe.db.sql("""
        SELECT
            la.employee_name,
            la.leave_type,
            la.from_date,
            la.to_date,
            la.total_leave_days,
            la.half_day,
            la.description,
            e.custom_campus
        FROM
            `tabLeave Application` la
        INNER JOIN
            `tabEmployee` e
        ON
            la.employee = e.name
        WHERE
            STR_TO_DATE(la.posting_date, '%%Y-%%m-%%d') = STR_TO_DATE(%s, '%%Y-%%m-%%d')
    """, (nowdate(),), as_dict=True)
    
    if not leaves:
        frappe.log_error("No leave records found for today's date.", "Daily Leave Logs to Discord")
        return
    
    # Group leave data by campus
    campus_leaves = {}
    for leave in leaves:
        campus = leave.get('custom_campus')
        if campus not in campus_channel_map:
            frappe.log_error(f"Campus '{campus}' does not have a mapped Discord channel.", "Unmapped Campus")
            continue
        
        if campus not in campus_leaves:
            campus_leaves[campus] = []
        
        # Construct the message based on half-day or full-day leave
        if leave.get('half_day'):
            message = (
                f"**{leave['employee_name']}** is on **Half Day Leave** on {leave['from_date']}.\n"
                f"**Reason:** {leave['description'] or 'No reason provided'}"
            )
        else:
            message = (
                f"**{leave['employee_name']}** is on leave from {leave['from_date']} to {leave['to_date']}.\n"
                f"**Reason:** {leave['description'] or 'No reason provided'}"
            )
        
        campus_leaves[campus].append(message)
    
    # Send leave data to respective Discord channels
    for campus, messages in campus_leaves.items():
        webhook_url = campus_channel_map.get(campus)
        if not webhook_url:
            frappe.log_error(f"Webhook URL not found for campus: {campus}", "Missing Webhook URL")
            continue
        
        # Combine all messages for the campus
        message = "\n\n".join(messages)
        payload = {"content": message}
        
        try:
            # Send POST request to Discord
            response = requests.post(webhook_url, json=payload)
            if response.status_code != 204:  # Discord webhook returns 204 No Content on success
                frappe.log_error(f"Failed to send message to Discord for campus {campus}. Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            frappe.log_error(f"Error sending message to Discord for campus {campus}: {e}", "Error in Discord Posting")
