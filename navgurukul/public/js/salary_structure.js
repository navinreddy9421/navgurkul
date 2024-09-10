frappe.ui.form.on("Salary Structure Assignment", {
    employee: function(frm) {
        
        if (frm.doc.employee) {
           
            frappe.db.get_value('Employee', frm.doc.employee, 'ctc', (r) => {
                if (r && r.ctc) {
                  
                    var ctc_value = r.ctc;

                    
                    var amount_to_subtract = 21600;

                    
                    var remaining_value = ctc_value - amount_to_subtract;

                
                    if (remaining_value > 0) {
                      
                        var base_value = remaining_value / 12;

                        frm.set_value('base', base_value);
                    } else {
                        frappe.msgprint("CTC amount is too low to subtract ₹21,600.");
                        frm.set_value('base', 0);
                    }
                } else {
                    frappe.msgprint("Could not fetch CTC value from the Employee record.");
                }
            });
        }
    }
});
