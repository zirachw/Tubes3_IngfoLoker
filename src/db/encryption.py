from typing import List, Dict, Any
from src.db.connection import DatabaseConnection
from src.crypto.FF3 import FF3Cipher

class EncryptionManager:
    """Handles encryption and decryption of sensitive applicant data."""
    
    @staticmethod
    def encrypt_database(db: DatabaseConnection, cipher: FF3Cipher) -> None:
        """Encrypt all sensitive data in ApplicantProfile table.
        
        Args:
            db (DatabaseConnection): Database connection instance
            cipher (FF3Cipher): Encryption cipher instance
        """
        
        try:
            query = "SELECT * FROM ApplicantProfile"
            applicants = db.execute_query(query)
            
            if not applicants:
                print("[Error] - No applicants found")
                return

            for applicant in applicants:
                applicant_id = applicant['applicant_id']
                
                encrypted_first_name = cipher.encrypt(applicant['first_name'], field_type='name') if applicant['first_name'] else None
                encrypted_last_name = cipher.encrypt(applicant['last_name'], field_type='name') if applicant['last_name'] else None
                encrypted_date_of_birth = cipher.encrypt(applicant['date_of_birth'], field_type='date') if applicant['date_of_birth'] else None
                encrypted_address = cipher.encrypt(applicant['address'], field_type='address') if applicant['address'] else None
                encrypted_phone_number = cipher.encrypt(applicant['phone_number'], field_type='phone') if applicant['phone_number'] else None
                
                update_query = """
                UPDATE ApplicantProfile 
                SET first_name = %s, last_name = %s, date_of_birth = %s, 
                    address = %s, phone_number = %s 
                WHERE applicant_id = %s
                """
                
                db.execute_update(update_query, (
                    encrypted_first_name,
                    encrypted_last_name,
                    encrypted_date_of_birth,
                    encrypted_address,
                    encrypted_phone_number,
                    applicant_id
                ))
                
        except Exception as e:
            print(f"[Error] - During encryption: {e}")
    
    @staticmethod
    def decrypt_applicant_data(applicant_data: Dict[str, Any], cipher: FF3Cipher) -> Dict[str, Any]:
        """Decrypt applicant data for display purposes.
        
        Args:
            applicant_data (Dict[str, Any]): Encrypted applicant data
            cipher (FF3Cipher): Decryption cipher instance
            
        Returns:
            Dict[str, Any]: Decrypted applicant data
        """

        decrypted_data = applicant_data.copy()
        
        try:
            if applicant_data.get('first_name'):
                decrypted_data['first_name'] = cipher.decrypt(applicant_data['first_name'], field_type='name')
            
            if applicant_data.get('last_name'):
                decrypted_data['last_name'] = cipher.decrypt(applicant_data['last_name'], field_type='name')
            
            if applicant_data.get('date_of_birth'):
                decrypted_data['date_of_birth'] = cipher.decrypt(applicant_data['date_of_birth'], field_type='date')
            
            if applicant_data.get('address'):
                decrypted_data['address'] = cipher.decrypt(applicant_data['address'], field_type='address')
            
            if applicant_data.get('phone_number'):
                decrypted_data['phone_number'] = cipher.decrypt(applicant_data['phone_number'], field_type='phone')
                
        except Exception as e:
            print(f"[Error] - Decrypting data: {e}")
            
        return decrypted_data
    
    @staticmethod
    def get_decrypted_applicants(db: DatabaseConnection, cipher: FF3Cipher) -> List[Dict[str, Any]]:
        """Retrieve all applicants with decrypted data.
        
        Args:
            db (DatabaseConnection): Database connection instance
            cipher (FF3Cipher): Decryption cipher instance
            
        Returns:
            List[Dict[str, Any]]: List of decrypted applicant records
        """

        query = "SELECT * FROM ApplicantProfile ORDER BY applicant_id"
        encrypted_applicants = db.execute_query(query)
        
        decrypted_applicants = []
        for applicant in encrypted_applicants:
            decrypted_applicant = EncryptionManager.decrypt_applicant_data(applicant, cipher)
            decrypted_applicants.append(decrypted_applicant)
        
        return decrypted_applicants