from math import gcd

# -------------------------
# MODULAR INVERSE
# -------------------------
def mod_inverse(r, q):
    for i in range(1, q):
        if (r * i) % q == 1:
            return i
    return None


# -------------------------
# PUBLIC KEY GENERATION
# b_i = (w_i * r) mod q
# -------------------------
def generate_public_key(w, r, q):
    return [(wi * r) % q for wi in w]


# -------------------------
# TEXT -> BITS (ASCII)
# -------------------------
def text_to_bits(text):
    bits = []
    for ch in text:
        bin_str = format(ord(ch), '08b')
        bits.extend([int(b) for b in bin_str])
    return bits


# -------------------------
# BITS -> TEXT
# -------------------------
def bits_to_text(bits):
    text = ""

    # 8-bit qilib o‘qiymiz
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]

        if len(byte) < 8:
            continue

        value = int("".join(map(str, byte)), 2)
        text += chr(value)

    return text


# -------------------------
# ENCRYPTION
# C = (sum(b_i * m_i)) mod q
# -------------------------
def encrypt_bits(bits, b, q):
    n = len(b)
    ciphertext = []

    for i in range(0, len(bits), n):
        chunk = bits[i:i+n]

        # padding
        if len(chunk) < n:
            chunk += [0] * (n - len(chunk))

        c = sum(b[j] * chunk[j] for j in range(n)) % q
        ciphertext.append(c)

    return ciphertext


# -------------------------
# DECRYPTION
# 1. s = (c * r^-1) mod q
# 2. subset sum with w
# -------------------------
def decrypt(ciphertext, w, r, q):
    r_inv = mod_inverse(r, q)

    if r_inv is None:
        raise ValueError("No modular inverse for r")

    bits = []

    for c in ciphertext:
        s = (c * r_inv) % q

        chunk = [0] * len(w)

        # greedy subset sum (super-increasing assumption)
        for i in reversed(range(len(w))):
            if w[i] <= s:
                chunk[i] = 1
                s -= w[i]

        bits.extend(chunk)

    return bits


# -------------------------
# KEY VALIDATION HELPERS
# -------------------------
def is_increasing(w):
    return all(w[i] < w[i+1] for i in range(len(w)-1))


def is_valid_q(w, q):
    return q > sum(w)


def is_coprime(r, q):
    return gcd(r, q) == 1