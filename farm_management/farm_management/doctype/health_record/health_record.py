# Copyright (c) 2024, Farm Management Solutions and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, date

class HealthRecord(Document):
	def validate(self):
		"""Validate health record before saving"""
		self.validate_animal_reference()
		self.validate_dates()
		self.set_default_quantity()
	
	def validate_animal_reference(self):
		"""Ensure at least one animal reference is provided"""
		if not any([self.animal, self.pig, self.poultry_batch]):
			frappe.throw("Please specify at least one animal reference (Animal, Pig, or Poultry Batch)")
		
		# Ensure only one animal reference is provided
		references = [self.animal, self.pig, self.poultry_batch]
		non_empty_refs = [ref for ref in references if ref]
		if len(non_empty_refs) > 1:
			frappe.throw("Please specify only one animal reference")
	
	def validate_dates(self):
		"""Validate date fields"""
		if self.date and self.date > date.today():
			frappe.throw("Health record date cannot be in the future")
		
		if self.follow_up_date and self.follow_up_date < self.date:
			frappe.throw("Follow-up date cannot be before the record date")
		
		if self.recovery_date and self.recovery_date < self.date:
			frappe.throw("Recovery date cannot be before the record date")
	
	def set_default_quantity(self):
		"""Set default quantity based on animal type"""
		if not self.quantity:
			if self.pig or self.animal:
				self.quantity = 1
			elif self.poultry_batch:
				# For poultry batch, default to 1 unless specified
				self.quantity = 1
	
	def on_submit(self):
		"""Actions to perform when record is submitted"""
		self.update_animal_health_status()
		self.create_follow_up_task()
	
	def update_animal_health_status(self):
		"""Update health status of the related animal"""
		if self.pig:
			pig = frappe.get_doc("Pig", self.pig)
			if self.record_type in ["Disease", "Injury", "Treatment"]:
				pig.health_status = "Sick"
			elif self.record_type == "Health Check" and self.status == "Recovered":
				pig.health_status = "Healthy"
			pig.last_health_check = self.date
			pig.save()
		
		elif self.poultry_batch:
			batch = frappe.get_doc("Poultry Batch", self.poultry_batch)
			if self.record_type in ["Disease", "Injury", "Treatment"]:
				batch.health_status = "Sick"
			elif self.record_type == "Health Check" and self.status == "Recovered":
				batch.health_status = "Healthy"
			batch.last_health_check = self.date
			batch.save()
		
		elif self.animal:
			animal = frappe.get_doc("Animal", self.animal)
			if self.record_type in ["Disease", "Injury", "Treatment"]:
				animal.health_status = "Sick"
			elif self.record_type == "Health Check" and self.status == "Recovered":
				animal.health_status = "Healthy"
			animal.last_health_check = self.date
			animal.save()
	
	def create_follow_up_task(self):
		"""Create follow-up task if follow-up date is specified"""
		if self.follow_up_date and self.follow_up_date > date.today():
			# Create a ToDo for follow-up
			todo = frappe.new_doc("ToDo")
			todo.description = f"Follow-up for {self.record_type}: {self.health_issue or 'Health Record'}"
			todo.date = self.follow_up_date
			todo.reference_type = "Health Record"
			todo.reference_name = self.name
			todo.assigned_by = frappe.session.user
			todo.save()
	
	def get_treatment_duration(self):
		"""Calculate treatment duration in days"""
		if self.date and self.recovery_date:
			return (self.recovery_date - self.date).days
		return None
	
	def is_follow_up_due(self):
		"""Check if follow-up is due"""
		if not self.follow_up_date:
			return False
		
		today = date.today()
		return today >= self.follow_up_date and self.status not in ["Recovered", "Dead"]
	
	def get_related_records(self):
		"""Get related health records for the same animal"""
		filters = {"name": ["!=", self.name]}
		
		if self.pig:
			filters["pig"] = self.pig
		elif self.poultry_batch:
			filters["poultry_batch"] = self.poultry_batch
		elif self.animal:
			filters["animal"] = self.animal
		
		return frappe.get_all("Health Record",
			filters=filters,
			fields=["*"],
			order_by="date desc"
		)
	
	def calculate_treatment_cost_per_animal(self):
		"""Calculate treatment cost per animal"""
		if self.treatment_cost and self.quantity and self.quantity > 0:
			return self.treatment_cost / self.quantity
		return self.treatment_cost or 0

