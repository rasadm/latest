#!/usr/bin/env python3
"""
Enhanced Settings Dashboard with Multilingual Support
GUI for managing application settings including WordPress websites and language configurations
"""

import sys
import os
# Add the parent directory to Python path to find our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import uuid
import os
from datetime import datetime
from core.settings_manager import SettingsManager, WordPressWebsite

class SettingsDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("⚙️ Settings Management")
        self.root.geometry("1200x700")
        self.root.configure(bg='#f8f9fa')
        
        # Initialize settings manager
        self.settings_manager = SettingsManager()
        self.current_website = None
        
        # Create main container
        self.main_container = tk.Frame(self.root, bg='#f8f9fa')
        self.main_container.pack(fill='both', expand=True)
        
        # Create header
        self.create_header()
        
        # Create main content with tabs
        self.create_main_content()
        
        # Load initial data
        self.refresh_websites_list()
        self.load_general_settings()
        self.load_language_settings()
    
    def create_header(self):
        """Create header section"""
        header_frame = tk.Frame(self.main_container, bg='#2c3e50', height=80)
        header_frame.pack(fill='x', padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Header content container
        header_content = tk.Frame(header_frame, bg='#2c3e50')
        header_content.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Back button (left side)
        back_btn = tk.Button(header_content, text="← Back to Dashboard", 
                            command=self.back_to_dashboard,
                            bg='#34495e', fg='white', font=('Arial', 10, 'bold'),
                            relief='flat', padx=20, pady=8,
                            activebackground='#4a6741', activeforeground='white')
        back_btn.pack(side='left', anchor='w')
        
        # Title and subtitle (center)
        title_frame = tk.Frame(header_content, bg='#2c3e50')
        title_frame.pack(side='top', expand=True)
        
        title_label = tk.Label(title_frame, text="⚙️ Settings Management", 
                              font=('Arial', 18, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="Configure WordPress websites, languages, and application settings", 
                                 font=('Arial', 11), fg='#ecf0f1', bg='#2c3e50')
        subtitle_label.pack()
    
    def create_main_content(self):
        """Create main content with tabs"""
        content_frame = tk.Frame(self.main_container, bg='#f8f9fa')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Create tabs
        self.create_wordpress_tab()
        self.create_language_tab()
        self.create_general_settings_tab()
        self.create_backup_tab()
    
    def create_wordpress_tab(self):
        """Create WordPress websites management tab"""
        wp_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(wp_frame, text="🌐 WordPress Websites")
        
        # Main container
        main_wp_frame = tk.Frame(wp_frame, bg='white')
        main_wp_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Left panel - Websites list
        left_panel = tk.Frame(main_wp_frame, bg='white', relief='solid', bd=1, width=400)
        left_panel.pack(side='left', fill='y', padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Websites list header
        list_header = tk.Frame(left_panel, bg='#3498db', height=50)
        list_header.pack(fill='x')
        list_header.pack_propagate(False)
        
        tk.Label(list_header, text="🌐 WordPress Websites", 
                font=('Arial', 12, 'bold'), fg='white', bg='#3498db').pack(expand=True)
        
        # Control buttons
        controls_frame = tk.Frame(left_panel, bg='white')
        controls_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(controls_frame, text="➕ Add Website", 
                 command=self.add_new_website,
                 bg='#27ae60', fg='white', font=('Arial', 10, 'bold'),
                 width=15).pack(side='left', padx=(0, 5))
        
        tk.Button(controls_frame, text="🔄 Refresh", 
                 command=self.refresh_websites_list,
                 bg='#3498db', fg='white', font=('Arial', 10, 'bold'),
                 width=10).pack(side='left')
        
        # Websites listbox
        list_frame = tk.Frame(left_panel, bg='white')
        list_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.websites_listbox = tk.Listbox(list_frame, font=('Arial', 10),
                                          yscrollcommand=scrollbar.set)
        self.websites_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.websites_listbox.yview)
        
        self.websites_listbox.bind('<<ListboxSelect>>', self.on_website_select)
        
        # Right panel - Website details and form
        right_panel = tk.Frame(main_wp_frame, bg='white', relief='solid', bd=1)
        right_panel.pack(side='right', fill='both', expand=True)
        
        # Form header
        form_header = tk.Frame(right_panel, bg='#34495e', height=50)
        form_header.pack(fill='x')
        form_header.pack_propagate(False)
        
        self.form_title_label = tk.Label(form_header, text="📝 Website Configuration", 
                                        font=('Arial', 12, 'bold'), fg='white', bg='#34495e')
        self.form_title_label.pack(expand=True)
        
        # Form content
        form_content = tk.Frame(right_panel, bg='white')
        form_content.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Website form
        self.create_website_form(form_content)
    
    def create_website_form(self, parent):
        """Create website configuration form"""
        # Basic information
        basic_frame = tk.LabelFrame(parent, text="📋 Basic Information", 
                                   font=('Arial', 11, 'bold'), bg='white', padx=15, pady=10)
        basic_frame.pack(fill='x', pady=(0, 15))
        
        # Website name
        tk.Label(basic_frame, text="Website Name:", font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=0, sticky='w', pady=5)
        self.website_name_var = tk.StringVar()
        tk.Entry(basic_frame, textvariable=self.website_name_var, width=40, font=('Arial', 10)).grid(row=0, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        # Website URL
        tk.Label(basic_frame, text="Website URL:", font=('Arial', 10, 'bold'), bg='white').grid(row=1, column=0, sticky='w', pady=5)
        self.website_url_var = tk.StringVar()
        tk.Entry(basic_frame, textvariable=self.website_url_var, width=40, font=('Arial', 10)).grid(row=1, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        # Description
        tk.Label(basic_frame, text="Description:", font=('Arial', 10, 'bold'), bg='white').grid(row=2, column=0, sticky='w', pady=5)
        self.website_desc_var = tk.StringVar()
        tk.Entry(basic_frame, textvariable=self.website_desc_var, width=40, font=('Arial', 10)).grid(row=2, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        basic_frame.columnconfigure(1, weight=1)
        
        # Authentication
        auth_frame = tk.LabelFrame(parent, text="🔐 Authentication", 
                                  font=('Arial', 11, 'bold'), bg='white', padx=15, pady=10)
        auth_frame.pack(fill='x', pady=(0, 15))
        
        # Username
        tk.Label(auth_frame, text="Username:", font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=0, sticky='w', pady=5)
        self.website_username_var = tk.StringVar()
        tk.Entry(auth_frame, textvariable=self.website_username_var, width=40, font=('Arial', 10)).grid(row=0, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        # Application Password
        tk.Label(auth_frame, text="App Password:", font=('Arial', 10, 'bold'), bg='white').grid(row=1, column=0, sticky='w', pady=5)
        self.website_password_var = tk.StringVar()
        self.password_entry = tk.Entry(auth_frame, textvariable=self.website_password_var, width=40, font=('Arial', 10), show='*')
        self.password_entry.grid(row=1, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        # Show/Hide password
        self.show_password_var = tk.BooleanVar()
        show_pass_check = tk.Checkbutton(auth_frame, text="Show password", variable=self.show_password_var,
                                        command=self.toggle_password_visibility,
                                        bg='white', font=('Arial', 9))
        show_pass_check.grid(row=2, column=1, sticky='w', padx=(10, 0), pady=5)
        
        auth_frame.columnconfigure(1, weight=1)
        
        # Status and settings
        status_frame = tk.LabelFrame(parent, text="📊 Status & Settings", 
                                    font=('Arial', 11, 'bold'), bg='white', padx=15, pady=10)
        status_frame.pack(fill='x', pady=(0, 15))
        
        # Active checkbox
        self.website_active_var = tk.BooleanVar(value=True)
        tk.Checkbutton(status_frame, text="Website is active", variable=self.website_active_var,
                      bg='white', font=('Arial', 10)).pack(anchor='w', pady=5)
        
        # Default website checkbox
        self.website_default_var = tk.BooleanVar()
        tk.Checkbutton(status_frame, text="Set as default website", variable=self.website_default_var,
                      bg='white', font=('Arial', 10)).pack(anchor='w', pady=5)
        
        # Test status
        self.test_status_label = tk.Label(status_frame, text="Connection: Not tested", 
                                         font=('Arial', 10), bg='white', fg='#7f8c8d')
        self.test_status_label.pack(anchor='w', pady=5)
        
        # Action buttons
        buttons_frame = tk.Frame(parent, bg='white')
        buttons_frame.pack(fill='x', pady=20)
        
        tk.Button(buttons_frame, text="💾 Save Website", 
                 command=self.save_website,
                 bg='#27ae60', fg='white', font=('Arial', 11, 'bold'),
                 width=15, height=2).pack(side='left', padx=(0, 10))
        
        tk.Button(buttons_frame, text="🧪 Test Connection", 
                 command=self.test_website_connection,
                 bg='#3498db', fg='white', font=('Arial', 11, 'bold'),
                 width=15, height=2).pack(side='left', padx=(0, 10))
        
        tk.Button(buttons_frame, text="🗑️ Delete Website", 
                 command=self.delete_website,
                 bg='#e74c3c', fg='white', font=('Arial', 11, 'bold'),
                 width=15, height=2).pack(side='left', padx=(0, 10))
        
        tk.Button(buttons_frame, text="🔄 Clear Form", 
                 command=self.clear_website_form,
                 bg='#95a5a6', fg='white', font=('Arial', 11, 'bold'),
                 width=15, height=2).pack(side='left')
    
    def toggle_password_visibility(self):
        """Toggle password visibility"""
        if self.show_password_var.get():
            self.password_entry.config(show='')
        else:
            self.password_entry.config(show='*')
    
    def create_language_tab(self):
        """Create language management tab"""
        lang_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(lang_frame, text="🌍 Languages")
        
        # Main container
        main_lang_frame = tk.Frame(lang_frame, bg='white')
        main_lang_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Language overview
        overview_frame = tk.LabelFrame(main_lang_frame, text="🌐 Multilingual Support Overview", 
                                      font=('Arial', 12, 'bold'), bg='white', padx=20, pady=15)
        overview_frame.pack(fill='x', pady=(0, 20))
        
        overview_text = """
This system supports multilingual content generation with cultural and editorial awareness:

• English: Western business context with direct communication style
• فارسی (Farsi/Persian): Persian/Islamic cultural context with respectful, formal tone
• Español (Spanish): Hispanic/Latin cultural context with warm, relationship-focused approach

Each language has its own SEO rules, cultural guidelines, and content templates.
        """
        
        tk.Label(overview_frame, text=overview_text.strip(), 
                font=('Arial', 10), bg='white', justify='left').pack(anchor='w')
        
        # Language settings
        settings_frame = tk.LabelFrame(main_lang_frame, text="🎛️ Language Settings", 
                                      font=('Arial', 12, 'bold'), bg='white', padx=20, pady=15)
        settings_frame.pack(fill='x', pady=(0, 20))
        
        # Default language
        default_lang_frame = tk.Frame(settings_frame, bg='white')
        default_lang_frame.pack(fill='x', pady=10)
        
        tk.Label(default_lang_frame, text="Default Language:", 
                font=('Arial', 11, 'bold'), bg='white').pack(side='left')
        
        self.default_language_var = tk.StringVar(value=self.settings_manager.get_default_language())
        default_lang_combo = ttk.Combobox(default_lang_frame, textvariable=self.default_language_var,
                                         values=["english", "farsi", "spanish"], state="readonly", width=15)
        default_lang_combo.pack(side='left', padx=(10, 0))
        
        # Language status indicators
        status_frame = tk.LabelFrame(main_lang_frame, text="📊 Language Status", 
                                    font=('Arial', 12, 'bold'), bg='white', padx=20, pady=15)
        status_frame.pack(fill='x', pady=(0, 20))
        
        # Create status grid
        status_grid = tk.Frame(status_frame, bg='white')
        status_grid.pack(fill='x')
        
        # Headers
        tk.Label(status_grid, text="Language", font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=0, sticky='w', padx=5, pady=5)
        tk.Label(status_grid, text="Native Name", font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=1, sticky='w', padx=5, pady=5)
        tk.Label(status_grid, text="Cultural Context", font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=2, sticky='w', padx=5, pady=5)
        tk.Label(status_grid, text="Status", font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=3, sticky='w', padx=5, pady=5)
        
        # Language rows
        languages = [
            ("english", "English", "Western Business", "✅ Active"),
            ("farsi", "فارسی", "Persian/Islamic", "✅ Active"),
            ("spanish", "Español", "Hispanic/Latin", "✅ Active")
        ]
        
        for i, (lang_code, native_name, context, status) in enumerate(languages, 1):
            tk.Label(status_grid, text=lang_code.title(), font=('Arial', 10), bg='white').grid(row=i, column=0, sticky='w', padx=5, pady=2)
            tk.Label(status_grid, text=native_name, font=('Arial', 10), bg='white').grid(row=i, column=1, sticky='w', padx=5, pady=2)
            tk.Label(status_grid, text=context, font=('Arial', 10), bg='white').grid(row=i, column=2, sticky='w', padx=5, pady=2)
            tk.Label(status_grid, text=status, font=('Arial', 10), fg='#27ae60', bg='white').grid(row=i, column=3, sticky='w', padx=5, pady=2)
        
        # Cultural guidelines
        guidelines_frame = tk.LabelFrame(main_lang_frame, text="📋 Cultural Guidelines", 
                                        font=('Arial', 12, 'bold'), bg='white', padx=20, pady=15)
        guidelines_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        # Create notebook for language guidelines
        guidelines_notebook = ttk.Notebook(guidelines_frame)
        guidelines_notebook.pack(fill='both', expand=True, pady=10)
        
        # English guidelines
        english_frame = tk.Frame(guidelines_notebook, bg='white')
        guidelines_notebook.add(english_frame, text="English")
        
        english_text = scrolledtext.ScrolledText(english_frame, height=8, font=('Arial', 9))
        english_text.pack(fill='both', expand=True, padx=10, pady=10)
        english_text.insert('1.0', """
English Content Guidelines:
• Communication Style: Direct and professional
• Formality Level: Professional but approachable
• Cultural Context: Western business environment
• Authority Distance: Low - egalitarian approach
• Content Structure: Clear headings, bullet points, actionable insights
• SEO Focus: Standard English SEO practices
• Tone: Authoritative yet helpful
• Examples: Practical business scenarios from Western companies
        """.strip())
        english_text.config(state='disabled')
        
        # Farsi guidelines
        farsi_frame = tk.Frame(guidelines_notebook, bg='white')
        guidelines_notebook.add(farsi_frame, text="فارسی (Farsi)")
        
        farsi_text = scrolledtext.ScrolledText(farsi_frame, height=8, font=('Arial', 9))
        farsi_text.pack(fill='both', expand=True, padx=10, pady=10)
        farsi_text.insert('1.0', """
راهنمای محتوای فارسی:
• سبک ارتباط: غیرمستقیم و محترمانه
• سطح رسمیت: بالا - استفاده از عبارات مؤدبانه
• زمینه فرهنگی: فرهنگ ایرانی-اسلامی
• فاصله قدرت: بالا - احترام به سلسله مراتب
• ساختار محتوا: مقدمه مفصل، استفاده از ادبیات کلاسیک
• تمرکز SEO: بهینه‌سازی برای کلمات کلیدی فارسی
• لحن: دانشمندانه و فروتنانه
• نمونه‌ها: شرکت‌های ایرانی و منطقه‌ای
        """.strip())
        farsi_text.config(state='disabled')
        
        # Spanish guidelines
        spanish_frame = tk.Frame(guidelines_notebook, bg='white')
        guidelines_notebook.add(spanish_frame, text="Español")
        
        spanish_text = scrolledtext.ScrolledText(spanish_frame, height=8, font=('Arial', 9))
        spanish_text.pack(fill='both', expand=True, padx=10, pady=10)
        spanish_text.insert('1.0', """
Guías de Contenido en Español:
• Estilo de Comunicación: Cálido y expresivo
• Nivel de Formalidad: Medio-alto con enfoque en relaciones
• Contexto Cultural: Hispano/Latino con valores familiares
• Distancia de Poder: Medio-alta - respeto por la autoridad
• Estructura de Contenido: Narrativa envolvente, ejemplos culturales
• Enfoque SEO: Optimización para palabras clave en español
• Tono: Conocedor pero accesible
• Ejemplos: Empresas hispanas y casos culturalmente relevantes
        """.strip())
        spanish_text.config(state='disabled')
        
        # Save button
        tk.Button(main_lang_frame, text="💾 Save Language Settings", 
                 command=self.save_language_settings,
                 bg='#27ae60', fg='white', font=('Arial', 12, 'bold'),
                 width=25, height=2).pack(pady=20)

    def load_language_settings(self):
        """Load language settings"""
        try:
            default_lang = self.settings_manager.get_default_language()
            self.default_language_var.set(default_lang)
        except Exception as e:
            print(f"Error loading language settings: {e}")

    def save_language_settings(self):
        """Save language settings"""
        try:
            default_lang = self.default_language_var.get()
            success = self.settings_manager.set_default_language(default_lang)
            
            if success:
                messagebox.showinfo("Success", f"Default language set to {default_lang}")
            else:
                messagebox.showerror("Error", "Failed to save language settings")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save language settings: {e}")
    
    def create_general_settings_tab(self):
        """Create general settings tab"""
        settings_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(settings_frame, text="⚙️ General Settings")
        
        # Main container
        main_settings_frame = tk.Frame(settings_frame, bg='white')
        main_settings_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Publishing settings
        pub_frame = tk.LabelFrame(main_settings_frame, text="📤 Publishing Settings", 
                                 font=('Arial', 12, 'bold'), bg='white', padx=20, pady=15)
        pub_frame.pack(fill='x', pady=(0, 20))
        
        # Auto publish
        self.auto_publish_var = tk.BooleanVar()
        tk.Checkbutton(pub_frame, text="Enable automatic publishing", variable=self.auto_publish_var,
                      bg='white', font=('Arial', 10)).pack(anchor='w', pady=5)
        
        tk.Label(pub_frame, text="ℹ️ Publishing intervals are now configured per-project", 
                font=('Arial', 9), fg='#7f8c8d', bg='white').pack(anchor='w', pady=5)
        
        # Performance settings
        perf_frame = tk.LabelFrame(main_settings_frame, text="⚡ Performance Settings", 
                                  font=('Arial', 12, 'bold'), bg='white', padx=20, pady=15)
        perf_frame.pack(fill='x', pady=(0, 20))
        
        # Max retries
        retries_frame = tk.Frame(perf_frame, bg='white')
        retries_frame.pack(fill='x', pady=5)
        
        tk.Label(retries_frame, text="Maximum retries:", font=('Arial', 10, 'bold'), bg='white').pack(side='left')
        self.max_retries_var = tk.StringVar(value="3")
        tk.Spinbox(retries_frame, from_=1, to=10, textvariable=self.max_retries_var, 
                  width=10, font=('Arial', 10)).pack(side='left', padx=(10, 0))
        
        # Timeout
        timeout_frame = tk.Frame(perf_frame, bg='white')
        timeout_frame.pack(fill='x', pady=5)
        
        tk.Label(timeout_frame, text="Request timeout (seconds):", font=('Arial', 10, 'bold'), bg='white').pack(side='left')
        self.timeout_var = tk.StringVar(value="30")
        tk.Spinbox(timeout_frame, from_=10, to=120, textvariable=self.timeout_var, 
                  width=10, font=('Arial', 10)).pack(side='left', padx=(10, 0))
        
        # Image settings
        img_frame = tk.LabelFrame(main_settings_frame, text="🖼️ Image Settings", 
                                 font=('Arial', 12, 'bold'), bg='white', padx=20, pady=15)
        img_frame.pack(fill='x', pady=(0, 20))
        
        # Image quality
        quality_frame = tk.Frame(img_frame, bg='white')
        quality_frame.pack(fill='x', pady=5)
        
        tk.Label(quality_frame, text="Image quality (%):", font=('Arial', 10, 'bold'), bg='white').pack(side='left')
        self.image_quality_var = tk.StringVar(value="85")
        tk.Scale(quality_frame, from_=50, to=100, orient='horizontal', variable=self.image_quality_var,
                length=200).pack(side='left', padx=(10, 0))
        
        # API Keys settings
        api_frame = tk.LabelFrame(main_settings_frame, text="🔑 API Keys", 
                                 font=('Arial', 12, 'bold'), bg='white', padx=20, pady=15)
        api_frame.pack(fill='x', pady=(0, 20))
        
        # Claude/Anthropic API Key
        claude_frame = tk.Frame(api_frame, bg='white')
        claude_frame.pack(fill='x', pady=5)
        
        tk.Label(claude_frame, text="Claude API Key:", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w')
        self.claude_api_key_var = tk.StringVar()
        claude_entry = tk.Entry(claude_frame, textvariable=self.claude_api_key_var, 
                               font=('Arial', 10), width=50, show="*")
        claude_entry.pack(fill='x', pady=(5, 0))
        
        # Show/Hide API key button
        self.claude_show_var = tk.BooleanVar()
        tk.Checkbutton(claude_frame, text="Show API key", variable=self.claude_show_var,
                      command=lambda: claude_entry.config(show="" if self.claude_show_var.get() else "*"),
                      bg='white', font=('Arial', 9)).pack(anchor='w', pady=(5, 0))
        
        tk.Label(claude_frame, text="💡 Get your API key from: https://console.anthropic.com/", 
                font=('Arial', 9), fg='#3498db', bg='white').pack(anchor='w', pady=(5, 0))
        
        # Feature toggles
        features_frame = tk.LabelFrame(main_settings_frame, text="🎛️ Feature Toggles", 
                                      font=('Arial', 12, 'bold'), bg='white', padx=20, pady=15)
        features_frame.pack(fill='x', pady=(0, 20))
        
        self.seo_enabled_var = tk.BooleanVar()
        tk.Checkbutton(features_frame, text="Enable SEO optimization", variable=self.seo_enabled_var,
                      bg='white', font=('Arial', 10)).pack(anchor='w', pady=5)
        
        self.backup_enabled_var = tk.BooleanVar()
        tk.Checkbutton(features_frame, text="Enable automatic backups", variable=self.backup_enabled_var,
                      bg='white', font=('Arial', 10)).pack(anchor='w', pady=5)
        
        self.analytics_enabled_var = tk.BooleanVar()
        tk.Checkbutton(features_frame, text="Enable analytics tracking", variable=self.analytics_enabled_var,
                      bg='white', font=('Arial', 10)).pack(anchor='w', pady=5)
        
        # Save button
        tk.Button(main_settings_frame, text="💾 Save General Settings", 
                 command=self.save_general_settings,
                 bg='#27ae60', fg='white', font=('Arial', 12, 'bold'),
                 width=25, height=2).pack(pady=20)
    
    def create_backup_tab(self):
        """Create backup and import/export tab"""
        backup_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(backup_frame, text="💾 Backup & Import")
        
        # Main container
        main_backup_frame = tk.Frame(backup_frame, bg='white')
        main_backup_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Export settings
        export_frame = tk.LabelFrame(main_backup_frame, text="📤 Export Settings", 
                                    font=('Arial', 12, 'bold'), bg='white', padx=20, pady=15)
        export_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(export_frame, text="Export all settings to a backup file", 
                font=('Arial', 10), bg='white').pack(anchor='w', pady=(0, 10))
        
        tk.Button(export_frame, text="📤 Export Settings", 
                 command=self.export_settings,
                 bg='#3498db', fg='white', font=('Arial', 11, 'bold'),
                 width=20, height=2).pack(anchor='w')
        
        # Import settings
        import_frame = tk.LabelFrame(main_backup_frame, text="📥 Import Settings", 
                                    font=('Arial', 12, 'bold'), bg='white', padx=20, pady=15)
        import_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(import_frame, text="Import settings from a backup file", 
                font=('Arial', 10), bg='white').pack(anchor='w', pady=(0, 10))
        
        tk.Button(import_frame, text="📥 Import Settings", 
                 command=self.import_settings,
                 bg='#e67e22', fg='white', font=('Arial', 11, 'bold'),
                 width=20, height=2).pack(anchor='w')
        
        # Reset settings
        reset_frame = tk.LabelFrame(main_backup_frame, text="🔄 Reset Settings", 
                                   font=('Arial', 12, 'bold'), bg='white', padx=20, pady=15)
        reset_frame.pack(fill='x')
        
        tk.Label(reset_frame, text="⚠️ Reset all settings to default values", 
                font=('Arial', 10), bg='white', fg='#e74c3c').pack(anchor='w', pady=(0, 10))
        
        tk.Button(reset_frame, text="🔄 Reset to Defaults", 
                 command=self.reset_settings,
                 bg='#e74c3c', fg='white', font=('Arial', 11, 'bold'),
                 width=20, height=2).pack(anchor='w')
    
    def refresh_websites_list(self):
        """Refresh the WordPress websites list"""
        self.websites_listbox.delete(0, tk.END)
        
        websites = self.settings_manager.list_wordpress_websites()
        for website in websites:
            status_icon = "🟢" if website.is_active else "🔴"
            default_website = self.settings_manager.get_default_website()
            default_icon = "⭐" if default_website and default_website.id == website.id else ""
            test_icon = "✅" if website.test_status == "success" else "❌" if website.test_status == "failed" else "❓"
            
            display_text = f"{status_icon}{default_icon} {website.name} {test_icon}"
            self.websites_listbox.insert(tk.END, display_text)
        
        if not websites:
            self.websites_listbox.insert(tk.END, "📝 No WordPress websites configured")
    
    def on_website_select(self, event):
        """Handle website selection"""
        selection = self.websites_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        websites = self.settings_manager.list_wordpress_websites()
        
        if websites and index < len(websites):
            self.current_website = websites[index]
            self.load_website_form()
            self.form_title_label.config(text=f"📝 Editing: {self.current_website.name}")
        else:
            self.clear_website_form()
    
    def load_website_form(self):
        """Load website data into form"""
        if not self.current_website:
            return
        
        website = self.current_website
        
        self.website_name_var.set(website.name)
        self.website_url_var.set(website.url)
        self.website_desc_var.set(website.description)
        self.website_username_var.set(website.username)
        self.website_password_var.set(website.password)
        self.website_active_var.set(website.is_active)
        
        # Check if this is the default website
        default_website = self.settings_manager.get_default_website()
        self.website_default_var.set(default_website and default_website.id == website.id)
        
        # Update test status
        if website.test_status == "success":
            self.test_status_label.config(text="Connection: ✅ Success", fg='#27ae60')
        elif website.test_status == "failed":
            self.test_status_label.config(text="Connection: ❌ Failed", fg='#e74c3c')
        else:
            self.test_status_label.config(text="Connection: ❓ Not tested", fg='#7f8c8d')
    
    def clear_website_form(self):
        """Clear the website form"""
        self.current_website = None
        self.website_name_var.set("")
        self.website_url_var.set("")
        self.website_desc_var.set("")
        self.website_username_var.set("")
        self.website_password_var.set("")
        self.website_active_var.set(True)
        self.website_default_var.set(False)
        self.test_status_label.config(text="Connection: Not tested", fg='#7f8c8d')
        self.form_title_label.config(text="📝 Website Configuration")
    
    def add_new_website(self):
        """Add a new website"""
        self.clear_website_form()
        self.form_title_label.config(text="📝 Add New Website")
    
    def save_website(self):
        """Save website configuration"""
        
        # Validate inputs
        name = self.website_name_var.get().strip()
        url = self.website_url_var.get().strip()
        username = self.website_username_var.get().strip()
        password = self.website_password_var.get().strip()
        
        if not all([name, url, username, password]):
            messagebox.showerror("Error", "Please fill in all required fields")
            return
        
        try:
            if self.current_website:
                # Update existing website
                self.current_website.name = name
                self.current_website.url = url
                self.current_website.username = username
                self.current_website.password = password
                self.current_website.description = self.website_desc_var.get().strip()
                
                success = self.settings_manager.update_wordpress_website(self.current_website)
                if success:
                    messagebox.showinfo("Success", "Website updated successfully!")
                    self.refresh_websites_list()
                    self.clear_website_form()
                else:
                    messagebox.showerror("Error", "Failed to update website")
            else:
                # Create new website
                from core.settings_manager import WordPressWebsite
                import uuid
                
                website = WordPressWebsite(
                    id=str(uuid.uuid4()),
                    name=name,
                    url=url,
                    username=username,
                    password=password,
                    description=self.website_desc_var.get().strip()
                )
                
                success = self.settings_manager.add_wordpress_website(website)
                if success:
                    messagebox.showinfo("Success", "Website added successfully!")
                    self.refresh_websites_list()
                    self.clear_website_form()
                else:
                    messagebox.showerror("Error", "Failed to add website")
                    
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def test_website_connection(self):
        """Test WordPress connection"""
        if not self.current_website:
            messagebox.showwarning("Warning", "Please select a website to test")
            return
        
        def test_thread():
            try:
                self.test_status_label.config(text="Connection: 🔄 Testing...", fg='#f39c12')
                self.root.update()
                
                success = self.settings_manager.test_wordpress_connection(self.current_website)
                
                if success:
                    self.test_status_label.config(text="Connection: ✅ Success", fg='#27ae60')
                    messagebox.showinfo("Success", "WordPress connection successful!")
                else:
                    self.test_status_label.config(text="Connection: ❌ Failed", fg='#e74c3c')
                    messagebox.showerror("Error", "WordPress connection failed!")
                
                self.refresh_websites_list()
                
            except Exception as e:
                self.test_status_label.config(text="Connection: ❌ Error", fg='#e74c3c')
                messagebox.showerror("Error", f"Test failed: {e}")
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def delete_website(self):
        """Delete selected website"""
        if not self.current_website:
            messagebox.showwarning("Warning", "Please select a website to delete")
            return
        
        result = messagebox.askyesno("Confirm Delete", 
                                    f"Are you sure you want to delete '{self.current_website.name}'?")
        
        if result:
            success = self.settings_manager.remove_wordpress_website(self.current_website.id)
            if success:
                messagebox.showinfo("Success", "Website deleted successfully!")
                self.refresh_websites_list()
                self.clear_website_form()
            else:
                messagebox.showerror("Error", "Failed to delete website")
    
    def load_general_settings(self):
        """Load general settings into form"""
        settings = self.settings_manager.settings
        
        self.auto_publish_var.set(settings.get("auto_publish", True))
        self.max_retries_var.set(str(settings.get("max_retries", 3)))
        self.timeout_var.set(str(settings.get("timeout", 30)))
        self.image_quality_var.set(str(settings.get("image_quality", 85)))
        self.seo_enabled_var.set(settings.get("seo_enabled", True))
        self.backup_enabled_var.set(settings.get("backup_enabled", True))
        self.analytics_enabled_var.set(settings.get("analytics_enabled", False))
        
        # Load API keys
        self.claude_api_key_var.set(settings.get("claude_api_key", ""))
    
    def save_general_settings(self):
        """Save general settings"""
        try:
            self.settings_manager.set_setting("auto_publish", self.auto_publish_var.get())
            self.settings_manager.set_setting("max_retries", int(self.max_retries_var.get()))
            self.settings_manager.set_setting("timeout", int(self.timeout_var.get()))
            self.settings_manager.set_setting("image_quality", int(self.image_quality_var.get()))
            self.settings_manager.set_setting("seo_enabled", self.seo_enabled_var.get())
            self.settings_manager.set_setting("backup_enabled", self.backup_enabled_var.get())
            self.settings_manager.set_setting("analytics_enabled", self.analytics_enabled_var.get())
            
            # Save API keys
            claude_key = self.claude_api_key_var.get().strip()
            if claude_key:
                self.settings_manager.set_setting("claude_api_key", claude_key)
                # Also set as environment variable for immediate use
                import os
                os.environ["ANTHROPIC_API_KEY"] = claude_key
            
            messagebox.showinfo("Success", "General settings saved successfully!")
            
        except ValueError as e:
            messagebox.showerror("Error", "Please enter valid numeric values")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def export_settings(self):
        """Export settings to file"""
        filename = filedialog.asksaveasfilename(
            title="Export Settings",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            success = self.settings_manager.export_settings(filename)
            if success:
                messagebox.showinfo("Success", f"Settings exported to {filename}")
            else:
                messagebox.showerror("Error", "Failed to export settings")
    
    def import_settings(self):
        """Import settings from file"""
        filename = filedialog.askopenfilename(
            title="Import Settings",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            result = messagebox.askyesno("Confirm Import", 
                                        "This will overwrite current settings. Continue?")
            if result:
                success = self.settings_manager.import_settings(filename)
                if success:
                    messagebox.showinfo("Success", "Settings imported successfully!")
                    self.refresh_websites_list()
                    self.load_general_settings()
                else:
                    messagebox.showerror("Error", "Failed to import settings")
    
    def reset_settings(self):
        """Reset all settings to defaults"""
        result = messagebox.askyesno("Confirm Reset", 
                                    "This will reset ALL settings to defaults. Continue?")
        
        if result:
            # Remove settings file and reload
            if os.path.exists(self.settings_manager.settings_file):
                os.remove(self.settings_manager.settings_file)
            
            self.settings_manager = SettingsManager()
            messagebox.showinfo("Success", "Settings reset to defaults!")
            self.refresh_websites_list()
            self.load_general_settings()
            self.clear_website_form()
    
    def back_to_dashboard(self):
        """Return to the main project dashboard"""
        try:
            import subprocess
            import sys
            
            # Close current settings window
            self.root.destroy()
            
            # Open project dashboard
            subprocess.Popen([sys.executable, "project_dashboard.py"])
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to return to dashboard: {e}")

def main():
    """Run the settings dashboard"""
    root = tk.Tk()
    app = SettingsDashboard(root)
    root.mainloop()

if __name__ == "__main__":
    main() 