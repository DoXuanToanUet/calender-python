import requests
from bs4 import BeautifulSoup
import json
import re

# Đọc danh sách URL từ file urls.txt
with open('urls.txt', 'r', encoding='utf-8') as f:
    urls = [line.strip() for line in f if line.strip()]

results = []

for url in urls:
    try:
        response = requests.get(url)
        response.raise_for_status()  # Kiểm tra lỗi HTTP nếu có
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Tìm thẻ div chứa dữ liệu (dựa vào class "lcghn bgwhite")
        container = soup.find("div", class_="lcghn")
        if not container:
            print(f"Không tìm thấy container cho URL: {url}")
            continue

        # Trích xuất ngày từ URL (VD: "suy-niem-loi-chua-ngay-01-01-2025" -> "01-01-2025")
        match = re.search(r'(\d{2}-\d{2}-\d{4})', url)
        date = match.group(1) if match else "Không rõ"

        # Lấy nội dung title từ thẻ h2
        title_tag = container.find("h2")
        title = title_tag.get_text(strip=True) if title_tag else ""

        # Lấy nội dung mô tả (desc) từ phần tử có class "ttlcghn"
        desc_tag = container.find(class_="ttlcghn")
        desc = desc_tag.get_text(strip=True) if desc_tag else ""

        # Lấy nội dung bài đọc (read) từ phần tử có class "dsbd"
        read_tag = container.find(class_="dsbd")
        if read_tag:
            read = read_tag.get_text("\n", strip=True)  # Lấy nội dung
            read = re.sub(r'^.*?Các bài đọc và tin mừng hôm nay', '', read, flags=re.DOTALL).strip()  # Bỏ phần tiêu đề
        else:
            read = ""

        # Lấy nội dung áo lễ (paole) từ phần tử có class "paole"
        paole_tag = container.find(class_="paole")
        paole = paole_tag.get_text(strip=True) if paole_tag else ""

        # Thêm dữ liệu vào danh sách kết quả
        results.append({
            "date": date,
            "title": title,
            "desc": desc,
            "read": read,
            "paole": paole
        })

        print(f"Đã crawl thành công: {date}")

    except Exception as e:
        print(f"Lỗi khi crawl {url}: {e}")

# Ghi kết quả ra file JSON
with open("lich_cong_giao_2025.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("Hoàn thành việc crawl và lưu dữ liệu vào lich_cong_giao_2025.json")
