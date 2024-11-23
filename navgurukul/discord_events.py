import frappe
import requests
from frappe.utils import nowdate
from datetime import datetime

def send_daily_logs_to_discord():
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
    
    # Fetch daily logs from Time Tracker
    logs = frappe.db.sql("""
        SELECT
            tt.employee_name,
            tt.report_manager,
            ttt.activity,
            ttt.hours,
            e.custom_campus
        FROM
            `tabTime Tracker` tt
        INNER JOIN
            `tabTime Tracker Table` ttt
        ON
            tt.name = ttt.parent
        INNER JOIN
            `tabEmployee` e
        ON
            tt.employee = e.name
        WHERE
            STR_TO_DATE(ttt.date, '%%d/%%m/%%Y') = STR_TO_DATE(%s, '%%d/%%m/%%Y')
            AND ttt.activity IS NOT NULL
            AND ttt.activity != ''
            AND ttt.hours IS NOT NULL
    """, (today_date,), as_dict=True)
    
    if not logs:
        frappe.log_error("No daily logs found for today's date.", "Daily Logs to Discord")
        return
    
    # Group logs by campus and manager
    campus_logs = {}
    for log in logs:
        campus = log.get('custom_campus')
        manager = log.get('report_manager')
        
        # Get the employee ID from Employee based on the report_manager's full name
        manager_id = frappe.db.get_value("Employee", {"employee_name": manager}, "name")

        # Now fetch the discord_id using the retrieved ID
        discord_id = frappe.db.get_value("Employee", {"name": manager_id}, "custom_discord_id")
        # print(discord_id, "discord_id")
        if not discord_id:
            frappe.log_error(f"Discord ID not found for manager: {manager}", "Missing Discord ID")
            continue
        
        if campus not in campus_channel_map:
            frappe.log_error(f"Campus '{campus}' does not have a mapped Discord channel.", "Unmapped Campus")
            continue
        
        if campus not in campus_logs:
            campus_logs[campus] = {}
        
        if discord_id not in campus_logs[campus]:
            campus_logs[campus][discord_id] = []
        
        campus_logs[campus][discord_id].append(
            f"- **{log['employee_name']}** :\n"
            + "".join(f"   - {line}\n" for line in log['activity'].splitlines())  # Nested bullet points
            + f"spent {log['hours']} hours on it."
        )
    
    # Send daily logs to respective Discord channels
    for campus, manager_logs in campus_logs.items():
        webhook_url = campus_channel_map.get(campus)
        if not webhook_url:
            frappe.log_error(f"Webhook URL not found for campus: {campus}", "Missing Webhook URL")
            continue
        
        messages = []
        for discord_id, logs in manager_logs.items():
            message = (
                "\n".join(logs)
                + f"\nCc: <@{discord_id}>"
                + "\n"
            )
            messages.append(message)
        
        # Combine all messages for the campus
        full_message = "\n".join(messages)
        payload = {"content": full_message}
        
        try:
            # Send POST request to Discord
            response = requests.post(webhook_url, json=payload)
            if response.status_code != 204:  # Discord webhook returns 204 No Content on success
                frappe.log_error(f"Failed to send message to Discord for campus {campus}. Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            frappe.log_error(f"Error sending message to Discord for campus {campus}: {e}", "Error in Discord Posting")
