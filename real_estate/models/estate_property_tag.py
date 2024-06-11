from odoo import models, fields


class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Real Estate Property Tag Model"
    _order = "name"

    # Fields
    name = fields.Char(
        string="Name",
        required=True
    )
    color = fields.Integer()

    # SQL Constrains
    _sql_constraints = [
        ("name_unique", "unique(name)", "The property tag's name must be unique!")
    ]
