# Copyright (c) 2024, Farm Management Solutions and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class EggProductionRecord(Document):
	def validate(self):
		"""Validate egg production record before saving"""
		self.calculate_good_eggs()
		self.calculate_production_rate()
		self.validate_egg_counts()
	
	def calculate_good_eggs(self):
		"""Calculate good eggs count"""
		broken = self.broken_eggs or 0
		dirty = self.dirty_eggs or 0
		self.good_eggs = self.eggs_collected - broken - dirty
	
	def calculate_production_rate(self):
		"""Calculate production rate based on batch size"""
		if self.poultry_batch:
			batch = frappe.get_doc("Poultry Batch", self.poultry_batch)
			if batch.current_count > 0:
				self.production_rate = (self.eggs_collected / batch.current_count) * 100
	
	def validate_egg_counts(self):
		"""Validate egg count fields"""
		broken = self.broken_eggs or 0
		dirty = self.dirty_eggs or 0
		
		if (broken + dirty) > self.eggs_collected:
			frappe.throw("Sum of broken and dirty eggs cannot exceed total eggs collected")
		
		if self.eggs_collected < 0:
			frappe.throw("Eggs collected cannot be negative")
	
	def on_submit(self):
		"""Actions to perform when record is submitted"""
		self.update_batch_production_stats()
	
	def update_batch_production_stats(self):
		"""Update production statistics in the poultry batch"""
		if self.poultry_batch:
			# This could update running averages or totals in the batch
			pass
	
	def get_quality_percentage(self):
		"""Get egg quality percentage"""
		if self.eggs_collected == 0:
			return 0
		return (self.good_eggs / self.eggs_collected) * 100
	
	def get_breakage_percentage(self):
		"""Get egg breakage percentage"""
		if self.eggs_collected == 0:
			return 0
		broken = self.broken_eggs or 0
		return (broken / self.eggs_collected) * 100

