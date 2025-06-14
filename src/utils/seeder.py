import os
import random

from faker import Faker
from pathlib import Path
from src.db.models import ApplicantProfile
from src.db.connection import DatabaseConnection

class ApplicantSeeder:
    """Generates and seeds fake applicant data using Indonesian locale."""
    
    def __init__(self, db: DatabaseConnection, applicant_count: int) -> None:
        """Initialize seeder with database connection and target count.
        
        Args:
            db (DatabaseConnection): Database connection instance
            applicant_count (int): Number of applicants to generate
        """

        self.db = db
        self.applicant_count = applicant_count
        self.fake = Faker('id_ID')
        Faker.seed(42)
    
    def generate(self) -> dict:
        """Generate fake applicant data using Indonesian locale.
        
        Returns:
            dict: Dictionary containing fake applicant information
        """

        return {
            'first_name': self.fake.first_name(),
            'last_name': self.fake.last_name(),
            'date_of_birth': self.fake.date_of_birth(minimum_age=25, maximum_age=45).strftime("%d-%m-%Y"),
            'address': f"{self.fake.street_address()}, {self.fake.city()}",
            'phone_number': f"+62-{random.randint(800, 899)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
        }
    
    def get_pdf_files(self) -> list:
        """Get list of PDF files from data directory.
        
        Returns:
            list: List of PDF filenames found in data folder
        """

        data_path = Path("data")
        if not data_path.exists():
            return []
        
        return [pdf.name for pdf in data_path.glob("*.pdf")]
    
    def seed(self) -> None:
        """Seed database with generated fake applicant data.
        
        Clears existing data and creates new applicant records with raw data.
        """

        print("[Log] - Seeding applicant profiles...")
        
        self.db.clear_data()
        print("[Log] - Cleared existing data")
        
        pdf_files = self.get_pdf_files()
        print(f"[Log] - Found {len(pdf_files)} PDF files in data folder")
        
        for i in range(self.applicant_count):
            data = self.generate()
            
            ApplicantProfile.create(
                self.db,
                first_name=data['first_name'],
                last_name=data['last_name'],
                date_of_birth=data['date_of_birth'],
                address=data['address'],
                phone_number=data['phone_number']
            )
        
        total = self.db.execute_query("SELECT COUNT(*) as count FROM ApplicantProfile")[0]['count']
        print(f"[Log] - Created {total} applicants with raw data successfully!")