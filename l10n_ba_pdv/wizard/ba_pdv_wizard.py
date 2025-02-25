from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from .date_util import DateUtil


ZAOKRUZENJE = 2

class BaPDVWizard(models.TransientModel):

    _name = 'ba.pdv.wizard'

    date_from = fields.Date(string="Obračun od:", required=True, default=DateUtil.default_date_from())
    date_to = fields.Date(string="do:", required=True, default=DateUtil.default_date_to())

    company_id = fields.Many2one(
        "res.company",
        string="Preduzeće:",
        default=lambda self: self.env.user.company_id,
    )

    enabavke_last_id = fields.Integer(string="Redni broj posljednje nabavke")
    eisporuke_last_id = fields.Integer(string="String redni posljednje isporuke")

    def _get_porezni_period(self, dat_od: datetime.date):
        # 2502 - februart 2025
        return dat_od.strftime("%y%m")
    
    def action_generate_xlsx(self):
        data = {'date_from': self.date_from,
                'date_to': self.date_to,
                'company_id': self.company_id.id,
                'enabavke_last_id': self.enabavke_last_id,
                'eisporuke_last_id': self.eisporuke_last_id,
                'model': self._name,
                'ids': self.ids,
                'docids': self.ids,
                'porezni_period': self._get_porezni_period(self.date_from),
                'csv_name': self.company_id.vat + "_" + self._get_porezni_period(self.date_from)
               }
        return self.env.ref('l10n_ba_pdv.pdv_xlsx_report').report_action(self, data=data)


    def action_generate_eisporuke_csv(self):
   
        data = {'date_from': self.date_from,
                'date_to': self.date_to,
                'enabavke_last_id': self.enabavke_last_id,
                'eisporuke_last_id': self.eisporuke_last_id,
                'company_id': self.company_id.id,
                'model': self._name,
                'ids': self.ids,
                'docids': self.ids,
                'porezni_period': self._get_porezni_period(self.date_from),
                'csv_name': self.company_id.vat + "_" + self._get_porezni_period(self.date_from) + "_2_01"
               }
        return self.env.ref('l10n_ba_pdv.eisporuke_csv').report_action(self, data)


    def action_generate_enabavke_csv(self):
   
        data = {'date_from': self.date_from,
                'date_to': self.date_to,
                'enabavke_last_id': self.enabavke_last_id,
                'eisporuke_last_id': self.eisporuke_last_id,
                'company_id': self.company_id.id,
                'model': self._name,
                'ids': self.ids,
                'docids': self.ids,
                'porezni_period': self._get_porezni_period(self.date_from),
                'csv_name': self.company_id.vat + "_" + self._get_porezni_period(self.date_from) + "_1_01"
               }
        return self.env.ref('l10n_ba_pdv.enabavke_csv').report_action(self, data)
