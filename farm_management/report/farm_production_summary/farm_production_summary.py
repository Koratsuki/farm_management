# Copyright (c) 2024, Farm Management Solutions and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	return [
		{
			"label": _("Farm"),
			"fieldname": "farm",
			"fieldtype": "Link",
			"options": "Farm",
			"width": 150
		},
		{
			"label": _("Farm Type"),
			"fieldname": "farm_type",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Total Animals"),
			"fieldname": "total_animals",
			"fieldtype": "Int",
			"width": 100
		},
		{
			"label": _("Poultry Batches"),
			"fieldname": "poultry_batches",
			"fieldtype": "Int",
			"width": 120
		},
		{
			"label": _("Total Birds"),
			"fieldname": "total_birds",
			"fieldtype": "Int",
			"width": 100
		},
		{
			"label": _("Total Pigs"),
			"fieldname": "total_pigs",
			"fieldtype": "Int",
			"width": 100
		},
		{
			"label": _("Eggs This Month"),
			"fieldname": "eggs_this_month",
			"fieldtype": "Int",
			"width": 120
		},
		{
			"label": _("Avg Daily Eggs"),
			"fieldname": "avg_daily_eggs",
			"fieldtype": "Float",
			"width": 120
		},
		{
			"label": _("Health Issues"),
			"fieldname": "health_issues",
			"fieldtype": "Int",
			"width": 100
		},
		{
			"label": _("Feed Cost (Monthly)"),
			"fieldname": "feed_cost_monthly",
			"fieldtype": "Currency",
			"width": 150
		}
	]

def get_data(filters):
	farms = frappe.get_all("Farm", fields=["name", "farm_type"])
	data = []
	
	for farm in farms:
		farm_data = {
			"farm": farm.name,
			"farm_type": farm.farm_type,
			"total_animals": 0,
			"poultry_batches": 0,
			"total_birds": 0,
			"total_pigs": 0,
			"eggs_this_month": 0,
			"avg_daily_eggs": 0,
			"health_issues": 0,
			"feed_cost_monthly": 0
		}
		
		# Get poultry data
		poultry_batches = frappe.get_all("Poultry Batch", 
			filters={"farm": farm.name},
			fields=["current_count"]
		)
		
		farm_data["poultry_batches"] = len(poultry_batches)
		farm_data["total_birds"] = sum([batch.current_count or 0 for batch in poultry_batches])
		
		# Get pig data
		pigs = frappe.get_all("Pig", 
			filters={"farm": farm.name, "health_status": ["!=", "Dead"]},
			fields=["name"]
		)
		farm_data["total_pigs"] = len(pigs)
		
		# Total animals
		farm_data["total_animals"] = farm_data["total_birds"] + farm_data["total_pigs"]
		
		# Get egg production for current month
		from datetime import datetime, timedelta
		current_month_start = datetime.now().replace(day=1)
		
		egg_records = frappe.db.sql("""
			SELECT SUM(eggs_collected) as total_eggs, COUNT(*) as days
			FROM `tabEgg Production Record`
			WHERE farm = %s AND date >= %s
		""", (farm.name, current_month_start), as_dict=True)
		
		if egg_records and egg_records[0].total_eggs:
			farm_data["eggs_this_month"] = egg_records[0].total_eggs
			if egg_records[0].days > 0:
				farm_data["avg_daily_eggs"] = egg_records[0].total_eggs / egg_records[0].days
		
		# Get health issues count
		health_issues = frappe.db.count("Health Record", {
			"farm": farm.name,
			"status": ["in", ["Active", "Ongoing"]],
			"record_type": ["in", ["Disease", "Injury", "Treatment"]]
		})
		farm_data["health_issues"] = health_issues
		
		# Get monthly feed cost
		feed_cost = frappe.db.sql("""
			SELECT SUM(total_cost) as total_cost
			FROM `tabFeed Record`
			WHERE farm = %s AND date >= %s
		""", (farm.name, current_month_start), as_dict=True)
		
		if feed_cost and feed_cost[0].total_cost:
			farm_data["feed_cost_monthly"] = feed_cost[0].total_cost
		
		data.append(farm_data)
	
	return data

