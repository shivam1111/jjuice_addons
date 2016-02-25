Setup
-----
The autocomplete feature causes problem. Hence in the view_form.js > instance.web.form.FieldMany2One > initialize_field replace it with the following

`    initialize_field: function() {
        this.is_started = true;
        instance.web.bus.on('click', this, function() {
            if (this.$input){
                    this.$input.autocomplete(); 
            }
            if (!this.get("effective_readonly") && this.$input && this.$input.autocomplete('widget').is(':visible')) {
                this.$input.autocomplete("close");
            }
        });
        instance.web.form.ReinitializeFieldMixin.initialize_field.call(this);
    },`
