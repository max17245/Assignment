from safety.safety import check
from safety.formatter import report

# Scan dependencies จาก requirements.txt
vulnerabilities = check(
    files=['requirements.txt'],  # ไฟล์ dependencies ของคุณ
    key=None,                     # ใส่ API key ถ้ามี
    cached=False,
    ignore_ids=[]
)

# แสดงผลลัพธ์
print("=== SCA Scan Result ===")
print(report(vulnerabilities, full=True, lines=100))
