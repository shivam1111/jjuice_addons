openerp.jjuice.pos = function (instance,local) {
	
	var _t = instance.web._t,
    _lt = instance.web._lt;
	var QWeb = instance.web.qweb;
	instance.web.jjuice = instance.web.jjuice || {}	
	
	/*
	 * Data to be loaded once
	 * ----------------------
	 * The tabs info
	 */

	Array.prototype.last = function(){
		if (this.length > 0){
			return this.length - 1;
		}else{
			return 0
		}
	}
	
	main_def = $.Deferred();
	$(document).ready(function(){
    	var mod = new instance.web.Model("product.tab", {}, []); // MODEL,CONTEXT,DOMAIN
    	mod.call("fetch_static_data",[]).done(function(res){ //search_read method will automatically not load active = False records
    		main_def.resolve(res)
    	})//end call
	})
	
	function sortProperties(obj)
	{
	  // convert object into array
	    var sortable=[];
	    for(var key in obj)
	        if(obj.hasOwnProperty(key))
	            sortable.push([key, obj[key]]); // each item is an array in format [key, value]
	    
	    // sort items by value
	    sortable.sort(function(a, b)
	    {
	    	return a[1].localeCompare(b[1]); // compare numbers
	    });
	    return sortable; // array in format [ [ key1, val1 ], [ key2, val2 ], ... ]
	}	
	
	remove_spaces = function(string){
		return string.replace(/\s/g, "");
	}
	
	local.product_lists = instance.Widget.extend({
		init:function(tab_parent,tab_data){
			this.tab_parent = tab_parent;
			this.data = tab_data;
			this.dfm = new instance.web.form.DefaultFieldManager(self);
			// List of objects with key as product id
			this.qty = {};
			this.price = {};
			this.subtotal = {};
		},
		
		get_width:function(){
			return this.data.input_width
		},
		
		get_price:function(product){
			return product.lst_price;
		},
		calculate_subtotal_money:function(product_id,qty){
			var self = this;
			old = self.subtotal[product_id].get_value() || 0 
			price = parseFloat(self.price[product_id].get_value() || 0);
			total = price * qty;
			self.subtotal[product_id].set_value(total);
			self.tab_parent.parent.trigger("subtotal_money_changed",{"old":old,"new_value":total})
		},
		calculate_subtotal_qty:function(){
			var self = this;
			total = 0;
			old_qty = self.subtotal_qty.get_value();
			_.each(self.qty,function(cell){
				total = total + parseFloat(cell.get_value() || 0);
			})
			self.subtotal_qty.set_value(total);
			self.tab_parent.parent.trigger("subtotal_change",{'old':old_qty,'new_value':total});
		},
		renderElement:function(){
			console.log("renderElement")
			var self=this;
			width = self.get_width();
			//Fetch Volume Prices first
			self.$el = $(QWeb.render('products_list',{'tab_style':self.data.tab_style}))
			_.each(self.data.product_ids,function(product){
				$row = $("<tr><td><strong>%NAME%</strong></td></tr>".replace("%NAME%",product.name))
				// Qty Column
				$col= $("<td></td>")
				widget = new instance.web.form.FieldFloat(self.dfm,{
	                attrs: {
	                    name: "qty_input_"+remove_spaces(product.name),
	                    type: "float",
	                    context: {
	                    },
	                    modifiers: '{"required": false}',
	                },
	            });
				self.qty[product.id] = widget;
				widget.appendTo($col);
				widget.set_dimensions("auto",width)
				$row.append($col);
				widget.on("changed_value",widget,function(event){
					if (self.data.tab_style == 2){
						self.calculate_subtotal_money(product.id,this.get_value())
					}
					self.calculate_subtotal_qty();
				})
				if (self.data.tab_style != 2){
					self.$el.find("#main_body").append($row);
					return
				}
				// Unit price column
				$col = $("<td></td>")
				widget = new instance.web.form.FieldFloat(self.dfm,{
	                attrs: {
	                    name: "unit_price_input_"+remove_spaces(product.name),
	                    type: "float",
	                    context: {
	                    },
	                    modifiers: '{"required": false}',
	                },
	            });
				self.price[product.id] = widget;
				widget.appendTo($col);
				widget.set_value(self.get_price(product));
				widget.on("changed_value",widget,function(event){
					self.calculate_subtotal_money(product.id,this.get_value())
				});
				widget.set_dimensions("auto",width)
				$row.append($col);
				
				// Subtotal column
				$col = $("<td></td>")
				widget = new instance.web.form.FieldFloat(self.dfm,{
	                attrs: {
	                    name: "subtotal_input_"+remove_spaces(product.name),
	                    type: "float",
	                    context: {
	                    },
	                    modifiers: '{"required": false,"readonly":true}',
	                },
	            });
				self.subtotal[product.id] = widget;
				widget.appendTo($col);
				widget.set_dimensions("auto",width)
				$row.append($col);
				self.$el.find("#main_body").append($row);
			});//end each
			$row = $("<tr class='success'><td><strong>Total Quantity</strong></td></tr>");
			$col = $("<td></td>")
			widget = new instance.web.form.FieldFloat(self.dfm,{
                attrs: {
                    name: "subtotal_qty_input",
                    type: "float",
                    context: {
                    },
                    modifiers: '{"required": false,"readonly":true}',
                },
            });
			self.subtotal_qty = widget;
			widget.appendTo($col);
			widget.set_dimensions("auto",width)
			$row.append($col);
			self.$el.find("#main_body").append($row);
		},
	})
	
	local.flavor_conc_matrix = instance.Widget.extend({
		init:function(tab_parent,tab_data){
			this.tab_parent = tab_parent;
			this.data = tab_data;
			this.product_data = {};
			this.dfm = new instance.web.form.DefaultFieldManager(self);
			this.available_flavors = {};
			this.available_conc = {}
			this.prices = {}; // It will contain flavor key and widget of price
			this.subtotal_money = {}; // It will contain flavor key and widget of subtotals
			this.subtotal_qty = {};// It will contain concentration key and widget of qty total
			this.initialize();
		},
		initialize:function(){
			var self = this;
			$.each(self.data.product_ids,function(index,product){
				conc = product.conc_id[0];
				flavor = product.flavor_id[0];
				self.available_flavors[flavor] = product.flavor_id[1];
				self.available_conc[conc] = product.conc_id[1];
				widget = new instance.web.form.FieldFloat(self.dfm,{
	                attrs: {
	                    name: "qty_input_"+remove_spaces(product.name),
	                    type: "float",
	                    context: {
	                    },
	                    modifiers: '{"required": false}',
	                },
	            });
				widget.set({
					'data': product
				})
				if ( _.contains(_.keys(self.product_data),String(flavor))){ // if flavor key is present in dictionary
					self.product_data[flavor][conc]=widget
				}else{
					self.product_data[flavor] = {
							[conc]:widget,
						}
				}//end else
			}) // end each
			self.available_flavors = sortProperties(self.available_flavors);
			self.available_conc = sortProperties(self.available_conc);
		},
		get_prices:function(){
			return this.tab_parent.parent.prices[this.data.vol_id[0]] || 0; 
		},
		get_width:function(){
			return this.data.input_width
		},
		calculate_subtotal_money:function(flavor_id){
			var self = this;
			qty_total = 0;
			old = self.subtotal_money[flavor_id].get_value() || 0 ;
			_.each(self.product_data[flavor_id],function(cell){
				qty_total = qty_total  + parseFloat((cell.get_value() || 0))
			})
			price = self.prices[flavor_id].get_value();
			total_value = price*qty_total;
			self.subtotal_money[flavor_id].set_value(total_value);
			self.tab_parent.parent.trigger("subtotal_money_changed",{"old":old,"new_value":total_value})
		},
		calculate_subtotal_qty:function(conc_id){
			var self=this;
			total_qty = 0;
			old_qty = self.subtotal_qty[conc_id].get_value() || 0;
			_.each(self.product_data,function(flavor){
				if (flavor[conc_id]){
					total_qty = total_qty + parseFloat(flavor[conc_id].get_value())
				}
			})
			self.subtotal_qty[conc_id].set_value(total_qty || 0);
			self.tab_parent.parent.trigger("subtotal_change",{'old':old_qty,'new_value':total_qty});
		},
		start:function(){
			var self=this;
		},
		renderElement:function(){
			console.log("renderElement")
			var self=this;
			price = self.get_prices();
			width = self.get_width();
			//Fetch Volume Prices first
			self.$el = $(QWeb.render('flavor_conc_matrix_table',{"concentration":self.available_conc,'tab_style':self.data.tab_style}))
			$.each(self.available_flavors,function(index_flavor,flavor){
				$row = $("<tr></tr>");
				// * First render the product cells
				$row.append(("<td><strong>%NAME%<strong></td>").replace("%NAME%",flavor[1]))
				$.each(self.available_conc,function(index_conc,conc){
					$col= $("<td></td>")
					if (self.product_data[flavor[0]][conc[0]]){
						self.product_data[flavor[0]][conc[0]].appendTo($col)
						self.product_data[flavor[0]][conc[0]].set_dimensions("auto",width);
						self.product_data[flavor[0]][conc[0]].on("changed_value",self.product_data[flavor[0]][conc[0]],function(event){
							if (self.data.tab_style == 1){
								self.calculate_subtotal_money(flavor[0]);
							}
							self.calculate_subtotal_qty(conc[0]);
						});
					}//end if
					$row.append($col)
				}) //end each
				// * Now render the prices and subtotal cells
				if (self.data.tab_style == 1){ // flavor concentration matrix without free samples
					$col_price= $("<td></td>")
					$col_subtotal = $("<td></td>")
					widget_subtotal = new instance.web.form.FieldFloat(self.dfm,{
		                attrs: {
		                    name: "subtotal_money_input",
		                    type: "float",
		                    context: {
		                    },
		                    modifiers: '{"required": false,"readonly":true}',
		                },
		            });
					widget_price = new instance.web.form.FieldFloat(self.dfm,{
		                attrs: {
		                    name: "price_input",
		                    type: "float",
		                    context: {
		                    },
		                    modifiers: '{"required": false}',
		                },
		            });
					
					widget_price.set_value(price)
					widget_price.appendTo($col_price)
					widget_price.set_dimensions("auto",width);
					widget_price.on("changed_value",widget_price,function(event){
						self.calculate_subtotal_money(flavor[0]);
					})
					widget_subtotal.appendTo($col_subtotal)
					widget_subtotal.set_dimensions("auto",width);
					$row.append($col_price)
					$row.append($col_subtotal)
					self.prices[flavor[0]] = widget_price
					self.subtotal_money[flavor[0]] = widget_subtotal
				}
				self.$el.find("#main_body").append($row);
			})//end each				
			// * Now rendering the subtotal_qty widget
			$row = $("<tr class='success'><td><strong>Total Per Strength</strong></td></tr>");
			$.each(self.available_conc,function(index_conc,conc){
				$col = $("<td></td>");
				widget_subtotal_qty = new instance.web.form.FieldFloat(self.dfm,{
	                attrs: {
	                    name: "subtotal_qty_input",
	                    type: "float",
	                    context: {
	                    },
	                    modifiers: '{"required": false,"readonly":true}',
	                },
	            });
				widget_subtotal_qty.appendTo($col)
				widget_subtotal_qty.set_dimensions("auto",width)
				$row.append($col);
				self.subtotal_qty[conc[0]] = widget_subtotal_qty
			});//end each
			self.$el.find("#main_body").append($row);
		},
	})
	
	local.tab = instance.Widget.extend({
		init:function(parent,class_state,dataset){ //dataset is tab data
			this._super(parent);
			this.tech_tab_name = remove_spaces(dataset.name);
			this.class_state = class_state;
			this.$tab = $(QWeb.render("nav_tabs", {'tab_name':dataset.name,'class_state':class_state,'tech_tab_name':this.tech_tab_name}));
			this.$body = $(QWeb.render("tab_panes", {'tab_name':dataset.name,'class_state':class_state,'tech_tab_name':this.tech_tab_name}));
			this.parent = parent;
			this.dataset = dataset;
		},
		start:function(){
			var self=this;
			var tmp = self._super()
			switch(self.dataset.tab_style){
				case 1://Flavor Concentration Matrix
					console.log("Flavour Concentration Matrix");
					var tab_widget = new local.flavor_conc_matrix(self,self.dataset);
					tab_widget.appendTo(self.$body);
					self.tab_widget = tab_widget;
					break;
				case 2://Products List
					console.log("Products List");
					var tab_widget = new local.product_lists(self,self.dataset);
					tab_widget.appendTo(self.$body);
					self.tab_widget = tab_widget;
					break;
				case 3: //Marketing
					console.log("Marketing");
					break;
				case 4: //Free Samples List
					console.log("Free Samples List");
					var tab_widget = new local.product_lists(self,self.dataset);
					tab_widget.appendTo(self.$body);
					self.tab_widget = tab_widget;
					break;
				case 5: //Free Samples Matrix
					console.log("Free Samples Matrix");
					var tab_widget = new local.flavor_conc_matrix(self,self.dataset);
					tab_widget.appendTo(self.$body);
					self.tab_widget = tab_widget;
					break;
				default:
					break;
			}
		},
		renderElement:function(){
			var self = this;
			self.$tab.appendTo(self.parent.tabs)
			self.$body.appendTo(self.parent.panes)
		}
	});
	
	local.payment_plan_line = instance.Widget.extend({
		template:"payment_plan_line",
		init:function(parent){
			this._super(parent);
			this.parent = parent
			this.dfm = new instance.web.form.DefaultFieldManager(this);
            this.dfm.extend_field_desc({
            	payment_method: {
                    relation: "account.journal",
                },
            });			
			this.payment_method = new instance.web.form.FieldMany2One(this.dfm,{
                attrs: {
                    name: "payment_method",
                    type: "many2one",
                    context: {
                    },
                    modifiers: '{"required": true}',
                }
            });			
			this.amount = new instance.web.form.FieldFloat(this.dfm,{
                attrs: {
                    name: "amount",
                    type: "float",
                    context: {
                    },
                    modifiers: '{"required": true}',
                }
            });
			this.date = new instance.web.form.FieldDate(this.dfm,{
                attrs: {
                    name: "date",
                    type: "date",
                    context: {
                    },
                    modifiers: '{"required": true}',
                }
            });	
			this.$delete = $("<span class='glyphicon glyphicon-remove-circle'></span>")
		},
		start:function(){
			var self = this;
			self.$delete.on("click",self,function(event){
				self.destroy();
			})
			self.amount.on("change",self,function(event){
				self.parent.trigger("recalculate_total",true);
			});
		},
		
		renderElement:function(){
			var self = this;
			this._super();
			self.payment_method.appendTo(self.$el.find("td#payment_method"))
			self.amount.appendTo(self.$el.find("td#amount"))
			self.date.appendTo(self.$el.find("td#date"))
			console.log(self.$el.find("td#delete"));
			self.$el.find("td#delete").append(self.$delete)
		},
		destroy:function(){
			this._super();
			this.parent.trigger("recalculate_total",true);
		},
		
	});
	
	local.payment_plan = instance.Widget.extend({
		template:"payment_plan",
		init:function(parent){
			this._super(parent);
			this.line = []
			this.total = 0.00;
			this.parent = parent;
		},
		renderElement:function(){
			var self = this;
			self._super();
			self.$add_an_item = $("<tr><td><a href='#'><u>Add an item</u></a></td></tr>") 
			self.$el.append(self.$add_an_item);
		},
		recalculate_total:function(){
			var self = this;
			_.each(self.line,function(line){
				self.total = self.total + parseFloat(line.amount.get_value() || 0)
			});
			self.parent.trigger("recalc_balance",true)
		},
		start:function(){
			var self = this;
			self.$add_an_item.on("click",self,function(event){
				line = new local.payment_plan_line(self)
				self.line.push(line);
				line.appendTo(self.$el)
			});
			self.on("recalculate_total",self,self.recalculate_total)
		},
	});
	
	// Main 
	instance.web.form.custom_widgets.add('jjuice', 'instance.jjuice.jjuice_interface_main');
	local.jjuice_interface_main = instance.web.form.FormWidget.extend({
    	template:'interface',
    	events:{
    		"click button#rate_request":"execute_rate_request"
    	},
    	init: function(field_manager,node) {
			this._super(field_manager, node);
    		this.field_manager = field_manager;
    		this.prices = {};
    		this.$prices = $.Deferred();
    		this.dfm = new instance.web.form.DefaultFieldManager(self);
    		this.taxes = [];
		},
		execute_rate_request:function(){
			var self = this;
			self.do_action({
                type: 'ir.actions.act_window',
                res_model: "rate.fedex.request",
                views: [[false, 'form']],
                context:{
                	"default_recipient_id":self.field_manager.datarecord.id
                },
                target: 'new'
			})
		},
		renderTabs:function(){
			var self = this;
			self.tabs = self.$el.find("ul[role='tablist']")
			self.panes = self.$el.find("div.tab-content")
			//Fetch Prices of current customer
			volume_prices_ids = self.field_manager.datarecord.volume_prices
			if (volume_prices_ids.length > 0){
				vol_price = new openerp.Model('volume.prices.line'); 
				vol_price.call('read',{
					'ids':volume_prices_ids,
					'fields':['product_attribute','price']
				}).done(function(prices){
					_.each(prices,function(elem){
						if (elem.product_attribute){
							self.prices[elem.product_attribute[0]]=elem.price; 
						}						
					})
					self.$prices.resolve()
				})
			}else{
				self.$prices.resolve()
			}//end if else
			
			$.when(main_def,self.$prices).done(function(res){
				self.tabs_object = []
				self.tabs_data = res.tabs; // Saving Tab data in Main widget
				_.each(res.taxes,function(tax){
					$row = $("<tr><td><span><strong>%NAME%</strong></span></td></tr>".replace("%NAME%",tax.name))
					$col = $("<td></td>")
					var tax_widget = new instance.web.form.FieldBoolean(self.dfm,{
		                attrs: {
		                    name: "tax_input",
		                    type: "boolean",
		                    context: {
		                    },
		                    modifiers: '{"required": false}',
		                },
					});
					tax_widget.appendTo($col);
					tax_widget.set({
						'id':tax.id,
						'amount':tax.amount,
					});
					tax_widget.on("change",self,self.tax_changed)
					$row.append($col);
					self.$el.find("tbody#taxes").append($row);
					self.taxes.push(tax_widget)
				});
				$.each(self.tabs_data ,function(index,tab){
					// Check first if the tab is to be displayed for this customer
					if (!tab.visible_all_customers){
						if (!_.contains(tab.specific_customer_ids,self.field_manager.datarecord.id)){
							return
						}
					}
					// state is a variable that decides whether the tab is by default active or not. In our case by default active is the first tab
					state = false
					if (self.tabs_object.length == 0){
						state=true;
					}
					var tab_widget = new local.tab(self,state,tab)
					state = true // First tab index = 0
					tab_widget.appendTo(self.$el)
					self.tabs_object.push(tab_widget)
				})
			}) // end when			
		},

		renderElement:function(){
			var self = this;
			self._super();
			self.renderTabs();
			$body = self.$el.find("tbody#main_body")
			self.total_units = new instance.web.form.FieldFloat(self.dfm,{
                attrs: {
                    name: "total_unit_input",
                    type: "float",
                    context: {
                    },
                    modifiers: '{"required": false,"readonly":true}',
                },
            });
			self.total_units.appendTo($body.find('td#total_units'))
			self.subtotal = new instance.web.form.FieldFloat(self.dfm,{
                attrs: {
                    name: "subtotal_input",
                    type: "float",
                    context: {
                    },
                    modifiers: '{"required": false,"readonly":true}',
                },
            });
			self.subtotal.appendTo($body.find('td#subtotal'))
			
			self.shipping_handling = new instance.web.form.FieldFloat(self.dfm,{
                attrs: {
                    name: "s_h_input",
                    type: "float",
                    context: {
                    },
                    modifiers: '{"required": false}',
                },
            });
			self.shipping_handling.appendTo($body.find("#s_h"))
				 
			self.order_notes = new instance.web.form.FieldText(self.dfm,{
                attrs: {
                    name: "order_notes_input",
                    type: "text",
                    context: {
                    },
                    modifiers: '{"required": false}',
                },
            });
			self.order_notes.appendTo($body.find("#order_notes"))
			
			self.discount_percentage = new instance.web.form.FieldFloat(self.dfm,{
                attrs: {
                    name: "discount_percentage_input",
                    type: "float",
                    context: {
                    },
                    modifiers: '{"required": false}',
                },
            });
			self.discount_percentage.appendTo($body.find("#discount_percentage"))
			self.discount_percentage.on("change",self,self.changed_discount);
			
			self.discount = new instance.web.form.FieldFloat(self.dfm,{
                attrs: {
                    name: "discount_input",
                    type: "float",
                    context: {
                    },
                    modifiers: '{"required": false}',
                },
            });
			self.discount.appendTo($body.find("#discount"))
			self.discount.on("change",self,self.changed_discount);
			
			self.tax_value = new instance.web.form.FieldFloat(self.dfm,{
                attrs: {
                    name: "tax_input",
                    type: "float",
                    context: {
                    },
                    modifiers: '{"required": false,"readonly":true}',
                }
            });
			self.tax_value.appendTo($body.find("td#tax_value"))
			self.total = new instance.web.form.FieldFloat(self.dfm,{
                attrs: {
                    name: "total",
                    type: "float",
                    context: {
                    },
                    modifiers: '{"required": false,"readonly":true}',
                }
            });
			self.total.appendTo($body.find("td#total"))			
			self.paid = new instance.web.form.FieldFloat(self.dfm,{
                attrs: {
                    name: "paid",
                    type: "float",
                    context: {
                    },
                    modifiers: '{"required": false}',
                }
            });
			self.paid.appendTo($body.find("td#paid"))						
			self.paid.on("change",self,function(){self.trigger("recalc_balance",true)});
			self.balance = new instance.web.form.FieldFloat(self.dfm,{
                attrs: {
                    name: "balance",
                    type: "float",
                    context: {
                    },
                    modifiers: '{"required": false,"readonly":true}',
                }
            });
			self.balance.appendTo($body.find("td#balance"))		
			self.payment_plan = new local.payment_plan(self);
			self.payment_plan.appendTo($body.find("td#payment_plans"))
		},
		trigger_recalculate:function(){
			var self = this;
			self.trigger("recalc_discount",self.discount_percentage)
			self.trigger("recalc_tax",true)
			self.trigger("recalc_total",true);
		},
		subtotal_changed:function(event_data){
			var self = this;
			old = self.total_units.get_value() || 0;
			new_total = old +  event_data.new_value - event_data.old;
			self.total_units.set_value(new_total)
		},		
		subtotal_money_changed:function(event_data){
			var self = this;
			old = self.subtotal.get_value() || 0;
			new_total = old - event_data.old + event_data.new_value
			self.subtotal.set_value(new_total)
			self.trigger_recalculate();
		},
		tax_changed:function(tax){
			var self=this;
			amount = 0
			subtotal = self.subtotal.get_value() || 0;
			s_h = parseFloat(self.shipping_handling.get_value()) || 0;
			subtotal = subtotal + s_h;
			discount = self.discount.get_value() || 0;
			taxable_amount = subtotal - discount
			_.each(self.taxes,function(tax){
				tax_amount = tax.get("amount");
				if (tax.get_value()){
					amount = amount +  taxable_amount * tax_amount
				}//end if
				console.log(amount);
			}); //end each
			self.tax_value.set_value(amount);
			self.trigger("recalc_total",true);
		},
		changed_discount:function(field){
			var self = this;
			console.log("discount")
			if (field.field_manager.eval_context.stop){
				return
			}
			field.field_manager.eval_context.stop = true;
			if (field.name == "discount_percentage_input"){
				discount_percentage = parseFloat(field.get_value()) || 0
				subtotal = self.subtotal.get_value() || 0;
				s_h = parseFloat(self.shipping_handling.get_value()) || 0;
				subtotal = subtotal + s_h;
				discount = (discount_percentage * subtotal)/100;
				self.discount.set_value(discount);
				
			}else if (field.name == "discount_input"){
				console.log(field,self)
				discount = parseFloat(field.get_value()) || 0;
				subtotal = self.subtotal.get_value() || 0;
				s_h = parseFloat(self.shipping_handling.get_value()) || 0;
				subtotal = subtotal + s_h;
				if (subtotal != 0){
					discount_percentage = (discount/subtotal)*100;
					self.discount_percentage.set_value(discount_percentage);												
				}
			}
			field.field_manager.eval_context.stop = false;
			self.trigger("recalc_tax",true)
			self.trigger("recalc_total",true);
		},		
		recalculate(event_data){
			var self = this;
			subtotal = parseFloat(self.subtotal.get_value()) || 0;
			shipping_handling = parseFloat(self.shipping_handling.get_value()) || 0;
			console.log( "*",shipping_handling );
			discount = parseFloat(self.discount.get_value()) || 0;
			tax_value = parseFloat(self.tax_value.get_value()) || 0;
			total = subtotal + shipping_handling - discount + tax_value
			self.total.set_value(total);
			self.trigger("recalc_balance",true)
		},
		recalculate_balance:function(event){
			var self = this;
			paid = parseFloat(self.paid.get_value()) || 0;
			total = parseFloat(self.total.get_value()) || 0;
			plan_total = self.payment_plan.total || 0;
			balance = total - paid - plan_total;
			self.balance.set_value(balance);
		},
		start:function(){
			var self = this;
			self.on("subtotal_change",self,self.subtotal_changed)
			self.on("subtotal_money_changed",self,self.subtotal_money_changed)
			self.on("recalc_total",self,self.recalculate);
			self.on("recalc_tax",self,self.tax_changed);
			self.on("recalc_discount",self,self.changed_discount);
			self.shipping_handling.on("change",self,self.trigger_recalculate);
			self.on("recalc_balance",self,self.recalculate_balance);
			this.field_manager.on("change",self,function(event){
				/*
				 * The view is not refreshed when we change the partner record. For that if we detect a change in field manager,
				 * we empty the $el of the parent and render according the new customer record
				 */  
				console.log("form changed2",event)
				console.log("field manager:",self.field_manager)
				self.$el.empty();
				self.renderElement();
			});			
		}
	});
}