# pageconv.py

import sqlite3
import os
import json

def convert_to_page(root_folder, post_id, conn):
    try:
        cursor = conn.cursor()

        # Step 1: Update the status by keeping 'draft' or 'published' and appending ', is-page'
        cursor.execute("SELECT status FROM posts WHERE id = ?", (post_id,))
        result = cursor.fetchone()
        if not result:
            raise ValueError(f"Post with ID {post_id} does not exist.")

        current_status = result[0]
        statuses = [s.strip() for s in current_status.split(',')]
        base_status = None
        for status in statuses:
            if status in ['draft', 'published']:
                base_status = status
                break
        if not base_status:
            raise ValueError(f"Post with ID {post_id} does not have a valid base status ('draft' or 'published').")

        new_status = f"{base_status}, is-page"
        cursor.execute("UPDATE posts SET status = ? WHERE id = ?", (new_status, post_id))

        # Step 2: Update posts_additional_data
        cursor.execute("""
            SELECT id FROM posts_additional_data
            WHERE post_id = ? AND key = 'postViewSettings'
        """, (post_id,))
        post_view_setting = cursor.fetchone()

        if post_view_setting:
            post_view_id = post_view_setting[0]
            cursor.execute("DELETE FROM posts_additional_data WHERE id = ?", (post_view_id,))

        new_page_view_settings = json.dumps({
            "displayDate": {"type": "select"},
            "displayAuthor": {"type": "select"},
            "displayLastUpdatedDate": {"type": "select"},
            "displayShareButtons": {"type": "select"},
            "displayAuthorBio": {"type": "select"},
            "displayChildPages": {"type": "select"},
            "displayComments": {"type": "select"}
        })

        cursor.execute("""
            INSERT INTO posts_additional_data (post_id, key, value)
            VALUES (?, 'pageViewSettings', ?)
        """, (post_id, new_page_view_settings))

        # Step 3: Update or create pages.config.json
        pages_config_path = os.path.join(root_folder, 'input', 'config', 'pages.config.json')

        page_entry = {
            "id": post_id,
            "subpages": []
        }

        if os.path.isfile(pages_config_path):
            with open(pages_config_path, 'r') as f:
                try:
                    data = json.load(f)
                    if not isinstance(data, list):
                        raise ValueError("pages.config.json is not a list.")
                except json.JSONDecodeError:
                    raise ValueError("pages.config.json contains invalid JSON.")

            # Check if entry already exists
            if any(entry.get("id") == post_id for entry in data):
                raise ValueError(f"Entry with id {post_id} already exists in pages.config.json.")

            data.append(page_entry)
            with open(pages_config_path, 'w') as f:
                json.dump(data, f, indent=4)
        else:
            data = [page_entry]
            os.makedirs(os.path.dirname(pages_config_path), exist_ok=True)
            with open(pages_config_path, 'w') as f:
                json.dump(data, f, indent=4)

        # Step 4: Delete records from posts_tags
        cursor.execute("DELETE FROM posts_tags WHERE post_id = ?", (post_id,))

        conn.commit()
        return "Post successfully converted to page."

    except Exception as e:
        conn.rollback()
        raise e
