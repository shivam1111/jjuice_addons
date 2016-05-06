openerp.jjuice.pos = function (instance,local) {
	
	var _t = instance.web._t,
    _lt = instance.web._lt;
	var QWeb = instance.web.qweb;
	instance.web.pls = instance.web.pls || {}	
	
	instance.web.form.custom_widgets.add('jjuice', 'instance.jjuice.action');
	instance.jjuice.action = instance.web.form.FormWidget.extend({
    	init: function(field_manager, node) {
    		this._super(field_manager, node);
    		this.field_manager_arr = [];
    		this.parent = parent;
    		this.index = 0;
    		this.price = 0;
    		this.total = 0.00;
    		this.subtotal = 0.00;
    		this.marketing_package = [] ;
    		this.product_availability = {};
    	},
		start:function(){	
			var self = this;
			console.log("interface.js");
		}
	});
}