# main_script.py
# version 0.1.0

import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import sqlite3
import os
import json
import pageconv

class DatabaseViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Post to Page Converter for Publii 0.46.x")
        self.root.geometry("660x340")

        self.conn = None
        self.root_folder = None
        self.db_path = None
        self.site_config_path = None
        self.theme = None
        self.theme_config_path = None

        self.root.columnconfigure(0, weight=3)
        self.root.columnconfigure(1, weight=2)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=0)

        self.left_frame = tk.Frame(self.root)
        self.left_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.right_frame = tk.Frame(self.root)
        self.right_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.status_label = tk.Label(self.root, text="Select a site to begin.", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.grid(row=1, column=0, columnspan=2, sticky="we")

        self.select_site_button = tk.Button(self.left_frame, text="Select Site", command=self.select_site, width=20)
        self.select_site_button.pack(pady=10)

        # Label for Posts
        self.posts_label = tk.Label(self.left_frame, text="Posts", font=("Arial", 12, "bold"))
        self.posts_label.pack(pady=(20, 5))

        # Posts Combobox (disabled initially)
        self.title_dropdown = ttk.Combobox(
            self.left_frame, values=[], state="disabled", width=40
        )
        self.title_dropdown.pack(pady=5)
        self.title_dropdown.bind("<<ComboboxSelected>>", lambda event: self.display_post_details())

        # Frame for post details and convert button
        self.details_frame = tk.Frame(self.left_frame)
        self.details_frame.pack(pady=10)

        self.convert_button = None

        self.labels = {}
        self.create_labels()

    def create_labels(self):
        # Site Label
        self.site_label = tk.Label(self.right_frame, text="Site: N/A", anchor="w", font=("Arial", 12))
        self.site_label.pack(anchor="w", pady=(0, 10))

        # Criteria Label
        self.criteria_label = tk.Label(self.right_frame, text="Criteria", anchor="w", font=("Arial", 12, "bold"))
        self.criteria_label.pack(anchor="w", pady=(0, 5))

        # Checkbox Labels
        items = ["Database", "Pages Support", "Posts"]
        for item in items:
            label = tk.Label(self.right_frame, text=f"[ ] {item}", anchor="w", font=("Arial", 12))
            label.pack(anchor="w", pady=2)
            self.labels[item] = label

        # Total Posts Label
        self.total_posts_label = tk.Label(self.right_frame, text="Total Qualifying Posts: 0", anchor="w", font=("Arial", 10))
        self.total_posts_label.pack(anchor="w", pady=(2, 10))

    def update_checkbox(self, item, checked=True):
        if item in self.labels:
            checkbox = "[x]" if checked else "[ ]"
            self.labels[item].config(text=f"{checkbox} {item}")

    def reset_checkboxes(self):
        for item in self.labels:
            self.update_checkbox(item, checked=False)
        self.site_label.config(text="Site: N/A")
        self.total_posts_label.config(text="Total Qualifying Posts: 0")

    def select_site(self):
        if self.conn:
            self.start_over()
            return

        root_folder = filedialog.askdirectory(title="Select Site Root Folder")

        if root_folder:
            self.root_folder = root_folder
            site_name = os.path.basename(os.path.normpath(self.root_folder))
            self.site_label.config(text=f"Site: {site_name}")
            self.site_config_path = os.path.join(self.root_folder, 'input', 'config', 'site.config.json')
            self.theme = None

            if os.path.isfile(self.site_config_path):
                try:
                    with open(self.site_config_path, 'r') as f:
                        config = json.load(f)
                        self.theme = config.get("theme", "Default")
                        display_theme = self.theme
                        self.status_label.config(text=f"Selected site: {site_name} | Theme: {display_theme}")
                        self.read_theme_config()
                except json.JSONDecodeError as e:
                    messagebox.showerror("JSON Error", f"Failed to parse site.config.json: {e}")
                    self.status_label.config(text=f"Theme: Error")
            else:
                messagebox.showwarning("Config Not Found", f"Config file not found at {self.site_config_path}")
                self.status_label.config(text=f"Theme: Not Found")
                self.reset_and_select_site()
        else:
            self.status_label.config(text="No folder selected.")

    def read_theme_config(self):
        self.theme_config_path = os.path.join(self.root_folder, 'input', 'themes', self.theme, 'config.json')

        if os.path.isfile(self.theme_config_path):
            try:
                with open(self.theme_config_path, 'r') as f:
                    config = json.load(f)
                    supported_features = config.get("supportedFeatures", {})
                    pages_supported = supported_features.get("pages", False)

                    if pages_supported:
                        self.update_checkbox("Pages Support", checked=True)
                        self.connect_database()
                    else:
                        messagebox.showinfo(
                            "Feature Not Supported",
                            f"The current theme for the site '{self.root_folder}' does not support the PAGES feature."
                        )
                        self.status_label.config(
                            text=f"Theme: {self.theme} | Pages Support: Disabled"
                        )
                        self.reset_and_select_site()
            except json.JSONDecodeError as e:
                messagebox.showerror("JSON Error", f"Failed to parse theme config.json: {e}")
                self.status_label.config(
                    text=f"Theme: {self.theme} | Pages Support: Error"
                )
                self.reset_and_select_site()
        else:
            messagebox.showwarning("Config Not Found", f"Theme config file not found at {self.theme_config_path}")
            self.status_label.config(
                text=f"Theme: {self.theme} | Pages Support: Not Found"
            )
            self.reset_and_select_site()

    def connect_database(self):
        self.db_path = os.path.join(self.root_folder, 'input', 'db.sqlite')

        if os.path.isfile(self.db_path):
            try:
                self.conn = sqlite3.connect(self.db_path)
                cursor = self.conn.cursor()
                display_db_path = self.db_path.replace("/", "\\")
                self.update_checkbox("Database", checked=True)
                self.status_label.config(text=f"Connected to database at {display_db_path} | Theme: {self.theme}")

                self.query_posts(cursor)
                self.select_site_button.config(text="Start Over")
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"An error occurred: {e}")
                self.status_label.config(text=f"Database Error: {e}")
                self.reset_and_select_site()
        else:
            messagebox.showerror("File Not Found", f"Database not found at {self.db_path}")
            display_db_path = self.db_path.replace("/", "\\")
            self.status_label.config(text=f"Database file not found at {display_db_path}.")
            self.reset_and_select_site()

    def query_posts(self, cursor):
        try:
            cursor.execute("""
                SELECT id, title, slug, status FROM posts
                WHERE (status LIKE 'draft%' OR status LIKE 'published%')
                AND NOT (status LIKE '%is-page%')
            """)
            posts = cursor.fetchall()
            qualifying_posts = [post for post in posts if post[1]]
            total_qualifying = len(qualifying_posts)

            if qualifying_posts:
                titles = [post[1] for post in qualifying_posts]
                self.title_dropdown.config(values=titles, state="readonly")
                self.title_dropdown.current(0)
                self.title_dropdown.bind("<<ComboboxSelected>>", lambda event: self.display_post_details())
                self.update_checkbox("Posts", checked=True)
                self.total_posts_label.config(text=f"Total Qualifying Posts: {total_qualifying}")
            else:
                messagebox.showinfo("No Qualifying Posts", "The site does not have any qualifying posts.")
                self.reset_and_select_site()
        except sqlite3.Error as e:
            messagebox.showerror("Database Query Error", f"An error occurred while querying posts: {e}")
            self.reset_and_select_site()

    def display_post_details(self):
        selected_title = self.title_dropdown.get()
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, slug, status FROM posts WHERE title = ?", (selected_title,))
        post = cursor.fetchone()
        if post:
            for widget in self.details_frame.winfo_children():
                widget.destroy()
            id_label = tk.Label(self.details_frame, text=f"ID: {post[0]}", anchor="w")
            id_label.pack(fill='x')
            slug_label = tk.Label(self.details_frame, text=f"Slug: {post[1]}", anchor="w")
            slug_label.pack(fill='x')
            status_label = tk.Label(self.details_frame, text=f"Status: {post[2]}", anchor="w")
            status_label.pack(fill='x')
            self.convert_button = tk.Button(self.details_frame, text="Convert to Page", command=lambda: self.convert_to_page(post))
            self.convert_button.pack(pady=10)

    def convert_to_page(self, post):
        confirm = messagebox.askyesno(
            "Confirm Conversion",
            f"Are you sure you want to convert the post '{post[0]}' to a page? It cannot be reversed."
        )
        if confirm:
            try:
                pageconv.convert_to_page(self.root_folder, post[0], self.conn)
                messagebox.showinfo("Success", f"Post '{post[0]}' has been converted to a page.")
                self.refresh_posts()
            except Exception as e:
                messagebox.showerror("Conversion Error", f"An error occurred during conversion: {e}")

    def refresh_posts(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT id, title, slug, status FROM posts
                WHERE (status LIKE 'draft%' OR status LIKE 'published%')
                AND NOT (status LIKE '%is-page%')
            """)
            posts = cursor.fetchall()
            qualifying_posts = [post for post in posts if post[1]]
            total_qualifying = len(qualifying_posts)

            if qualifying_posts:
                titles = [post[1] for post in qualifying_posts]
                self.title_dropdown.config(values=titles, state="readonly")
                self.title_dropdown.current(0)
                self.title_dropdown.bind("<<ComboboxSelected>>", lambda event: self.display_post_details())
                self.update_checkbox("Posts", checked=True)
                self.total_posts_label.config(text=f"Total Qualifying Posts: {total_qualifying}")
            else:
                messagebox.showinfo("No Qualifying Posts", "The site does not have any qualifying posts.")
                self.reset_and_select_site()

            # Clear post details and convert button
            for widget in self.details_frame.winfo_children():
                widget.destroy()
            self.convert_button = None

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to refresh posts: {e}")
            self.reset_and_select_site()

    def reset_and_select_site(self):
        self.start_over()

    def start_over(self):
        if self.conn:
            try:
                self.conn.close()
                self.conn = None
                self.status_label.config(text="Database connection closed. Select a new site.")
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Failed to close the database: {e}")
                self.status_label.config(text=f"Error closing database: {e}")
                return

        if self.title_dropdown:
            self.title_dropdown.config(values=[], state="disabled")
            self.title_dropdown.set('')

        for widget in self.details_frame.winfo_children():
            widget.destroy()
        self.convert_button = None

        self.reset_checkboxes()
        self.select_site_button.config(text="Select Site")
        self.status_label.config(text="Select a site to begin.")

def main():
    root = tk.Tk()
    app = DatabaseViewerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
