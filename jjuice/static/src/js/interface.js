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
    	mod.call("search_read",{'order':'sequence',}).done(function(tabs){ //search_read method will automatically not load active = False records
    		product = new openerp.Model('product.product',{},[])
    		// tabs is an array
    		$.each(tabs,function(index,tab){
    			if (tab.product_ids.length > 0){
    				product.call("read",{
    					"ids":tab.product_ids,
    					"fields":['name','vol_id','conc_id','flavor_id','lst_price']
    				}).done(function(data){
    					tab.product_ids = data
    					if (index == tabs.last()){
    						main_def.resolve(tabs)
    					}
    				})
    			}else{
    				if (index == tabs.last()){
						main_def.resolve(tabs)
					}
    			}
    		})
    	})
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
		},
		
		get_width:function(){
			return this.data.input_width
		},
		
		get_price:function(product){
			return product.lst_price;
		},
		
		renderElement:function(){
			console.log("renderElement")
			var self=this;
			width = self.get_width();
			//Fetch Volume Prices first
			self.$el = $(QWeb.render('products_list',{'tab_style':self.data.tab_style}))
			console.log(self.data)
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
	                    name: "qty_input"+remove_spaces(product.name),
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
			_.each(self.product_data[flavor_id],function(cell){
				console.log(cell.get_value());
				qty_total = qty_total  + parseFloat((cell.get_value() || 0))
			})
			price = self.prices[flavor_id].get_value();
			total_value = price*qty_total;
			self.subtotal_money[flavor_id].set_value(total_value);
		},
		calculate_subtotal_qty:function(conc_id){
			var self=this;
			total_qty = 0;
			_.each(self.product_data,function(flavor){
				if (flavor[conc_id]){
					total_qty = total_qty + parseFloat(flavor[conc_id].get_value())
				}
			})
			self.subtotal_qty[conc_id].set_value(total_qty);
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
				$row.append(("<td>%NAME%</td>").replace("%NAME%",flavor[1]))
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
			$row = $("<tr class='success'><td>Total Per Strength</td></tr>");
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
			console.log(self);
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
	})
	
	// Main 
	instance.web.form.custom_widgets.add('jjuice', 'instance.jjuice.jjuice_interface_main');
	local.jjuice_interface_main = instance.web.form.FormWidget.extend({
    	template:'interface',
		init: function(field_manager,node) {
			this._super(field_manager, node);
    		this.field_manager = field_manager;
    		this.prices = {};
    		this.$prices = $.Deferred();
		},
		start:function(){
			var self = this;
			this.tabs_object = []
			this.field_manager.on("change",self,function(){
				/*
				 * The view is not refreshed when we change the partner record. For that if we detect a change in field manager,
				 * we empty the $el of the parent and render according the new customer record
				 */  
				self.$el.empty();
				self.renderElement();
				self.start();
			});			
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
			}					
			$.when(main_def,self.$prices).done(function(tabs){
				console.log(self.prices);
				self.tabs_data = tabs; // Saving Tab data in Main widget
				$.each(tabs,function(index,tab){
					// Check first if the tab is to be displayed for this customer
					if (!tab.visible_all_customers){
						if (!_.contains(tab.specific_customer_ids,self.field_manager.datarecord.id)){
							return
						}
					}
					// state is a variable that decides whether the tab is by default active or not. In our case by default active is the first tab
					state = false
					if (self.tabs_object.length == 0){
						state = true // First tab index = 0
					}
					var tab_widget = new local.tab(self,state,tab)
					tab_widget.appendTo(self.$el)
					self.tabs_object.push(tab_widget)
				})
			})
		}
	});
}