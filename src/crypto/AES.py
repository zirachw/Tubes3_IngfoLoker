from typing import List

class AESCipher:
    """AES (Advanced Encryption Standard) cipher implementation supporting 128, 192, and 256-bit keys.

    AES is a symmetric block cipher that encrypts data in 16-byte blocks using a series of
    transformation rounds. The algorithm consists of four main operations performed in each round:
    1. SubBytes - Non-linear substitution using an S-box lookup table
    2. ShiftRows - Cyclically shifts bytes in each row of the state matrix
    3. MixColumns - Linear mixing operation on columns (except final round)
    4. AddRoundKey - XOR operation with round-specific key material

    The number of rounds depends on key size: 10 rounds (128-bit), 12 rounds (192-bit),
    or 14 rounds (256-bit). This implementation in AES-ECB (Electronic Codebook) mode,
    where each 16-byte block is encrypted independently using the same key.

    Components:
    - Key: 128/192/256-bit symmetric encryption key used for all operations
    - Block Size: Fixed 16-byte (128-bit) input/output blocks
    - State Matrix: 4x4 byte array representing the current block during processing
    - Round Keys: Derived keys for each round generated through key expansion using 
    rotation, S-box substitution, and XOR with round constants (RCON)
    """
    
    # AES S-box for SubBytes transformation
    SBOX = [
        0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
        0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
        0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
        0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
        0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
        0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
        0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
        0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
        0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
        0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
        0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
        0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
        0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
        0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
        0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
        0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16
    ]

    # Round constants for key expansion
    RCON = [
        0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36, 0x6c, 0xd8, 0xab, 0x4d, 0x9a
    ]

    # AES mode constants
    MODE_ECB = 1

    def __init__(self, key: bytes, mode: int) -> None:
        """Initialize AES cipher with key and mode.
        
        Args:
            key (bytes): AES key (16, 24, or 32 bytes)
            mode (int): Cipher mode (only ECB supported)
        """

        if mode != self.MODE_ECB:
            raise ValueError("Only ECB mode is implemented")
        
        if len(key) not in [16, 24, 32]:
            raise ValueError("Key must be 16, 24, or 32 bytes")
        
        self.key = key
        self.mode = mode

    def _sub_bytes(self, state: List[int]) -> None:
        """Apply S-box substitution to each byte in the state.
        
        Args:
            state (list): 16-byte state array to modify in-place
        """
        for i in range(16):
            state[i] = self.SBOX[state[i]]

    def _shift_rows(self, state: List[int]) -> None:
        """Perform the ShiftRows transformation.
        
        Args:
            state (list): 16-byte state array to modify in-place
        """

        # Row 1: shift left by 1
        temp = state[1]
        state[1] = state[5]
        state[5] = state[9]
        state[9] = state[13]
        state[13] = temp
        
        # Row 2: shift left by 2  
        temp1, temp2 = state[2], state[6]
        state[2] = state[10]
        state[6] = state[14]
        state[10] = temp1
        state[14] = temp2
        
        # Row 3: shift left by 3 (equivalent to shift right by 1)
        temp = state[15]
        state[15] = state[11]
        state[11] = state[7]
        state[7] = state[3]
        state[3] = temp

    def _gmul(self, a: int, b: int) -> int:
        """Galois Field multiplication in GF(2^8).
        
        Args:
            a (int): First operand
            b (int): Second operand
            
        Returns:
            int: Product in GF(2^8)
        """

        p = 0
        for i in range(8):
            if b & 1:
                p ^= a
            hi_bit_set = a & 0x80
            a <<= 1
            if hi_bit_set:
                a ^= 0x1b  # AES irreducible polynomial
            b >>= 1
        return p & 0xff

    def _mix_columns(self, state: List[int]) -> None:
        """Perform the MixColumns transformation.
        
        Args:
            state (list): 16-byte state array to modify in-place
        """

        # MixColumns matrix
        mix = [
            [0x02, 0x03, 0x01, 0x01],
            [0x01, 0x02, 0x03, 0x01], 
            [0x01, 0x01, 0x02, 0x03],
            [0x03, 0x01, 0x01, 0x02]
        ]
        
        for col in range(4):
            col_start = col * 4
            column = [state[col_start], state[col_start+1], state[col_start+2], state[col_start+3]]
            
            for row in range(4):
                result = 0
                for i in range(4):
                    result ^= self._gmul(mix[row][i], column[i])
                state[col_start + row] = result

    def _add_round_key(self, state: List[int], round_key: List[int]) -> None:
        """XOR the state with the round key.
        
        Args:
            state (list): 16-byte state array to modify in-place
            round_key (list): 16-byte round key
        """

        for i in range(16):
            state[i] ^= round_key[i]

    def _rot_word(self, word: List[int]) -> List[int]:
        """Rotate a 4-byte word left by one byte.
        
        Args:
            word (list): 4-byte word
            
        Returns:
            list: Rotated 4-byte word
        """

        return word[1:] + word[:1]

    def _sub_word(self, word: List[int]) -> List[int]:
        """Apply S-box to each byte in a 4-byte word.
        
        Args:
            word (list): 4-byte word
            
        Returns:
            list: S-box substituted 4-byte word
        """

        return [self.SBOX[b] for b in word]

    def _key_expansion(self, key: bytes) -> List[List[int]]:
        """Expand the key into round keys.
        
        Args:
            key (bytes): Original AES key
            
        Returns:
            list: List of round keys, each 16 bytes
        """

        key_len = len(key)
        
        if key_len == 16:  # AES-128
            rounds = 10
            nk = 4
        elif key_len == 24:  # AES-192
            rounds = 12
            nk = 6
        elif key_len == 32:  # AES-256
            rounds = 14
            nk = 8
        else:
            raise ValueError("Invalid key length. Must be 16, 24, or 32 bytes.")
        
        w = []
        
        # First nk words are the original key
        for i in range(nk):
            w.append([key[4*i], key[4*i+1], key[4*i+2], key[4*i+3]])
        
        # Generate remaining words
        for i in range(nk, 4 * (rounds + 1)):
            temp = w[i-1][:]
            
            if i % nk == 0:
                temp = self._sub_word(self._rot_word(temp))
                temp[0] ^= self.RCON[i//nk - 1]
            elif nk > 6 and i % nk == 4:
                temp = self._sub_word(temp)
            
            w.append([w[i-nk][j] ^ temp[j] for j in range(4)])
        
        # Convert to round keys
        round_keys = []
        for round_num in range(rounds + 1):
            round_key = []
            for i in range(4):
                round_key.extend(w[round_num * 4 + i])
            round_keys.append(round_key)
        
        return round_keys

    def _encrypt_block(self, plaintext_block: bytes) -> bytes:
        """Encrypt a single 16-byte block using AES.
        
        Args:
            plaintext_block (bytes): 16 bytes of plaintext
            
        Returns:
            bytes: 16 bytes of ciphertext
        """

        if len(plaintext_block) != 16:
            raise ValueError("Block must be exactly 16 bytes")
        
        state = list(plaintext_block)
        round_keys = self._key_expansion(self.key)
        rounds = len(round_keys) - 1
        
        # Initial round key addition
        self._add_round_key(state, round_keys[0])
        
        # Main rounds
        for round_num in range(1, rounds):
            self._sub_bytes(state)
            self._shift_rows(state)
            self._mix_columns(state)
            self._add_round_key(state, round_keys[round_num])
        
        # Final round (no MixColumns)
        self._sub_bytes(state)
        self._shift_rows(state)
        self._add_round_key(state, round_keys[rounds])
        
        return bytes(state)

    def encrypt(self, plaintext: bytes) -> bytes:
        """Encrypt data using AES-ECB.
        
        Args:
            plaintext (bytes): Data to encrypt (must be multiple of 16 bytes)
        
        Returns:
            bytes: Encrypted data
        """

        if len(plaintext) % 16 != 0:
            raise ValueError("Plaintext length must be multiple of 16 bytes for ECB mode")
        
        ciphertext = b''
        
        for i in range(0, len(plaintext), 16):
            block = plaintext[i:i+16]
            encrypted_block = self._encrypt_block(block)
            ciphertext += encrypted_block
        
        return ciphertext