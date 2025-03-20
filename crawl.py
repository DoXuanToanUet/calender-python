import requests
from bs4 import BeautifulSoup
import json
import re
import time

# Đọc danh sách URL từ file urls.txt
with open('urls.txt', 'r', encoding='utf-8') as f:
    urls = [line.strip() for line in f if line.strip()]

results = []
BATCH_SIZE = 100  # Mỗi batch có 100 URL
success_count = 0
fail_count = 0
failed_urls = []

total_urls = len(urls)
start_time = time.time()  # Bắt đầu đếm thời gian

for i in range(0, total_urls, BATCH_SIZE):
    batch = urls[i:i + BATCH_SIZE]
    
    print(f"\n🔄 Đang crawl batch {i // BATCH_SIZE + 1}/{(total_urls // BATCH_SIZE) + 1} ({i+1}-{min(i+BATCH_SIZE, total_urls)}/{total_urls})...\n")
    
    for index, url in enumerate(batch, start=i+1):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Kiểm tra lỗi HTTP nếu có
            soup = BeautifulSoup(response.text, "html.parser")

            # Tìm thẻ div chứa dữ liệu (dựa vào class "lcghn bgwhite")
            container = soup.find("div", class_="lcghn")
            if not container:
                print(f"❌ Không tìm thấy container: {url}")
                fail_count += 1
                failed_urls.append(url)
                continue

            # Trích xuất ngày từ URL (VD: "suy-niem-loi-chua-ngay-01-01-2025" -> "01-01-2025")
            match = re.search(r'(\d{2}-\d{2}-\d{4})', url)
            date = match.group(1) if match else "Không rõ"

            # Lấy nội dung title từ thẻ h2
            title = container.find("h2").get_text(strip=True) if container.find("h2") else ""

            # Lấy nội dung mô tả (desc) từ phần tử có class "ttlcghn"
            desc = container.find(class_="ttlcghn").get_text(strip=True) if container.find(class_="ttlcghn") else ""

            # Lấy nội dung bài đọc (read) từ phần tử có class "dsbd"
            read_tag = container.find(class_="dsbd")
            if read_tag:
                read = read_tag.get_text("\n", strip=True)  # Lấy nội dung
                read = re.sub(r'^.*?Các bài đọc và tin mừng hôm nay', '', read, flags=re.DOTALL).strip()  # Bỏ phần tiêu đề
            else:
                read = ""

            # Lấy nội dung áo lễ (paole) từ phần tử có class "paole"
            paole = container.find(class_="paole").get_text(strip=True) if container.find(class_="paole") else ""

            # Thêm dữ liệu vào danh sách kết quả
            results.append({
                "date": date,
                "title": title,
                "desc": desc,
                "read": read,
                "paole": paole
            })

            success_count += 1
            print(f"✅ {index}/{total_urls} - Đã crawl thành công: {date}")

        except requests.exceptions.RequestException as e:
            print(f"⚠️ Lỗi request {url}: {e}")
            fail_count += 1
            failed_urls.append(url)
        except Exception as e:
            print(f"⚠️ Lỗi khác {url}: {e}")
            fail_count += 1
            failed_urls.append(url)

        time.sleep(0.5)  # Nghỉ 0.5 giây giữa các request để tránh bị chặn

# Ghi kết quả ra file JSON
with open("lich_cong_giao_2025.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

# Ghi danh sách URL thất bại ra file
if failed_urls:
    with open("failed_urls.txt", "w", encoding="utf-8") as f:
        for url in failed_urls:
            f.write(url + "\n")

# Kết thúc đếm thời gian
end_time = time.time()
total_time = end_time - start_time  # Tổng thời gian crawl

# Thống kê kết quả cuối cùng
print("\n📊 **TỔNG KẾT:**")
print(f"✅ Thành công: {success_count}/{total_urls}")
print(f"❌ Thất bại: {fail_count}/{total_urls}")
print(f"⏳ Tổng thời gian crawl: {total_time:.2f} giây ({total_time/60:.2f} phút)")
if fail_count > 0:
    print(f"📁 Danh sách URL thất bại đã lưu vào 'failed_urls.txt'")

print("\n🎉 Hoàn thành việc crawl và lưu dữ liệu vào 'lich_cong_giao_2025.json'")
