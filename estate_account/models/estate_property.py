from odoo import models, fields, api


class EstateProperty(models.Model):
    _inherit = "estate.property"

    # Related Fields
    invoice_id = fields.Many2one(
        comodel_name="account.move",
        string="Invoice"
    )

    # Computed Fields
    invoice_count = fields.Integer(
        compute="_compute_invoice_count",
        store=True
    )

    @api.depends("invoice_id")
    def _compute_invoice_count(self):
        for record in self:
            if record.invoice_id:
                record.invoice_count = 1
            else:
                record.invoice_count = 0

    # Overriding Sold Method
    def sold_action(self):
        salesman = self.salesman_id.partner_id
        commission_amount = 0.06 * self.selling_price
        admin_fee = 100.00
        self.invoice_id = self.env['account.move'].create({
            'partner_id': salesman.id,
            'move_type': 'out_invoice',
            'invoice_line_ids': [
                (0, 0, {
                    'name': 'Commission (6% of selling price)',
                    'quantity': 1,
                    'price_unit': commission_amount,
                }),
                (0, 0, {
                    'name': 'Administrative Fees',
                    'quantity': 1,
                    'price_unit': admin_fee,
                })
            ]
        })
        return super(EstateProperty, self).sold_action()

    # Action to Open The Invoice Using The Smart Button
    def action_view_invoice(self):
        return {
        'type': 'ir.actions.act_window',
        'res_model': 'account.move',
        'view_mode': 'form',
        'res_id': self.invoice_id.id,
        'target': 'current',
    }
