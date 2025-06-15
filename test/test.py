#!/usr/bin/env python3
"""
Corrected debug script that properly compares the same data
"""

import os
from src.db.connection import DatabaseConnection
from src.crypto.FF3 import FF3Cipher
from src.db.models import ApplicationDetail
from src.db.encryption import EncryptionManager

def debug_corrected_flow():
    """Debug with correct data comparison."""
    
    print("=== CORRECTED DEBUG FLOW ===")
    
    db = DatabaseConnection()
    detail_id = 18
    
    # Method 1: Direct query for the applicant associated with detail_id 18
    print("Method 1: Direct query for applicant associated with detail_id 18")
    direct_query = """
    SELECT ap.* FROM ApplicantProfile ap
    JOIN ApplicationDetail ad ON ap.applicant_id = ad.applicant_id  
    WHERE ad.detail_id = %s
    """
    
    direct_result = db.execute_query(direct_query, (detail_id,))
    if direct_result:
        direct_applicant = direct_result[0]
        print(f"  applicant_id: {direct_applicant['applicant_id']}")
        print(f"  first_name: '{direct_applicant['first_name']}'")
        print(f"  last_name: '{direct_applicant['last_name']}'")
        print(f"  address: '{direct_applicant['address']}'")
        print(f"  phone_number: '{direct_applicant['phone_number']}'")
    else:
        print("  No applicant found for detail_id 18")
        return
    
    print()
    
    # Method 2: Using ApplicationDetail.get_applicant (same as your app)
    print("Method 2: Using ApplicationDetail.get_applicant (your app's method)")
    method_result = ApplicationDetail.get_applicant(db, detail_id)
    if method_result:
        print(f"  applicant_id: {method_result['applicant_id']}")
        print(f"  first_name: '{method_result['first_name']}'")
        print(f"  last_name: '{method_result['last_name']}'")
        print(f"  address: '{method_result['address']}'")
        print(f"  phone_number: '{method_result['phone_number']}'")
    else:
        print("  No applicant found")
        return
    
    print()
    
    # Method 3: Compare the two methods
    print("Method 3: Data consistency check")
    data_matches = (
        direct_applicant['applicant_id'] == method_result['applicant_id'] and
        direct_applicant['first_name'] == method_result['first_name'] and
        direct_applicant['last_name'] == method_result['last_name']
    )
    print(f"  Both methods return same data: {'✓' if data_matches else '✗'}")
    
    if not data_matches:
        print("  ERROR: The two methods return different data!")
        return
    
    print()
    
    # Method 4: Test encryption/decryption on the correct data
    print("Method 4: Encryption/Decryption test on correct data")
    cipher = FF3Cipher(os.getenv('FF3_KEY'), os.getenv('FF3_TWEAK'))
    
    # Test decryption of current database values
    print("  Decrypting current database values:")
    try:
        decrypted_first = cipher.decrypt(direct_applicant['first_name'], field_type='name')
        print(f"    first_name: '{direct_applicant['first_name']}' -> '{decrypted_first}'")
        
        decrypted_last = cipher.decrypt(direct_applicant['last_name'], field_type='name')
        print(f"    last_name: '{direct_applicant['last_name']}' -> '{decrypted_last}'")
        
        decrypted_address = cipher.decrypt(direct_applicant['address'], field_type='address')
        print(f"    address: '{direct_applicant['address']}' -> '{decrypted_address}'")
        
        decrypted_phone = cipher.decrypt(direct_applicant['phone_number'], field_type='phone')
        print(f"    phone: '{direct_applicant['phone_number']}' -> '{decrypted_phone}'")
        
    except Exception as e:
        print(f"    Decryption failed: {e}")
    
    print()
    
    # Method 5: Test EncryptionManager.decrypt_applicant_data
    print("Method 5: Testing EncryptionManager.decrypt_applicant_data")
    decrypted_data = EncryptionManager.decrypt_applicant_data(method_result)
    print(f"  Input: {method_result}")
    print(f"  Output: {decrypted_data}")
    
    # Check if the results match what we got from direct decryption
    if 'decrypted_first' in locals():
        manual_match = (
            decrypted_data['first_name'] == decrypted_first and
            decrypted_data['last_name'] == decrypted_last
        )
        print(f"  Matches manual decryption: {'✓' if manual_match else '✗'}")
    
    db.close()

def check_detail_to_applicant_mapping():
    """Show the mapping between detail_id and applicant_id."""
    
    print("\n=== DETAIL_ID to APPLICANT_ID MAPPING ===")
    
    db = DatabaseConnection()
    
    query = """
    SELECT ad.detail_id, ad.applicant_id, ap.first_name, ap.last_name
    FROM ApplicationDetail ad
    JOIN ApplicantProfile ap ON ad.applicant_id = ap.applicant_id
    ORDER BY ad.detail_id
    """
    
    results = db.execute_query(query)
    
    print("detail_id -> applicant_id (first_name, last_name)")
    print("-" * 50)
    for row in results:
        print(f"{row['detail_id']:8} -> {row['applicant_id']:11} ({row['first_name']}, {row['last_name']})")
    
    db.close()

if __name__ == "__main__":
    debug_corrected_flow()
    check_detail_to_applicant_mapping()