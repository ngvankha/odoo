from odoo import fields, models
from odoo.tools.convert import relativedelta

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "this is my new model at odoo 16"

    name = fields.Char(string="Title", required=True)
    description = fields.Text()
    postcode = fields.Char()
    availability_date = fields.Date(
        string="Available From",
        copy=False,
        default=fields.date.today() + relativedelta(months=+3),
    )
    date_availability = fields.Date(
        string="Available From",
        copy=False,
        default=fields.date.today() + relativedelta(months=+3),
    )
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer(string="Living Area (sqm)")
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        selection=[
            ("North", "North"),
            ("South", "South"),
            ("East", "East"),
            ("West", "West"),
        ]
    )
    
    active = fields.Boolean(string="Active", default=True)
    state = fields.Selection(
        selection=[
            ('new', 'New'),
            ('offer_received', 'Offer Received'),
            ('offer_accepted', 'Offer Accepted'),
            ('sold', 'Sold'),
            ('canceled', 'Canceled')
        ],
        string='Status',
        required=True,
        copy=False,
        default='new'
    )
    
    # Add a one2many relationship to property model (will be defined in property model)
    property_ids = fields.One2many('estate.property', 'property_type_id', string="Properties")
    
    # Add the many2one field to link to property type
    property_type_id = fields.Many2one('estate.property.type', string="Property Type")
    