from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QPushButton, 
    QFrame, QScrollArea, QWidget, QComboBox, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import os

class SummaryDialog(QDialog):
    def __init__(self, profile: dict, detail_data: dict, parent=None):
        super().__init__(parent)
        self.setObjectName("SummaryDialog")
        self.setWindowTitle("CV Summary")
        self.setModal(True)

        if parent is not None:
            # ambil geometri parent
            pg = parent.geometry()
            self.setGeometry(pg.x(), pg.y(), pg.width(), pg.height())
        else:
            # fallback jika tanpa parent
            self.resize(700, 600)

        scroll_area = QScrollArea(self)
        scroll_area.setObjectName("summaryScrollArea")
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        content_widget = QWidget()
        scroll_area.setWidget(content_widget)
        
        main = QVBoxLayout(content_widget)
        main.setObjectName("summaryMainLayout")
        main.setSpacing(20)
        main.setContentsMargins(30, 30, 30, 20)

        title_label = QLabel("CV Summary")
        title_label.setObjectName("summaryTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main.addWidget(title_label)

        name = f"{profile.get('first_name','')} {profile.get('last_name','')}".strip()
        birthdate = profile.get('date_of_birth', '')
        address = profile.get('address', '')
        phone = profile.get('phone_number', '')
        
        header = QGroupBox("Personal Information")
        header.setObjectName("profileGroup")
        
        hlay = QVBoxLayout(header)
        hlay.setSpacing(12)
        hlay.setContentsMargins(15, 25, 15, 15)
        
        name_label = QLabel(f"👤 <b>{name}</b>")
        name_label.setObjectName("nameLabel")
        hlay.addWidget(name_label)
        
        info_items = [
            ("🎂", "Birthdate", birthdate),
            ("📍", "Address", address),
            ("📞", "Phone", phone)
        ]
        
        for icon, label, value in info_items:
            if value:
                info_label = QLabel(f"{icon} <b>{label}:</b> {value}")
                info_label.setObjectName("profileInfoLabel")
                hlay.addWidget(info_label)
        
        main.addWidget(header)

        summary = detail_data.get("Summary", {}).get("details", "")
        if summary:
            summary_group = QGroupBox("Summary")
            summary_group.setObjectName("summaryGroup")
            
            summary_layout = QVBoxLayout(summary_group)
            summary_layout.setSpacing(8)
            summary_layout.setContentsMargins(15, 25, 15, 15)
            
            summary_label = QLabel(summary)
            summary_label.setObjectName("summaryLabel")
            summary_label.setWordWrap(True)
            summary_layout.addWidget(summary_label)
            
            main.addWidget(summary_group)

        skills = detail_data.get("Skills", [])
        if skills:
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

        jobs = detail_data.get("Experience", [])
        if jobs:
            job_group = QGroupBox("Professional Experience")
            job_group.setObjectName("experienceGroup")
            
            job_v = QVBoxLayout(job_group)
            job_v.setSpacing(15)
            job_v.setContentsMargins(15, 25, 15, 15)
            
            for job in jobs:
                job_card = QFrame()
                job_card.setObjectName("jobCard")
                
                job_layout = QVBoxLayout(job_card)
                job_layout.setSpacing(6)
                
                role = job.get("role", "")
                interval = job.get("interval", "")
                details = job.get("details", "")
                
                if role:
                    title_label = QLabel(f"<b>{role}</b>")
                    title_label.setObjectName("jobTitleLabel")
                    job_layout.addWidget(title_label)
                
                if interval:
                    years_label = QLabel(f"📅 {interval}")
                    years_label.setObjectName("jobYearsLabel")
                    job_layout.addWidget(years_label)
                
                if details:
                    desc_label = QLabel(details)
                    desc_label.setObjectName("jobDescLabel")
                    desc_label.setWordWrap(True)
                    job_layout.addWidget(desc_label)
                
                job_v.addWidget(job_card)
            
            main.addWidget(job_group)

        edus = detail_data.get("Education", [])
        if edus:
            edu_group = QGroupBox("Education")
            edu_group.setObjectName("educationGroup")
            
            edu_v = QVBoxLayout(edu_group)
            edu_v.setSpacing(12)
            edu_v.setContentsMargins(15, 25, 15, 15)
            
            for edu in edus:
                edu_card = QFrame()
                edu_card.setObjectName("eduCard")
                
                edu_layout = QVBoxLayout(edu_card)
                edu_layout.setSpacing(6)
                
                degree = edu.get("degree", "")
                school = edu.get("school", "")
                year = edu.get("year", "")
                
                if degree:
                    program_label = QLabel(f"<b>{degree}</b>")
                    program_label.setObjectName("eduProgramLabel")
                    edu_layout.addWidget(program_label)
                
                if school:
                    inst_label = QLabel(f"🏫 {school}")
                    inst_label.setObjectName("eduInstLabel")
                    edu_layout.addWidget(inst_label)
                
                if year:
                    years_label = QLabel(f"📅 {year}")
                    years_label.setObjectName("eduYearsLabel")
                    edu_layout.addWidget(years_label)
                
                edu_v.addWidget(edu_card)
            
            main.addWidget(edu_group)

        dialog_layout = QVBoxLayout(self)
        dialog_layout.setContentsMargins(0, 0, 0, 20)
        dialog_layout.addWidget(scroll_area)

        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setObjectName("summaryButtonLayout")
        button_layout.setContentsMargins(30, 10, 30, 10)
        
        btn_close = QPushButton("Close")
        btn_close.setObjectName("summaryCloseButton")
        btn_close.clicked.connect(self.accept)
        
        button_layout.addStretch()
        button_layout.addWidget(btn_close)
        dialog_layout.addWidget(button_container)