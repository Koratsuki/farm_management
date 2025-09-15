# Copyright (c) 2024, Farm Management Solutions and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, date, timedelta

class PoultryBatch(Document):
	def validate(self):
		"""Validate poultry batch data before saving"""
		self.validate_counts()
		self.calculate_mortality_rate()
		self.validate_dates()
		self.set_expected_laying_start()
	
	def validate_counts(self):
		"""Validate count fields"""
		if self.current_count > self.initial_count:
			frappe.throw("Current count cannot be greater than initial count")
		
		if self.mortality_count and self.mortality_count > self.initial_count:
			frappe.throw("Mortality count cannot be greater than initial count")
		
		# Auto-calculate mortality count if not provided
		if not self.mortality_count:
			self.mortality_count = self.initial_count - self.current_count
	
	def calculate_mortality_rate(self):
		"""Calculate mortality rate percentage"""
		if self.initial_count and self.mortality_count:
			self.mortality_rate = (self.mortality_count / self.initial_count) * 100
	
	def validate_dates(self):
		"""Validate date fields"""
		if self.hatch_date and self.acquisition_date:
			if self.hatch_date > self.acquisition_date:
				frappe.throw("Hatch date cannot be after acquisition date")
	
	def set_expected_laying_start(self):
		"""Set expected laying start date for layers"""
		if self.batch_type == "Layers" and self.hatch_date and not self.expected_laying_start:
			# Typically layers start laying at 18-20 weeks
			laying_start = self.hatch_date + timedelta(weeks=19)
			self.expected_laying_start = laying_start
	
	def get_age_in_weeks(self):
		"""Get current age of the batch in weeks"""
		if not self.hatch_date:
			return 0
		
		today = date.today()
		age_days = (today - self.hatch_date).days
		return age_days // 7
	
	def get_production_records(self, from_date=None, to_date=None):
		"""Get egg production records for this batch"""
		filters = {"poultry_batch": self.name}
		if from_date:
			filters["date"] = [">=", from_date]
		if to_date:
			filters["date"] = ["<=", to_date]
		
		return frappe.get_all("Egg Production Record",
			filters=filters,
			fields=["*"],
			order_by="date desc"
		)
	
	def get_total_egg_production(self, from_date=None, to_date=None):
		"""Get total egg production for this batch"""
		filters = {"poultry_batch": self.name}
		if from_date:
			filters["date"] = [">=", from_date]
		if to_date:
			filters["date"] = ["<=", to_date]
		
		result = frappe.db.sql("""
			SELECT SUM(eggs_collected) as total_eggs,
				   AVG(eggs_collected) as avg_daily_eggs
			FROM `tabEgg Production Record`
			WHERE poultry_batch = %s
			AND date BETWEEN %s AND %s
		""", (self.name, from_date or "1900-01-01", to_date or "2100-12-31"), as_dict=True)
		
		if result and result[0]:
			return {
				"total_eggs": result[0].total_eggs or 0,
				"average_daily": result[0].avg_daily_eggs or 0
			}
		return {"total_eggs": 0, "average_daily": 0}
	
	def update_mortality(self, dead_count, reason=None):
		"""Update mortality count and create mortality record"""
		self.mortality_count += dead_count
		self.current_count -= dead_count
		self.calculate_mortality_rate()
		self.save()
		
		# Create mortality record
		mortality_record = frappe.new_doc("Health Record")
		mortality_record.farm = self.farm
		mortality_record.poultry_batch = self.name
		mortality_record.date = date.today()
		mortality_record.record_type = "Mortality"
		mortality_record.quantity = dead_count
		if reason:
			mortality_record.notes = f"Mortality reason: {reason}"
		mortality_record.save()
		
		return mortality_record
	
	def get_feed_consumption_summary(self, from_date=None, to_date=None):
		"""Get feed consumption summary for this batch"""
		filters = {"poultry_batch": self.name}
		if from_date:
			filters["date"] = [">=", from_date]
		if to_date:
			filters["date"] = ["<=", to_date]
		
		result = frappe.db.sql("""
			SELECT SUM(quantity) as total_feed,
				   AVG(quantity) as avg_daily_feed
			FROM `tabFeed Record`
			WHERE poultry_batch = %s
			AND date BETWEEN %s AND %s
		""", (self.name, from_date or "1900-01-01", to_date or "2100-12-31"), as_dict=True)
		
		if result and result[0]:
			return {
				"total_feed": result[0].total_feed or 0,
				"average_daily": result[0].avg_daily_feed or 0,
				"feed_per_bird": (result[0].avg_daily_feed or 0) / self.current_count if self.current_count > 0 else 0
			}
		return {"total_feed": 0, "average_daily": 0, "feed_per_bird": 0}

