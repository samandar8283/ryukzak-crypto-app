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