# Copyright (c) 2024, Farm Management Solutions and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, date, timedelta

class Pig(Document):
	def validate(self):
		"""Validate pig data before saving"""
		self.validate_dates()
		self.validate_parents()
		self.validate_breeding_info()
		self.calculate_age()
		self.set_expected_slaughter_date()
	
	def validate_dates(self):
		"""Validate date fields"""
		if self.birth_date and self.acquisition_date:
			if self.birth_date > self.acquisition_date:
				frappe.throw("Birth date cannot be after acquisition date")
		
		if self.birth_date and self.birth_date > date.today():
			frappe.throw("Birth date cannot be in the future")
		
		if self.last_breeding_date and self.last_breeding_date > date.today():
			frappe.throw("Last breeding date cannot be in the future")
	
	def validate_parents(self):
		"""Validate parent information"""
		if self.sire:
			sire = frappe.get_doc("Pig", self.sire)
			if sire.gender not in ["Male", "Castrated Male"]:
				frappe.throw("Sire must be a male pig")
		
		if self.dam:
			dam = frappe.get_doc("Pig", self.dam)
			if dam.gender != "Female":
				frappe.throw("Dam must be a female pig")
	
	def validate_breeding_info(self):
		"""Validate breeding information"""
		if self.is_breeding_pig and self.gender == "Castrated Male":
			frappe.throw("Castrated males cannot be breeding pigs")
		
		if self.breeding_status == "Pregnant" and self.gender != "Female":
			frappe.throw("Only female pigs can be pregnant")
		
		if self.breeding_status == "Lactating" and self.gender != "Female":
			frappe.throw("Only female pigs can be lactating")
	
	def calculate_age(self):
		"""Calculate and set age in days"""
		if self.birth_date:
			today = date.today()
			age_days = (today - self.birth_date).days
			self.age_days = age_days
	
	def set_expected_slaughter_date(self):
		"""Set expected slaughter date for meat production pigs"""
		if (self.purpose == "Meat Production" and self.birth_date and 
			not self.expected_slaughter_date and not self.is_breeding_pig):
			# Typical slaughter age is 6 months (180 days)
			slaughter_date = self.birth_date + timedelta(days=180)
			self.expected_slaughter_date = slaughter_date
	
	def get_age_string(self):
		"""Get formatted age string"""
		if not self.birth_date:
			return "Unknown"
		
		today = date.today()
		age_days = (today - self.birth_date).days
		
		if age_days < 30:
			return f"{age_days} days"
		elif age_days < 365:
			months = age_days // 30
			return f"{months} months"
		else:
			years = age_days // 365
			remaining_months = (age_days % 365) // 30
			if remaining_months > 0:
				return f"{years} years, {remaining_months} months"
			else:
				return f"{years} years"
	
	def get_weight_records(self):
		"""Get all weight records for this pig"""
		return frappe.get_all("Weight Record",
			filters={"pig": self.name},
			fields=["*"],
			order_by="date desc"
		)
	
	def get_latest_weight(self):
		"""Get the latest weight record"""
		weight_records = self.get_weight_records()
		if weight_records:
			latest = weight_records[0]
			self.current_weight = latest.weight
			self.last_weight_date = latest.date
			return latest
		return None
	
	def get_breeding_records(self):
		"""Get all breeding records for this pig"""
		return frappe.get_all("Breeding Record",
			filters={"pig": self.name},
			fields=["*"],
			order_by="breeding_date desc"
		)
	
	def get_offspring_count(self):
		"""Get count of offspring"""
		if self.gender == "Male":
			return frappe.db.count("Pig", {"sire": self.name})
		elif self.gender == "Female":
			return frappe.db.count("Pig", {"dam": self.name})
		return 0
	
	def calculate_daily_weight_gain(self, days=30):
		"""Calculate average daily weight gain over specified period"""
		weight_records = self.get_weight_records()
		if len(weight_records) < 2:
			return 0
		
		# Get records within the specified period
		recent_records = []
		cutoff_date = date.today() - timedelta(days=days)
		
		for record in weight_records:
			if record.date >= cutoff_date:
				recent_records.append(record)
		
		if len(recent_records) < 2:
			recent_records = weight_records[:2]  # Use last 2 records
		
		if len(recent_records) >= 2:
			latest = recent_records[0]
			earliest = recent_records[-1]
			
			weight_diff = latest.weight - earliest.weight
			days_diff = (latest.date - earliest.date).days
			
			if days_diff > 0:
				return weight_diff / days_diff
		
		return 0
	
	def is_ready_for_breeding(self):
		"""Check if pig is ready for breeding"""
		if not self.is_breeding_pig or self.health_status != "Healthy":
			return False
		
		if self.gender == "Female":
			# Sows typically ready at 8 months and 120kg
			age_months = self.get_age_in_months()
			return age_months >= 8 and (self.current_weight or 0) >= 120
		
		elif self.gender == "Male":
			# Boars typically ready at 8 months and 140kg
			age_months = self.get_age_in_months()
			return age_months >= 8 and (self.current_weight or 0) >= 140
		
		return False
	
	def get_age_in_months(self):
		"""Get age in months"""
		if not self.birth_date:
			return 0
		
		today = date.today()
		age_days = (today - self.birth_date).days
		return age_days // 30
	
	def update_weight(self, weight, date=None, notes=None):
		"""Update pig weight and create weight record"""
		if not date:
			date = date.today()
		
		self.current_weight = weight
		self.last_weight_date = date
		self.save()
		
		# Create weight record
		weight_record = frappe.new_doc("Weight Record")
		weight_record.pig = self.name
		weight_record.farm = self.farm
		weight_record.date = date
		weight_record.weight = weight
		if notes:
			weight_record.notes = notes
		weight_record.save()
		
		return weight_record

