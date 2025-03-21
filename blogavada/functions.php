<?php

function wpcrawler_custom_slug($post_id)
{
    // Kiểm tra nếu đây là bài viết do WP Content Crawler tạo
    if (get_post_meta($post_id, '_original_slug_set', true)) {
        return;
    }

    // Lấy URL gốc từ meta data (WP Content Crawler thường lưu ở 'wpcrawler_source_url')
    $source_url = get_post_meta($post_id, 'wpcrawler_source_url', true);

    if (!$source_url) {
        return;
    }

    // Trích xuất slug từ URL gốc bằng regex
    preg_match('/https?:\/\/[^\/]+\/(.+?)\.html/', $source_url, $matches);

    if (!empty($matches[1])) {
        $new_slug = sanitize_title($matches[1]);

        // Cập nhật slug của bài viết
        wp_update_post([
            'ID'        => $post_id,
            'post_name' => $new_slug,
        ]);

        // Đánh dấu đã cập nhật slug để tránh lặp lại
        update_post_meta($post_id, '_original_slug_set', true);
    }
}

// Kích hoạt khi bài viết được đăng hoặc cập nhật
add_action('save_post', 'wpcrawler_custom_slug');

