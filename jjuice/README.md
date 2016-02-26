#JJUICE
------

- Change Sales person of Multiple Customers by opening wizard from the More Menu in tree view of customers. 
- Hide Title in Customer and Partners

## Sale

- [x] When "Confirm Sale" is clicked the related partner turns into lead if it is a lead (sale_order.py function action_wait())

## Interface

> Interface for creating Sales Order from Customers Form

- Added Stock Check Availability Functionality
	* ISSUE SOLVED: The input fields remained red after repeated click on check availability button
- Marketing package functionality (Javascript)
- If it is a new record of parnter the interface will not be generated. (jjuice.js line no.935)
 	 

##Partner

- Added fields (fields.py)
	1. Skype Id
	2. Type Of Account
	3. Account Classification(For Finance)

##Leads/Potential Customers 

> This is our own workflow for leads

- [x] A new Menu item Leads/Potential Customers is created (res_partner_view.xml)
- [x] A customer cannot be a partner and lead at the same time (res_partner.py) 
- [x] By default when creating a new lead the lead checkbox should be ticked (res_partner.py)	
- [x] Quotation button to view all the quotations created for the lead (res_partner_view.xml)
- [x] Added Smart Button 'Quotation'. It shows the quotations associated with the partner (res_partner.py,field:"draft_order_count") 
- [x] Add the customized filter (jjuice.js search_customer())

## Reporting

- [x] Treasury Analysis report can be filtered based on "Type of Account" field in Partners(model:res.partner, report/account_treasury_report.py) 
- [x] Reports Sale Analysis , Treasury Analysis -> Add Filter options with field "Type of Account" and Account Classification (for Finance) in Partner(model:res.partner) 
	 
