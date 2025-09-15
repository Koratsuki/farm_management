# Copyright (c) 2024, Farm Management Solutions and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, date

class Animal(Document):
	def validate(self):
		"""Validate animal data before saving"""
		self.validate_dates()
		self.validate_parents()
		self.calculate_age()
	
	def validate_dates(self):
		"""Validate date fields"""
		if self.birth_date and self.acquisition_date:
			if self.birth_date > self.acquisition_date:
				frappe.throw("Birth date cannot be after acquisition date")
		
		if self.birth_date and self.birth_date > date.today():
			frappe.throw("Birth date cannot be in the future")
	
	def validate_parents(self):
		"""Validate parent information"""
		if self.parent_male:
			parent_male = frappe.get_doc("Animal", self.parent_male)
			if parent_male.gender != "Male":
				frappe.throw("Parent (Male) must be a male animal")
		
		if self.parent_female:
			parent_female = frappe.get_doc("Animal", self.parent_female)
			if parent_female.gender != "Female":
				frappe.throw("Parent (Female) must be a female animal")
	
	def calculate_age(self):
		"""Calculate and set age in days"""
		if self.birth_date:
			today = date.today()
			age_days = (today - self.birth_date).days
			self.age_days = age_days
	
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
	
	def get_health_records(self):
		"""Get all health records for this animal"""
		return frappe.get_all("Health Record", 
			filters={"animal": self.name},
			fields=["*"],
			order_by="date desc"
		)
	
	def get_latest_weight(self):
		"""Get the latest weight record"""
		if self.animal_type == "Pig":
			weight_records = frappe.get_all("Weight Record",
				filters={"pig": self.name},
				fields=["weight", "date"],
				order_by="date desc",
				limit=1
			)
			if weight_records:
				return weight_records[0]
		return None
	
	def update_health_status(self, status, notes=None):
		"""Update health status and create health record"""
		self.health_status = status
		self.last_health_check = date.today()
		self.save()
		
		# Create health record
		health_record = frappe.new_doc("Health Record")
		health_record.animal = self.name
		health_record.farm = self.farm
		health_record.date = date.today()
		health_record.record_type = "Health Check"
		health_record.status = status
		if notes:
			health_record.notes = notes
		health_record.save()
		
		return health_record

