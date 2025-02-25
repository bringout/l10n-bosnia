# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name": """Bosnia and Herzegovina fiskalizacija""",
    "version": "1.00.00",
    "category": "Accounting/Localizations/EDI",
    "depends": [
        "account_edi",
        "l10n_ba",
    ],
    "description": """
Bosnian - E Fiskalizacija
====================

    """,
    "data": [
        "data/account_edi_data.xml",
        "views/res_config_settings_views.xml",
        "views/edi_pdf_report.xml",
        "views/account_move_views.xml",
    ],
    "installable": True,
    "license": "AGPL",
}
