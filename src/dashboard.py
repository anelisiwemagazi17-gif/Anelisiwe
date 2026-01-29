"""
MindWorx SOR Dashboard
Professional desktop dashboard for managing SOR automation
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime, timedelta
import threading
import webbrowser
from PIL import Image, ImageTk
from .dashboard_db import dashboard_db
from .config import config
from .database import db
from .moodle_service import moodle_service

class SORDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("MINDWORX SOR Automation Dashboard")

        # Get screen dimensions and set window to fit nicely
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Use 95% of screen width and 90% of screen height
        window_width = int(screen_width * 0.95)
        window_height = int(screen_height * 0.90)

        # Center the window
        x_position = int((screen_width - window_width) / 2)
        y_position = int((screen_height - window_height) / 2)

        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        self.root.configure(bg='#E8EDF2')

        # MindWorx Colors (Enhanced modern palette)
        self.colors = {
            'primary': '#F26522',      # MindWorx Orange (exact from logo)
            'primary_dark': '#D94F1A', # Darker Orange
            'primary_light': '#FF8A5B', # Lighter Orange for hover
            'success': '#10b981',      # Green for success
            'success_light': '#34D399', # Light green for hover
            'warning': '#F59E0B',      # Amber for warnings
            'danger': '#EF4444',       # Red for errors
            'secondary': '#3D3D3D',    # Dark Gray (from logo)
            'bg': '#E8EDF2',           # Lighter modern gray background
            'card_bg': '#FFFFFF',      # White cards
            'text': '#1F2937',         # Darker text for better contrast
            'text_light': '#6B7280',   # Medium gray text
            'text_lighter': '#9CA3AF', # Lighter gray text
            'border': '#E5E7EB',       # Subtle border color
            'shadow': '#00000010',     # Subtle shadow
            'pending': '#F26522',      # MindWorx Orange for pending
            'uploaded': '#10B981',     # Green for uploaded
            'failed': '#EF4444'        # Red for failed
        }

        self.setup_ui()
        # Load data in background thread to prevent GUI freeze
        self.root.after(100, self.load_initial_data)

    def lighten_color(self, hex_color, factor=0.9):
        """Lighten a hex color by moving it towards white"""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        # Lighten by moving towards white (255)
        r = int(r + (255 - r) * factor)
        g = int(g + (255 - g) * factor)
        b = int(b + (255 - b) * factor)

        return f'#{r:02x}{g:02x}{b:02x}'

    def setup_ui(self):
        """Setup the main UI layout"""
        # Header
        self.create_header()

        # Main content area with scrollbar
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Overview Cards
        self.create_overview_cards(main_container)

        # Learner Table Section
        self.create_learner_section(main_container)

    def create_header(self):
        """Create dashboard header with shadow effect"""
        # Header with subtle shadow
        header_container = tk.Frame(self.root, bg=self.colors['bg'], height=100)
        header_container.pack(fill=tk.X)
        header_container.pack_propagate(False)

        header = tk.Frame(header_container, bg='white', height=95)
        header.pack(fill=tk.BOTH, padx=8, pady=(8, 4))
        header.pack_propagate(False)

        # Logo and title container (centered vertically)
        title_frame = tk.Frame(header, bg='white')
        title_frame.place(relx=0, rely=0.5, anchor='w', x=30)

        # Load and display MindWorx logo
        try:
            logo_path = r"C:\Users\10028897\Desktop\Mindworx_dashboard.png"
            logo_image = Image.open(logo_path)
            # Resize logo - wider for balanced proportions with text
            logo_image = logo_image.resize((250, 47), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_image)

            logo_label = tk.Label(
                title_frame,
                image=self.logo_photo,
                bg='white'
            )
            logo_label.pack(side=tk.LEFT, padx=(0, 25))
        except Exception as e:
            print(f"[!] Warning: Could not load logo: {e}")
            # Fallback to text if logo fails
            fallback_label = tk.Label(
                title_frame,
                text="MINDWORX",
                font=('Arial', 28, 'bold'),
                bg='white',
                fg=self.colors['primary']
            )
            fallback_label.pack(side=tk.LEFT, padx=(0, 25))

        # SOR DASHBOARD text next to logo (same size as logo)
        dashboard_label = tk.Label(
            title_frame,
            text="SOR DASHBOARD",
            font=('Arial', 28, 'bold'),
            bg='white',
            fg=self.colors['secondary']
        )
        dashboard_label.pack(side=tk.LEFT)

        # Refresh button (modern rounded style)
        refresh_btn = tk.Button(
            header,
            text="⟳ Refresh",
            command=self.refresh_data,
            bg=self.colors['primary'],
            fg='white',
            font=('Segoe UI', 11, 'bold'),
            relief=tk.FLAT,
            padx=30,
            pady=12,
            cursor='hand2',
            borderwidth=0,
            activebackground=self.colors['primary_dark'],
            activeforeground='white'
        )
        refresh_btn.pack(side=tk.RIGHT, padx=10, pady=20)

        # Add hover effect
        refresh_btn.bind('<Enter>', lambda e: refresh_btn.config(bg=self.colors['primary_light']))
        refresh_btn.bind('<Leave>', lambda e: refresh_btn.config(bg=self.colors['primary']))

        # Bulk Sync Grades button
        bulk_sync_btn = tk.Button(
            header,
            text="📤 Sync Grades to Moodle",
            command=self.bulk_sync_grades,
            bg=self.colors['success'],
            fg='white',
            font=('Segoe UI', 11, 'bold'),
            relief=tk.FLAT,
            padx=20,
            pady=12,
            cursor='hand2',
            borderwidth=0,
            activebackground=self.colors['success_light'],
            activeforeground='white'
        )
        bulk_sync_btn.pack(side=tk.RIGHT, padx=10, pady=20)

        # Add hover effect
        bulk_sync_btn.bind('<Enter>', lambda e: bulk_sync_btn.config(bg=self.colors['success_light']))
        bulk_sync_btn.bind('<Leave>', lambda e: bulk_sync_btn.config(bg=self.colors['success']))

        # Last updated label
        self.last_updated_label = tk.Label(
            header,
            text=f"Last updated: {datetime.now().strftime('%H:%M:%S')}",
            font=('Segoe UI', 10),
            bg='white',
            fg=self.colors['text']
        )
        self.last_updated_label.pack(side=tk.RIGHT, padx=10)

    def create_overview_cards(self, parent):
        """Create overview statistics cards"""
        cards_frame = tk.Frame(parent, bg=self.colors['bg'])
        cards_frame.pack(fill=tk.X, pady=(0, 20))

        self.stat_cards = {}

        cards_config = [
            ('total', 'Total SORs', self.colors['secondary'], '[#]'),
            ('pending', 'Pending', self.colors['pending'], '[...]'),
            ('signature_sent', 'Awaiting Signature', self.colors['primary'], '[✎]'),
            ('signed', 'Signed', self.colors['success'], '[OK]'),
            ('uploaded', 'Uploaded', self.colors['uploaded'], '[UP]'),
            ('failed', 'Failed', self.colors['failed'], '[X]'),
            ('overdue', 'Overdue', self.colors['danger'], '[!]'),
        ]

        for i, (key, title, color, icon) in enumerate(cards_config):
            card = self.create_stat_card(cards_frame, title, "0", color, icon)
            card.grid(row=0, column=i, padx=8, sticky='ew')
            cards_frame.grid_columnconfigure(i, weight=1)
            self.stat_cards[key] = card

    def create_stat_card(self, parent, title, value, color, icon):
        """Create a single statistics card with modern styling and shadow"""
        # Outer frame for shadow effect
        shadow_frame = tk.Frame(parent, bg=self.colors['bg'])

        # Inner card with rounded appearance
        card = tk.Frame(
            shadow_frame,
            bg=self.colors['card_bg'],
            relief=tk.FLAT,
            borderwidth=0,
            highlightbackground=self.colors['border'],
            highlightthickness=2
        )
        card.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        card.grid_propagate(False)

        # Colored accent bar at top
        accent_bar = tk.Frame(card, bg=color, height=4)
        accent_bar.pack(fill=tk.X)

        # Icon and title
        header_frame = tk.Frame(card, bg=self.colors['card_bg'])
        header_frame.pack(fill=tk.X, padx=20, pady=(18, 5))

        # Circular icon background with lightened color
        light_bg = self.lighten_color(color, 0.85)
        icon_bg = tk.Frame(header_frame, bg=light_bg, width=40, height=40)
        icon_bg.pack(side=tk.LEFT)
        icon_bg.pack_propagate(False)

        icon_label = tk.Label(
            icon_bg,
            text=icon,
            font=('Segoe UI', 16, 'bold'),
            bg=light_bg,
            fg=color
        )
        icon_label.place(relx=0.5, rely=0.5, anchor='center')

        title_label = tk.Label(
            header_frame,
            text=title,
            font=('Segoe UI', 10),
            bg=self.colors['card_bg'],
            fg=self.colors['text_light']
        )
        title_label.pack(side=tk.LEFT, padx=(12, 0))

        # Value with larger, bolder font
        value_label = tk.Label(
            card,
            text=value,
            font=('Segoe UI', 36, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text']
        )
        value_label.pack(pady=(8, 22))

        # Store reference to value label for updates
        shadow_frame.value_label = value_label

        # Add subtle hover effect (only change color, not thickness)
        def on_enter(e):
            card.config(highlightbackground=color)

        def on_leave(e):
            card.config(highlightbackground=self.colors['border'])

        card.bind('<Enter>', on_enter)
        card.bind('<Leave>', on_leave)

        return shadow_frame

    def create_learner_section(self, parent):
        """Create learner table section"""
        section = tk.Frame(parent, bg=self.colors['bg'])
        section.pack(fill=tk.BOTH, expand=True)

        # Section header with search
        header_frame = tk.Frame(section, bg=self.colors['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 10))

        section_title = tk.Label(
            header_frame,
            text="All SOR Requests",
            font=('Segoe UI', 18, 'bold'),
            bg=self.colors['bg'],
            fg=self.colors['text']
        )
        section_title.pack(side=tk.LEFT)

        # Search and filter controls with modern styling
        search_frame = tk.Frame(header_frame, bg=self.colors['bg'])
        search_frame.pack(side=tk.RIGHT)

        # Search icon and input
        search_container = tk.Frame(search_frame, bg='white', relief=tk.SOLID, borderwidth=1)
        search_container.pack(side=tk.LEFT, padx=(0, 10))

        search_icon = tk.Label(
            search_container,
            text="🔍",
            font=('Segoe UI', 10),
            bg='white',
            fg=self.colors['text_light']
        )
        search_icon.pack(side=tk.LEFT, padx=(8, 4))

        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.filter_table())

        search_entry = tk.Entry(
            search_container,
            textvariable=self.search_var,
            font=('Segoe UI', 10),
            width=28,
            relief=tk.FLAT,
            borderwidth=0,
            bg='white',
            fg=self.colors['text']
        )
        search_entry.pack(side=tk.LEFT, padx=(0, 8), pady=6)

        # Add placeholder text
        def add_placeholder():
            if not self.search_var.get():
                search_entry.config(fg=self.colors['text_lighter'])
                search_entry.insert(0, "Search by name or email...")

        def remove_placeholder(event):
            if search_entry.get() == "Search by name or email...":
                search_entry.delete(0, tk.END)
                search_entry.config(fg=self.colors['text'])

        def restore_placeholder(event):
            if not search_entry.get():
                add_placeholder()

        search_entry.bind('<FocusIn>', remove_placeholder)
        search_entry.bind('<FocusOut>', restore_placeholder)
        add_placeholder()

        # Add focus border effect
        def on_search_focus_in(event):
            search_container.config(highlightbackground=self.colors['primary'], highlightthickness=2, relief=tk.SOLID)

        def on_search_focus_out(event):
            search_container.config(highlightbackground=self.colors['border'], highlightthickness=1, relief=tk.SOLID)

        search_entry.bind('<FocusIn>', lambda e: [remove_placeholder(e), on_search_focus_in(e)])
        search_entry.bind('<FocusOut>', lambda e: [restore_placeholder(e), on_search_focus_out(e)])

        # Status filter with label
        filter_container = tk.Frame(search_frame, bg=self.colors['bg'])
        filter_container.pack(side=tk.LEFT)

        tk.Label(
            filter_container,
            text="Status:",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['bg'],
            fg=self.colors['text']
        ).pack(side=tk.LEFT, padx=(0, 8))

        # Style the combobox
        style = ttk.Style()
        style.configure('Custom.TCombobox', padding=5)

        self.status_filter = ttk.Combobox(
            filter_container,
            values=['All', 'Pending', 'Signature Sent', 'Signed', 'Uploaded', 'Failed'],
            state='readonly',
            width=16,
            font=('Segoe UI', 10),
            style='Custom.TCombobox'
        )
        self.status_filter.set('All')
        self.status_filter.bind('<<ComboboxSelected>>', lambda e: self.filter_table())
        self.status_filter.pack(side=tk.LEFT)

        # Table container with white background and border
        table_container = tk.Frame(section, bg='white', relief=tk.SOLID, borderwidth=1, highlightbackground=self.colors['border'], highlightthickness=1)
        table_container.pack(fill=tk.BOTH, expand=True, pady=(0, 0))

        table_frame = tk.Frame(table_container, bg='white')
        table_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # Style the Treeview with modern appearance
        style = ttk.Style()
        style.theme_use('clam')

        # Configure Treeview style
        style.configure("Treeview",
            background="white",
            foreground=self.colors['text'],
            rowheight=35,
            fieldbackground="white",
            borderwidth=0,
            font=('Segoe UI', 10)
        )

        style.configure("Treeview.Heading",
            background=self.colors['bg'],
            foreground=self.colors['text'],
            relief=tk.FLAT,
            borderwidth=1,
            font=('Segoe UI', 10, 'bold')
        )

        style.map('Treeview.Heading',
            background=[('active', self.colors['border'])]
        )

        # Create Treeview
        columns = ('ID', 'Learner Name', 'Email', 'Status', 'Score', 'Created', 'Last Updated')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)

        # Define column headings and widths
        col_widths = {'ID': 60, 'Learner Name': 220, 'Email': 240, 'Status': 140, 'Score': 90, 'Created': 150, 'Last Updated': 150}

        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_column(c))
            self.tree.column(col, width=col_widths.get(col, 100), anchor='w' if col in ['Learner Name', 'Email'] else 'center')

        # Modern scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Grid layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Configure tags for modern row colors with better contrast
        self.tree.tag_configure('pending', background='#FFF4ED', foreground=self.colors['text'])
        self.tree.tag_configure('pdf_generated', background='#FFF4ED', foreground=self.colors['text'])
        self.tree.tag_configure('signature_sent', background='#FEF3C7', foreground=self.colors['text'])
        self.tree.tag_configure('signed', background='#ECFDF5', foreground=self.colors['text'])
        self.tree.tag_configure('uploaded', background='#D1FAE5', foreground=self.colors['text'])
        self.tree.tag_configure('failed', background='#FEE2E2', foreground=self.colors['text'])

        # Double-click to view details
        self.tree.bind('<Double-1>', self.show_details)

        # Store all data for filtering
        self.all_requests = []

    def load_initial_data(self):
        """Load initial data in background to prevent GUI freeze"""
        def load_in_background():
            self.refresh_data()

        # Run in background thread
        thread = threading.Thread(target=load_in_background, daemon=True)
        thread.start()

    def refresh_data(self):
        """Refresh all dashboard data"""
        try:
            # Update statistics
            stats = dashboard_db.get_dashboard_stats()
            for key, card in self.stat_cards.items():
                card.value_label.config(text=str(stats.get(key, 0)))

            # Update table
            self.all_requests = dashboard_db.get_all_sor_requests(limit=1000)
            self.filter_table()

            # Update timestamp
            self.last_updated_label.config(text=f"Last updated: {datetime.now().strftime('%H:%M:%S')}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh data: {e}")

    def filter_table(self):
        """Filter table based on search and status"""
        # Check if tree exists (it's created after search box)
        if not hasattr(self, 'tree'):
            return

        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        search_term = self.search_var.get().lower()
        status_filter = self.status_filter.get()

        # Ignore placeholder text
        if search_term == "search by name or email...":
            search_term = ""

        for request in self.all_requests:
            # Apply search filter
            if search_term:
                if search_term not in request['learner_name'].lower() and \
                   search_term not in (request.get('learner_email') or '').lower():
                    continue

            # Apply status filter
            if status_filter != 'All':
                status_map = {
                    'Pending': 'pending',
                    'Signature Sent': 'signature_sent',
                    'Signed': ['pdf_generated', 'signed'],  # Combine both statuses
                    'Uploaded': 'uploaded',
                    'Failed': 'failed'
                }
                filter_status = status_map.get(status_filter)
                # Handle both single status and list of statuses
                if isinstance(filter_status, list):
                    if request['status'] not in filter_status:
                        continue
                else:
                    if request['status'] != filter_status:
                        continue

            # Format score properly
            score_value = request.get('overall_score')
            if score_value is not None:
                # Handle both float and already-formatted strings
                try:
                    score_display = f"{float(score_value):.2f}%"
                except (ValueError, TypeError):
                    score_display = 'N/A'
            else:
                score_display = 'N/A'

            # Insert into tree
            values = (
                request['id'],
                request['learner_name'],
                request.get('learner_email', 'N/A'),
                request['status'].replace('_', ' ').title(),
                score_display,
                request['created_at'].strftime('%Y-%m-%d %H:%M') if request['created_at'] else 'N/A',
                request['updated_at'].strftime('%Y-%m-%d %H:%M') if request['updated_at'] else 'N/A'
            )
            self.tree.insert('', 'end', values=values, tags=(request['status'],))

    def sort_column(self, col):
        """Sort table by column"""
        # This is a placeholder - implement if needed
        pass

    def show_details(self, event):
        """Show detailed view of selected SOR request"""
        selection = self.tree.selection()
        if not selection:
            return

        item = self.tree.item(selection[0])
        sor_id = item['values'][0]

        # Create details window
        details_window = tk.Toplevel(self.root)
        details_window.title(f"SOR Request Details - ID: {sor_id}")
        details_window.geometry("800x600")
        details_window.configure(bg=self.colors['bg'])

        # Get full request data
        request = dashboard_db.get_sor_request(sor_id)
        audit_log = dashboard_db.get_audit_log(sor_id)

        # Request details
        details_frame = tk.LabelFrame(details_window, text="Request Information", font=('Arial', 12, 'bold'), bg=self.colors['card_bg'], padx=20, pady=15)
        details_frame.pack(fill=tk.X, padx=20, pady=10)

        # Format score properly
        score_value = request.get('overall_score')
        if score_value is not None:
            try:
                score_display = f"{float(score_value):.2f}%"
            except (ValueError, TypeError):
                score_display = 'N/A'
        else:
            score_display = 'N/A'

        details_text = f"""
Learner ID: {request['learner_id']}
Learner Name: {request['learner_name']}
Email: {request.get('learner_email', 'N/A')}
Status: {request['status'].replace('_', ' ').title()}
Overall Score: {score_display}
PDF Path: {request.get('pdf_path', 'N/A')}
Signature Request ID: {request.get('signature_request_id', 'N/A')}
Created: {request['created_at']}
Last Updated: {request['updated_at']}
        """

        tk.Label(details_frame, text=details_text, justify=tk.LEFT, bg=self.colors['card_bg'], font=('Arial', 10)).pack(anchor='w')

        # Moodle Status Section
        moodle_frame = tk.LabelFrame(details_window, text="Moodle Status", font=('Arial', 12, 'bold'), bg=self.colors['card_bg'], padx=20, pady=15)
        moodle_frame.pack(fill=tk.X, padx=20, pady=10)

        # Moodle buttons and status
        moodle_btn_frame = tk.Frame(moodle_frame, bg=self.colors['card_bg'])
        moodle_btn_frame.pack(fill=tk.X)

        # Check Moodle button
        check_moodle_btn = tk.Button(
            moodle_btn_frame,
            text="Check Moodle Status",
            command=lambda: self.check_moodle_status(request, moodle_status_label),
            bg=self.colors['primary'],
            fg='white',
            font=('Arial', 10, 'bold'),
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor='hand2'
        )
        check_moodle_btn.pack(side=tk.LEFT, padx=5)

        # View in Moodle button
        view_moodle_btn = tk.Button(
            moodle_btn_frame,
            text="View in Moodle",
            command=lambda: self.open_moodle_assignment(request),
            bg=self.colors['success'],
            fg='white',
            font=('Arial', 10, 'bold'),
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor='hand2'
        )
        view_moodle_btn.pack(side=tk.LEFT, padx=5)

        # Status label
        moodle_status_label = tk.Label(
            moodle_frame,
            text="Click 'Check Moodle Status' to verify submission",
            bg=self.colors['card_bg'],
            fg=self.colors['text_light'],
            font=('Arial', 10),
            wraplength=700,
            justify=tk.LEFT
        )
        moodle_status_label.pack(anchor='w', pady=(10, 0))

        # Moodle Grading Section
        grading_frame = tk.LabelFrame(details_window, text="Moodle Grading", font=('Arial', 12, 'bold'), bg=self.colors['card_bg'], padx=20, pady=15)
        grading_frame.pack(fill=tk.X, padx=20, pady=10)

        # Grade input row
        grade_input_frame = tk.Frame(grading_frame, bg=self.colors['card_bg'])
        grade_input_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(grade_input_frame, text="Grade (%):", font=('Arial', 10, 'bold'), bg=self.colors['card_bg']).pack(side=tk.LEFT)

        # Pre-fill with SOR score if available
        grade_var = tk.StringVar()
        if score_value is not None:
            try:
                grade_var.set(f"{float(score_value):.2f}")
            except:
                grade_var.set("")

        grade_entry = tk.Entry(grade_input_frame, textvariable=grade_var, font=('Arial', 10), width=10)
        grade_entry.pack(side=tk.LEFT, padx=(10, 20))

        # Sync Grade button
        sync_grade_btn = tk.Button(
            grade_input_frame,
            text="Sync Grade to Moodle",
            command=lambda: self.sync_grade_to_moodle(request, grade_var.get(), grading_status_label),
            bg=self.colors['primary'],
            fg='white',
            font=('Arial', 10, 'bold'),
            relief=tk.FLAT,
            padx=15,
            pady=6,
            cursor='hand2'
        )
        sync_grade_btn.pack(side=tk.LEFT, padx=5)

        # Use SOR Score button
        use_sor_btn = tk.Button(
            grade_input_frame,
            text="Use SOR Score",
            command=lambda: grade_var.set(f"{float(score_value):.2f}" if score_value else ""),
            bg=self.colors['secondary'],
            fg='white',
            font=('Arial', 10),
            relief=tk.FLAT,
            padx=10,
            pady=6,
            cursor='hand2'
        )
        use_sor_btn.pack(side=tk.LEFT, padx=5)

        # Feedback row
        feedback_frame = tk.Frame(grading_frame, bg=self.colors['card_bg'])
        feedback_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(feedback_frame, text="Feedback:", font=('Arial', 10, 'bold'), bg=self.colors['card_bg']).pack(anchor='w')

        feedback_text = tk.Text(feedback_frame, font=('Arial', 10), height=3, width=60)
        feedback_text.pack(fill=tk.X, pady=(5, 0))
        feedback_text.insert('1.0', f"SOR Assessment completed. Score: {score_display}")

        # Grading status label
        grading_status_label = tk.Label(
            grading_frame,
            text="Enter grade and click 'Sync Grade to Moodle' to update Moodle gradebook",
            bg=self.colors['card_bg'],
            fg=self.colors['text_light'],
            font=('Arial', 10),
            wraplength=700,
            justify=tk.LEFT
        )
        grading_status_label.pack(anchor='w', pady=(5, 0))

        # Store feedback_text reference for sync function
        sync_grade_btn.config(command=lambda: self.sync_grade_to_moodle(
            request, grade_var.get(), grading_status_label, feedback_text.get('1.0', tk.END).strip()
        ))

        # Audit log
        log_frame = tk.LabelFrame(details_window, text="Activity Log", font=('Arial', 12, 'bold'), bg=self.colors['card_bg'], padx=20, pady=15)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        log_text = scrolledtext.ScrolledText(log_frame, height=15, font=('Courier', 9))
        log_text.pack(fill=tk.BOTH, expand=True)

        for entry in audit_log:
            log_line = f"[{entry['created_at']}] {entry['action']} - {entry['status']}\n"
            if entry.get('details'):
                log_line += f"  Details: {entry['details']}\n"
            log_text.insert(tk.END, log_line)

        log_text.config(state=tk.DISABLED)

    def check_moodle_status(self, request, status_label):
        """Check Moodle submission status"""
        status_label.config(text="[...] Checking Moodle... Please wait...", fg=self.colors['primary'])
        self.root.update()

        try:
            learner_name = request['learner_name']
            learner_id = request.get('learner_id')
            assignment_id = request.get('assignment_id')

            if not assignment_id:
                # Try to get assignment ID from config
                assignment_id = config.ASSIGNMENT_COURSEMODULE_ID
                status_label.config(
                    text="[!] Using default assignment ID from config. Update database with correct assignment_id for accurate results.",
                    fg=self.colors['warning']
                )

            # Verify submission (pass learner_id to avoid API permission issues)
            result = moodle_service.verify_submission(learner_name, assignment_id, learner_id)

            if result['found']:
                status_text = f"[OK] Submission Found!\n"
                status_text += f"Status: {result['status']}\n"
                if result.get('timemodified'):
                    modified_time = datetime.fromtimestamp(result['timemodified'])
                    status_text += f"Last Modified: {modified_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                status_text += f"User ID: {result.get('userid', 'N/A')}\n"
                status_text += f"\n{result['message']}"

                status_label.config(text=status_text, fg=self.colors['success'])

                # Log to audit trail
                dashboard_db.log_action(
                    request['id'],
                    'moodle_verification',
                    f"Verified in Moodle - Status: {result['status']}",
                    'success'
                )
            else:
                status_text = f"[X] {result['message']}\n"
                status_text += f"Status: {result['status']}"
                status_label.config(text=status_text, fg=self.colors['danger'])

                dashboard_db.log_action(
                    request['id'],
                    'moodle_verification',
                    result['message'],
                    'warning'
                )

        except Exception as e:
            status_label.config(
                text=f"[X] Error checking Moodle: {str(e)}",
                fg=self.colors['danger']
            )

    def open_moodle_assignment(self, request):
        """Open Moodle assignment in browser"""
        try:
            url = moodle_service.get_moodle_url_for_assignment(config.ASSIGNMENT_COURSEMODULE_ID)

            # Ask user confirmation
            if messagebox.askyesno(
                "Open Moodle",
                f"This will open Moodle in your browser:\n\n{url}\n\nYou may need to login to Moodle.\n\nContinue?"
            ):
                webbrowser.open(url)

                # Log action
                dashboard_db.log_action(
                    request['id'],
                    'open_moodle_assignment',
                    f"Opened assignment in browser: {url}",
                    'success'
                )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Moodle: {e}")

    def sync_grade_to_moodle(self, request, grade_str, status_label, feedback=''):
        """Sync grade to Moodle gradebook"""
        status_label.config(text="[...] Syncing grade to Moodle...", fg=self.colors['primary'])
        self.root.update()

        try:
            # Validate grade
            try:
                grade = float(grade_str)
                if grade < 0 or grade > 100:
                    raise ValueError("Grade must be between 0 and 100")
            except ValueError as e:
                status_label.config(text=f"[X] Invalid grade: {e}", fg=self.colors['danger'])
                return

            learner_id = request.get('learner_id')
            if not learner_id:
                status_label.config(text="[X] No learner ID found in database", fg=self.colors['danger'])
                return

            # Get assignment ID
            assignment_id = request.get('assignment_id')
            if not assignment_id:
                # Get assignment info from config
                assignment_info = moodle_service.get_assignment_info(config.ASSIGNMENT_COURSEMODULE_ID)
                if assignment_info:
                    assignment_id = assignment_info.get('id')
                else:
                    status_label.config(
                        text="[X] Could not find assignment. Check ASSIGNMENT_COURSEMODULE_ID in config.",
                        fg=self.colors['danger']
                    )
                    return

            # Sync grade to Moodle
            result = moodle_service.sync_grade_to_moodle(
                learner_id=learner_id,
                assignment_id=assignment_id,
                score=grade,
                feedback=feedback if feedback else None
            )

            if result.get('success'):
                status_text = f"[OK] Grade synced successfully!\n"
                status_text += f"Grade: {grade}%\n"
                status_text += f"User ID: {learner_id}\n"
                status_text += f"Assignment ID: {assignment_id}"
                status_label.config(text=status_text, fg=self.colors['success'])

                # Log to audit trail
                dashboard_db.log_action(
                    request['id'],
                    'moodle_grade_sync',
                    f"Grade synced to Moodle: {grade}%",
                    'success'
                )

                messagebox.showinfo("Success", f"Grade {grade}% synced to Moodle successfully!")
            else:
                status_text = f"[X] Failed to sync grade\n{result.get('message', 'Unknown error')}"
                status_label.config(text=status_text, fg=self.colors['danger'])

                dashboard_db.log_action(
                    request['id'],
                    'moodle_grade_sync',
                    f"Failed to sync grade: {result.get('message')}",
                    'failed'
                )

        except Exception as e:
            status_label.config(
                text=f"[X] Error syncing grade: {str(e)}",
                fg=self.colors['danger']
            )

    def bulk_sync_grades(self):
        """Bulk sync all SOR grades to Moodle"""
        if not messagebox.askyesno(
            "Bulk Grade Sync",
            "This will sync all uploaded SOR grades to Moodle.\n\nAre you sure you want to continue?"
        ):
            return

        try:
            # Get all uploaded requests with scores
            requests = dashboard_db.get_all_sor_requests(limit=1000)
            uploaded_requests = [r for r in requests if r['status'] == 'uploaded' and r.get('overall_score')]

            if not uploaded_requests:
                messagebox.showinfo("No Records", "No uploaded SOR requests with scores found.")
                return

            # Get assignment ID
            assignment_info = moodle_service.get_assignment_info(config.ASSIGNMENT_COURSEMODULE_ID)
            if not assignment_info:
                messagebox.showerror("Error", "Could not find assignment in Moodle.")
                return

            assignment_id = assignment_info.get('id')

            # Prepare grades list
            grades = []
            for req in uploaded_requests:
                grades.append({
                    'userid': req['learner_id'],
                    'grade': float(req['overall_score']),
                    'feedback': f"SOR Assessment completed. Score: {req['overall_score']}%"
                })

            # Bulk sync
            result = moodle_service.bulk_grade_submissions(assignment_id, grades)

            message = f"Bulk sync completed!\n\n"
            message += f"Total processed: {result['total_processed']}\n"
            message += f"Successful: {result['success_count']}\n"
            message += f"Failed: {result['fail_count']}"

            if result['success']:
                messagebox.showinfo("Bulk Sync Complete", message)
            else:
                messagebox.showwarning("Bulk Sync Partial", message)

        except Exception as e:
            messagebox.showerror("Error", f"Bulk sync failed: {e}")


def main():
    """Launch the dashboard"""
    root = tk.Tk()
    app = SORDashboard(root)
    root.mainloop()


if __name__ == "__main__":
    main()
