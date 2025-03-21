# Bước 1: Đọc file crawl.txt và loại bỏ khoảng trắng thừa
with open("docurl.txt", "r", encoding="utf-8") as file:
    raw_links = [line.strip() for line in file if line.strip()]

# Tổng số link ban đầu
total_links = len(raw_links)

# Bước 2: Xử lý các link: nếu link có đuôi ".html" thì loại bỏ phần đuôi đó
processed_links = []
html_removed_count = 0

for link in raw_links:
    # Nếu link kết thúc bằng ".html" thì loại bỏ phần đuôi
    if link.endswith(".html"):
        new_link = link[:-5]  # loại bỏ 5 ký tự cuối: ".html"
        processed_links.append(new_link)
        html_removed_count += 1
    else:
        processed_links.append(link)

# Bước 3: Loại bỏ các link trùng lặp (giữ lại thứ tự xuất hiện ban đầu)
unique_links = []
duplicate_count = 0
seen = set()

for link in processed_links:
    if link not in seen:
        unique_links.append(link)
        seen.add(link)
    else:
        duplicate_count += 1

# Bước 4: Ghi kết quả vào file mới filtered_links.txt
with open("filtered_links.txt", "w", encoding="utf-8") as outfile:
    for link in unique_links:
        outfile.write(link + "\n")

# In tiến trình và tổng kết
print(f"Tổng số link ban đầu: {total_links}")
print(f"Số link đã được xử lý loại bỏ '.html': {html_removed_count}")
print(f"Số link trùng lặp đã loại bỏ: {duplicate_count}")
print(f"Tổng số link sau khi lọc: {len(unique_links)}")
print("Đã ghi kết quả vào file filtered_links.txt")
