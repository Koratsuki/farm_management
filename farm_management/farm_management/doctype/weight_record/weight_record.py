# Copyright (c) 2024, Farm Management Solutions and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, date

class WeightRecord(Document):
	def validate(self):
		"""Validate weight record before saving"""
		self.calculate_age()
		self.calculate_weight_gain()
		self.validate_weight()
	
	def calculate_age(self):
		"""Calculate age in days at time of weighing"""
		if self.pig and self.date:
			pig = frappe.get_doc("Pig", self.pig)
			if pig.birth_date:
				self.age_days = (self.date - pig.birth_date).days
	
	def calculate_weight_gain(self):
		"""Calculate weight gain since last weighing"""
		if not self.pig:
			return
		
		# Get previous weight record
		previous_records = frappe.get_all("Weight Record",
			filters={
				"pig": self.pig,
				"date": ["<", self.date],
				"name": ["!=", self.name]
			},
			fields=["weight", "date"],
			order_by="date desc",
			limit=1
		)
		
		if previous_records:
			previous_record = previous_records[0]
			self.weight_gain = self.weight - previous_record.weight
			
			# Calculate daily weight gain
			days_diff = (self.date - previous_record.date).days
			if days_diff > 0:
				self.daily_weight_gain = self.weight_gain / days_diff
	
	def validate_weight(self):
		"""Validate weight value"""
		if self.weight <= 0:
			frappe.throw("Weight must be greater than zero")
		
		# Check for unrealistic weight changes
		if self.weight_gain and abs(self.weight_gain) > 50:  # 50kg change seems unrealistic
			frappe.msgprint("Warning: Large weight change detected. Please verify the weight.")
	
	def on_submit(self):
		"""Actions to perform when record is submitted"""
		self.update_pig_weight()
	
	def update_pig_weight(self):
		"""Update current weight in pig record"""
		if self.pig:
			pig = frappe.get_doc("Pig", self.pig)
			pig.current_weight = self.weight
			pig.last_weight_date = self.date
			pig.save()
	
	def get_weight_trend(self):
		"""Get weight trend (gaining, losing, stable)"""
		if not self.weight_gain:
			return "No Previous Data"
		
		if self.weight_gain > 0.1:  # Gaining more than 100g
			return "Gaining"
		elif self.weight_gain < -0.1:  # Losing more than 100g
			return "Losing"
		else:
			return "Stable"
	
	def is_growth_rate_normal(self):
		"""Check if growth rate is within normal range"""
		if not self.daily_weight_gain or not self.age_days:
			return None
		
		# Normal daily weight gain varies by age
		if self.age_days < 60:  # Piglets (0-2 months)
			normal_range = (0.2, 0.5)  # 200-500g per day
		elif self.age_days < 120:  # Growing pigs (2-4 months)
			normal_range = (0.5, 0.8)  # 500-800g per day
		else:  # Finishing pigs (4+ months)
			normal_range = (0.6, 1.0)  # 600-1000g per day
		
		return normal_range[0] <= self.daily_weight_gain <= normal_range[1]
	
	def get_target_weight_for_age(self):
		"""Get target weight based on age"""
		if not self.age_days:
			return None
		
		# Rough target weights by age (can be breed-specific)
		if self.age_days < 30:  # 0-1 month
			return 5 + (self.age_days * 0.3)  # 5kg + 300g per day
		elif self.age_days < 60:  # 1-2 months
			return 14 + ((self.age_days - 30) * 0.4)  # 14kg + 400g per day
		elif self.age_days < 120:  # 2-4 months
			return 26 + ((self.age_days - 60) * 0.6)  # 26kg + 600g per day
		else:  # 4+ months
			return 62 + ((self.age_days - 120) * 0.7)  # 62kg + 700g per day
	
	def is_underweight(self):
		"""Check if pig is underweight for its age"""
		target_weight = self.get_target_weight_for_age()
		if target_weight:
			return self.weight < (target_weight * 0.85)  # 15% below target
		return False
	
	def is_overweight(self):
		"""Check if pig is overweight for its age"""
		target_weight = self.get_target_weight_for_age()
		if target_weight:
			return self.weight > (target_weight * 1.15)  # 15% above target
		return False

