"""
MindWorx SOR Automation System - Main Launcher
A user-friendly GUI to run all system functions with button clicks
"""
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
import threading
from datetime import datetime

class SORLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("MindWorx SOR Automation System")

        # Get screen dimensions
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Window size
        window_width = 800
        window_height = 700

        # Center the window
        x_position = int((screen_width - window_width) / 2)
        y_position = int((screen_height - window_height) / 2)

        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        self.root.resizable(False, False)
        self.root.configure(bg='#E8EDF2')

        # MindWorx Colors
        self.colors = {
            'primary': '#F26522',
            'primary_dark': '#D94F1A',
            'primary_light': '#FF8A5B',
            'success': '#10B981',
            'success_light': '#34D399',
            'warning': '#F59E0B',
            'danger': '#EF4444',
            'secondary': '#3D3D3D',
            'bg': '#E8EDF2',
            'card_bg': '#FFFFFF',
            'text': '#1F2937',
            'text_light': '#6B7280',
            'border': '#E5E7EB',
        }

        self.setup_ui()

    def setup_ui(self):
        """Setup the main UI"""
        # Header
        self.create_header()

        # Main content
        self.create_main_content()

        # Status bar
        self.create_status_bar()

    def create_header(self):
        """Create header with logo and title"""
        header = tk.Frame(self.root, bg='white', height=100)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        # Logo and title container
        title_frame = tk.Frame(header, bg='white')
        title_frame.place(relx=0.5, rely=0.5, anchor='center')

        # Try to load logo
        try:
            from PIL import Image, ImageTk
            logo_path = r"C:\Users\10028897\Desktop\Mindworx_dashboard.png"
            logo_image = Image.open(logo_path)
            logo_image = logo_image.resize((200, 38), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_image)

            logo_label = tk.Label(title_frame, image=self.logo_photo, bg='white')
            logo_label.pack(side=tk.LEFT, padx=(0, 20))
        except:
            # Fallback text
            tk.Label(
                title_frame,
                text="MINDWORX",
                font=('Arial', 24, 'bold'),
                bg='white',
                fg=self.colors['primary']
            ).pack(side=tk.LEFT, padx=(0, 20))

        tk.Label(
            title_frame,
            text="SOR AUTOMATION",
            font=('Arial', 24, 'bold'),
            bg='white',
            fg=self.colors['secondary']
        ).pack(side=tk.LEFT)

    def create_main_content(self):
        """Create main content area with action buttons"""
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)

        # Welcome message
        tk.Label(
            main_frame,
            text="Welcome to the SOR Automation System",
            font=('Segoe UI', 14),
            bg=self.colors['bg'],
            fg=self.colors['text_light']
        ).pack(pady=(0, 20))

        # Action buttons grid
        buttons_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        buttons_frame.pack(fill=tk.BOTH, expand=True)

        # Configure grid
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)

        # Button configurations
        buttons = [
            {
                'title': 'Open Dashboard',
                'desc': 'View all SOR requests and status',
                'icon': '[D]',
                'color': self.colors['primary'],
                'command': self.open_dashboard,
                'row': 0, 'col': 0
            },
            {
                'title': 'Process New Requests',
                'desc': 'Generate PDFs for pending SORs',
                'icon': '[+]',
                'color': self.colors['success'],
                'command': self.process_new_requests,
                'row': 0, 'col': 1
            },
            {
                'title': 'Check Signatures',
                'desc': 'Check status of pending signatures',
                'icon': '[✎]',
                'color': self.colors['warning'],
                'command': self.check_signatures,
                'row': 1, 'col': 0
            },
            {
                'title': 'Upload to Moodle',
                'desc': 'Upload signed documents to Moodle',
                'icon': '[UP]',
                'color': '#3B82F6',
                'command': self.upload_to_moodle,
                'row': 1, 'col': 1
            },
            {
                'title': 'Sync Grades',
                'desc': 'Sync SOR grades to Moodle gradebook',
                'icon': '[G]',
                'color': '#8B5CF6',
                'command': self.sync_grades,
                'row': 2, 'col': 0
            },
            {
                'title': 'Run Full Automation',
                'desc': 'Run complete SOR processing cycle',
                'icon': '[>>]',
                'color': self.colors['secondary'],
                'command': self.run_full_automation,
                'row': 2, 'col': 1
            },
        ]

        for btn_config in buttons:
            self.create_action_button(buttons_frame, btn_config)

        # Quick actions section
        self.create_quick_actions(main_frame)

    def create_action_button(self, parent, config):
        """Create a single action button card"""
        # Card frame
        card = tk.Frame(
            parent,
            bg=self.colors['card_bg'],
            highlightbackground=self.colors['border'],
            highlightthickness=2
        )
        card.grid(row=config['row'], column=config['col'], padx=10, pady=10, sticky='nsew')

        # Accent bar
        accent = tk.Frame(card, bg=config['color'], height=4)
        accent.pack(fill=tk.X)

        # Content
        content = tk.Frame(card, bg=self.colors['card_bg'])
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        # Icon and title row
        header = tk.Frame(content, bg=self.colors['card_bg'])
        header.pack(fill=tk.X)

        # Icon
        icon_label = tk.Label(
            header,
            text=config['icon'],
            font=('Segoe UI', 18, 'bold'),
            bg=self.colors['card_bg'],
            fg=config['color']
        )
        icon_label.pack(side=tk.LEFT)

        # Title
        tk.Label(
            header,
            text=config['title'],
            font=('Segoe UI', 14, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text']
        ).pack(side=tk.LEFT, padx=(10, 0))

        # Description
        tk.Label(
            content,
            text=config['desc'],
            font=('Segoe UI', 10),
            bg=self.colors['card_bg'],
            fg=self.colors['text_light']
        ).pack(anchor='w', pady=(5, 10))

        # Action button
        btn = tk.Button(
            content,
            text="Launch",
            command=config['command'],
            bg=config['color'],
            fg='white',
            font=('Segoe UI', 10, 'bold'),
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor='hand2',
            activebackground=self.colors['primary_dark'],
            activeforeground='white'
        )
        btn.pack(anchor='w')

        # Hover effects
        def on_enter(e):
            card.config(highlightbackground=config['color'])

        def on_leave(e):
            card.config(highlightbackground=self.colors['border'])

        card.bind('<Enter>', on_enter)
        card.bind('<Leave>', on_leave)
        for widget in [content, header, icon_label]:
            widget.bind('<Enter>', on_enter)
            widget.bind('<Leave>', on_leave)

    def create_quick_actions(self, parent):
        """Create quick actions section"""
        quick_frame = tk.Frame(parent, bg=self.colors['bg'])
        quick_frame.pack(fill=tk.X, pady=(20, 0))

        tk.Label(
            quick_frame,
            text="Quick Actions:",
            font=('Segoe UI', 11, 'bold'),
            bg=self.colors['bg'],
            fg=self.colors['text']
        ).pack(side=tk.LEFT, padx=(0, 15))

        quick_buttons = [
            ("View Logs", self.view_logs, self.colors['text_light']),
            ("Settings", self.open_settings, self.colors['text_light']),
            ("Help", self.show_help, self.colors['primary']),
        ]

        for text, command, color in quick_buttons:
            btn = tk.Button(
                quick_frame,
                text=text,
                command=command,
                bg=self.colors['card_bg'],
                fg=color,
                font=('Segoe UI', 10),
                relief=tk.FLAT,
                padx=15,
                pady=5,
                cursor='hand2',
                borderwidth=1,
                highlightbackground=self.colors['border']
            )
            btn.pack(side=tk.LEFT, padx=5)

    def create_status_bar(self):
        """Create status bar at bottom"""
        status_frame = tk.Frame(self.root, bg='white', height=40)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)

        self.status_label = tk.Label(
            status_frame,
            text="Ready",
            font=('Segoe UI', 10),
            bg='white',
            fg=self.colors['text_light']
        )
        self.status_label.pack(side=tk.LEFT, padx=20, pady=10)

        # Version
        tk.Label(
            status_frame,
            text="v1.0.0",
            font=('Segoe UI', 9),
            bg='white',
            fg=self.colors['text_light']
        ).pack(side=tk.RIGHT, padx=20, pady=10)

    def update_status(self, message, color=None):
        """Update status bar message"""
        self.status_label.config(text=message)
        if color:
            self.status_label.config(fg=color)
        self.root.update()

    # ===== Action Functions =====

    def open_dashboard(self):
        """Open the SOR Dashboard"""
        self.update_status("Opening Dashboard...", self.colors['primary'])
        try:
            # Run dashboard in separate process
            subprocess.Popen([sys.executable, "run_dashboard.py"],
                           cwd=os.path.dirname(os.path.abspath(__file__)))
            self.update_status("Dashboard opened", self.colors['success'])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open dashboard: {e}")
            self.update_status("Error opening dashboard", self.colors['danger'])

    def process_new_requests(self):
        """Process new SOR requests"""
        self.update_status("Processing new requests...", self.colors['primary'])

        def run_process():
            try:
                result = subprocess.run(
                    [sys.executable, "-c",
                     "from src.main import process_pending_requests; process_pending_requests()"],
                    cwd=os.path.dirname(os.path.abspath(__file__)),
                    capture_output=True,
                    text=True,
                    timeout=300
                )

                self.root.after(0, lambda: self.show_process_result(
                    "Process New Requests",
                    result.stdout + result.stderr,
                    result.returncode == 0
                ))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

        thread = threading.Thread(target=run_process, daemon=True)
        thread.start()

    def check_signatures(self):
        """Check pending signature status"""
        self.update_status("Checking signatures...", self.colors['primary'])

        def run_check():
            try:
                result = subprocess.run(
                    [sys.executable, "-c",
                     "from src.main import check_signature_status; check_signature_status()"],
                    cwd=os.path.dirname(os.path.abspath(__file__)),
                    capture_output=True,
                    text=True,
                    timeout=120
                )

                self.root.after(0, lambda: self.show_process_result(
                    "Check Signatures",
                    result.stdout + result.stderr,
                    result.returncode == 0
                ))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

        thread = threading.Thread(target=run_check, daemon=True)
        thread.start()

    def upload_to_moodle(self):
        """Upload signed documents to Moodle"""
        self.update_status("Uploading to Moodle...", self.colors['primary'])

        def run_upload():
            try:
                result = subprocess.run(
                    [sys.executable, "-c",
                     "from src.main import upload_signed_documents; upload_signed_documents()"],
                    cwd=os.path.dirname(os.path.abspath(__file__)),
                    capture_output=True,
                    text=True,
                    timeout=300
                )

                self.root.after(0, lambda: self.show_process_result(
                    "Upload to Moodle",
                    result.stdout + result.stderr,
                    result.returncode == 0
                ))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

        thread = threading.Thread(target=run_upload, daemon=True)
        thread.start()

    def sync_grades(self):
        """Sync grades to Moodle"""
        if not messagebox.askyesno("Sync Grades",
            "This will sync all uploaded SOR grades to Moodle.\n\nContinue?"):
            return

        self.update_status("Syncing grades...", self.colors['primary'])

        def run_sync():
            try:
                result = subprocess.run(
                    [sys.executable, "-c", """
from src.dashboard_db import dashboard_db
from src.moodle_service import moodle_service
from src.config import config

requests = dashboard_db.get_all_sor_requests(limit=1000)
uploaded = [r for r in requests if r['status'] == 'uploaded' and r.get('overall_score')]

if not uploaded:
    print("No uploaded SOR requests with scores found.")
else:
    assignment_info = moodle_service.get_assignment_info(config.ASSIGNMENT_COURSEMODULE_ID)
    if assignment_info:
        assignment_id = assignment_info.get('id')
        grades = [{'userid': r['learner_id'], 'grade': float(r['overall_score'])} for r in uploaded]
        result = moodle_service.bulk_grade_submissions(assignment_id, grades)
        print(f"Synced {result['success_count']}/{result['total_processed']} grades")
    else:
        print("Could not find assignment in Moodle")
"""],
                    cwd=os.path.dirname(os.path.abspath(__file__)),
                    capture_output=True,
                    text=True,
                    timeout=300
                )

                self.root.after(0, lambda: self.show_process_result(
                    "Sync Grades",
                    result.stdout + result.stderr,
                    result.returncode == 0
                ))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

        thread = threading.Thread(target=run_sync, daemon=True)
        thread.start()

    def run_full_automation(self):
        """Run the complete automation cycle"""
        if not messagebox.askyesno("Full Automation",
            "This will run the complete SOR automation cycle:\n\n"
            "1. Process new requests (generate PDFs)\n"
            "2. Check signature status\n"
            "3. Upload signed documents\n"
            "4. Sync grades to Moodle\n\n"
            "Continue?"):
            return

        self.update_status("Running full automation...", self.colors['primary'])

        def run_auto():
            try:
                result = subprocess.run(
                    [sys.executable, "run_automation.py"],
                    cwd=os.path.dirname(os.path.abspath(__file__)),
                    capture_output=True,
                    text=True,
                    timeout=600
                )

                self.root.after(0, lambda: self.show_process_result(
                    "Full Automation",
                    result.stdout + result.stderr,
                    result.returncode == 0
                ))
            except subprocess.TimeoutExpired:
                self.root.after(0, lambda: messagebox.showwarning(
                    "Timeout", "Automation process timed out after 10 minutes"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

        thread = threading.Thread(target=run_auto, daemon=True)
        thread.start()

    def view_logs(self):
        """View system logs"""
        log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs", "automation.log")

        if os.path.exists(log_path):
            os.startfile(log_path)
        else:
            messagebox.showinfo("Logs", "No log file found yet.\nLogs are created when automation runs.")

    def open_settings(self):
        """Open settings window"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("500x400")
        settings_window.configure(bg=self.colors['bg'])

        tk.Label(
            settings_window,
            text="Settings",
            font=('Segoe UI', 16, 'bold'),
            bg=self.colors['bg'],
            fg=self.colors['text']
        ).pack(pady=20)

        # Settings info
        settings_frame = tk.Frame(settings_window, bg=self.colors['card_bg'])
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        tk.Label(
            settings_frame,
            text="Configuration is managed through the .env file.\n\n"
                 "Key settings:\n"
                 "- MOODLE_URL: Your Moodle server URL\n"
                 "- MOODLE_TOKEN: API token for Moodle\n"
                 "- DB_HOST, DB_USER, DB_PASSWORD: Database settings\n"
                 "- DROPBOX_SIGN_API_KEY: For e-signatures\n\n"
                 "Edit the .env file in the project root to change settings.",
            font=('Segoe UI', 10),
            bg=self.colors['card_bg'],
            fg=self.colors['text'],
            justify=tk.LEFT,
            wraplength=450
        ).pack(padx=20, pady=20, anchor='w')

        # Open .env button
        tk.Button(
            settings_frame,
            text="Open .env File",
            command=lambda: os.startfile(os.path.join(
                os.path.dirname(os.path.abspath(__file__)), ".env")),
            bg=self.colors['primary'],
            fg='white',
            font=('Segoe UI', 10, 'bold'),
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor='hand2'
        ).pack(pady=10)

    def show_help(self):
        """Show help information"""
        help_text = """
MindWorx SOR Automation System - Help

MAIN FUNCTIONS:

[D] Open Dashboard
    View all SOR requests, their status, and manage individual records.
    Double-click any record to see details and sync grades.

[+] Process New Requests
    Generates PDF documents for pending SOR submissions.
    Sends documents for electronic signature.

[✎] Check Signatures
    Checks the status of documents sent for signature.
    Downloads signed documents when available.

[UP] Upload to Moodle
    Uploads signed PDF documents to Moodle assignments.

[G] Sync Grades
    Syncs SOR scores to the Moodle gradebook.

[>>] Run Full Automation
    Runs all steps automatically in sequence.

NEED HELP?
Contact your system administrator or check the documentation.
        """

        help_window = tk.Toplevel(self.root)
        help_window.title("Help")
        help_window.geometry("550x500")
        help_window.configure(bg='white')

        text_widget = tk.Text(
            help_window,
            font=('Consolas', 10),
            bg='white',
            fg=self.colors['text'],
            padx=20,
            pady=20,
            wrap=tk.WORD
        )
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert('1.0', help_text)
        text_widget.config(state=tk.DISABLED)

    def show_process_result(self, title, output, success):
        """Show result of a process in a popup"""
        self.update_status("Ready", self.colors['text_light'])

        result_window = tk.Toplevel(self.root)
        result_window.title(f"{title} - {'Success' if success else 'Error'}")
        result_window.geometry("600x400")
        result_window.configure(bg='white')

        # Status header
        status_color = self.colors['success'] if success else self.colors['danger']
        status_text = "Completed Successfully" if success else "Completed with Errors"

        tk.Label(
            result_window,
            text=status_text,
            font=('Segoe UI', 14, 'bold'),
            bg='white',
            fg=status_color
        ).pack(pady=15)

        # Output text
        text_frame = tk.Frame(result_window, bg='white')
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        text_widget = tk.Text(
            text_frame,
            font=('Consolas', 9),
            bg='#F8F9FA',
            fg=self.colors['text'],
            wrap=tk.WORD
        )
        text_widget.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(text_widget, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)

        text_widget.insert('1.0', output if output.strip() else "No output")
        text_widget.config(state=tk.DISABLED)

        # Close button
        tk.Button(
            result_window,
            text="Close",
            command=result_window.destroy,
            bg=self.colors['primary'],
            fg='white',
            font=('Segoe UI', 10, 'bold'),
            relief=tk.FLAT,
            padx=30,
            pady=8,
            cursor='hand2'
        ).pack(pady=(0, 20))


def main():
    root = tk.Tk()
    app = SORLauncher(root)
    root.mainloop()


if __name__ == "__main__":
    main()
