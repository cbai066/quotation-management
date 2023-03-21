odoo.define('product_supplier.list_view_button', function (require) {
    "use strict";

    var ListController = require('web.ListController');

    ListController.include({
        renderButtons: function () {
            this._super.apply(this, arguments);
            if (this.$buttons) {

                var btn = this.$buttons.find('.o_button_supplier_import_data');

                btn.on('click', this.proxy('sysn_import_data'));
            }


        },
        sysn_import_data: function () {
            var self = this;

            self._rpc({
                'model': 'all.supplier.products.wizard',
                'method': 'alert_all_supplier_products_form',
                'args': []
            }).then(function (action) {
                if(!!action){
                self.do_action(action)
            }})
        },
    });
});
