from odoo import fields, models

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Real Estate Property Type"

    name = fields.Char("Name", required=True)
    
    # Add a one2many relationship to property model (will be defined in property model)
    property_ids = fields.One2many('estate.property', 'property_type_id', string="Properties")