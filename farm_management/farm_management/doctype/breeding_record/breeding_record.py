# Copyright (c) 2024, Farm Management Solutions and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, date, timedelta

class BreedingRecord(Document):
	def validate(self):
		"""Validate breeding record before saving"""
		self.validate_animals()
		self.calculate_expected_farrowing_date()
		self.calculate_gestation_period()
		self.validate_piglet_counts()
		self.determine_breeding_success()
	
	def validate_animals(self):
		"""Validate sow and boar information"""
		if self.sow:
			sow = frappe.get_doc("Pig", self.sow)
			if sow.gender != "Female":
				frappe.throw("Sow must be a female pig")
		
		if self.boar:
			boar = frappe.get_doc("Pig", self.boar)
			if boar.gender not in ["Male", "Castrated Male"]:
				frappe.throw("Boar must be a male pig")
			if boar.gender == "Castrated Male":
				frappe.throw("Castrated males cannot be used for breeding")
	
	def calculate_expected_farrowing_date(self):
		"""Calculate expected farrowing date (114 days gestation)"""
		if self.breeding_date:
			self.expected_farrowing_date = self.breeding_date + timedelta(days=114)
	
	def calculate_gestation_period(self):
		"""Calculate actual gestation period if farrowing occurred"""
		if self.breeding_date and self.actual_farrowing_date:
			self.gestation_period = (self.actual_farrowing_date - self.breeding_date).days
	
	def validate_piglet_counts(self):
		"""Validate piglet count fields"""
		if self.total_piglets_born and self.live_piglets and self.stillborn_piglets:
			if (self.live_piglets + self.stillborn_piglets) != self.total_piglets_born:
				frappe.throw("Live piglets + Stillborn piglets must equal Total piglets born")
		
		# Auto-calculate if some fields are missing
		if self.live_piglets and self.stillborn_piglets and not self.total_piglets_born:
			self.total_piglets_born = self.live_piglets + self.stillborn_piglets
		elif self.total_piglets_born and self.live_piglets and not self.stillborn_piglets:
			self.stillborn_piglets = self.total_piglets_born - self.live_piglets
		elif self.total_piglets_born and self.stillborn_piglets and not self.live_piglets:
			self.live_piglets = self.total_piglets_born - self.stillborn_piglets
	
	def determine_breeding_success(self):
		"""Determine if breeding was successful"""
		if self.actual_farrowing_date and self.live_piglets and self.live_piglets > 0:
			self.breeding_success = 1
		elif self.actual_farrowing_date and (not self.live_piglets or self.live_piglets == 0):
			self.breeding_success = 0
	
	def on_submit(self):
		"""Actions to perform when record is submitted"""
		self.update_sow_status()
		self.create_piglet_records()
	
	def update_sow_status(self):
		"""Update sow breeding status"""
		if self.sow and self.pregnancy_confirmed:
			sow = frappe.get_doc("Pig", self.sow)
			if self.actual_farrowing_date:
				sow.breeding_status = "Lactating"
			else:
				sow.breeding_status = "Pregnant"
			sow.last_breeding_date = self.breeding_date
			sow.save()
	
	def create_piglet_records(self):
		"""Create individual pig records for live piglets"""
		if self.live_piglets and self.actual_farrowing_date:
			for i in range(self.live_piglets):
				piglet = frappe.new_doc("Pig")
				piglet.pig_id = f"{self.sow}-{self.actual_farrowing_date.strftime('%Y%m%d')}-{i+1:02d}"
				piglet.farm = self.farm
				piglet.birth_date = self.actual_farrowing_date
				piglet.acquisition_date = self.actual_farrowing_date
				piglet.source = "Born on Farm"
				piglet.sire = self.boar
				piglet.dam = self.sow
				piglet.purpose = "Meat Production"  # Default purpose
				
				# Set breed based on parents
				if self.sow:
					sow = frappe.get_doc("Pig", self.sow)
					piglet.breed = sow.breed
				
				# Set birth weight if available
				if self.average_birth_weight:
					piglet.birth_weight = self.average_birth_weight
					piglet.current_weight = self.average_birth_weight
				
				piglet.save()
	
	def get_survival_rate(self):
		"""Calculate piglet survival rate"""
		if not self.total_piglets_born or self.total_piglets_born == 0:
			return 0
		return (self.live_piglets / self.total_piglets_born) * 100
	
	def get_weaning_age(self):
		"""Calculate weaning age in days"""
		if self.actual_farrowing_date and self.weaning_date:
			return (self.weaning_date - self.actual_farrowing_date).days
		return None
	
	def is_overdue(self):
		"""Check if farrowing is overdue"""
		if not self.expected_farrowing_date or self.actual_farrowing_date:
			return False
		
		today = date.today()
		return today > self.expected_farrowing_date
	
	def days_until_farrowing(self):
		"""Calculate days until expected farrowing"""
		if not self.expected_farrowing_date or self.actual_farrowing_date:
			return None
		
		today = date.today()
		days = (self.expected_farrowing_date - today).days
		return days

