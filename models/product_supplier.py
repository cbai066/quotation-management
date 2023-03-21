# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import base64
import datetime
import xlrd
from xlrd import xldate_as_tuple
import re
from odoo.exceptions import ValidationError


class ProductTable(models.Model):
    """
        产品表
    """

    _name = 'product.table'

    _description = 'Product Table'


    mpn = fields.Char(string='mpn', help='mpn')

    price = fields.Float(string='Price', help='Price')

    supplier_id = fields.Many2one(comodel_name='supplier.table', string='Supplier')

    available_units = fields.Char(string='Available Units', help='Available Units')

    import_date = fields.Date(string="Date", help="Date")



class AllSupplierProducts(models.Model):
    """
        供应商导入数据表
    """

    _name = 'all.supplier.products'

    _description = 'All Supplier Products'


    mpn = fields.Char(string='mpn', help='mpn')

    supplier_id = fields.Many2one(comodel_name='supplier.table', string='Supplier')

    price = fields.Float(string='Price', help='Price')

    available_units = fields.Char(string='Available Units', help='Available Units')

    product_detail = fields.Char(string='Product Detail', help='Product Detail')

    import_date = fields.Date(string="Date", help="Date")

    @api.depends('mpn', 'supplier_id', 'import_date')
    def _compute_quatations_ids(self):
        pass
        quatations_ids = [-1]
        for n in self.env['product.table'].search([('mpn', '=', self.mpn), ('import_date', '=', self.import_date)]):
            quatations_ids.append(n.id)
        self.quatations_ids = self.env['product.table'].search([('id', 'in', quatations_ids)])

    @api.model
    def _default_quatations_ids(self):
        list = []
        for n in self.env['product.table'].search([('mpn', '=', self.mpn), ('import_date', '=', self.import_date)]):
            list.append(n.id)
        return list

    quatations_ids = fields.Many2many(comodel_name='product.table', string='Quatations',
                                            compute='_compute_quatations_ids',
                                            default=_default_quatations_ids)

    @api.depends('mpn', 'supplier_id')
    def _compute_supplier_ids(self):
        pass
        supplier_ids = [-1]
        for n in self.env['all.supplier.products'].search([('mpn', '=', self.mpn)]):
            supplier_ids.append(n.id)
        self.supplier_ids = self.env['all.supplier.products'].search([('id', 'in', supplier_ids)])

    @api.model
    def _default_supplier_ids(self):
        list = []
        for n in self.env['all.supplier.products'].search([('mpn', '=', self.mpn)]):
            list.append(n.id)
        return list

    supplier_ids = fields.Many2many(comodel_name='all.supplier.products', string='Quatations',
                                            compute='_compute_supplier_ids',
                                            default=_default_supplier_ids)


class SupplierTable(models.Model):
    """
        供应商表
    """
    _name = 'supplier.table'

    name = fields.Char(string='Name', help='Name')

class AllSupplierProductsWizard(models.TransientModel):

    _name = 'all.supplier.products.wizard'


    supplier_id = fields.Many2one(comodel_name='supplier.table', string='Supplier')

    upload_excel_file_id = fields.Binary(string='import data')


    @api.model
    def alert_all_supplier_products_form(self):
        view_id = self.env.ref('product_supplier.all_supplier_products_wizard_form').id
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'target': 'new'
        }

    def import_data(self):
        map_data = {
            'mpn': ['model', 'part', 'sku'],
            'available_units': ['stock', 'inventory', 'qty'],
            'price': ['price', 'offer'],
            'product_detail': ['description', 'productname', 'descrition']
        }
        if not self.upload_excel_file_id:
            raise ValidationError(_('please select file!'))
        workbook = xlrd.open_workbook(file_contents=base64.decodebytes(self.upload_excel_file_id))
        all_supplier_products_obj = self.env['all.supplier.products']
        product_obj = self.env['product.table']

        for i in range(len(workbook.sheets())):
            sheet_obj = workbook.sheet_by_index(i)
            title_list = []
            for i in range(0, sheet_obj.nrows):
                temp = {'supplier_id': self.supplier_id.id, 'import_date': fields.Date.today()}
                print(temp)
                if i == 0:
                    title_list = [title.lower() for title in sheet_obj.row_values(i)]
                    continue
                line_data = [self._format_string(row_data) for row_data in sheet_obj.row_values(i)]
                for index, title in enumerate(title_list):
                    for k, v in map_data.items():
                        for rec in v:
                            if re.findall(rec, title) and not (title == 'reduced price' and line_data[index] == ''):
                                temp[k] = line_data[index]
                product_data = product_obj.search(
                    [('mpn', '=', temp['mpn']), ('supplier_id', '=', self.supplier_id.id), ('price', '=', temp['price'])])
                if temp['mpn']:
                    all_supplier_products_obj.create(temp)
                if product_data:
                    product_data.write({
                        'available_units': product_data.available_units + temp['available_units']
                    })
                else:
                    del temp['product_detail']
                    if temp['mpn']:
                        product_data.create(temp)

    @api.model
    def _format_string(self, s):
        if isinstance(s, float):
            string = str(s)
            return string
        else:
            return s
