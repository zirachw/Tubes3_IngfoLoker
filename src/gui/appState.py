import os
from src.db.connection import DatabaseConnection
from src.db.encryption import EncryptionManager
from src.utils.seeder import ApplicantSeeder
from src.db.manager import DataManager
from src.crypto.FF3 import FF3Cipher
from src.utils.regex import Summary
from src.utils.setup import SetupPDFData

class AppState:
    """Main state class that orchestrates the ATS setup workflow."""

    def __init__(self):
        """Initialize ATS components and configuration from environment variables."""

        self.db = DatabaseConnection()
        self.data_folder = os.getenv('DATA_FOLDER', 'data')
        self.data_manager = DataManager(self.db, self.data_folder)
        self.applicant_count = int(os.getenv('APPLICANT_COUNT', 10))
        self.enable_encryption = os.getenv('ENABLE_FF3', 'false').lower() == 'true'
        self.enable_demo = os.getenv('ENABLE_DEMO', 'false').lower() == 'true'

    def run(self):
        """Execute the complete ATS setup workflow.
        
        Workflow steps:
        1. Re-initialize database from init.sql (fresh start)
        2. Clear temporary files and seed applicant data
        3. Extract PDF content and determine job roles
        4. Bind PDFs to applicants in database
        5. Encrypt sensitive data if enabled
        """

        try:
            print("[Log] - Starting ATS setup...")
            
            # Re-initialize database to original state (prevents double encryption)
            if self.enable_demo:
                print("[Log] - Re-initializing database from init.sql...")
                self.db.initialize_database("database/init.sql")
            
            self.data_manager.clear_temp()
            # SetupPDFData().tidy()

            if not self.enable_demo:
                seeder = ApplicantSeeder(self.db, self.applicant_count)
                seeder.seed()
        
            self.data_manager.extract_pdf()
            
            if self.enable_encryption:
                print("[Log] - Encrypting sensitive data...")
                EncryptionManager.encrypt_database(self.db)
            else:
                print("[Log] - Encryption disabled - data remains in raw format")

            print("[Log] - ATS setup completed successfully!")

            texts = self.data_manager.get_extracted_texts('clean')

            print("[Log] - All operations completed successfully!")

            extracted_raw_texts = Summary.generate(self.data_manager.get_extracted_texts('raw'))
            self.data_manager.extracted_raw_texts = extracted_raw_texts

            Summary.export_to_json(extracted_raw_texts, os.path.join(self.data_folder, 'summary.json'))

        except Exception as e:
            print(f"[Error] - During setup: {e}")
            import traceback
            traceback.print_exc()
            print("[Error] - Setup failed, please check the logs for details.")
            raise

    def end(self):
        """Close the database connection and clean up resources."""
        
        try:
            self.data_manager.clear_temp()
            self.db.close()
            print("[Log] - Database connection closed successfully.")
        except Exception as e:
            print(f"[Error] - Closing database connection: {e}")