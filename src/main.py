import os
from src.db.connection import DatabaseConnection
from src.db.encryption import EncryptionManager
from src.utils.seeder import ApplicantSeeder
from src.utils.data import DataManager
from src.crypto.FF3 import FF3Cipher

class Main:
    """Main application class that orchestrates the ATS setup workflow."""

    def __init__(self):
        """Initialize ATS components and configuration from environment variables."""

        self.db = DatabaseConnection()
        self.data_folder = os.getenv('DATA_FOLDER', 'data')
        self.data_manager = DataManager(self.db, self.data_folder)
        self.applicant_count = int(os.getenv('APPLICANT_COUNT', 10))
        self.enable_encryption = os.getenv('ENABLE_FF3', 'false').lower() == 'true'
        self.cipher = FF3Cipher(os.getenv('FF3_KEY'), os.getenv('FF3_TWEAK')) if self.enable_encryption else None

    def run(self):
        """Execute the complete ATS setup workflow.
        
        Workflow steps:
        1. Clear temporary files and seed applicant data
        2. Extract PDF content and determine job roles
        3. Bind PDFs to applicants in database
        4. Encrypt sensitive data if enabled
        """

        try:
            print("[Log] - Starting ATS setup...")
            
            self.data_manager.clear_temp()
            seeder = ApplicantSeeder(self.db, self.applicant_count)
            seeder.seed()
        
            self.data_manager.extract_pdf()
            self.data_manager.bind_pdf()
            
            if self.enable_encryption and self.cipher:
                print("[Log] - Encrypting sensitive data...")
                EncryptionManager.encrypt_database(self.db, self.cipher)
            else:
                print("[Log] - Encryption disabled - data remains in raw format")

            print("[Log] - ATS setup completed successfully!")

            texts = DataManager.get_extracted_texts()

            # Returns list of strings, each containing one txt file's content
            for i, content in enumerate(texts):
                print(f"File {i+1}: {len(content)} characters")
            
        except Exception as e:
            print(f"[Error] - During setup: {e}")
            raise
        
        finally:

            print("[Option] - Enter any key to clean up temporary files and close the database connection...")
            input()
            try:
                self.data_manager.clear_temp()
                self.db.close()
                print("[Log] - Cleanup completed")

            except Exception as cleanup_error:
                print(f"[Warning] - Cleanup error: {cleanup_error}")

if __name__ == "__main__":
    main = Main()
    main.run()