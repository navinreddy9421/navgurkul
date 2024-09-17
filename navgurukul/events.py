
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


import frappe
from frappe.utils.pdf import get_pdf
from frappe.core.doctype.communication.email import make
from datetime import datetime
@frappe.whitelist(allow_guest=True)
def send_salary_slip(doc,method):
   
	salary_slip = frappe.get_doc("Salary Slip",doc.name)
	current_date =salary_slip.start_date
	# current_date = datetime.now()
	formatted_date = current_date.strftime('%B %Y')
	
	employee = frappe.get_doc("Employee", salary_slip.employee)
   
   
	if not employee.user_id:
		frappe.throw("Employee does not have an email address (user_id) associated.")
	
	pdf_data = frappe.attach_print('Salary Slip', salary_slip.name, print_format="Salary Slip", doc=salary_slip)
	subject = f"Salary Slip for {employee.employee_name} - "
	message = f"Dear {employee.employee_name},<br><br>Please find attached your Salary Slip for {formatted_date}<br><br>Best regards,<br>NavGurukul"
   
	attachments = [pdf_data]
	
	frappe.sendmail(
		recipients=[employee.user_id],
		subject=subject,
		message=message,
		attachments=attachments,
		now=True
	)

	frappe.msgprint(f"Salary slip sent to {employee.user_id} successfully.")


import frappe
from frappe.utils import getdate
from datetime import datetime

@frappe.whitelist()
def leave_policy_assignment(doc,method):
	try:
		current_year = datetime.now().year
		name = doc if isinstance(doc, str) else doc.name
		policy_assignment = frappe.get_doc("Leave Policy Assignment", name)
		employee = frappe.get_doc("Employee", policy_assignment.employee)
		leave_policy_details = frappe.get_doc("Leave Policy", policy_assignment.leave_policy)
		
		start_date = getdate(policy_assignment.effective_from)
		end_date = getdate(policy_assignment.effective_to)
		day_of_month = start_date.day
		joining_month = start_date.month
		remaining_months = 12 - joining_month + 1
				
		def calculate_leaves(leave_type, allocation, divisor):
			new_leaves_allocated = (divisor / 12) * remaining_months
			decimal_part = new_leaves_allocated - int(new_leaves_allocated)

			# Keep the decimal part as is if it's exactly 0.5
			if decimal_part == 0.5:
				rounded_value = new_leaves_allocated
			else:
				rounded_value = round(new_leaves_allocated)

			# Use the rounded value for further operations
			if rounded_value > leave_type.max_leaves_allowed:
				frappe.log_error(
					f"Attempted to allocate {rounded_value} leaves, which exceeds the maximum allowed {leave_type.max_leaves_allowed} for {leave_type.name} for employee {employee.name}",
					"Leave Allocation Error"
				)
				return

			# Existing leave allocation check
			existing_allocation = frappe.db.exists("Leave Allocation", {
				"employee": employee.name,
				"leave_type": leave_type.name,
				"from_date": ("<=", start_date),
				"to_date": (">=", end_date),
				"leave_policy_assignment": policy_assignment.name
			})
			
			if existing_allocation:
				existing_doc = frappe.get_doc("Leave Allocation", existing_allocation)
				
				if existing_doc.docstatus == 1:
					existing_doc.cancel()
				
				frappe.delete_doc("Leave Allocation", existing_allocation)
				frappe.db.commit()

			leave_allocation = frappe.new_doc("Leave Allocation")
			leave_allocation.update({
				"employee": employee.name,
				"leave_type": leave_type.name,
				"from_date": start_date,
				"to_date": end_date,
				"leave_policy_assignment": policy_assignment.name,
				"new_leaves_allocated": rounded_value,  # Use rounded_value here
				"docstatus": 1  # Submitting the document
			})
			leave_allocation.insert()
			leave_allocation.submit()

		for data in leave_policy_details.leave_policy_details:
			leave_type = frappe.get_doc("Leave Type", data.leave_type)
			allocation = data.annual_allocation
			print(day_of_month)
			
			divisor = allocation
			calculate_leaves(leave_type, allocation, divisor)
		frappe.db.commit()

	except frappe.exceptions.ValidationError as e:
		frappe.log_error(f"Validation Error: {str(e)}", "Leave Allocation Error")
		raise
	except Exception as e:
		frappe.log_error(f"Unexpected Error: {str(e)}", "Leave Allocation Error")
		raise

