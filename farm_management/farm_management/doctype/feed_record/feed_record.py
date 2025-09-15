# Copyright (c) 2024, Farm Management Solutions and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, date

class FeedRecord(Document):
	def validate(self):
		"""Validate feed record before saving"""
		self.validate_animal_reference()
		self.calculate_total_cost()
		self.set_animal_count()
		self.validate_quantities()
	
	def validate_animal_reference(self):
		"""Ensure at least one animal reference is provided"""
		if not any([self.pig, self.poultry_batch]):
			frappe.throw("Please specify either a Pig or Poultry Batch")
		
		# Ensure only one animal reference is provided
		if self.pig and self.poultry_batch:
			frappe.throw("Please specify only one animal reference (Pig or Poultry Batch)")
	
	def calculate_total_cost(self):
		"""Calculate total cost based on quantity and cost per unit"""
		if self.quantity and self.cost_per_unit:
			self.total_cost = self.quantity * self.cost_per_unit
		elif self.quantity and self.feed_type:
			# Get cost from feed type if not specified
			feed_type = frappe.get_doc("Feed Type", self.feed_type)
			if feed_type.cost_per_unit:
				self.cost_per_unit = feed_type.cost_per_unit
				self.total_cost = self.quantity * self.cost_per_unit
	
	def set_animal_count(self):
		"""Set animal count based on the reference"""
		if self.pig:
			self.animal_count = 1
		elif self.poultry_batch:
			batch = frappe.get_doc("Poultry Batch", self.poultry_batch)
			self.animal_count = batch.current_count
	
	def validate_quantities(self):
		"""Validate quantity fields"""
		if self.quantity <= 0:
			frappe.throw("Quantity must be greater than zero")
		
		if self.wastage_quantity and self.wastage_quantity > self.quantity:
			frappe.throw("Wastage quantity cannot be greater than total quantity")
		
		if self.leftover_quantity and self.leftover_quantity > self.quantity:
			frappe.throw("Leftover quantity cannot be greater than total quantity")
	
	def on_submit(self):
		"""Actions to perform when record is submitted"""
		self.update_stock_ledger()
		self.update_animal_feed_consumption()
	
	def update_stock_ledger(self):
		"""Update stock ledger for feed consumption"""
		# This would integrate with ERPNext's stock system
		# Create stock ledger entry for feed consumption
		pass
	
	def update_animal_feed_consumption(self):
		"""Update feed consumption in animal records"""
		if self.poultry_batch:
			batch = frappe.get_doc("Poultry Batch", self.poultry_batch)
			# Update daily feed consumption average
			if self.animal_count > 0:
				daily_per_bird = self.quantity / self.animal_count
				batch.feed_consumption_daily = daily_per_bird
				batch.save()
	
	def get_feed_per_animal(self):
		"""Calculate feed quantity per animal"""
		if self.animal_count and self.animal_count > 0:
			return self.quantity / self.animal_count
		return 0
	
	def get_cost_per_animal(self):
		"""Calculate cost per animal"""
		if self.animal_count and self.animal_count > 0 and self.total_cost:
			return self.total_cost / self.animal_count
		return 0
	
	def get_wastage_percentage(self):
		"""Calculate wastage percentage"""
		if self.quantity > 0 and self.wastage_quantity:
			return (self.wastage_quantity / self.quantity) * 100
		return 0
	
	def get_consumption_efficiency(self):
		"""Calculate consumption efficiency (actual consumed vs provided)"""
		actual_consumed = self.quantity
		if self.leftover_quantity:
			actual_consumed -= self.leftover_quantity
		if self.wastage_quantity:
			actual_consumed -= self.wastage_quantity
		
		if self.quantity > 0:
			return (actual_consumed / self.quantity) * 100
		return 0
	
	def is_feed_suitable(self):
		"""Check if feed type is suitable for the animal"""
		if not self.feed_type:
			return True
		
		feed_type = frappe.get_doc("Feed Type", self.feed_type)
		
		if self.pig:
			return feed_type.is_suitable_for_animal_type("Pig")
		elif self.poultry_batch:
			return feed_type.is_suitable_for_animal_type("Poultry")
		
		return True
	
	def get_nutritional_intake(self):
		"""Calculate nutritional intake based on feed type"""
		if not self.feed_type:
			return {}
		
		feed_type = frappe.get_doc("Feed Type", self.feed_type)
		nutritional_summary = feed_type.get_nutritional_summary()
		
		# Calculate actual intake based on quantity
		intake = {}
		for nutrient, percentage in nutritional_summary.items():
			if percentage:
				intake[nutrient] = (self.quantity * percentage) / 100
		
		return intake

