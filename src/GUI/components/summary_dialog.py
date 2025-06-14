# File: src/GUI/components/summary_dialog.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QPushButton, 
    QFrame, QScrollArea, QWidget, QComboBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import os

class SummaryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SummaryDialog")
        self.setWindowTitle("CV Summary")
        self.resize(700, 600)
        self.setModal(True)

        scroll_area = QScrollArea(self)
        scroll_area.setObjectName("summaryScrollArea")
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        content_widget = QWidget()
        scroll_area.setWidget(content_widget)
        
        main = QVBoxLayout(content_widget)
        main.setSpacing(20)
        main.setContentsMargins(30, 30, 30, 20)

        title_label = QLabel("CV Summary")
        title_label.setObjectName("summaryTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main.addWidget(title_label)

        profile = {
            "name": "Farhan",
            "birthdate": "05-19-2025",
            "address": "Masjid Salman ITB",
            "phone": "0812 3456 7890"
        }
        
        header = QGroupBox("Personal Information")
        header.setObjectName("profileGroup")
        
        hlay = QVBoxLayout(header)
        hlay.setSpacing(12)
        hlay.setContentsMargins(15, 25, 15, 15)
        
        name_label = QLabel(f"👤 <b>{profile['name']}</b>")
        name_label.setObjectName("nameLabel")
        hlay.addWidget(name_label)
        
        info_items = [
            ("🎂", "Birthdate", profile['birthdate']),
            ("📍", "Address", profile['address']),
            ("📞", "Phone", profile['phone'])
        ]
        
        for icon, label, value in info_items:
            info_label = QLabel(f"{icon} <b>{label}:</b> {value}")
            info_label.setObjectName("profileInfoLabel")
            hlay.addWidget(info_label)
        
        main.addWidget(header)

        skills = ["React", "Express", "HTML", "JavaScript", "Python", "Node.js"]
        sk_group = QGroupBox("Technical Skills")
        sk_group.setObjectName("skillsGroup")

        sk_v = QVBoxLayout(sk_group)
        sk_v.setSpacing(8)
        sk_v.setContentsMargins(15, 25, 15, 15)

        for skill in skills:
            skill_label = QLabel(f"• {skill}")
            skill_label.setObjectName("skillLabel")
            skill_label.setContentsMargins(5, 2, 5, 2)
            sk_v.addWidget(skill_label)

        sk_v.addStretch()
        main.addWidget(sk_group)

        jobs = [
            ("CTO", "2003–2004", "TechCorp Inc.", "Led technology strategy and team of 15+ developers"),
            ("Lead Developer", "2005–2008", "Innova Solutions", "Architected scalable web applications using modern frameworks")
        ]
        
        job_group = QGroupBox("Professional Experience")
        job_group.setObjectName("experienceGroup")
        
        job_v = QVBoxLayout(job_group)
        job_v.setSpacing(15)
        job_v.setContentsMargins(15, 25, 15, 15)
        
        for title, years, company, description in jobs:
            job_card = QFrame()
            job_card.setObjectName("jobCard")
            
            job_layout = QVBoxLayout(job_card)
            job_layout.setSpacing(6)
            
            title_label = QLabel(f"<b>{title}</b> at <b>{company}</b>")
            title_label.setObjectName("jobTitleLabel")
            job_layout.addWidget(title_label)
            
            years_label = QLabel(f"📅 {years}")
            years_label.setObjectName("jobYearsLabel")
            job_layout.addWidget(years_label)
            
            desc_label = QLabel(description)
            desc_label.setObjectName("jobDescLabel")
            desc_label.setWordWrap(True)
            job_layout.addWidget(desc_label)
            
            job_v.addWidget(job_card)
        
        main.addWidget(job_group)

        edus = [
            ("Informatics Engineering", "Institut Teknologi Bandung", "2022–2026", "Bachelor's Degree")
        ]
        
        edu_group = QGroupBox("Education")
        edu_group.setObjectName("educationGroup")
        
        edu_v = QVBoxLayout(edu_group)
        edu_v.setSpacing(12)
        edu_v.setContentsMargins(15, 25, 15, 15)
        
        for program, institution, years, degree in edus:
            edu_card = QFrame()
            edu_card.setObjectName("eduCard")
            
            edu_layout = QVBoxLayout(edu_card)
            edu_layout.setSpacing(6)
            
            program_label = QLabel(f"<b>{program}</b> ({degree})")
            program_label.setObjectName("eduProgramLabel")
            edu_layout.addWidget(program_label)
            
            inst_label = QLabel(f"🏫 {institution}")
            inst_label.setObjectName("eduInstLabel")
            edu_layout.addWidget(inst_label)
            
            years_label = QLabel(f"📅 {years}")
            years_label.setObjectName("eduYearsLabel")
            edu_layout.addWidget(years_label)
            
            edu_v.addWidget(edu_card)
        
        main.addWidget(edu_group)

        dialog_layout = QVBoxLayout(self)
        dialog_layout.setContentsMargins(0, 0, 0, 20)
        dialog_layout.addWidget(scroll_area)

        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(30, 10, 30, 10)
        
        btn_close = QPushButton("Close")
        btn_close.setObjectName("summaryCloseButton")
        btn_close.clicked.connect(self.accept)
        
        button_layout.addStretch()
        button_layout.addWidget(btn_close)
        dialog_layout.addWidget(button_container)