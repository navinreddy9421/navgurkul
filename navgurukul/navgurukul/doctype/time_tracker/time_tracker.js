frappe.ui.form.on("Time Tracker", {
    month: function(frm) {
        if (frm.doc.month) {
            populate_dates(frm);
        }
    },
    employee: function(frm) {
        if (frm.doc.employee) {
            fetch_holidays(frm);
        }
    }
});

function populate_dates(frm) {
    const selected_month = frm.doc.month;
    const year = frm.doc.year || new Date().getFullYear();

    if (!selected_month) {
        frappe.msgprint(__("Please select a valid month."));
        return;
    }

    const month_number = get_month_number(selected_month);
    if (month_number === -1) {
        frappe.msgprint(__("Invalid month selected."));
        return;
    }

    frm.clear_table("time_tracker_table");

    const start_date = new Date(year, month_number, 1);
    const end_date = new Date(year, month_number + 1, 0);

    for (let date = new Date(start_date); date <= end_date; date.setDate(date.getDate() + 1)) {
        let correct_date = new Date(date);
        correct_date.setHours(0, 0, 0, 0);

        let day_name = correct_date.toLocaleString('en-IN', { weekday: 'long' });

        let formatted_date = `${correct_date.getDate().toString().padStart(2, '0')}/${(correct_date.getMonth() + 1).toString().padStart(2, '0')}/${correct_date.getFullYear()}`;

        let child = frm.add_child("time_tracker_table");
        child.date = formatted_date;
        child.days = day_name;
    }

    frm.refresh_field("time_tracker_table");

    if (frm.doc.employee) {
        fetch_holidays(frm);
    }
}

function get_month_number(month_name) {
    const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    return months.indexOf(month_name);
}

function fetch_holidays(frm) {
    frappe.call({
        method: "frappe.client.get",
        args: {
            doctype: "Employee",
            name: frm.doc.employee
        },
        callback: function(response) {
            const employee = response.message;
            const holiday_list = employee.holiday_list;

            if (!holiday_list) {
                frappe.msgprint(__("The selected employee does not have a holiday list."));
                return;
            }

            frappe.call({
                method: "frappe.client.get",
                args: {
                    doctype: "Holiday List",
                    name: holiday_list
                },
                callback: function(response) {
                    if (response.message) {
                        const holiday_list_doc = response.message;
                        if (holiday_list_doc.holidays) {
                            const holidays = holiday_list_doc.holidays || [];
                            if (holidays.length > 0) {
                                assign_holidays_to_activity(frm, holidays);
                            } else {
                                frappe.msgprint(__("No holidays found in the selected holiday list."));
                            }
                        } else {
                            frappe.msgprint(__("No holidays field found in the holiday list."));
                        }
                    } else {
                        frappe.msgprint(__("Holiday List not found or is empty."));
                    }
                },
                error: function(error) {
                    frappe.msgprint(__("An error occurred while fetching the holiday list."));
                }
            });
        },
        error: function(error) {
            frappe.msgprint(__("An error occurred while fetching employee data."));
        }
    });
}

function assign_holidays_to_activity(frm, holidays) {
    frm.doc.time_tracker_table.forEach(row => {
        const date_str = row.date;
        const date_parts = date_str.split("/");
        const date_obj = new Date(date_parts[2], date_parts[1] - 1, date_parts[0]);

        const is_holiday = holidays.some(h => {
            const holiday_date_parts = h.holiday_date.split("-");
            const holiday_date_obj = new Date(holiday_date_parts[0], holiday_date_parts[1] - 1, holiday_date_parts[2]);
            return holiday_date_obj.getTime() === date_obj.getTime();
        });

        if (is_holiday) {
            row.activity = "Holiday";
        } else {
            row.activity = ""; 
        }
    });

    frm.refresh_field("time_tracker_table");
}




// -------------------------------------Explaination of the code line by line as per better understanding----------------------------------------------------------

// // Triggered when the 'month' field is changed in the 'Time Tracker' doctype
// frappe.ui.form.on("Time Tracker", {
//     month: function(frm) {
//         if (frm.doc.month) { // If a month is selected
//             populate_dates(frm); // Call the function to populate dates in the child table
//         }
//     },
//     employee: function(frm) {
//         if (frm.doc.employee) { // If an employee is selected
//             fetch_holidays(frm); // Call the function to fetch holidays associated with the employee
//         }
//     }
// });

// // Function to populate the child table 'time_tracker_table' with dates and days based on the selected month
// function populate_dates(frm) {
//     const selected_month = frm.doc.month; // Get the selected month
//     const year = frm.doc.year || new Date().getFullYear(); // Get the selected year, or use the current year if not provided

//     if (!selected_month) { // Check if the month is valid
//         frappe.msgprint(__("Please select a valid month.")); // Show an error message if not
//         return;
//     }

//     const month_number = get_month_number(selected_month); // Convert month name to a number
//     if (month_number === -1) { // If the month name is invalid
//         frappe.msgprint(__("Invalid month selected.")); // Show an error message
//         return;
//     }

//     frm.clear_table("time_tracker_table"); // Clear the child table before populating new data

//     const start_date = new Date(year, month_number, 1); // Get the first date of the selected month
//     const end_date = new Date(year, month_number + 1, 0); // Get the last date of the selected month

//     // Loop through each day of the month
//     for (let date = new Date(start_date); date <= end_date; date.setDate(date.getDate() + 1)) {
//         let correct_date = new Date(date); // Create a new date object for the current loop iteration
//         correct_date.setHours(0, 0, 0, 0); // Normalize the time to avoid time zone issues

//         let day_name = correct_date.toLocaleString('en-IN', { weekday: 'long' }); // Get the day name in 'en-IN' locale

//         let formatted_date = `${correct_date.getDate().toString().padStart(2, '0')}/${(correct_date.getMonth() + 1).toString().padStart(2, '0')}/${correct_date.getFullYear()}`; // Format the date as 'dd/mm/yyyy'

//         let child = frm.add_child("time_tracker_table"); // Add a new row to the child table
//         child.date = formatted_date; // Set the formatted date in the 'date' field
//         child.days = day_name; // Set the day name in the 'days' field
//     }

//     frm.refresh_field("time_tracker_table"); // Refresh the child table to show the new data

//     // If an employee is selected, fetch holidays and update the activities column
//     if (frm.doc.employee) {
//         fetch_holidays(frm); // Call the function to fetch holidays
//     }
// }

// // Helper function to convert a month name to its corresponding month number (0-11)
// function get_month_number(month_name) {
//     const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
//                     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]; // Array of month abbreviations
//     return months.indexOf(month_name); // Return the index of the month, or -1 if not found
// }

// // Function to fetch the holiday list associated with the selected employee
// function fetch_holidays(frm) {
//     frappe.call({
//         method: "frappe.client.get", // API call to get the Employee doctype
//         args: {
//             doctype: "Employee",
//             name: frm.doc.employee // Pass the selected employee's name
//         },
//         callback: function(response) {
//             const employee = response.message; // Get the employee data from the response
//             const holiday_list = employee.holiday_list; // Get the holiday list associated with the employee

//             if (!holiday_list) { // If no holiday list is assigned
//                 frappe.msgprint(__("The selected employee does not have a holiday list.")); // Show an error message
//                 return;
//             }

//             frappe.call({
//                 method: "frappe.client.get", // API call to get the Holiday List doctype
//                 args: {
//                     doctype: "Holiday List",
//                     name: holiday_list // Pass the holiday list name
//                 },
//                 callback: function(response) {
//                     if (response.message) {
//                         const holiday_list_doc = response.message; // Get the holiday list document
//                         if (holiday_list_doc.holidays) {
//                             const holidays = holiday_list_doc.holidays || []; // Get the holidays from the child table
//                             if (holidays.length > 0) {
//                                 assign_holidays_to_activity(frm, holidays); // Assign holidays to the activity column
//                             } else {
//                                 frappe.msgprint(__("No holidays found in the selected holiday list.")); // Show an error message if no holidays found
//                             }
//                         } else {
//                             frappe.msgprint(__("No holidays field found in the holiday list.")); // Show an error message if holidays field is missing
//                         }
//                     } else {
//                         frappe.msgprint(__("Holiday List not found or is empty.")); // Show an error message if holiday list is not found
//                     }
//                 },
//                 error: function(error) {
//                     frappe.msgprint(__("An error occurred while fetching the holiday list.")); // Show an error message if the API call fails
//                 }
//             });
//         },
//         error: function(error) {
//             frappe.msgprint(__("An error occurred while fetching employee data.")); // Show an error message if the API call fails
//         }
//     });
// }

// // Function to assign holidays to the 'activity' field in the 'time_tracker_table'
// function assign_holidays_to_activity(frm, holidays) {
//     frm.doc.time_tracker_table.forEach(row => { // Loop through each row in the child table
//         const date_str = row.date; // Get the date string from the row
//         const date_parts = date_str.split("/"); // Split the date string into day, month, and year
//         const date_obj = new Date(date_parts[2], date_parts[1] - 1, date_parts[0]); // Create a date object

//         // Check if the current date matches any holiday date
//         const is_holiday = holidays.some(h => {
//             const holiday_date_parts = h.holiday_date.split("-"); // Split the holiday date string into year, month, day
//             const holiday_date_obj = new Date(holiday_date_parts[0], holiday_date_parts[1] - 1, holiday_date_parts[2]); // Create a holiday date object
//             return holiday_date_obj.getTime() === date_obj.getTime(); // Compare the holiday date with the current date
//         });

//         if (is_holiday) {
//             row.activity = "Holiday"; // Set the activity to "Holiday" if it's a holiday
//         } else {
//             row.activity = ""; // Clear the activity if it's not a holiday
//         }
//     });

//     frm.refresh_field("time_tracker_table"); // Refresh the child table to show the updated activities
// }
