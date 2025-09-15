from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"module_name": "Farm Management",
			"category": "Modules",
			"label": _("Farm Management"),
			"color": "#2ecc71",
			"icon": "fa fa-leaf",
			"type": "module",
			"description": _("Comprehensive farm management for poultry and pig farms")
		}
	]
