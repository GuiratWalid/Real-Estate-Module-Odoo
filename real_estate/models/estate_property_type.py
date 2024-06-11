from odoo import models, fields, api


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Real Estate Property Type Model"
    _order = "sequence, name"

    # Fields
    name = fields.Char(
        string="Name",
        required=True
    )
    property_ids = fields.One2many(
        comodel_name="estate.property",
        inverse_name="property_type_id"
    )
    sequence = fields.Integer(
        default=1,
        help="Used to order stages. Lower is better."
    )
    offer_ids = fields.One2many(
        comodel_name="estate.property.offer",
        inverse_name="property_type_id"
    )

    # Computed Fields
    offer_count = fields.Integer(
        compute="_compute_offer_count",
        string="Offers"
    )

    @api.depends("offer_ids")
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)

    # SQL Constrains
    _sql_constraints = [
        ("name_unique", "unique(name)", "The property type's name must be unique!")
    ]
