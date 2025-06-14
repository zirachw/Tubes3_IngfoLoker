import os
import shutil
import fitz
import random
from pathlib import Path
from typing import List

from src.db.connection import DatabaseConnection
from src.db.models import ApplicantProfile, ApplicationDetail

class DataManager:
    """Manages PDF extraction, text filtering, and database binding operations."""

    def __init__(self, db: DatabaseConnection, data_folder: str):
        """Initialize DataManager with database and file paths.
        
        Args:
            db (DatabaseConnection): Database connection instance
            data_folder (str): Path to folder containing PDF files
        """

        self.db = db
        self.data_folder = data_folder
        self.pdf_files = self.get_pdf_files()
        self.roles = []
        self.fallback_roles = ["Software Engineer", "Data Scientist", "Product Manager",
                               "UX Designer", "DevOps Engineer", "Project Manager", "Business Analyst"]
    
    def get_pdf_files(self) -> list:
        """Get list of PDF files from data folder.
        
        Returns:
            list: List of PDF filenames found in data folder
        """

        data_path = Path(self.data_folder)
        if not data_path.exists():
            return []
        
        return [pdf.name for pdf in data_path.glob("*.pdf")]

    def filter_text(self, text: str) -> str:
        """Filter text to keep only professional characters and normalize spacing.
        
        Args:
            text (str): Raw text input
            
        Returns:
            str: Filtered and normalized text
        """

        text = text.replace('\n', ' ').replace('\t', ' ')
        text = text.lower()
        
        allowed_chars = set('abcdefghijklmnopqrstuvwxyz0123456789.,;:!?/-+()%@\'"& ')
        filtered_text = ''.join(char for char in text if char in allowed_chars)
        filtered_text = ' '.join(filtered_text.split())
        
        return filtered_text

    def extract_first_line_role(self, raw_text: str) -> str:
        """Extract job role from the first line of PDF text.
        
        Args:
            raw_text (str): Raw text extracted from PDF
            
        Returns:
            str: Extracted role or fallback role if extraction fails
        """

        if not raw_text.strip():
            return self.fallback_roles[random.randint(0, len(self.fallback_roles) - 1)]
        
        first_line = raw_text.split('\n')[0].strip()
        
        if not first_line:
            return self.fallback_roles[random.randint(0, len(self.fallback_roles) - 1)]
        
        allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,;:!?/-+()%@\'"& ')
        filtered_first_line = ''.join(char for char in first_line if char in allowed_chars)
        filtered_first_line = ' '.join(filtered_first_line.split())
        
        if not filtered_first_line:
            return self.fallback_roles[random.randint(0, len(self.fallback_roles) - 1)]
        
        return filtered_first_line
    
    def extract_pdf(self) -> None:
        """Extract text from all PDF files and determine job roles.
        
        Creates temporary text files with filtered content and populates roles list.
        """

        temp_dir = Path("temp/raw")
    
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        
        temp_dir.mkdir(parents=True, exist_ok=True)
        data_path = Path(self.data_folder)

        if not data_path.exists():
            print("[Error] - Data folder does not exist")
            return

        if not self.pdf_files:
            print("[Error] - No PDF files found")
            return
        
        print(f"[Log] - Found {len(self.pdf_files)} PDF files")

        for pdf_file in self.pdf_files:
            pdf_path = data_path / pdf_file

            try:
                with fitz.open(pdf_path) as doc:
                    full_text = ""
                    for page in doc:
                        full_text += page.get_text()

                    role_display = self.extract_first_line_role(full_text)
                    self.roles.append(role_display)
                    filtered_text = self.filter_text(full_text)

                pdf_name = Path(pdf_file).stem
                output_file = temp_dir / f"{pdf_name}.txt"
                
                try:
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(filtered_text)
                    print(f"[Log] - Extracted {pdf_file} -> {pdf_name}.txt")

                except Exception as file_error:
                    print(f"[Error] - Saving {output_file}: {file_error}")
                
            except Exception as e:
                print(f"[Error] - Extracting {pdf_file}: {e}")
                self.roles.append("error")

    def bind_pdf(self) -> None:
        """Bind extracted PDF files to random applicants in database.
        
        Creates ApplicationDetail records linking PDFs to applicants with extracted roles.
        """

        if not self.pdf_files:
            print("[Error] - No PDF files found")
            return
        
        if not self.roles:
            print("[Error] - No roles found")
            return
        
        applicants = ApplicantProfile.get_all(self.db)

        if not applicants:
            print("[Error] - No applicants found")
            return
        
        print(f"[Log] - Binding {len(self.pdf_files)} PDFs to {len(applicants)} applicants")
        
        for idx, pdf_file in enumerate(self.pdf_files):
            applicant = applicants[random.randint(0, len(applicants) - 1)]
            role = self.roles[idx] if idx < len(self.roles) else self.fallback_roles[random.randint(0, len(self.fallback_roles) - 1)]
            
            ApplicationDetail.create(
                self.db,
                applicant_id=applicant['applicant_id'],
                application_role=role,
                cv_path=str(Path(self.data_folder) / pdf_file)
            )
            
            full_name = f"{applicant['first_name']} {applicant['last_name']}"
            print(f"[Log] - Bound {pdf_file} (role: '{role}') to {full_name} (ID: {applicant['applicant_id']})")

    def clear_temp(self) -> None:
        """Remove temporary extraction directory and all contents."""

        temp_dir = Path("temp/raw")
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            Path("temp").rmdir()
            print("[Log] - Removed temp directory")