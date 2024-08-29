
import frappe
from frappe.utils import getdate, today

def age_increase():
    current_date = getdate(today())
    current_year = current_date.year
    current_month = current_date.month
    current_day = current_date.day

    # Fetch employees whose date of birth is set
    employees = frappe.get_all(
        "Employee", 
        filters={"date_of_birth": ["is", "set"]}, 
        fields=['name', 'employee_name', 'date_of_birth']
    )

    for employee in employees:
        dob = getdate(employee['date_of_birth'])

        # Check if today is the employee's birthday
        if dob.month == current_month and dob.day == current_day:
            age = current_year - dob.year
            
            # Update the custom age field for the employee
            frappe.db.set_value("Employee", employee['name'], {"custom_age": age})
    
    # Commit the changes to the database
    frappe.db.commit()

def exprencess_incress():
    current_date = getdate(today())
    current_year = current_date.year
    current_month = current_date.month
    current_day = current_date.day
    
    employees = frappe.get_all(
        "Employee", 
        filters={"date_of_joining": ["is", "set"]}, 
        fields=['name', 'date_of_joining']
    )
    
    for employee in employees:
        date_of_joining = getdate(employee['date_of_joining'])
        if date_of_joining.month == current_month and date_of_joining.day == current_day:
            exprenc = current_year - date_of_joining.year
            frappe.db.set_value("Employee", employee['name'], {"custom_current_experience_": exprenc})
    
    frappe.db.commit()



def leaveapplication(doc, method):
    
    if doc.status =="Rejected":
        frappe.msgprint(f"🚨 Heyy 👩🏻‍💻!! Leave Application is Rejected for {doc.employee_name}!! 📣")
    else:
        frappe.msgprint(f"🚨Heyy 👩🏻‍💻!! Leave Application is Raised for {doc.employee_name}!! 📣!")


def onsubmit(doc, method):
    frappe.msgprint(f"🚨Heyy 👩🏻‍💻!! Leave Application is {doc.status} for {doc.employee_name}!! 📣")


def attendancerequest(doc,method):
    if doc.workflow_state =="Pending":
        frappe.msgprint(f"🚨 Heyy 👩🏻‍💻!! The Attedance Request is Raised for {doc.employee_name}!! 📣")
    if doc.workflow_state == "Rejected":
        frappe.msgprint(f"🚨 Heyy 👩🏻‍💻!! The Attedance Request is Rejected for {doc.employee_name}!! 📣")




def attendancework(doc,method):

    if doc.workflow_state == "Approved":
        frappe.msgprint(f"🚨 Heyy 👩🏻‍💻!! The Attedance Request is Approved for {doc.employee_name}!! 📣")

def compoff(doc,method):
    if doc.workflow_state =="Pending":
        frappe.msgprint(f"🚨 Heyy 👩🏻‍💻!! The CompOff Leave Request is Raised for {doc.employee_name}!! 📣")
    if doc.workflow_state == "Rejected":
        frappe.msgprint(f"🚨 Heyy 👩🏻‍💻!! The CompOff Leave Request is Rejected for {doc.employee_name}!! 📣")




def compoffsub(doc,method):

    if doc.workflow_state == "Approved":
        frappe.msgprint(f"🚨 Heyy 👩🏻‍💻!! The CompOff Leave Request is Approved for {doc.employee_name}!! 📣")


def timetracker(doc,method):

    if doc.workflow_state == "Approved":
        frappe.msgprint(f"🚨 Heyy  👩🏻‍💻!! The Time Tracker is Approved For {doc.employee_name}!! 📣")        