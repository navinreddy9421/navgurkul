# # Copyright (c) 2024, Navgurukul and contributors
# # For license information, please see license.txt

import frappe

from datetime import datetime,timedelta
import calendar
from frappe.model.document import Document


class TimeTracker(Document):


	def on_submit(doc):
		try:
			current_year = datetime.now().year

			month_map = {
				'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4,
				'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8,
				'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
			}

			selected_month_name = doc.month
			selected_month = month_map.get(selected_month_name)

			if not selected_month:
				frappe.throw(f"Invalid month selected: {selected_month_name}")

			employee = frappe.get_doc("Employee", doc.employee)
			holiday_list = frappe.get_doc("Holiday List", employee.holiday_list)

			# Fetch holiday dates
			holiday_dates = {
				datetime.strptime(str(holiday.holiday_date), '%Y-%m-%d').date() 
				for holiday in holiday_list.holidays
			}

			# Process time tracker table
			for entry in doc.time_tracker_table:
				entry_date = datetime.strptime(entry.date, '%d/%m/%Y').date()

				if entry.hours is None:
					# set these as per adjustment
					entry.hours = 0 
					# frappe.throw(f"Hours not entered for date: {entry.date}")

				if entry.hours > 12:
					frappe.throw("You have entered more than 12 hours of working for a day!")

				if entry.hours > 4:
					new_doc = frappe.new_doc("Attendance")
					new_doc.update({
						"employee": doc.employee,
						"status": "Present",
						"attendance_date": entry_date.strftime('%Y-%m-%d'),
						"docstatus": 1,
					})
					new_doc.insert()

				elif entry.hours > 0:
					new_doc = frappe.new_doc("Attendance")
					new_doc.update({
						"employee": doc.employee,
						"status": "Half Day",
						"attendance_date": entry_date.strftime('%Y-%m-%d'),
						"docstatus": 1,
					})
					new_doc.insert()

					# Only create Leave Without Pay if the entry date is not a holiday
					if entry_date not in holiday_dates:
						existing_lwp = frappe.get_all("Leave Application",
							filters={
								"employee": doc.employee,
								"leave_type": "Leave Without Pay",
								"from_date": entry_date,
								"to_date": entry_date,
								"status": "Approved",
							}
						)

						if not existing_lwp:
							new_lwp = frappe.new_doc("Leave Application")
							new_lwp.update({
								"employee": doc.employee,
								"leave_type": "Leave Without Pay",
								"from_date": entry_date,
								"to_date": entry_date,
								"half_day": 1,
								"leave_approver": employee.leave_approver,
								"status": "Approved",
								"docstatus": 1
							})
							new_lwp.insert()

			num_days = calendar.monthrange(current_year, selected_month)[1]

			all_dates = {datetime(current_year, selected_month, day).strftime('%Y-%m-%d') for day in range(1, num_days + 1)}

			entered_dates = {datetime.strptime(entry.date, '%d/%m/%Y').strftime('%Y-%m-%d') for entry in doc.time_tracker_table}

			missing_dates = all_dates - entered_dates

			# Exclude holidays from missing dates before marking as absent
			missing_dates = missing_dates - {holiday.strftime('%Y-%m-%d') for holiday in holiday_dates}

			if missing_dates :
				for missing_date in missing_dates:
					new_doc = frappe.new_doc("Attendance")
					new_doc.update({
						"employee": doc.employee,
						"status": "Absent",
						"attendance_date": missing_date,
						"docstatus": 1,
					})
					new_doc.insert()

			frappe.db.commit()

		except Exception as e:
			frappe.throw(f"An error occurred: {str(e)}")
