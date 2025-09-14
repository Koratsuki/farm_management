# Copyright (c) 2024, Farm Management Solutions and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class FeedType(Document):
	def validate(self):
		"""Validate feed type data before saving"""
		self.validate_nutritional_content()
		self.validate_stock_levels()
	
	def validate_nutritional_content(self):
		"""Validate nutritional content percentages"""
		total_percentage = 0
		
		if self.protein_content:
			total_percentage += self.protein_content
		if self.fat_content:
			total_percentage += self.fat_content
		if self.fiber_content:
			total_percentage += self.fiber_content
		
		# Allow some flexibility as other components exist
		if total_percentage > 100:
			frappe.throw("Total of protein, fat, and fiber content cannot exceed 100%")
	
	def validate_stock_levels(self):
		"""Validate stock level settings"""
		if self.minimum_stock_level and self.reorder_level:
			if self.reorder_level < self.minimum_stock_level:
				frappe.throw("Reorder level should be greater than or equal to minimum stock level")
	
	def get_current_stock(self):
		"""Get current stock level from Stock Ledger Entry"""
		# This would integrate with ERPNext's stock system
		stock_qty = frappe.db.sql("""
			SELECT SUM(actual_qty) as stock_qty
			FROM `tabStock Ledger Entry`
			WHERE item_code = %s
		""", (self.name,), as_dict=True)
		
		if stock_qty and stock_qty[0].stock_qty:
			return stock_qty[0].stock_qty
		return 0
	
	def is_stock_low(self):
		"""Check if stock is below minimum level"""
		current_stock = self.get_current_stock()
		return current_stock < (self.minimum_stock_level or 0)
	
	def needs_reorder(self):
		"""Check if stock needs reordering"""
		current_stock = self.get_current_stock()
		return current_stock <= (self.reorder_level or 0)
	
	def get_feeding_cost_per_kg(self):
		"""Calculate feeding cost per kg"""
		if self.cost_per_unit and self.unit_of_measure:
			if self.unit_of_measure == "kg":
				return self.cost_per_unit
			elif self.unit_of_measure == "lbs":
				return self.cost_per_unit * 2.20462  # Convert to kg
			elif self.unit_of_measure == "tons":
				return self.cost_per_unit / 1000  # Convert to kg
		return 0
	
	def get_nutritional_summary(self):
		"""Get nutritional summary as dictionary"""
		return {
			"protein": self.protein_content or 0,
			"fat": self.fat_content or 0,
			"fiber": self.fiber_content or 0,
			"energy": self.energy_content or 0,
			"calcium": self.calcium_content or 0,
			"phosphorus": self.phosphorus_content or 0
		}
	
	def is_suitable_for_animal_type(self, animal_type):
		"""Check if feed is suitable for specific animal type"""
		return self.animal_type in [animal_type, "Both"]
	
	def is_expired(self, purchase_date):
		"""Check if feed is expired based on purchase date"""
		if not self.shelf_life_days or not purchase_date:
			return False
		
		from datetime import date, timedelta
		expiry_date = purchase_date + timedelta(days=self.shelf_life_days)
		return date.today() > expiry_date

