# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# Author: Ernad Husremovic
# mail:   hernad@bring.out.ba
{
    "name": "Bosnia and Herzegovina",
    "description": """
Bosnian localisation.
======================

Author: Ernad Husremovic bring.out doo Sarajevo

Description:

Bosnian cities


""",
    "version": "16.0.0",
    "author": "bring.out",
    'category': 'Localization',
    "website": "https://github.com/hernad/odoo",
    'depends': [
        "base_address_extended",
        "account"
    ],
    'data': [
        "data/account_chart_template_data_1.xml",
        "data/account.account.template.csv",
        "data/account_chart_template_data_2.xml",
        "data/account.group.template.csv",
        "data/account_tax_group_data.xml",
        'data/account_tax_report_data.xml',
        "data/account_tax_template_data.xml",
        "data/account_chart_template_configure_data.xml",
        'data/country_enforce_cities.xml',
        'data/res.country.state.csv',
        'data/res.city.csv',
        'views/enforce_cities.xml',
        "data/menuitem_data.xml",
    ],
    "active": False,
    'license': 'AGPL',
}
