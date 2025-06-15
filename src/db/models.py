from typing import Optional, List, Dict, Any
from src.db.connection import DatabaseConnection

class ApplicantProfile:
    """Model for managing applicant profile data without encryption."""

    @staticmethod
    def create(db: DatabaseConnection, first_name: str, last_name: str, date_of_birth: str = None,
               address: str = None, phone_number: str = None) -> None:
        """Create new applicant profile with raw data.
        
        Args:
            db (DatabaseConnection): Database connection instance
            first_name (str): Applicant's first name
            last_name (str): Applicant's last name
            date_of_birth (str, optional): Date of birth in DD-MM-YYYY format
            address (str, optional): Home address
            phone_number (str, optional): Contact phone number
        """
        
        query = """
        INSERT INTO ApplicantProfile (first_name, last_name, date_of_birth, address, phone_number)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        db.execute_update(query, (first_name, last_name, date_of_birth, address, phone_number))
    
    @staticmethod
    def get_by_id(db: DatabaseConnection, applicant_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve applicant by ID.
        
        Args:
            db (DatabaseConnection): Database connection instance
            applicant_id (int): Unique applicant identifier
            
        Returns:
            Optional[Dict[str, Any]]: Applicant data or None if not found
        """

        query = "SELECT * FROM ApplicantProfile WHERE applicant_id = %s"
        result = db.execute_query(query, (applicant_id,))
        
        if not result:
            return None

        applicant = result[0]
        return {
            'applicant_id': applicant['applicant_id'],
            'first_name': applicant['first_name'],
            'last_name': applicant['last_name'],
            'date_of_birth': applicant['date_of_birth'],
            'address': applicant['address'],
            'phone_number': applicant['phone_number']
        }
    
    @staticmethod
    def get_all(db: DatabaseConnection) -> List[Dict[str, Any]]:
        """Retrieve all applicants ordered by ID.
        
        Args:
            db (DatabaseConnection): Database connection instance
            
        Returns:
            List[Dict[str, Any]]: List of all applicant records
        """

        query = "SELECT * FROM ApplicantProfile ORDER BY applicant_id"
        results = db.execute_query(query)
        
        applicants = []
        for data in results:
            applicant = {
                'applicant_id': data['applicant_id'],
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'date_of_birth': data['date_of_birth'],
                'address': data['address'],
                'phone_number': data['phone_number']
            }
            applicants.append(applicant)
        
        return applicants


class ApplicationDetail:
    """Model for managing application details and CV associations."""
    
    @staticmethod
    def create(db: DatabaseConnection, applicant_id: int, application_role: str = None, 
               cv_path: str = None) -> None:
        """Create new application detail record.
        
        Args:
            db (DatabaseConnection): Database connection instance
            applicant_id (int): ID of associated applicant
            application_role (str, optional): Job role applied for
            cv_path (str, optional): Path to CV file
        """

        query = """
        INSERT INTO ApplicationDetail (applicant_id, application_role, cv_path)
        VALUES (%s, %s, %s)
        """
        
        db.execute_update(query, (applicant_id, application_role, cv_path))
    
    @staticmethod
    def get_by_id(db: DatabaseConnection, detail_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve application detail by ID.
        
        Args:
            db (DatabaseConnection): Database connection instance
            detail_id (int): Unique detail identifier
            
        Returns:
            Optional[Dict[str, Any]]: Application detail data or None if not found
        """

        query = "SELECT * FROM ApplicationDetail WHERE detail_id = %s"
        result = db.execute_query(query, (detail_id,))
        
        if not result:
            return None

        detail = result[0]
        return {
            'detail_id': detail['detail_id'],
            'applicant_id': detail['applicant_id'],
            'application_role': detail['application_role'] if detail['application_role'] else "Unknown",
            'cv_path': detail['cv_path']
        }
    
    @staticmethod
    def get_applicant(db: DatabaseConnection, detail_id: int) -> Optional[Dict[str, Any]]:
        """Get associated applicant profile.
        
        Args:
            db (DatabaseConnection): Database connection instance
            applicant_id (int): Applicant identifier
            
        Returns:
            Optional[Dict[str, Any]]: Associated applicant data or None
        """

        query = """
        SELECT ap.applicant_id FROM ApplicantProfile ap
        JOIN ApplicationDetail ad ON ap.applicant_id = ad.applicant_id
        WHERE ad.detail_id = %s
        """
        result = db.execute_query(query, (detail_id,))

        if not result:
            return None
        
        result = result[0]['applicant_id']

        return ApplicantProfile.get_by_id(db, result)
    
    @staticmethod
    def get_applicant_id(db: DatabaseConnection, detail_id: int) -> Optional[Dict[str, Any]]:
        """Get associated applicant profile.
        
        Args:
            db (DatabaseConnection): Database connection instance
            applicant_id (int): Applicant identifier
            
        Returns:
            Optional[Dict[str, Any]]: Associated applicant data or None
        """

        query = """
        SELECT ap.applicant_id FROM ApplicantProfile ap
        JOIN ApplicationDetail ad ON ap.applicant_id = ad.applicant_id
        WHERE ad.detail_id = %s
        """
        result = db.execute_query(query, (detail_id,))

        if not result:
            return None

        return result[0]['applicant_id']