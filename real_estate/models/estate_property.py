from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero
from dateutil.relativedelta import relativedelta


GARDEN_ORIENTATION_VALUES = [
    ("north", "North"),
    ("south", "South"),
    ("east", "East"),
    ("west", "West")
]
STATE_VALUES = [
    ("new", "New"),
    ("offer_received", "Offer Received"),
    ("offer_accepted", "Offer Accepted"),
    ("sold", "Sold"),
    ("canceled", "Canceled")
]


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate Property Model"
    _order = "id desc"

    # Fields
    name = fields.Char(
        string="Title",
        required=True
    )
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(
        string="Available From",
        copy=False,
        default=lambda self: fields.Date.today() + relativedelta(months=3)
    )
    expected_price = fields.Float(
        required=True
    )
    selling_price = fields.Float(
        readonly=True,
        copy=False
    )
    bedrooms = fields.Integer(
        default=2
    )
    living_area = fields.Integer(
        string="Living Area (sqm)"
    )
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer(
        string="Garden Area (sqm)"
    )
    garden_orientation = fields.Selection(
        selection=GARDEN_ORIENTATION_VALUES
    )
    active = fields.Boolean(
        default=True
    )
    state = fields.Selection(
        selection=STATE_VALUES,
        required=True,
        copy=False,
        default="new",
        string="Status"
    )
    # Related Fields
    property_type_id = fields.Many2one(
        comodel_name="estate.property.type",
        string="Type"
    )
    salesman_id = fields.Many2one(
        comodel_name="res.users",
        string="Salesman",
        default=lambda self: self.env.user
    )
    buyer_id = fields.Many2one(
        comodel_name="res.partner",
        string="Buyer",
        copy=False
    )
    tag_ids = fields.Many2many(
        comodel_name="estate.property.tag"
    )
    offer_ids = fields.One2many(
        comodel_name="estate.property.offer",
        inverse_name="property_id"
    )

    # Computed Fields
    total_area = fields.Integer(
        string="Total Area (sqm)",
        compute="_compute_total_area"
    )
    best_offer = fields.Float(
        compute="_compute_best_offer"
    )

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids")
    def _compute_best_offer(self):
        for record in self:
            if record.offer_ids:
                record.best_offer = max(record.offer_ids.mapped("price"))
            else:
                record.best_offer = 0.0

    # Onchanges
    @api.onchange("garden")
    def _onchange_garden(self):
        for record in self:
            if record.garden:
                record.garden_area = 10
                record.garden_orientation = "north"
            else:
                record.garden_area = 0
                record.garden_orientation = ""

    # Button Actions
    def sold_action(self):
        for record in self:
            if record.state == "canceled":
                raise UserError("Canceled properties can not be sold.")
            else:
                record.state = "sold"

    def cancel_action(self):
        for record in self:
            if record.state == "sold":
                raise UserError("Sold properties can not be canceled.")
            else:
                record.state = "canceled"

    # SQL Constrains
    @api.constrains("expected_price", "selling_price")
    def _check_prices(self):
        for record in self:
            if record.expected_price <= 0:
                raise ValidationError("The expected price must be strictly positive.")            
            if record.selling_price <= 0 and 'accepted' in record.offer_ids.mapped("status"):
                raise ValidationError("The selling price must be strictly positive.")

            # The selling price cannot be lower than 90% of the expected price
            if not float_is_zero(record.selling_price, precision_rounding=0.01):
                # Calculate 90% of the expected price
                minimum_price = record.expected_price * 0.9
                # Compare selling price with 90% of the expected price
                if float_compare(record.selling_price, minimum_price, precision_rounding=0.01) == -1:
                    raise ValidationError("The selling price cannot be lower than 90% of the expected price.")

    # Override CRUD Methods
    @api.ondelete(at_uninstall=False)
    def _unlink_if_state_not_in_new_or_canceled(self):
        for record in self:
            if record.state not in ("new", "canceled"):
                raise UserError("Only new and canceled properties can be deleted!")
