import os
import time
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def extract_links(url, summary_lines):
    """
    Sử dụng Selenium để render trang, cuộn trang nếu cần, chờ cho đến khi container có class "container py-12"
    xuất hiện, sau đó trích xuất các giá trị href chỉ từ các thẻ <a> nằm trong thẻ <h2> bên trong container.
    Nếu href là relative, chuyển thành absolute URL dựa trên URL gốc.
    """
    # Cấu hình Chrome ở chế độ headless
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)

    try:
        # Chờ container có class "container py-12" xuất hiện (tối đa 15 giây)
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.container.py-12")))
    except Exception as e:
        msg = f"Không tìm thấy container trong thời gian chờ tại {url}: {e}"
        print(msg)
        summary_lines.append(msg)
        driver.quit()
        return []
    
    # Cuộn trang xuống dưới để kích hoạt lazy load (nếu có)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  # Đợi thêm 2 giây sau khi cuộn

    # Lấy HTML sau khi render
    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, 'html.parser')
    container = soup.select_one("div.container.py-12")
    if not container:
        msg = f"Không tìm thấy container 'container py-12' ở {url}"
        print(msg)
        summary_lines.append(msg)
        return []

    links = []
    # Lặp qua tất cả các thẻ <h2> trong container
    for h2 in container.find_all('h2'):
        # Chỉ lấy thẻ <a> nếu nó nằm trong <h2>
        a_tag = h2.find('a', href=True)
        if a_tag:
            href = a_tag['href']
            if href.startswith('/'):
                href = requests.compat.urljoin(url, href)
            links.append(href)

    if not links:
        msg = f"Không tìm thấy link nào trong các thẻ <h2> tại {url}"
        print(msg)
        summary_lines.append(msg)
    else:
        msg = f"Tìm thấy {len(links)} link ở {url}"
        print(msg)
        summary_lines.append(msg)
    return links

def main():
    summary_lines = []
    start_time = datetime.now()
    summary_lines.append(f"Thời gian bắt đầu: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Kiểm tra file doc.txt tồn tại
    if not os.path.exists('doc.txt'):
        msg = "Không tìm thấy file 'doc.txt'. Vui lòng kiểm tra lại tên file và đường dẫn."
        print(msg)
        summary_lines.append(msg)
        with open('crawl_summary.txt', 'w', encoding='utf-8') as f:
            f.write("\n".join(summary_lines))
        return

    with open('doc.txt', 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    total_urls = len(urls)
    summary_lines.append(f"Tổng số URL cần xử lý: {total_urls}\n")
    all_links = []
    
    # Xử lý từng URL
    for index, url in enumerate(urls, start=1):
        msg = f"Đang xử lý URL {index}/{total_urls}: {url}"
        print(msg)
        summary_lines.append(msg)
        links = extract_links(url, summary_lines)
        if links:
            all_links.extend(links)
        else:
            summary_lines.append("  Không tìm thấy link nào trong container")
    
    # Ghi tất cả các link thu thập được ra file docurl.txt
    try:
        with open('docurl.txt', 'w', encoding='utf-8') as f:
            for link in all_links:
                f.write(link + "\n")
        msg = f"Hoàn thành. Đã lưu {len(all_links)} link vào file 'docurl.txt'."
        print(msg)
        summary_lines.append(msg)
    except Exception as e:
        msg = f"Lỗi khi ghi file 'docurl.txt': {e}"
        print(msg)
        summary_lines.append(msg)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    summary_lines.append(f"\nThời gian kết thúc: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    summary_lines.append(f"Thời gian chạy: {duration} giây")

    # Ghi file tổng kết crawl_summary.txt
    try:
        with open('crawl_summary.txt', 'w', encoding='utf-8') as f:
            f.write("\n".join(summary_lines))
        print("Đã lưu file tổng kết 'crawl_summary.txt'.")
    except Exception as e:
        print(f"Lỗi khi ghi file 'crawl_summary.txt': {e}")

if __name__ == '__main__':
    main()
