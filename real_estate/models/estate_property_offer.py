from odoo import models, fields, api
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from datetime import datetime


STATUS_VALUES = [
    ("accepted", "Accepted"),
    ("refused", "Refused")
]


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Real Estate Property Offer Model"
    _order = "price desc"

    # Fields
    price = fields.Float()
    status = fields.Selection(
        selection=STATUS_VALUES,
        copy=False
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        required=True
    )
    property_id = fields.Many2one(
        comodel_name="estate.property",
        required=True,
        ondelete="cascade"
    )
    validity = fields.Integer(
        string="Validity (days)",
        default=7
    )

    # Computed Fields
    date_deadline = fields.Date(
        string="Deadline",
        compute="_compute_date_deadline",
        inverse="_inverse_date_deadline",
        store=True
    )

    # Realted fields
    property_type_id = fields.Many2one(
        comodel_name="estate.property.type",
        string="Property Type",
        related="property_id.property_type_id",
        store=True
    )

    @api.depends("create_date", "validity")
    def _compute_date_deadline(self):
        for record in self:
            if record.create_date:
                if record.validity:
                    record.date_deadline = record.create_date + relativedelta(days=record.validity)
                else:
                    record.date_deadline = record.create_date
            else:
                if record.validity:
                    record.date_deadline = fields.Date.today() + relativedelta(days=record.validity)
                else:
                    record.date_deadline = fields.Date.today()

    def _inverse_date_deadline(self):
        for record in self:
            if record.date_deadline:
                date_deadline = datetime.strptime(record.date_deadline.strftime("%Y-%m-%d"), "%Y-%m-%d").date()
                create_date = datetime.strptime(record.create_date.strftime("%Y-%m-%d"), "%Y-%m-%d").date()
                delta = date_deadline - create_date
                record.validity = delta.days
            else:
                record.validity = 0

    # Button Actions
    def action_accept(self):
        for record in self:
            record.status = "accepted"
            record.property_id.buyer_id = record.partner_id
            record.property_id.selling_price = record.price
            record.property_id.state = "offer_accepted"
            for offer in record.property_id.offer_ids:
                if offer.id != record.id:
                    offer.status = "refused"

    def action_refuse(self):
        for record in self:
            record.status = "refused"

    # SQL Constrains
    @api.constrains("price")
    def _check_prices(self):
        for record in self:
            if record.price <= 0:
                raise ValidationError("The " + record.partner_id.name + " offer's price must be strictly positive.")

    # Override CRUD Methods
    @api.model
    def create(self, vals):
        # Check if the property already has higher offers
        property_id = self.env["estate.property"].browse(vals["property_id"])
        if property_id.offer_ids:
            max_offer = max(property_id.offer_ids.mapped("price"))
            if max_offer >= vals["price"]:
                raise ValidationError(f"The offer must be higher than {max_offer}.")
        # Set the property state to 'Offer Received'
        property_id.state = 'offer_received'
        return super(EstatePropertyOffer, self).create(vals)
