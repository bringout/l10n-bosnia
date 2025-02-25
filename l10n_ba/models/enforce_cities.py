from odoo import api, models, fields

# https://www.odoo.com/forum/help-1/replace-city-field-in-res-partner-with-city-id-of-res-city-161839

class ResPartner(models.Model):
    _inherit = 'res.partner'
    city_id = fields.Many2one('res.city', string='City')

    @api.depends('city_id')
    def set_city(self):
       for partner in self:
          partner.city = partner.city_id.name
          partner.zip = partner.city_id.zipcode
          partner.state_id = partner.city_id.state_id
          partner.country_id = partner.city_id.country_id


    city = fields.Char(compute=set_city, store=True)

class ResCity(models.Model):
   _inherit = 'res.city'

   code = fields.Char(string='Šifra JP')