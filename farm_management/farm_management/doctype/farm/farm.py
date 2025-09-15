# Copyright (c) 2024, Farm Management Solutions and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Farm(Document):
	def validate(self):
		"""Validate farm data before saving"""
		self.validate_area()
		self.validate_contact_info()
	
	def validate_area(self):
		"""Validate that usable area is not greater than total area"""
		if self.total_area and self.usable_area:
			if self.usable_area > self.total_area:
				frappe.throw("Usable area cannot be greater than total area")
	
	def validate_contact_info(self):
		"""Validate contact information"""
		if self.email and "@" not in self.email:
			frappe.throw("Please enter a valid email address")
	
	def get_animal_count(self):
		"""Get total count of animals in this farm"""
		poultry_count = frappe.db.count("Poultry Batch", {"farm": self.name})
		pig_count = frappe.db.count("Pig", {"farm": self.name})
		return {
			"poultry_batches": poultry_count,
			"pigs": pig_count,
			"total": poultry_count + pig_count
		}
	
	def get_production_summary(self, from_date=None, to_date=None):
		"""Get production summary for the farm"""
		filters = {"farm": self.name}
		if from_date:
			filters["date"] = [">=", from_date]
		if to_date:
			filters["date"] = ["<=", to_date]
		
		# Get egg production
		egg_production = frappe.db.sql("""
			SELECT SUM(eggs_collected) as total_eggs
			FROM `tabEgg Production Record`
			WHERE farm = %s
			AND date BETWEEN %s AND %s
		""", (self.name, from_date or "1900-01-01", to_date or "2100-12-31"), as_dict=True)
		
		return {
			"total_eggs": egg_production[0].total_eggs if egg_production[0].total_eggs else 0
		}

