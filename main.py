import sys
import random
from math import gcd
from PyQt5.QtWidgets import QMainWindow, QApplication

from ui_main import Ui_MainWindow
from knapsack import (
    generate_public_key,
    decrypt,
    text_to_bits,
    bits_to_text
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.w = None
        self.q = None
        self.r = None
        self.b = None

        # signals
        self.ui.btnValidate.clicked.connect(self.validate_keys)
        self.ui.btnAutoGenerate.clicked.connect(self.auto_generate)
        self.ui.encryptBtn.clicked.connect(self.encrypt)
        self.ui.decryptBtn.clicked.connect(self.decrypt)
        self.ui.resetBtn.clicked.connect(self.reset_all)

    # -------------------------
    # LOG SYSTEM (SIMPLE)
    # -------------------------
    def log(self, msg):
        self.ui.logText.append(msg)

    def set_error(self, msg):
        self.ui.logText.append(f"❌ {msg}")

    def set_success(self, msg):
        self.ui.logText.append(f"✔ {msg}")

    # -------------------------
    # INPUT PARSE
    # -------------------------
    def parse_inputs(self):
        try:
            w = list(map(int, self.ui.lineEdit_w.text().strip().split()))
            q = int(self.ui.lineEdit_q.text().strip())
            r = int(self.ui.lineEdit_r.text().strip())
            return (w, q, r), None

        except Exception:
            return None, "Input noto‘g‘ri formatda kiritilgan"

    # -------------------------
    # VALIDATION
    # -------------------------
    def validate_keys(self):
        self.ui.logText.clear()
        data, error = self.parse_inputs()

        if error:
            self.set_error(error)
            return

        self.w, self.q, self.r = data

        errors = []

        original_w = self.w.copy()
        self.w = sorted(self.w)
        if original_w != self.w:
            self.log("📊 w tartiblandi:")
            self.log(f"   oldin: {original_w}")
            self.log(f"   keyin: {self.w}")

        if not self.is_superincreasing(self.w):
            errors.append("w super-o‘suvchi (har element oldingilar yig‘indisidan katta) bo‘lishi kerak")

        if self.q <= sum(self.w):
            errors.append("q > sum(w) bo‘lishi kerak")

        if gcd(self.q, self.r) != 1:
            errors.append("r va q o‘zaro tub bo‘lishi kerak")

        if errors:
            for e in errors:
                self.set_error(e)
            self.b = None
            return

        self.b = generate_public_key(self.w, self.r, self.q)
        self.set_success(f"Kalitlar to‘g‘ri. Public key: {self.b}")

    # -------------------------
    # Superincreasing tekshirish
    # -------------------------
    def is_superincreasing(self, w):
        total = 0
        for x in w:
            if x <= total:
                return False
            total += x
        return True
    
    # -------------------------
    # Modular inverse
    # -------------------------
    def mod_inverse_log(self, r, q):
        self.log(f"🔍 Modular inverse topish: {r} mod {q}")
        self.log(f"📌 r*x + q*y = 1")
        self.log(f"🔁 Extended Euclid boshlanishi: r={r}, q={q}")

        g, x, y = self.extended_gcd_log(r, q)

        self.log(f"📊 gcd({r},{q}) = {g}")

        if g != 1:
            self.log("❌ Inverse mavjud emas!")
            return None

        if x < 0:
            self.log(f"📌 x = {x} (negativ, shuning uchun mod q bilan to‘g‘rilanadi)")
            self.log(f"   {x} mod {q} = {x % q}")
        inv = x % q

        self.log(f"✅ Inverse topildi:")
        self.log(f"   {r}⁻¹ mod {q} = {inv}")

        return inv
    
    # -------------------------
    # Extended Euclidean Algorithm (for modular inverse)
    # -------------------------
    def extended_gcd_log(self, r, q):

        if q == 0:
            self.log(f"📌 Base case: gcd = {r}")
            return r, 1, 0

        self.log(f"➡ {r} = {q} * ({r // q}) + {r % q}")

        g, x1, y1 = self.extended_gcd_log(q, r % q)

        x = y1
        y = x1 - (r // q) * y1

        self.log(f"⬅ Back step:")
        self.log(f"   x = {y1}")
        self.log(f"   y = {x1} - ({r}//{q})*{y1} = {y}")

        return g, x, y
    
    # -------------------------
    # AUTO GENERATE
    # -------------------------
    def auto_generate(self):
        self.ui.logText.clear()
        self.w = []
        total = 0

        for i in range(4):
            val = total + random.randint(1, 10)
            self.w.append(val)
            total += val
        self.q = sum(self.w) + random.randint(10, 50)

        self.r = random.randint(2, self.q - 1)
        while gcd(self.r, self.q) != 1:
            self.r = random.randint(2, self.q - 1)

        self.b = generate_public_key(self.w, self.r, self.q)

        self.ui.lineEdit_w.setText(" ".join(map(str, self.w)))
        self.ui.lineEdit_q.setText(str(self.q))
        self.ui.lineEdit_r.setText(str(self.r))

        self.set_success("Auto generate bajarildi")
        self.log(f"w = {self.w}")
        self.log(f"q = {self.q}")
        self.log(f"r = {self.r}")
        self.log(f"Public key = {self.b}")

    # -------------------------
    # ENCRYPT
    # -------------------------
    def encrypt(self):
        if not self.b:
            self.set_error("Avval kalitlarni validatsiya qiling")
            return

        text = self.ui.inputText.toPlainText().strip()

        if not text:
            self.set_error("Matn bo‘sh")
            return

        self.ui.logText.clear()

        self.log("🔐 SHIFRLASH BOSHLANDI")
        self.log(f"Plain text: {text}")

        bits = text_to_bits(text)

        self.log("\n🔤 Harf → bit:")
        for ch in text:
            self.log(f"{ch} → {format(ord(ch), '08b')}")

        self.log(f"\nFull bits: {bits}")

        n = len(self.b)
        cipher = []

        self.log(f"\nBlock size: {n}")

        for i in range(0, len(bits), n):
            chunk = bits[i:i + n]

            if len(chunk) < n:
                chunk += [0] * (n - len(chunk))

            self.log(f"\nBlock {i//n + 1}: {chunk}")

            c = 0
            for j in range(n):
                mul = self.b[j] * chunk[j]
                c += mul
                self.log(f"   {self.b[j]} * {chunk[j]} = {mul}")

            self.log(f"   sum = {c}")

            c = c % self.q
            self.log(f"   mod q = {c}")

            cipher.append(c)

        self.ui.outputText.setText(str(cipher))

        self.set_success(f"Natija: {cipher}")
        self.set_success("Shifrlash tugadi")

    # -------------------------
    # DECRYPT
    # -------------------------
    def decrypt(self):
        if not self.w:
            self.set_error("Avval kalitlarni kiriting")
            return

        cipher_text = self.ui.outputText.toPlainText().strip()

        if not cipher_text:
            self.set_error("Cipher bo‘sh")
            return

        cipher = eval(cipher_text, {"__builtins__": {}})

        self.ui.logText.clear()

        self.log("🔓 DECRYPTION BOSHLANDI")
        self.log(f"Cipher: {cipher}")

        r_inv = self.mod_inverse_log(self.r, self.q)

        self.log(f"\nr⁻¹ mod q = {r_inv}")

        c_primes = []

        for c in cipher:
            c_prime = (c * r_inv) % self.q
            c_primes.append(c_prime)
            self.log(f"{c} * {r_inv} mod {self.q} = {c_prime}")

        self.log("\n📦 GREEDY BIT RECOVERY")

        bits = []

        for idx, c in enumerate(c_primes):
            self.log(f"\nBlock {idx+1}: c' = {c}")

            block_bits = []

            for i in range(len(self.w) - 1, -1, -1):
                if c >= self.w[i]:
                    block_bits.insert(0, 1)
                    self.log(f"   {self.w[i]} <= {c} → 1")
                    c -= self.w[i]
                else:
                    block_bits.insert(0, 0)
                    self.log(f"   {self.w[i]} > {c} → 0")

            self.log(f"Block bits: {block_bits}")
            bits.extend(block_bits)

        text = bits_to_text(bits)

        self.ui.inputText.setText(text)

        self.set_success(f"Natija: {text}")

    # -------------------------
    # RESET
    # -------------------------
    def reset_all(self):
        self.ui.lineEdit_w.clear()
        self.ui.lineEdit_q.clear()
        self.ui.lineEdit_r.clear()

        self.ui.inputText.clear()
        self.ui.outputText.clear()
        self.ui.logText.clear()

        self.w = self.q = self.r = self.b = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())