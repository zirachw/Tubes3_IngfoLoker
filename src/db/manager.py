import os
import shutil
import fitz
import random
from pathlib import Path
from typing import Dict, Optional

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
        self.enable_save = os.getenv('ENABLE_SAVE', 'false').lower() == 'true'
        self.extracted_raw_texts = {}    # Dict[int, str] - detail_id -> raw_text
        self.extracted_clean_texts = {}  # Dict[int, str] - detail_id -> clean_text

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
            return random.choice(self.fallback_roles)
        
        first_line = raw_text.split('\n')[0].strip()
        
        if not first_line:
            return random.choice(self.fallback_roles)
        
        allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,;:!?/-+()%@\'"& ')
        filtered_first_line = ''.join(char for char in first_line if char in allowed_chars)
        filtered_first_line = ' '.join(filtered_first_line.split())
        
        if not filtered_first_line:
            return random.choice(self.fallback_roles)
        
        return filtered_first_line
    
    def bind_pdf(self) -> None:
        """Bind text from all PDF files and determine job roles.
        
        Populates roles list and extracted text dictionaries mapped by detail_id.
        """
        
        data_path = Path(self.data_folder)
        if not data_path.exists():
            print("[Error] - Data folder does not exist")
            return
            
        if not self.pdf_files:
            print("[Error] - No PDF files found")
            return
        
        if self.enable_save:
            temp_dir = Path("temp")
            raw_dir = Path("temp/raw")
            clean_dir = Path("temp/clean")

            temp_dir.mkdir(exist_ok=True)
            raw_dir.mkdir(exist_ok=True)
            clean_dir.mkdir(exist_ok=True)
        
        print(f"[Log] - Found {len(self.pdf_files)} PDF files")
        
        for idx, pdf_file in enumerate(self.pdf_files):
            pdf_path = data_path / pdf_file

            try:
                with fitz.open(pdf_path) as doc:
                    full_text = ""
                    for page in doc:
                        full_text += page.get_text()
                    
                    role_display = self.extract_first_line_role(full_text)
                    applicant = random.choice(ApplicantProfile.get_all(self.db))
                    role = role_display if role_display else random.choice(["Software Engineer", 
                                                                            "Data Scientist", 
                                                                            "Product Manager", 
                                                                            "UX Designer", 
                                                                            "Business Analyst"])
                    
                    ApplicationDetail.create(
                        self.db,
                        applicant_id=applicant['applicant_id'],
                        application_role=role,
                        cv_path=pdf_file
                    )

                filtered_text = self.filter_text(full_text)
                self.extracted_raw_texts[idx + 1] = full_text
                self.extracted_clean_texts[idx + 1] = filtered_text

                if self.enable_save:
                    pdf_name = pdf_file.rsplit('.', 1)[0]
                    raw_output = raw_dir / f"{pdf_name}.txt"
                    clean_output = clean_dir / f"{pdf_name}.txt"
                    
                    try:
                        with open(raw_output, 'w', encoding='utf-8') as f:
                            f.write(full_text)
                        print(f"[Log] - Saved raw text: {pdf_file} -> raw/{pdf_name}.txt ({len(full_text)} chars)")
                    except Exception as file_error:
                        print(f"[Error] - Saving raw text {raw_output}: {file_error}")
                    
                    try:
                        with open(clean_output, 'w', encoding='utf-8') as f:
                            f.write(filtered_text)
                        print(f"[Log] - Saved clean text: {pdf_file} -> clean/{pdf_name}.txt ({len(filtered_text)} chars)")
                    except Exception as file_error:
                        print(f"[Error] - Saving clean text {clean_output}: {file_error}")
                
            except Exception as e:
                print(f"[Error] - Extracting {pdf_file}: {e}")
                self.extracted_raw_texts[idx + 1] = ""
                self.extracted_clean_texts[idx + 1] = ""

    def get_extracted_texts(self, text_type: str) -> Dict[int, str]:
        """Get all extracted text content mapped by detail_id.
        
        Args:
            text_type (str): Type of text to retrieve - "raw" or "clean"
            
        Returns:
            Dict[int, str]: Dictionary mapping detail_id to extracted text content
        """

        if text_type == "raw":
            return self.extracted_raw_texts
        
        elif text_type == "clean":
            return self.extracted_clean_texts
        
        else:
            raise ValueError("text_type must be 'raw' or 'clean'")
        
    def get_cv_path(self, detail_id: int) -> Optional[str]:
        """Retrieve CV file path by detail ID.
        
        Args:
            db (DatabaseConnection): Database connection instance
            detail_id (int): Unique detail identifier
            
        Returns:
            Optional[str]: CV file path or None if not found
        """

        query = "SELECT cv_path FROM ApplicationDetail WHERE detail_id = %s"
        result = self.db.execute_query(query, (detail_id,))
        
        if not result:
            return None
        
        return result[0]['cv_path']
        
    def clear_temp(self):
        """Remove temporary extraction directory and all contents."""

        temp_dir = Path("temp")
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            print("[Log] - Cleared temporary files (temp/ directory)")