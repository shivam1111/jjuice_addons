#JJUICE
------

- Change Sales person of Multiple Customers by opening wizard from the More Menu in tree view of customers. 
- Hide Title in Customer and Partners

## Interface

> Interface for creating Sales Order from Customers Form

- Added Stock Check Availability Functionality
	* ISSUE SOLVED: The input fields remained red after repeated click on check availability button
- Marketing package functionality (Javascript)
- If it is a new record of parnter the interface will not be generated. (jjuice.js line no.935)
 	 

##Leads/Potential Customers 

> This is our own workflow for leads

- [x] A new Menu item Leads/Potential Customers is created (res_partner_view.xml)
- [x] A customer cannot be a partner and lead at the same time (res_partner.py) 
- [x] By default when creating a new lead the lead checkbox should be ticked (res_partner.py)	
- [x] Quotation button to view all the quotations created for the lead (res_partner_view.xml)
- [x] Added Smart Button 'Quotation'. It shows the quotations associated with the partner (res_partner.py,field="draft_order_count") 

