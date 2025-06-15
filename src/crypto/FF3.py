import logging
import math
import string
from typing import Dict, Union, Optional

from src.crypto.AES import AESCipher

logger = logging.getLogger(__name__)

class FF3Cipher:
    """FF3 (Format Preserving Encryption) cipher implementing the NIST-approved FPE algorithm.

    FF3 is a Feistel-based format-preserving encryption algorithm that encrypts data while
    maintaining the original format and length.FF3 ensures encrypted data conforms to the 
    same character set and length constraints as the input.

    The algorithm uses a 4-round Feistel network where:
    1. Input is split into left (A) and right (B) halves
    2. Each round applies a round function F(tweak, key, half) using AES encryption
    3. The halves are swapped and the process repeats for 8 total rounds
    4. Output maintains the exact format of the input

    Components:
    - Key: 128/192/256-bit AES key used for the underlying encryption in each round
    - Tweak: 56 or 64-bit value providing domain separation and ensuring different 
      ciphertexts for the same plaintext in different contexts
    - Radix: Base of the numeral system (2-256) determining the character alphabet size

    The implementation includes pre-configured field types optimized for common database
    columns with appropriate character sets and length constraints.
    """
    
    # FF3 Algorithm Constants
    NUM_ROUNDS = 8
    BLOCK_SIZE = 16                     # ECB Mode aes.BlockSize
    TWEAK_LEN = 8                       # Original FF3 tweak length
    TWEAK_LEN_NEW = 7                   # FF3-1 tweak length
    HALF_TWEAK_LEN = TWEAK_LEN // 2
    
    # Domain and Radix Limits
    DOMAIN_MIN = 1_000_000              # 1M required in FF3-1
    RADIX_MAX = 256                     # Support 8-bit alphabets for now
    
    # Base62 Alphabet
    BASE62 = string.digits + string.ascii_lowercase + string.ascii_uppercase
    BASE62_LEN = len(BASE62)

    # Database field type configurations
    FIELD_CONFIGS = {
        'name': {
            'radix': 62,    # Letters only (a-z, A-Z) = 26 + 26 = 52
            'min_len': 1,   # Allow short names like "J"
            'max_len': 50,  # VARCHAR(50) limit
            'alphabet': string.ascii_lowercase + string.ascii_uppercase + string.digits
        },
        'phone': {
            'radix': 15,    # Digits + phone symbols: 0-9, +, -, space, ( )
            'min_len': 6,   # Security minimum
            'max_len': 20,  # VARCHAR(20) limit  
            'alphabet': string.digits + '+- ()'  # International phone format
        },
        'date': {
            'radix': 11,    # Digits + dash for date format (YYYY-MM-DD)
            'min_len': 8,   # Minimum date length
            'max_len': 10,  # VARCHAR(10) limit
            'alphabet': string.digits + '-'  # Digits and dash
        },
        'address': {
            'radix': 72,
            'min_len': 1,
            'max_len': 255,
            'alphabet': string.digits + string.ascii_lowercase + string.ascii_uppercase + " .,-'#/()&"
        }
    }

    def __init__(self, key: str, tweak: str, radix: int = 10) -> None:
        """Initialize FF3Cipher with key and tweak.
        
        Args:
            key (str): AES key (hex string)
            tweak (str): FF3 tweak (hex string) 
            radix (int): Default radix for basic operations (when no field_type specified)
        """

        keybytes = bytes.fromhex(key)
        self.key = key
        self.tweak = tweak
        self.default_radix = radix
        
        # Set up default alphabet for the default radix
        if radix <= self.BASE62_LEN:
            self.default_alphabet = self.BASE62[0:radix]
        else:
            self.default_alphabet = None

        # Default min/max for the default radix
        self.default_min_len = math.ceil(math.log(self.DOMAIN_MIN) / math.log(radix))
        self.default_max_len = 2 * math.floor(96/math.log2(radix))
        
        klen = len(keybytes)

        # Check if the key is 128, 192, or 256 bits = 16, 24, or 32 bytes
        if klen not in (16, 24, 32):
            raise ValueError(f'key length is {klen} but must be 128, 192, or 256 bits')

        # While FF3 allows radices in [2, 2^16], commonly useful range is 2..256
        if (radix < 2) or (radix > self.RADIX_MAX):
            raise ValueError(f"radix must be between 2 and {self.RADIX_MAX}, inclusive")

        # Make sure 2 <= minLength <= maxLength for default
        if (self.default_min_len < 2) or (self.default_max_len < self.default_min_len):
            raise ValueError("Default minLen or maxLen invalid, adjust your radix")

        # AES block cipher in ECB mode with the block size derived based on the length of the key
        self.aesCipher = AESCipher(self._reverse_string(keybytes), AESCipher.MODE_ECB)

    def _reverse_string(self, txt: Union[str, bytes]) -> Union[str, bytes]:
        """Reverse a string or bytes object.
        
        Args:
            txt: String or bytes to reverse
            
        Returns:
            Reversed string or bytes
        """

        return txt[::-1]

    def _get_field_config(self, field_type: str) -> Dict:
        """Get configuration for a specific field type.
        
        Args:
            field_type (str): Field type identifier
            
        Returns:
            dict: Field configuration
        """

        if field_type not in self.FIELD_CONFIGS:
            raise ValueError(f"Unknown field_type: {field_type}. "
                           f"Available: {list(self.FIELD_CONFIGS.keys())}")
        
        return self.FIELD_CONFIGS[field_type]

    def _validate_field_input(self, plaintext: str, field_type: str) -> None:
        """Validate input against field type constraints.
        
        Args:
            plaintext (str): Input text to validate
            field_type (str): Field type identifier
        """

        config = self._get_field_config(field_type)
        
        # Check length bounds
        if len(plaintext) < config['min_len'] or len(plaintext) > config['max_len']:
            raise ValueError(f"Input length {len(plaintext)} is not within "
                           f"min {config['min_len']} and max {config['max_len']} "
                           f"bounds for field_type '{field_type}'")
        
        # Check alphabet constraints
        if config['alphabet']:
            invalid_chars = set(plaintext) - set(config['alphabet'])
            if invalid_chars:
                raise ValueError(f"Invalid characters {invalid_chars} for field_type '{field_type}'. "
                               f"Allowed: {config['alphabet']}")

    def _calculate_p(self, i: int, alphabet: str, W: bytes, B: str) -> bytearray:
        """Calculate P for AES input in Feistel round.
        
        Args:
            i (int): Round number
            alphabet (str): Character alphabet
            W (bytes): Tweak portion
            B (str): Right side of Feistel split
            
        Returns:
            bytearray: 16-byte P value for AES input
        """

        # P is always 16 bytes
        P = bytearray(self.BLOCK_SIZE)

        # Calculate P by XORing W, i into the first 4 bytes of P
        P[0] = W[0]
        P[1] = W[1]
        P[2] = W[2]
        P[3] = W[3] ^ int(i)

        # The remaining 12 bytes of P are for rev(B) with padding
        val = self._decode_int_r(B, alphabet)
        try:
            BBytes = val.to_bytes(12, "big")
        except OverflowError:
            # Use modulo arithmetic to fit large values in 12 bytes
            max_12_byte_int = (1 << 96) - 1  # 2^96 - 1
            val = val % (max_12_byte_int + 1)
            BBytes = val.to_bytes(12, "big")

        logger.debug(f"B: {B} val: {val} BBytes: {BBytes.hex()}")

        P[self.BLOCK_SIZE - len(BBytes):] = BBytes
        logger.debug(f"[round: {i}] P: {P.hex()} W: {W.hex()} ")

        return P

    def _calculate_tweak64_ff3_1(self, tweak56: bytes) -> bytearray:
        """Convert 56-bit FF3-1 tweak to 64-bit FF3 tweak.
        
        Args:
            tweak56 (bytes): 7-byte FF3-1 tweak
            
        Returns:
            bytearray: 8-byte FF3 tweak
        """

        tweak64 = bytearray(8)
        tweak64[0] = tweak56[0]
        tweak64[1] = tweak56[1]
        tweak64[2] = tweak56[2]
        tweak64[3] = (tweak56[3] & 0xF0)
        tweak64[4] = tweak56[4]
        tweak64[5] = tweak56[5]
        tweak64[6] = tweak56[6]
        tweak64[7] = ((tweak56[3] & 0x0F) << 4)

        return tweak64

    def _encode_int_r(self, n: int, alphabet: str, length: int = 0) -> str:
        """Return a string representation of a number in the given base system.
        
        The string is left in a reversed order expected by the calling cryptographic function.
        
        Args:
            n (int): Number to encode
            alphabet (str): Character alphabet for encoding
            length (int): Minimum length of result (padded if necessary)
            
        Returns:
            str: Encoded string in reversed order
        """

        base = len(alphabet)
        if (base > self.RADIX_MAX):
            raise ValueError(f"Base {base} is outside range of supported radix "
                           f"2..{self.RADIX_MAX}")

        x = ''
        while n >= base:
            n, b = divmod(n, base)
            x += alphabet[b]
        x += alphabet[n]

        if len(x) < length:
            x = x.ljust(length, alphabet[0])

        return x

    def _decode_int_r(self, astring: str, alphabet: str) -> int:
        """Decode a Base X encoded string into a number.
        
        Args:
            astring (str): The encoded string
            alphabet (str): The alphabet to use for decoding
            
        Returns:
            int: Decoded integer value
        """

        strlen = len(astring)
        base = len(alphabet)
        
        num = 0
        idx = 0

        try:
            for char in reversed(astring):
                power = (strlen - (idx + 1))
                num += alphabet.index(char) * (base ** power)
                idx += 1

        except ValueError:
            raise ValueError(f'char {char} not found in alphabet {alphabet}')

        return num

    def encrypt(self, plaintext: str, field_type: Optional[str] = None) -> str:
        """Encrypts the plaintext string and returns a ciphertext of the same length and format.
        
        Args:
            plaintext (str): String to encrypt
            field_type (str, optional): Field type ('name', 'phone', 'date', 'address')
                       If None, uses default radix and alphabet
        
        Returns:
            str: Encrypted string with same format as plaintext
        """

        if field_type:
            config = self._get_field_config(field_type)
            self._validate_field_input(plaintext, field_type)
            alphabet = config['alphabet'] if config['alphabet'] else self.BASE62[0:config['radix']]
            
            return self._encrypt_with_config(plaintext, self.tweak, config['radix'], alphabet)
        else:
            return self._encrypt_with_config(plaintext, self.tweak, self.default_radix, self.default_alphabet)

    def decrypt(self, ciphertext: str, field_type: Optional[str] = None) -> str:
        """Decrypts the ciphertext string and returns a plaintext of the same length and format.
        
        Args:
            ciphertext (str): String to decrypt
            field_type (str, optional): Field type ('name', 'phone', 'date', 'address')
                       If None, uses default radix and alphabet
        
        Returns:
            str: Decrypted string with same format as ciphertext
        """

        if field_type:
            config = self._get_field_config(field_type)
            alphabet = config['alphabet'] if config['alphabet'] else self.BASE62[0:config['radix']]
            
            return self._decrypt_with_config(ciphertext, self.tweak, config['radix'], alphabet, 
                                           config['min_len'], config['max_len'])
        else:
            return self._decrypt_with_config(ciphertext, self.tweak, self.default_radix, 
                                           self.default_alphabet, self.default_min_len, self.default_max_len)

    def encrypt_with_tweak(self, plaintext: str, tweak: str, field_type: Optional[str] = None) -> str:
        """Encrypts with custom tweak.
        
        Args:
            plaintext (str): String to encrypt
            tweak (str): Custom tweak (hex string)
            field_type (str, optional): Field type identifier
            
        Returns:
            str: Encrypted string
        """

        if field_type:
            config = self._get_field_config(field_type)
            self._validate_field_input(plaintext, field_type)
            alphabet = config['alphabet'] if config['alphabet'] else self.BASE62[0:config['radix']]
            return self._encrypt_with_config(plaintext, tweak, config['radix'], alphabet)
        else:
            return self._encrypt_with_config(plaintext, tweak, self.default_radix, self.default_alphabet)

    def decrypt_with_tweak(self, ciphertext: str, tweak: str, field_type: Optional[str] = None) -> str:
        """Decrypts with custom tweak.
        
        Args:
            ciphertext (str): String to decrypt
            tweak (str): Custom tweak (hex string)
            field_type (str, optional): Field type identifier
            
        Returns:
            str: Decrypted string
        """

        if field_type:
            config = self._get_field_config(field_type)
            alphabet = config['alphabet'] if config['alphabet'] else self.BASE62[0:config['radix']]
            return self._decrypt_with_config(ciphertext, tweak, config['radix'], alphabet,
                                           config['min_len'], config['max_len'])
        else:
            return self._decrypt_with_config(ciphertext, tweak, self.default_radix, 
                                           self.default_alphabet, self.default_min_len, self.default_max_len)

    def _encrypt_with_config(self, plaintext: str, tweak: str, radix: int, alphabet: str) -> str:
        """Internal encryption with specific configuration.
        
        Args:
            plaintext (str): Text to encrypt
            tweak (str): Tweak value (hex string)
            radix (int): Number base
            alphabet (str): Character alphabet
            
        Returns:
            str: Encrypted text
        """

        tweakBytes = bytes.fromhex(tweak)
        n = len(plaintext)

        if len(tweakBytes) not in [self.TWEAK_LEN, self.TWEAK_LEN_NEW]:
            raise ValueError(f"tweak length {len(tweakBytes)} invalid: tweak must be 56"
                             f" or 64 bits")

        # Calculate split point
        u = math.ceil(n / 2)
        v = n - u

        # Split the message
        A = plaintext[:u]
        B = plaintext[u:]

        if len(tweakBytes) == self.TWEAK_LEN_NEW:
            # FF3-1
            tweakBytes = self._calculate_tweak64_ff3_1(tweakBytes)

        Tl = tweakBytes[:self.HALF_TWEAK_LEN]
        Tr = tweakBytes[self.HALF_TWEAK_LEN:]
        logger.debug(f"Tweak: {tweak}, tweakBytes:{tweakBytes.hex()}")

        # Pre-calculate the modulus since it's only one of 2 values
        modU = radix ** u
        modV = radix ** v
        logger.debug(f"modU: {modU} modV: {modV}")

        # Main Feistel Round, 8 times
        for i in range(self.NUM_ROUNDS):
            logger.debug(f"-------- Round {i}")
            # Determine alternating Feistel round side
            if i % 2 == 0:
                m = u
                W = Tr
            else:
                m = v
                W = Tl

            # P is fixed-length 16 bytes
            P = self._calculate_p(i, alphabet, W, B)
            revP = self._reverse_string(P)

            S = self.aesCipher.encrypt(bytes(revP))
            S = self._reverse_string(S)
            logger.debug(f"S: {S.hex()}")

            y = int.from_bytes(S, byteorder='big')

            # Calculate c
            c = self._decode_int_r(A, alphabet)
            c = c + y

            if i % 2 == 0:
                c = c % modU
            else:
                c = c % modV

            logger.debug(f"m: {m} A: {A} c: {c} y: {y}")
            C = self._encode_int_r(c, alphabet, int(m))

            # Final steps
            A = B
            B = C

            logger.debug(f"A: {A} B: {B}")

        return A + B

    def _decrypt_with_config(self, ciphertext: str, tweak: str, radix: int, alphabet: str, min_len: int, max_len: int) -> str:
        """Internal decryption with specific configuration.
        
        Args:
            ciphertext (str): Text to decrypt
            tweak (str): Tweak value (hex string)
            radix (int): Number base
            alphabet (str): Character alphabet
            min_len (int): Minimum allowed length
            max_len (int): Maximum allowed length
            
        Returns:
            str: Decrypted text
        """

        tweakBytes = bytes.fromhex(tweak)
        n = len(ciphertext)

        # Check if message length is within bounds
        if (n < min_len) or (n > max_len):
            raise ValueError(f"message length {n} is not within min {min_len} and "
                             f"max {max_len} bounds")

        if len(tweakBytes) not in [self.TWEAK_LEN, self.TWEAK_LEN_NEW]:
            raise ValueError(f"tweak length {len(tweakBytes)} invalid: tweak must be 8 "
                             f"bytes, or 64 bits")

        # Calculate split point
        u = math.ceil(n/2)
        v = n - u

        # Split the message
        A = ciphertext[:u]
        B = ciphertext[u:]

        if len(tweakBytes) == self.TWEAK_LEN_NEW:
            # FF3-1
            tweakBytes = self._calculate_tweak64_ff3_1(tweakBytes)

        Tl = tweakBytes[:self.HALF_TWEAK_LEN]
        Tr = tweakBytes[self.HALF_TWEAK_LEN:]
        logger.debug(f"Tweak: {tweak}, tweakBytes:{tweakBytes.hex()}")

        # Pre-calculate the modulus since it's only one of 2 values
        modU = radix ** u
        modV = radix ** v
        logger.debug(f"modU: {modU} modV: {modV}")

        # Main Feistel Round, 8 times
        for i in reversed(range(self.NUM_ROUNDS)):
            logger.debug(f"-------- Round {i}")
            # Determine alternating Feistel round side
            if i % 2 == 0:
                m = u
                W = Tr
            else:
                m = v
                W = Tl

            # P is fixed-length 16 bytes
            P = self._calculate_p(i, alphabet, W, A)
            revP = self._reverse_string(P)

            S = self.aesCipher.encrypt(bytes(revP))
            S = self._reverse_string(S)
            logger.debug("S:    ", S.hex())

            y = int.from_bytes(S, byteorder='big')

            # Calculate c
            c = self._decode_int_r(B, alphabet)
            c = c - y

            if i % 2 == 0:
                c = c % modU
            else:
                c = c % modV

            logger.debug(f"m: {m} B: {B} c: {c} y: {y}")
            C = self._encode_int_r(c, alphabet, int(m))

            # Final steps
            B = A
            A = C

            logger.debug(f"A: {A} B: {B}")

        return A + B

    @staticmethod
    def withCustomAlphabet(key: str, tweak: str, alphabet: str) -> 'FF3Cipher':
        """Factory method to create a FF3Cipher object with a custom alphabet.
        
        Args:
            key (str): AES key (hex string)
            tweak (str): FF3 tweak (hex string)
            alphabet (str): Custom alphabet string
            
        Returns:
            FF3Cipher: New FF3Cipher instance with custom alphabet
        """

        c = FF3Cipher(key, tweak, len(alphabet))
        c.default_alphabet = alphabet
        return c