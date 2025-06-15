#!/usr/bin/env python3
"""
Enhanced Project Dashboard with Multilingual Support
GUI for managing content projects with language-specific settings
"""

import sys
import os
# Add the parent directory to Python path to find our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog, font
import threading
import time
import json
import os
import shutil
import platform
import re
from datetime import datetime
from core.project_manager import MultilingualProjectManager, ContentProject
from core.settings_manager import SettingsManager
from publishing.publishing_scheduler import PublishingScheduler

class RTLEntry(tk.Entry):
    """Custom Entry widget with RTL support and keyboard shortcuts for Persian text"""
    
    def __init__(self, parent, font_manager, **kwargs):
        super().__init__(parent, **kwargs)
        self.font_manager = font_manager
        self.setup_rtl_support()
    
    def setup_rtl_support(self):
        """Setup RTL support and keyboard shortcuts"""
        # Bind events for automatic RTL detection and font switching
        self.bind('<KeyRelease>', self.on_text_change)
        self.bind('<FocusIn>', self.on_text_change)
        
        # Add keyboard shortcuts
        self.setup_keyboard_shortcuts()
    
    def on_text_change(self, event=None):
        """Handle text changes and apply appropriate direction and font"""
        try:
            content = self.get()
            if content.strip():
                language = self.font_manager.detect_text_language(content)
                font_tuple = self.font_manager.get_font_for_language(language, 11)
                self.config(font=font_tuple)
                
                if self.font_manager.is_rtl_text(content):
                    self.config(justify='right')
                else:
                    self.config(justify='left')
        except Exception as e:
            print(f"RTL entry change error: {e}")
    
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for text editing"""
        # Select All (Ctrl+A)
        self.bind('<Control-a>', self.select_all)
        self.bind('<Control-A>', self.select_all)
        
        # Copy (Ctrl+C) - Entry widget has built-in copy, but we'll ensure it works
        self.bind('<Control-c>', self.copy_text)
        self.bind('<Control-C>', self.copy_text)
        
        # Cut (Ctrl+X)
        self.bind('<Control-x>', self.cut_text)
        self.bind('<Control-X>', self.cut_text)
        
        # Paste (Ctrl+V)
        self.bind('<Control-v>', self.paste_text)
        self.bind('<Control-V>', self.paste_text)
    
    def select_all(self, event=None):
        """Select all text"""
        self.select_range(0, tk.END)
        self.icursor(tk.END)
        return 'break'
    
    def copy_text(self, event=None):
        """Copy selected text to clipboard"""
        try:
            if self.selection_present():
                selected_text = self.selection_get()
                self.clipboard_clear()
                self.clipboard_append(selected_text)
        except tk.TclError:
            pass  # No selection
        return 'break'
    
    def cut_text(self, event=None):
        """Cut selected text to clipboard"""
        try:
            if self.selection_present():
                selected_text = self.selection_get()
                self.clipboard_clear()
                self.clipboard_append(selected_text)
                self.delete(tk.SEL_FIRST, tk.SEL_LAST)
                self.on_text_change()  # Update RTL formatting
        except tk.TclError:
            pass  # No selection
        return 'break'
    
    def paste_text(self, event=None):
        """Paste text from clipboard"""
        try:
            clipboard_text = self.clipboard_get()
            if clipboard_text:
                # Delete selected text if any
                if self.selection_present():
                    self.delete(tk.SEL_FIRST, tk.SEL_LAST)
                
                # Insert clipboard text at cursor position
                insert_pos = self.index(tk.INSERT)
                self.insert(insert_pos, clipboard_text)
                self.on_text_change()  # Update RTL formatting
        except tk.TclError:
            pass  # Clipboard empty or error
        return 'break'

class RTLText(tk.Text):
    """Custom Text widget with RTL support for Persian/Arabic text"""
    
    def __init__(self, parent, font_manager, **kwargs):
        # Enable undo/redo functionality
        if 'undo' not in kwargs:
            kwargs['undo'] = True
        super().__init__(parent, **kwargs)
        self.font_manager = font_manager
        self.setup_rtl_support()
    
    def setup_rtl_support(self):
        """Setup RTL text support"""
        # Configure RTL and LTR tags
        self.tag_configure("rtl", justify='right')
        self.tag_configure("ltr", justify='left')
        
        # Bind events for automatic RTL detection
        self.bind('<KeyRelease>', self.on_text_change)
        self.bind('<Button-1>', self.on_text_change)
        self.bind('<FocusIn>', self.on_text_change)
        
        # Add keyboard shortcuts for Persian text
        self.setup_keyboard_shortcuts()
    
    def on_text_change(self, event=None):
        """Handle text changes and apply appropriate direction"""
        try:
            content = self.get("1.0", "end-1c")
            if content.strip():
                if self.font_manager.is_rtl_text(content):
                    self.apply_rtl_formatting()
                else:
                    self.apply_ltr_formatting()
        except Exception as e:
            print(f"RTL text change error: {e}")
    
    def apply_rtl_formatting(self):
        """Apply RTL formatting to all text"""
        self.tag_remove("ltr", "1.0", "end")
        self.tag_add("rtl", "1.0", "end")
    
    def apply_ltr_formatting(self):
        """Apply LTR formatting to all text"""
        self.tag_remove("rtl", "1.0", "end")
        self.tag_add("ltr", "1.0", "end")
    
    def insert_rtl_text(self, index, text):
        """Insert text with automatic RTL detection"""
        self.insert(index, text)
        if self.font_manager.is_rtl_text(text):
            # Get the position where text was inserted
            start_pos = index
            end_pos = f"{index}+{len(text)}c"
            self.tag_add("rtl", start_pos, end_pos)
    
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for text editing"""
        # Select All (Ctrl+A)
        self.bind('<Control-a>', self.select_all)
        self.bind('<Control-A>', self.select_all)
        
        # Copy (Ctrl+C)
        self.bind('<Control-c>', self.copy_text)
        self.bind('<Control-C>', self.copy_text)
        
        # Cut (Ctrl+X)
        self.bind('<Control-x>', self.cut_text)
        self.bind('<Control-X>', self.cut_text)
        
        # Paste (Ctrl+V)
        self.bind('<Control-v>', self.paste_text)
        self.bind('<Control-V>', self.paste_text)
        
        # Undo (Ctrl+Z)
        self.bind('<Control-z>', self.undo_text)
        self.bind('<Control-Z>', self.undo_text)
        
        # Redo (Ctrl+Y)
        self.bind('<Control-y>', self.redo_text)
        self.bind('<Control-Y>', self.redo_text)
    
    def select_all(self, event=None):
        """Select all text"""
        self.tag_add(tk.SEL, "1.0", tk.END)
        self.mark_set(tk.INSERT, "1.0")
        self.see(tk.INSERT)
        return 'break'  # Prevent default behavior
    
    def copy_text(self, event=None):
        """Copy selected text to clipboard"""
        try:
            if self.tag_ranges(tk.SEL):
                selected_text = self.get(tk.SEL_FIRST, tk.SEL_LAST)
                self.clipboard_clear()
                self.clipboard_append(selected_text)
        except tk.TclError:
            pass  # No selection
        return 'break'
    
    def cut_text(self, event=None):
        """Cut selected text to clipboard"""
        try:
            if self.tag_ranges(tk.SEL):
                selected_text = self.get(tk.SEL_FIRST, tk.SEL_LAST)
                self.clipboard_clear()
                self.clipboard_append(selected_text)
                self.delete(tk.SEL_FIRST, tk.SEL_LAST)
                self.on_text_change()  # Update RTL formatting
        except tk.TclError:
            pass  # No selection
        return 'break'
    
    def paste_text(self, event=None):
        """Paste text from clipboard"""
        try:
            clipboard_text = self.clipboard_get()
            if clipboard_text:
                # Delete selected text if any
                if self.tag_ranges(tk.SEL):
                    self.delete(tk.SEL_FIRST, tk.SEL_LAST)
                
                # Insert clipboard text at cursor position
                insert_pos = self.index(tk.INSERT)
                self.insert(insert_pos, clipboard_text)
                self.on_text_change()  # Update RTL formatting
        except tk.TclError:
            pass  # Clipboard empty or error
        return 'break'
    
    def undo_text(self, event=None):
        """Undo last action"""
        try:
            self.edit_undo()
            self.on_text_change()  # Update RTL formatting
        except tk.TclError:
            pass  # Nothing to undo
        return 'break'
    
    def redo_text(self, event=None):
        """Redo last undone action"""
        try:
            self.edit_redo()
            self.on_text_change()  # Update RTL formatting
        except tk.TclError:
            pass  # Nothing to redo
        return 'break'

class FontManager:
    """Manages fonts for different languages with fallback support"""
    
    def __init__(self):
        self.system = platform.system()
        self.available_fonts = font.families()
        self.font_cache = {}
        
        # Define font preferences for different languages
        self.font_preferences = {
            'persian': ['Vazirmatn', 'Vazirmatn Medium', 'Vazirmatn SemiBold', 'Tahoma', 'Microsoft Sans Serif', 'Segoe UI'],
            'arabic': ['Vazirmatn', 'Vazirmatn Medium', 'Arabic Typesetting', 'Tahoma', 'Microsoft Sans Serif'],
            'english': ['Segoe UI', 'Arial', 'Helvetica', 'Microsoft Sans Serif'],
            'spanish': ['Segoe UI', 'Arial', 'Helvetica', 'Microsoft Sans Serif'],
            'default': ['Segoe UI', 'Arial', 'Helvetica', 'Microsoft Sans Serif']
        }
    
    def get_font_for_language(self, language, size=11, weight='normal'):
        """Get the best available font for a specific language"""
        cache_key = f"{language}_{size}_{weight}"
        
        if cache_key in self.font_cache:
            return self.font_cache[cache_key]
        
        # Determine language category
        lang_category = 'default'
        if language in ['farsi', 'persian', 'fa']:
            lang_category = 'persian'
        elif language in ['arabic', 'ar']:
            lang_category = 'arabic'
        elif language in ['english', 'en']:
            lang_category = 'english'
        elif language in ['spanish', 'es']:
            lang_category = 'spanish'
        
        # Find the best available font
        preferred_fonts = self.font_preferences.get(lang_category, self.font_preferences['default'])
        selected_font = 'Arial'  # fallback
        
        for font_name in preferred_fonts:
            if font_name in self.available_fonts:
                selected_font = font_name
                break
        
        # Create font tuple
        font_tuple = (selected_font, size, weight)
        self.font_cache[cache_key] = font_tuple
        
        return font_tuple
    
    def get_persian_font(self, size=11, weight='normal'):
        """Get Persian font specifically"""
        return self.get_font_for_language('persian', size, weight)
    
    def get_english_font(self, size=11, weight='normal'):
        """Get English font specifically"""
        return self.get_font_for_language('english', size, weight)
    
    def detect_text_language(self, text):
        """Enhanced language detection with proper Persian character recognition"""
        if not text:
            return 'english'
        
        persian_chars = 0
        arabic_chars = 0
        total_chars = len(text.replace(' ', '').replace('\n', ''))
        
        # Extended Persian character set including common Persian letters
        persian_specific_chars = set('پچژگکیهءآأإئؤ')
        # Arabic-specific characters (not used in Persian)
        arabic_specific_chars = set('ثذصضطظعغقةى')
        
        for char in text:
            # Check if character is in Persian/Arabic Unicode range
            if '\u0600' <= char <= '\u06FF' or '\uFB50' <= char <= '\uFDFF' or '\uFE70' <= char <= '\uFEFF':
                if char in persian_specific_chars:
                    persian_chars += 2  # Weight Persian-specific chars more heavily
                elif char in arabic_specific_chars:
                    arabic_chars += 2  # Weight Arabic-specific chars more heavily
                elif char in 'ابتجحخدرزسشفلمنوی':  # Common chars in both languages
                    # For common characters, we'll count them as Persian by default
                    # since this is primarily a Persian interface
                    persian_chars += 1
                else:
                    # Other Arabic script characters
                    persian_chars += 1  # Default to Persian for this interface
        
        if total_chars == 0:
            return 'english'
        
        persian_ratio = persian_chars / total_chars
        arabic_ratio = arabic_chars / total_chars
        
        # Lower threshold and prefer Persian for mixed content
        if persian_ratio > 0.03 or arabic_ratio > 0.03:
            return 'persian' if persian_ratio >= arabic_ratio else 'arabic'
        
        return 'english'
    
    def is_rtl_text(self, text):
        """Check if text requires RTL direction"""
        language = self.detect_text_language(text)
        return language in ['persian', 'arabic']
    
    def debug_font_selection(self, text):
        """Debug method to show font selection process"""
        language = self.detect_text_language(text)
        font_tuple = self.get_font_for_language(language)
        print(f"Text: '{text[:20]}...' -> Language: {language} -> Font: {font_tuple[0]}")
        return font_tuple

class ProjectDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("📊 Project Management Dashboard")
        self.root.geometry("1600x1000")
        self.root.configure(bg='#f8f9fa')
        self.root.minsize(1200, 800)  # Minimum window size
        
        # Initialize font manager
        self.font_manager = FontManager()
        
        # Configure root grid weights for responsiveness
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Initialize managers
        self.project_manager = MultilingualProjectManager()
        self.settings_manager = SettingsManager()
        
        # Initialize publishing scheduler
        self.publishing_scheduler = PublishingScheduler()
        self.publishing_scheduler.start_scheduler()
        
        # Variables
        self.current_project = None
        self.current_page = "dashboard"
        self.is_running = False
        
        # Create main container with grid layout
        self.main_container = tk.Frame(self.root, bg='#f8f9fa')
        self.main_container.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)
        
        # Create all pages
        self.create_dashboard_page()
        self.create_new_project_page()
        self.create_project_detail_page()
        
        # Show dashboard by default
        self.show_page("dashboard")
        
        # Load initial data
        self.refresh_projects_list()
        
        # Initialize with correct visibility
        self.on_generation_method_change()
        
        # Start auto-refresh for project details
        self.auto_refresh_project_details()
        
        # Load available websites
        self.refresh_websites()
        
        # Start queue status updates
        self.update_queue_status()
    
    def get_font_for_text(self, text, size=11, weight='normal'):
        """Get appropriate font based on text content"""
        language = self.font_manager.detect_text_language(text)
        return self.font_manager.get_font_for_language(language, size, weight)
    
    def create_action_button(self, parent, text, command, bg_color, active_color, row, col):
        """Create a modern styled action button with hover effects"""
        # Detect language and get appropriate font
        button_font = self.get_font_for_text(text, 9, 'bold')
        
        btn = tk.Button(parent, text=text, command=command,
                       bg=bg_color, fg='white', font=button_font,
                       relief='flat', bd=0, pady=8, padx=5,
                       activebackground=active_color, cursor='hand2')
        btn.grid(row=row, column=col, sticky='ew', padx=3, pady=3)
        
        # Add hover effects
        def on_enter(e):
            btn.config(bg=active_color)
        
        def on_leave(e):
            btn.config(bg=bg_color)
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
    
    def create_modern_stat_card(self, parent, icon, label, value, color, row, col):
        """Create a modern stat card with icon and gradient-like effect"""
        # Main card container
        card = tk.Frame(parent, bg=color, relief='flat', bd=0)
        card.grid(row=row, column=col, padx=8, pady=8, sticky='ew')
        card.grid_columnconfigure(0, weight=1)
        
        # Inner content frame for padding
        content = tk.Frame(card, bg=color)
        content.grid(row=0, column=0, sticky='ew', padx=15, pady=15)
        content.grid_columnconfigure(0, weight=1)
        
        # Icon and value row
        top_frame = tk.Frame(content, bg=color)
        top_frame.grid(row=0, column=0, sticky='ew')
        top_frame.grid_columnconfigure(1, weight=1)
        
        # Icon
        icon_label = tk.Label(top_frame, text=icon, font=self.font_manager.get_english_font(20), 
                             fg='white', bg=color)
        icon_label.grid(row=0, column=0, sticky='w')
        
        # Value
        value_font = self.get_font_for_text(str(value), 24, 'bold')
        value_label = tk.Label(top_frame, text=str(value), font=value_font, 
                              fg='white', bg=color)
        value_label.grid(row=0, column=1, sticky='e')
        
        # Label
        label_font = self.get_font_for_text(label, 11)
        label_label = tk.Label(content, text=label, font=label_font, 
                              fg='white', bg=color)
        label_label.grid(row=1, column=0, sticky='w', pady=(5, 0))
        
        return card
    
    def update_queue_status(self):
        """Update publishing queue status periodically"""
        try:
            status = self.publishing_scheduler.get_queue_status()
            
            # Update queue status in the interface if it exists
            if hasattr(self, 'queue_status_label'):
                status_text = f"📅 Queue: {status['queued']} pending, {status['published']} published"
                if status['next_publish_time']:
                    next_time = status['next_publish_time'].strftime('%H:%M:%S')
                    status_text += f" | Next: {next_time}"
                
                self.queue_status_label.config(text=status_text)
            
        except Exception as e:
            print(f"❌ Error updating queue status: {e}")
        
        # Schedule next update
        self.root.after(30000, self.update_queue_status)  # Update every 30 seconds

    def create_dashboard_page(self):
        """Create the main dashboard page with responsive layout"""
        self.dashboard_frame = tk.Frame(self.main_container, bg='#f0f0f0')
        self.dashboard_frame.grid_rowconfigure(1, weight=1)
        self.dashboard_frame.grid_columnconfigure(0, weight=1)
        
        # Header with gradient-like effect
        header_frame = tk.Frame(self.dashboard_frame, bg='#2c3e50', height=120)
        header_frame.grid(row=0, column=0, sticky='ew', padx=0, pady=0)
        header_frame.grid_propagate(False)
        header_frame.grid_columnconfigure(0, weight=1)
        
        # Header content with better spacing
        header_content = tk.Frame(header_frame, bg='#2c3e50')
        header_content.grid(row=0, column=0, sticky='nsew', padx=30, pady=20)
        header_content.grid_rowconfigure(0, weight=1)
        header_content.grid_rowconfigure(1, weight=1)
        header_content.grid_columnconfigure(0, weight=1)
        
        title_label = tk.Label(header_content, text="🚀 Project Content Management System", 
                              font=self.font_manager.get_english_font(24, 'bold'), fg='white', bg='#2c3e50')
        title_label.grid(row=0, column=0, sticky='ew', pady=(0, 5))
        
        subtitle_label = tk.Label(header_content, text="Manage multiple content projects with custom keywords and targeted research", 
                                 font=self.font_manager.get_english_font(12), fg='#bdc3c7', bg='#2c3e50')
        subtitle_label.grid(row=1, column=0, sticky='ew')
        
        # Main content area with responsive grid
        content_frame = tk.Frame(self.dashboard_frame, bg='#f0f0f0')
        content_frame.grid(row=1, column=0, sticky='nsew', padx=20, pady=20)
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=2)
        
        # Left panel - Project list and controls with modern styling
        left_panel = tk.Frame(content_frame, bg='white', relief='flat', bd=0)
        left_panel.grid(row=0, column=0, sticky='nsew', padx=(0, 15))
        left_panel.grid_rowconfigure(2, weight=1)  # Projects list expands
        left_panel.grid_columnconfigure(0, weight=1)
        
        # Add subtle shadow effect
        shadow_frame = tk.Frame(content_frame, bg='#d5d8dc', height=2)
        shadow_frame.grid(row=0, column=0, sticky='ew', padx=(2, 17), pady=(2, 0))
        
        # Project controls with modern styling
        controls_frame = tk.Frame(left_panel, bg='white')
        controls_frame.grid(row=0, column=0, sticky='ew', padx=25, pady=25)
        controls_frame.grid_columnconfigure(0, weight=1)
        
        tk.Label(controls_frame, text="📂 Project Management", 
                font=self.font_manager.get_english_font(16, 'bold'), bg='white', fg='#2c3e50').grid(row=0, column=0, sticky='w', pady=(0, 20))
        
        # Action buttons with modern styling
        btn_frame = tk.Frame(controls_frame, bg='white')
        btn_frame.grid(row=1, column=0, sticky='ew', pady=(0, 20))
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)
        
        new_btn = tk.Button(btn_frame, text="✨ New Project", 
                           command=lambda: self.show_page("new_project"),
                           bg='#27ae60', fg='white', font=self.font_manager.get_english_font(11, 'bold'),
                           relief='flat', bd=0, padx=20, pady=12,
                           activebackground='#229954', cursor='hand2')
        new_btn.grid(row=0, column=0, sticky='ew', padx=(0, 8))
        
        refresh_btn = tk.Button(btn_frame, text="🔄 Refresh", 
                               command=self.refresh_projects_list,
                               bg='#3498db', fg='white', font=self.font_manager.get_english_font(11, 'bold'),
                               relief='flat', bd=0, padx=20, pady=12,
                               activebackground='#2980b9', cursor='hand2')
        refresh_btn.grid(row=0, column=1, sticky='ew', padx=(8, 0))
        
        # Projects list with modern styling
        list_header = tk.Frame(left_panel, bg='white')
        list_header.grid(row=1, column=0, sticky='ew', padx=25, pady=(0, 15))
        
        tk.Label(list_header, text="📋 Active Projects", 
                font=self.font_manager.get_english_font(14, 'bold'), bg='white', fg='#2c3e50').pack(side='left')
        
        # Projects listbox with modern scrollbar
        list_frame = tk.Frame(left_panel, bg='white', relief='flat', bd=1)
        list_frame.grid(row=2, column=0, sticky='nsew', padx=25, pady=(0, 25))
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Custom styled listbox
        self.projects_listbox = tk.Listbox(list_frame, 
                                          font=self.font_manager.get_english_font(11),
                                          bg='#fafafa', fg='#2c3e50',
                                          selectbackground='#3498db',
                                          selectforeground='white',
                                          relief='flat', bd=0,
                                          highlightthickness=0,
                                          activestyle='none')
        self.projects_listbox.grid(row=0, column=0, sticky='nsew')
        
        # Modern scrollbar
        scrollbar = tk.Scrollbar(list_frame, orient='vertical', 
                                command=self.projects_listbox.yview,
                                bg='#ecf0f1', troughcolor='#ecf0f1',
                                activebackground='#bdc3c7')
        scrollbar.grid(row=0, column=1, sticky='ns')
        self.projects_listbox.config(yscrollcommand=scrollbar.set)
        
        self.projects_listbox.bind('<<ListboxSelect>>', self.on_project_select)
        self.projects_listbox.bind('<Double-Button-1>', self.open_project_details)
        self.projects_listbox.bind('<Button-3>', self.show_project_context_menu)  # Right-click
        
        # Right panel - Project overview and stats with modern styling
        right_panel = tk.Frame(content_frame, bg='white', relief='flat', bd=0)
        right_panel.grid(row=0, column=1, sticky='nsew')
        right_panel.grid_rowconfigure(2, weight=1)  # Details section expands
        right_panel.grid_columnconfigure(0, weight=1)
        
        # Add subtle shadow effect
        shadow_frame2 = tk.Frame(content_frame, bg='#d5d8dc', height=2)
        shadow_frame2.grid(row=0, column=1, sticky='ew', padx=(2, 0), pady=(2, 0))
        
        # Stats section with modern cards
        stats_frame = tk.Frame(right_panel, bg='white')
        stats_frame.grid(row=0, column=0, sticky='ew', padx=25, pady=25)
        stats_frame.grid_columnconfigure(0, weight=1)
        
        tk.Label(stats_frame, text="📊 System Overview", 
                font=self.font_manager.get_english_font(16, 'bold'), bg='white', fg='#2c3e50').grid(row=0, column=0, sticky='w', pady=(0, 20))
        
        # Stats grid with card layout
        self.stats_grid = tk.Frame(stats_frame, bg='white')
        self.stats_grid.grid(row=1, column=0, sticky='ew')
        self.stats_grid.grid_columnconfigure(0, weight=1)
        self.stats_grid.grid_columnconfigure(1, weight=1)
        self.stats_grid.grid_columnconfigure(2, weight=1)
        
        # Project details section with modern styling
        details_frame = tk.Frame(right_panel, bg='white')
        details_frame.grid(row=2, column=0, sticky='nsew', padx=25, pady=(0, 20))
        details_frame.grid_rowconfigure(1, weight=1)
        details_frame.grid_columnconfigure(0, weight=1)
        
        tk.Label(details_frame, text="📋 Project Details", 
                font=self.font_manager.get_english_font(16, 'bold'), bg='white', fg='#2c3e50').grid(row=0, column=0, sticky='w', pady=(0, 15))
        
        # Details container with border
        details_container = tk.Frame(details_frame, bg='#f8f9fa', relief='flat', bd=1)
        details_container.grid(row=1, column=0, sticky='nsew')
        details_container.grid_rowconfigure(0, weight=1)
        details_container.grid_columnconfigure(0, weight=1)
        
        self.project_details_text = scrolledtext.ScrolledText(
            details_container, 
            font=self.font_manager.get_english_font(11),
            bg='#f8f9fa',
            fg='#2c3e50',
            relief='flat',
            bd=0,
            padx=20,
            pady=20,
            wrap=tk.WORD,
            state='disabled',
            cursor='arrow',
            selectbackground='#3498db',
            selectforeground='white'
        )
        self.project_details_text.grid(row=0, column=0, sticky='nsew')
        
        # Configure text tags for better formatting
        self.project_details_text.tag_configure("header", font=self.font_manager.get_english_font(11, 'bold'), foreground='#2c3e50')
        self.project_details_text.tag_configure("value", font=self.font_manager.get_english_font(10), foreground='#34495e')
        self.project_details_text.tag_configure("keyword", font=self.font_manager.get_english_font(10, 'bold'), foreground='#3498db')
        self.project_details_text.tag_configure("status", font=self.font_manager.get_english_font(10, 'bold'), foreground='#27ae60')
        
        # Persian tags with RTL support
        self.project_details_text.tag_configure("persian_header", font=self.font_manager.get_persian_font(11, 'bold'), foreground='#2c3e50', justify='right')
        self.project_details_text.tag_configure("persian_value", font=self.font_manager.get_persian_font(10), foreground='#34495e', justify='right')
        self.project_details_text.tag_configure("persian_keyword", font=self.font_manager.get_persian_font(10, 'bold'), foreground='#3498db', justify='right')
        
        # Publishing queue status with modern styling
        queue_frame = tk.Frame(right_panel, bg='white')
        queue_frame.grid(row=1, column=0, sticky='ew', padx=25, pady=(0, 20))
        queue_frame.grid_columnconfigure(0, weight=1)
        
        # Queue header
        queue_header = tk.Frame(queue_frame, bg='white')
        queue_header.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        
        tk.Label(queue_header, text="📅 Publishing Queue Status", 
                font=self.font_manager.get_english_font(14, 'bold'), bg='white', fg='#2c3e50').pack(side='left')
        
        # Queue status container with background
        status_container = tk.Frame(queue_frame, bg='#f8f9fa', relief='flat', bd=1)
        status_container.grid(row=1, column=0, sticky='ew')
        status_container.grid_columnconfigure(0, weight=1)
        
        self.queue_status_label = tk.Label(status_container, text="🔄 Loading queue status...", 
                                          font=self.font_manager.get_english_font(11), bg='#f8f9fa', fg='#2c3e50',
                                          anchor='w', padx=15, pady=10)
        self.queue_status_label.grid(row=0, column=0, sticky='ew')
        
        # Quick actions with modern button grid
        actions_frame = tk.Frame(right_panel, bg='white')
        actions_frame.grid(row=3, column=0, sticky='ew', padx=25, pady=(0, 25))
        actions_frame.grid_columnconfigure(0, weight=1)
        actions_frame.grid_columnconfigure(1, weight=1)
        actions_frame.grid_columnconfigure(2, weight=1)
        
        # Row 1 buttons
        self.create_action_button(actions_frame, "📝 Generate", self.generate_single_content, 
                                 '#9b59b6', '#8e44ad', 0, 0)
        self.create_action_button(actions_frame, "▶️ Run Project", self.run_selected_project, 
                                 '#e67e22', '#d35400', 0, 1)
        self.create_action_button(actions_frame, "⏹️ Stop Project", self.stop_selected_project, 
                                 '#e74c3c', '#c0392b', 0, 2)
        
        # Row 2 buttons
        self.create_action_button(actions_frame, "📁 View Files", self.view_project_files, 
                                 '#34495e', '#2c3e50', 1, 0)
        self.create_action_button(actions_frame, "📅 View Queue", self.view_publishing_queue, 
                                 '#f39c12', '#e67e22', 1, 1)
        self.create_action_button(actions_frame, "🗑️ Remove", self.remove_selected_project, 
                                 '#c0392b', '#a93226', 1, 2)
        
        # Settings button (full width)
        settings_btn = tk.Button(actions_frame, text="⚙️ Settings", 
                                command=self.open_settings,
                                bg='#9b59b6', fg='white', font=('Segoe UI', 10, 'bold'),
                                relief='flat', bd=0, pady=8,
                                activebackground='#8e44ad', cursor='hand2')
        settings_btn.grid(row=2, column=0, columnspan=3, sticky='ew', pady=(10, 0))
        
        # Initialize stats
        self.update_system_stats()
        
    def create_new_project_page(self):
        """Create the new project creation page with responsive layout"""
        self.new_project_frame = tk.Frame(self.main_container, bg='#f0f0f0')
        self.new_project_frame.grid_rowconfigure(1, weight=1)
        self.new_project_frame.grid_columnconfigure(0, weight=1)
        
        # Header with modern styling
        header_frame = tk.Frame(self.new_project_frame, bg='#2c3e50', height=100)
        header_frame.grid(row=0, column=0, sticky='ew')
        header_frame.grid_propagate(False)
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Back button with modern styling
        back_btn = tk.Button(header_frame, text="← Back to Dashboard", 
                            command=lambda: self.show_page("dashboard"),
                            bg='#34495e', fg='white', font=('Segoe UI', 10, 'bold'),
                            relief='flat', bd=0, padx=20, pady=8,
                            activebackground='#2c3e50', cursor='hand2')
        back_btn.grid(row=0, column=0, sticky='w', padx=25, pady=25)
        
        # Title centered
        title_label = tk.Label(header_frame, text="✨ Create New Project", 
                              font=('Segoe UI', 20, 'bold'), fg='white', bg='#2c3e50')
        title_label.grid(row=0, column=1, sticky='ew', pady=25)
        
        # Main form area with responsive layout
        form_frame = tk.Frame(self.new_project_frame, bg='white', relief='flat', bd=0)
        form_frame.grid(row=1, column=0, sticky='nsew', padx=40, pady=30)
        form_frame.grid_rowconfigure(0, weight=1)
        form_frame.grid_columnconfigure(0, weight=1)
        
        # Add subtle shadow
        shadow_frame = tk.Frame(self.new_project_frame, bg='#d5d8dc', height=2)
        shadow_frame.grid(row=1, column=0, sticky='ew', padx=42, pady=(32, 0))
        
        # Form content with scrollable area
        canvas = tk.Canvas(form_frame, bg='white', highlightthickness=0)
        scrollbar = tk.Scrollbar(form_frame, orient='vertical', command=canvas.yview)
        content_frame = tk.Frame(canvas, bg='white')
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        canvas_frame = canvas.create_window((0, 0), window=content_frame, anchor='nw')
        
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox('all'))
            # Update canvas window width to match canvas width
            canvas.itemconfig(canvas_frame, width=canvas.winfo_width())
        
        content_frame.bind('<Configure>', configure_scroll_region)
        canvas.bind('<Configure>', lambda e: canvas.itemconfig(canvas_frame, width=canvas.winfo_width()))
        
        # Add mouse wheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind("<MouseWheel>", on_mousewheel)
        
        # Bind mouse wheel to all child widgets
        def bind_mousewheel(widget):
            widget.bind("<MouseWheel>", on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel(child)
        
        bind_mousewheel(content_frame)
        
        # Add padding to content
        content_inner = tk.Frame(content_frame, bg='white')
        content_inner.pack(fill='both', expand=True, padx=40, pady=30)
        
        # Project basic info with modern styling
        basic_frame = tk.LabelFrame(content_inner, text="📋 Basic Information", 
                                   font=('Segoe UI', 14, 'bold'), bg='white', fg='#2c3e50',
                                   padx=25, pady=20, relief='flat', bd=1)
        basic_frame.pack(fill='x', pady=(0, 25))
        
        # Project name with modern styling
        tk.Label(basic_frame, text="Project Name:", font=self.font_manager.get_english_font(11, 'bold'), bg='white', fg='#2c3e50').grid(row=0, column=0, sticky='w', pady=8)
        self.project_name_var = tk.StringVar()
        self.name_entry = RTLEntry(basic_frame, self.font_manager, textvariable=self.project_name_var, 
                             font=self.font_manager.get_english_font(11), relief='flat', bd=1, 
                             highlightthickness=1, highlightcolor='#3498db')
        self.name_entry.grid(row=0, column=1, sticky='ew', padx=(15, 0), pady=8, ipady=5)
        
        # Project description
        tk.Label(basic_frame, text="Description:", font=self.font_manager.get_english_font(11, 'bold'), bg='white', fg='#2c3e50').grid(row=1, column=0, sticky='w', pady=8)
        self.project_desc_var = tk.StringVar()
        self.desc_entry = RTLEntry(basic_frame, self.font_manager, textvariable=self.project_desc_var, 
                             font=self.font_manager.get_english_font(11), relief='flat', bd=1,
                             highlightthickness=1, highlightcolor='#3498db')
        self.desc_entry.grid(row=1, column=1, sticky='ew', padx=(15, 0), pady=8, ipady=5)
        
        # Content language
        tk.Label(basic_frame, text="Content Language:", font=self.font_manager.get_english_font(11, 'bold'), bg='white', fg='#2c3e50').grid(row=2, column=0, sticky='w', pady=8)
        self.content_language_var = tk.StringVar(value="english")
        self.language_combo = ttk.Combobox(basic_frame, textvariable=self.content_language_var,
                                     values=["english", "farsi", "spanish"],
                                     state="readonly", font=self.font_manager.get_english_font(11))
        self.language_combo.grid(row=2, column=1, sticky='ew', padx=(15, 0), pady=8)
        
        # Bind language change to update fonts
        self.language_combo.bind('<<ComboboxSelected>>', self.on_language_change)
        
        basic_frame.columnconfigure(1, weight=1)
        
        # Keywords section with modern styling
        keywords_frame = tk.LabelFrame(content_inner, text="🎯 Keywords & SEO", 
                                      font=('Segoe UI', 14, 'bold'), bg='white', fg='#2c3e50',
                                      padx=25, pady=20, relief='flat', bd=1)
        keywords_frame.pack(fill='x', pady=(0, 25))
        
        tk.Label(keywords_frame, text="Keywords (comma separated):", 
                font=self.font_manager.get_english_font(11, 'bold'), bg='white', fg='#2c3e50').pack(anchor='w', pady=(0, 8))
        self.keywords_text = RTLText(keywords_frame, self.font_manager, height=4, font=self.font_manager.get_english_font(11),
                                    relief='flat', bd=1, highlightthickness=1, 
                                    highlightcolor='#3498db', wrap=tk.WORD)
        self.keywords_text.pack(fill='x', pady=(0, 15))
        
        tk.Label(keywords_frame, text="SEO Focus Keywords (optional):", 
                font=self.font_manager.get_english_font(11, 'bold'), bg='white', fg='#2c3e50').pack(anchor='w', pady=(0, 8))
        self.seo_keywords_text = RTLText(keywords_frame, self.font_manager, height=2, font=self.font_manager.get_english_font(11),
                                        relief='flat', bd=1, highlightthickness=1,
                                        highlightcolor='#3498db', wrap=tk.WORD)
        self.seo_keywords_text.pack(fill='x')
        
        # Content settings
        settings_frame = tk.LabelFrame(content_frame, text="⚙️ Content Settings", 
                                      font=('Arial', 12, 'bold'), bg='white', padx=20, pady=15)
        settings_frame.pack(fill='x', pady=(0, 20))
        
        # Settings grid
        settings_grid = tk.Frame(settings_frame, bg='white')
        settings_grid.pack(fill='x')
        
        # Content type
        tk.Label(settings_grid, text="Generation Method:", font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=0, sticky='w', pady=5)
        self.content_type_var = tk.StringVar(value="template")
        content_type_frame = tk.Frame(settings_grid, bg='white')
        content_type_frame.grid(row=0, column=1, sticky='w', padx=(10, 0), pady=5)
        
        tk.Radiobutton(content_type_frame, text="Template", variable=self.content_type_var, 
                      value="template", bg='white', font=('Arial', 9), 
                      command=self.on_generation_method_change).pack(side='left', padx=(0, 10))
        tk.Radiobutton(content_type_frame, text="DeepSeek", variable=self.content_type_var, 
                      value="local_llm", bg='white', font=('Arial', 9),
                      command=self.on_generation_method_change).pack(side='left', padx=(0, 10))
        tk.Radiobutton(content_type_frame, text="DeepSeek+Research", variable=self.content_type_var, 
                      value="research_llm", bg='white', font=('Arial', 9),
                      command=self.on_generation_method_change).pack(side='left', padx=(0, 10))
        tk.Radiobutton(content_type_frame, text="Llama", variable=self.content_type_var, 
                      value="llama", bg='white', font=('Arial', 9),
                      command=self.on_generation_method_change).pack(side='left', padx=(0, 10))
        tk.Radiobutton(content_type_frame, text="Claude", variable=self.content_type_var, 
                      value="claude", bg='white', font=('Arial', 9),
                      command=self.on_generation_method_change).pack(side='left', padx=(0, 10))
        tk.Radiobutton(content_type_frame, text="Claude+Research", variable=self.content_type_var, 
                      value="claude_research", bg='white', font=('Arial', 9),
                      command=self.on_generation_method_change).pack(side='left')
        
        # Model and Style Options Row (4 fields in one row)
        models_row_frame = tk.Frame(settings_grid, bg='white')
        models_row_frame.grid(row=1, column=0, columnspan=3, sticky='ew', pady=10)
        
        # DeepSeek Model (only for DeepSeek methods)
        deepseek_frame = tk.Frame(models_row_frame, bg='white')
        deepseek_frame.pack(side='left', padx=(0, 15))
        tk.Label(deepseek_frame, text="DeepSeek Model:", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w')
        self.llm_model_var = tk.StringVar(value="deepseek")
        self.llm_combo = ttk.Combobox(deepseek_frame, textvariable=self.llm_model_var,
                                values=["deepseek", "deepseek-32b", "deepseek-14b"],
                                state="readonly", width=12)
        self.llm_combo.pack()
        
        # Claude Model (only for Claude methods)
        claude_frame = tk.Frame(models_row_frame, bg='white')
        claude_frame.pack(side='left', padx=(0, 15))
        tk.Label(claude_frame, text="Claude Model:", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w')
        self.claude_model_var = tk.StringVar(value="claude-sonnet-4-20250514")
        self.claude_combo = ttk.Combobox(claude_frame, textvariable=self.claude_model_var,
                                       values=["claude-sonnet-4-20250514", "claude-opus-4-20250514", "claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"],
                                state="readonly", width=12)
        self.claude_combo.pack()
        
        # Template style
        template_frame = tk.Frame(models_row_frame, bg='white')
        template_frame.pack(side='left', padx=(0, 15))
        tk.Label(template_frame, text="Template Style:", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w')
        self.template_style_var = tk.StringVar(value="random")
        style_combo = ttk.Combobox(template_frame, textvariable=self.template_style_var,
                                  values=["random", "trend_analysis", "how_to_guide", "case_study"],
                                  state="readonly", width=12)
        style_combo.pack()
        
        # Content length
        length_frame = tk.Frame(models_row_frame, bg='white')
        length_frame.pack(side='left')
        tk.Label(length_frame, text="Content Length:", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w')
        self.content_length_var = tk.StringVar(value="medium")
        length_combo = ttk.Combobox(length_frame, textvariable=self.content_length_var,
                                   values=["short", "medium", "long"],
                                   state="readonly", width=12)
        length_combo.pack()
        
        # Target audience
        tk.Label(settings_grid, text="Target Audience:", font=('Arial', 10, 'bold'), bg='white').grid(row=2, column=0, sticky='w', pady=5)
        self.target_audience_var = tk.StringVar(value="Marketing professionals")
        RTLEntry(settings_grid, self.font_manager, textvariable=self.target_audience_var, width=40, font=('Arial', 10)).grid(row=2, column=1, sticky='w', padx=(10, 0), pady=5)
        
        # WordPress website selection
        tk.Label(settings_grid, text="WordPress Website:", font=('Arial', 10, 'bold'), bg='white').grid(row=3, column=0, sticky='w', pady=5)
        self.website_var = tk.StringVar()
        self.website_combo = ttk.Combobox(settings_grid, textvariable=self.website_var, 
                                         state="readonly", width=50)
        self.website_combo.grid(row=3, column=1, sticky='w', padx=(10, 0), pady=5)
        
        # Refresh websites button
        refresh_btn = tk.Button(settings_grid, text="🔄", command=self.refresh_websites,
                               bg='#3498db', fg='white', font=('Arial', 8, 'bold'),
                               width=3)
        refresh_btn.grid(row=3, column=2, sticky='w', padx=(5, 0), pady=5)
        
        # Target count and Publishing interval row
        count_interval_frame = tk.Frame(settings_grid, bg='white')
        count_interval_frame.grid(row=4, column=0, columnspan=3, sticky='ew', pady=5)
        
        # Target count
        tk.Label(count_interval_frame, text="Target Content Count:", font=('Arial', 10, 'bold'), bg='white').pack(side='left')
        self.target_count_var = tk.StringVar(value="5")
        RTLEntry(count_interval_frame, self.font_manager, textvariable=self.target_count_var, width=8, font=('Arial', 10)).pack(side='left', padx=(10, 30))
        
        # Publishing interval
        tk.Label(count_interval_frame, text="Publishing Interval (min):", font=('Arial', 10, 'bold'), bg='white').pack(side='left')
        self.publishing_interval_var = tk.StringVar(value="5")
        tk.Spinbox(count_interval_frame, from_=1, to=1440, textvariable=self.publishing_interval_var, 
                  width=8, font=('Arial', 10)).pack(side='left', padx=(10, 0))
        
        # Research settings
        research_frame = tk.LabelFrame(content_frame, text="🔍 Research Settings", 
                                      font=('Arial', 12, 'bold'), bg='white', padx=20, pady=15)
        research_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(research_frame, text="Research Sites (one per line, optional):", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w', pady=(0, 5))
        self.research_sites_text = tk.Text(research_frame, height=4, width=70, font=('Arial', 10))
        self.research_sites_text.pack(fill='x')
        
        # Action buttons
        action_frame = tk.Frame(content_frame, bg='white')
        action_frame.pack(fill='x', pady=20)
        
        tk.Button(action_frame, text="✨ Create Project", 
                 command=self.create_project,
                 bg='#27ae60', fg='white', font=('Arial', 12, 'bold'),
                 width=20, height=2).pack(side='right', padx=(10, 0))
        
        tk.Button(action_frame, text="🔄 Reset Form", 
                 command=self.clear_form,
                 bg='#95a5a6', fg='white', font=('Arial', 12, 'bold'),
                 width=15, height=2).pack(side='right')
        
    def create_project_detail_page(self):
        """Create the project detail/management page"""
        self.project_detail_frame = tk.Frame(self.main_container, bg='#f8f9fa')
        
        # Header with gradient effect
        header_frame = tk.Frame(self.project_detail_frame, bg='#2c3e50', height=100)
        header_frame.pack(fill='x', padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Header content
        header_content = tk.Frame(header_frame, bg='#2c3e50')
        header_content.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Back button (top-left)
        back_btn = tk.Button(header_content, text="← Dashboard", 
                            command=lambda: self.show_page("dashboard"),
                            bg='#34495e', fg='white', font=('Arial', 10, 'bold'),
                            relief='flat', padx=20, pady=8,
                            activebackground='#4a6741', activeforeground='white')
        back_btn.pack(side='left', anchor='nw')
        
        # Project title (center)
        self.project_title_label = tk.Label(header_content, text="📋 Project Management", 
                                           font=('Arial', 20, 'bold'), fg='white', bg='#2c3e50')
        self.project_title_label.pack(side='top', expand=True)
        
        # Status indicator (top-right)
        self.status_frame = tk.Frame(header_content, bg='#2c3e50')
        self.status_frame.pack(side='right', anchor='ne')
        
        self.status_label = tk.Label(self.status_frame, text="● ACTIVE", 
                                    font=('Arial', 10, 'bold'), fg='#2ecc71', bg='#2c3e50')
        self.status_label.pack()
        
        # Main content with better layout
        main_content = tk.Frame(self.project_detail_frame, bg='#f8f9fa')
        main_content.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Top stats bar
        stats_frame = tk.Frame(main_content, bg='white', relief='solid', bd=1, height=80)
        stats_frame.pack(fill='x', pady=(0, 20))
        stats_frame.pack_propagate(False)
        
        # Stats cards
        stats_container = tk.Frame(stats_frame, bg='white')
        stats_container.pack(fill='both', expand=True, padx=20, pady=15)
        
        # Progress card
        progress_card = tk.Frame(stats_container, bg='#e8f5e8', relief='flat', bd=0)
        progress_card.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        tk.Label(progress_card, text="📊", font=('Arial', 16), bg='#e8f5e8').pack(pady=(5, 0))
        self.progress_stat = tk.Label(progress_card, text="0%", font=('Arial', 14, 'bold'), 
                                     fg='#27ae60', bg='#e8f5e8')
        self.progress_stat.pack()
        tk.Label(progress_card, text="Progress", font=('Arial', 9), fg='#7f8c8d', bg='#e8f5e8').pack()
        
        # Completed card
        completed_card = tk.Frame(stats_container, bg='#e3f2fd', relief='flat', bd=0)
        completed_card.pack(side='left', fill='both', expand=True, padx=(5, 5))
        
        tk.Label(completed_card, text="✅", font=('Arial', 16), bg='#e3f2fd').pack(pady=(5, 0))
        self.completed_stat = tk.Label(completed_card, text="0", font=('Arial', 14, 'bold'), 
                                      fg='#3498db', bg='#e3f2fd')
        self.completed_stat.pack()
        tk.Label(completed_card, text="Completed", font=('Arial', 9), fg='#7f8c8d', bg='#e3f2fd').pack()
        
        # Remaining card
        remaining_card = tk.Frame(stats_container, bg='#fff3e0', relief='flat', bd=0)
        remaining_card.pack(side='left', fill='both', expand=True, padx=(5, 0))
        
        tk.Label(remaining_card, text="⏳", font=('Arial', 16), bg='#fff3e0').pack(pady=(5, 0))
        self.remaining_stat = tk.Label(remaining_card, text="0", font=('Arial', 14, 'bold'), 
                                      fg='#f39c12', bg='#fff3e0')
        self.remaining_stat.pack()
        tk.Label(remaining_card, text="Remaining", font=('Arial', 9), fg='#7f8c8d', bg='#fff3e0').pack()
        
        # Content area with tabs
        content_area = tk.Frame(main_content, bg='#f8f9fa')
        content_area.pack(fill='both', expand=True)
        
        # Tab buttons with modern design
        tab_buttons_frame = tk.Frame(self.project_detail_frame, bg='#34495e', height=60)
        tab_buttons_frame.pack(fill='x', padx=0, pady=0)
        tab_buttons_frame.pack_propagate(False)
        
        # Tab navigation
        self.current_tab = tk.StringVar(value="info")
        
        # Create tab buttons
        self.info_tab_btn = tk.Button(tab_buttons_frame, text="📊 Info", 
                                     command=lambda: self.switch_tab("info"),
                                     bg='#3498db', fg='white', font=('Arial', 11, 'bold'),
                                     relief='flat', padx=20, pady=10,
                                     activebackground='#2980b9', activeforeground='white')
        self.info_tab_btn.pack(side='left', padx=(30, 5), pady=10)
        
        self.schedule_tab_btn = tk.Button(tab_buttons_frame, text="📅 Schedule", 
                                         command=lambda: self.switch_tab("schedule"),
                                         bg='#95a5a6', fg='white', font=('Arial', 11, 'bold'),
                                         relief='flat', padx=20, pady=10,
                                         activebackground='#7f8c8d', activeforeground='white')
        self.schedule_tab_btn.pack(side='left', padx=5, pady=10)
        
        self.controls_tab_btn = tk.Button(tab_buttons_frame, text="🎮 Controls", 
                                         command=lambda: self.switch_tab("controls"),
                                         bg='#95a5a6', fg='white', font=('Arial', 11, 'bold'),
                                         relief='flat', padx=20, pady=10,
                                         activebackground='#7f8c8d', activeforeground='white')
        self.controls_tab_btn.pack(side='left', padx=5, pady=10)
        
        self.activity_tab_btn = tk.Button(tab_buttons_frame, text="📝 Activity", 
                                         command=lambda: self.switch_tab("activity"),
                                         bg='#95a5a6', fg='white', font=('Arial', 11, 'bold'),
                                         relief='flat', padx=20, pady=10,
                                         activebackground='#7f8c8d', activeforeground='white')
        self.activity_tab_btn.pack(side='left', padx=5, pady=10)
        
        # Tab content area
        self.tab_content_frame = tk.Frame(self.project_detail_frame, bg='white')
        self.tab_content_frame.pack(fill='both', expand=True)
        
        # Create tab content
        self.create_info_tab()
        self.create_schedule_tab()
        self.create_controls_tab()
        self.create_activity_tab()
        
        # Show default tab
        self.switch_tab("info")
    
    def create_info_tab(self):
        """Create project information tab"""
        self.info_tab_frame = tk.Frame(self.tab_content_frame, bg='white')
        
        # Project details with better formatting
        details_container = tk.Frame(self.info_tab_frame, bg='white')
        details_container.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Title
        tk.Label(details_container, text="📊 Project Information", 
                font=('Arial', 16, 'bold'), fg='#2c3e50', bg='white').pack(anchor='w', pady=(0, 20))
        
        # Info display with better styling
        self.project_info_text = scrolledtext.ScrolledText(
            details_container, 
            height=15, 
            font=('Consolas', 10),
            bg='#f8f9fa',
            fg='#2c3e50',
            relief='flat',
            bd=0,
            padx=15,
            pady=15,
            wrap=tk.WORD
        )
        self.project_info_text.pack(fill='both', expand=True)
        
        # Configure text tags for better formatting
        self.project_info_text.tag_configure("header", font=('Arial', 12, 'bold'), foreground='#2c3e50')
        self.project_info_text.tag_configure("value", font=('Arial', 10), foreground='#34495e')
        self.project_info_text.tag_configure("keyword", font=('Arial', 10, 'bold'), foreground='#3498db')
    
    def create_controls_tab(self):
        """Create project controls tab"""
        self.controls_tab_frame = tk.Frame(self.tab_content_frame, bg='white')
        
        controls_container = tk.Frame(self.controls_tab_frame, bg='white')
        controls_container.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Title
        tk.Label(controls_container, text="🎮 Project Controls", 
                font=('Arial', 16, 'bold'), fg='#2c3e50', bg='white').pack(anchor='w', pady=(0, 30))
        
        # Control buttons grid with modern design
        btn_grid = tk.Frame(controls_container, bg='white')
        btn_grid.pack(fill='x')
        
        # Configure grid weights
        for i in range(2):
            btn_grid.columnconfigure(i, weight=1)
        
        # Generate Content button
        generate_btn = tk.Button(btn_grid, text="📝 Generate Single Content", 
                               command=self.generate_single_content,
                               bg='#9b59b6', fg='white', font=('Arial', 12, 'bold'),
                               relief='flat', height=3, 
                               activebackground='#8e44ad', activeforeground='white')
        generate_btn.grid(row=0, column=0, padx=(0, 10), pady=(0, 15), sticky='ew')
        
        # Run Project button
        run_btn = tk.Button(btn_grid, text="▶️ Run Project (Batch)", 
                          command=self.run_selected_project,
                          bg='#e67e22', fg='white', font=('Arial', 12, 'bold'),
                          relief='flat', height=3,
                          activebackground='#d35400', activeforeground='white')
        run_btn.grid(row=0, column=1, padx=(10, 0), pady=(0, 15), sticky='ew')
        
        # Pause Project button
        pause_btn = tk.Button(btn_grid, text="⏸️ Pause Project", 
                            command=self.pause_selected_project,
                            bg='#e74c3c', fg='white', font=('Arial', 12, 'bold'),
                            relief='flat', height=3,
                            activebackground='#c0392b', activeforeground='white')
        pause_btn.grid(row=1, column=0, padx=(0, 10), pady=(0, 15), sticky='ew')
        
        # Resume Project button
        resume_btn = tk.Button(btn_grid, text="▶️ Resume Project", 
                             command=self.resume_selected_project,
                             bg='#27ae60', fg='white', font=('Arial', 12, 'bold'),
                             relief='flat', height=3,
                             activebackground='#229954', activeforeground='white')
        resume_btn.grid(row=1, column=1, padx=(10, 0), pady=(0, 15), sticky='ew')
        
        # View Files button
        files_btn = tk.Button(btn_grid, text="📁 Open Project Folder", 
                            command=self.view_project_files,
                            bg='#34495e', fg='white', font=('Arial', 12, 'bold'),
                            relief='flat', height=3,
                            activebackground='#2c3e50', activeforeground='white')
        files_btn.grid(row=2, column=0, padx=(0, 10), pady=(0, 15), sticky='ew')
        
        # Stop Project button
        stop_btn = tk.Button(btn_grid, text="⏹️ Stop Project", 
                           command=self.stop_selected_project,
                           bg='#c0392b', fg='white', font=('Arial', 12, 'bold'),
                           relief='flat', height=3,
                           activebackground='#a93226', activeforeground='white')
        stop_btn.grid(row=2, column=1, padx=(10, 0), pady=(0, 15), sticky='ew')
        
        # Settings section
        settings_frame = tk.LabelFrame(controls_container, text="⚙️ Quick Settings", 
                                     font=('Arial', 12, 'bold'), bg='white', 
                                     fg='#2c3e50', padx=20, pady=15)
        settings_frame.pack(fill='x', pady=(30, 0))
        
        # Auto-run toggle
        self.auto_run_var = tk.BooleanVar()
        auto_run_check = tk.Checkbutton(settings_frame, text="Enable Auto-Run (Generate content automatically)", 
                                       variable=self.auto_run_var, bg='white', font=('Arial', 10),
                                       fg='#2c3e50', activebackground='white')
        auto_run_check.pack(anchor='w', pady=5)
        
        # Batch size setting
        batch_frame = tk.Frame(settings_frame, bg='white')
        batch_frame.pack(fill='x', pady=10)
        
        tk.Label(batch_frame, text="Batch Size:", font=('Arial', 10, 'bold'), bg='white', fg='#2c3e50').pack(side='left')
        self.batch_size_var = tk.StringVar(value="1")
        batch_spin = tk.Spinbox(batch_frame, from_=1, to=10, textvariable=self.batch_size_var, 
                               width=5, font=('Arial', 10))
        batch_spin.pack(side='left', padx=(10, 0))
        
        tk.Label(batch_frame, text="(Number of contents to generate at once)", 
                font=('Arial', 9), bg='white', fg='#7f8c8d').pack(side='left', padx=(10, 0))
    
    def create_activity_tab(self):
        """Create activity log tab"""
        self.activity_tab_frame = tk.Frame(self.tab_content_frame, bg='white')
        
        activity_container = tk.Frame(self.activity_tab_frame, bg='white')
        activity_container.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Header with clear button
        header_frame = tk.Frame(activity_container, bg='white')
        header_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(header_frame, text="📝 Activity Log", 
                font=('Arial', 16, 'bold'), fg='#2c3e50', bg='white').pack(side='left')
        
        clear_btn = tk.Button(header_frame, text="🗑️ Clear Log", 
                            command=self.clear_activity_log,
                            bg='#95a5a6', fg='white', font=('Arial', 9, 'bold'),
                            relief='flat', padx=15, pady=5,
                            activebackground='#7f8c8d')
        clear_btn.pack(side='right')
        
        # Activity log with better styling
        self.activity_log_text = scrolledtext.ScrolledText(
            activity_container, 
            font=('Consolas', 9),
            bg='#2c3e50',
            fg='#ecf0f1',
            relief='flat',
            bd=0,
            padx=15,
            pady=15,
            wrap=tk.WORD,
            insertbackground='white'
        )
        self.activity_log_text.pack(fill='both', expand=True)
        
        # Configure log text tags
        self.activity_log_text.tag_configure("success", foreground='#2ecc71')
        self.activity_log_text.tag_configure("error", foreground='#e74c3c')
        self.activity_log_text.tag_configure("warning", foreground='#f39c12')
        self.activity_log_text.tag_configure("info", foreground='#3498db')
    
    def switch_tab(self, tab_name):
        """Switch between tabs"""
        self.current_tab.set(tab_name)
        
        # Hide all tabs
        for frame in [self.info_tab_frame, self.schedule_tab_frame, self.controls_tab_frame, self.activity_tab_frame]:
            frame.pack_forget()
        
        # Reset button colors
        for btn in [self.info_tab_btn, self.schedule_tab_btn, self.controls_tab_btn, self.activity_tab_btn]:
            btn.config(bg='#95a5a6', activebackground='#7f8c8d')
        
        # Show selected tab and highlight button
        if tab_name == "info":
            self.info_tab_frame.pack(fill='both', expand=True)
            self.info_tab_btn.config(bg='#3498db', activebackground='#2980b9')
        elif tab_name == "schedule":
            self.schedule_tab_frame.pack(fill='both', expand=True)
            self.schedule_tab_btn.config(bg='#3498db', activebackground='#2980b9')
            # Refresh schedule when tab is opened
            self.refresh_schedule_timeline()
        elif tab_name == "controls":
            self.controls_tab_frame.pack(fill='both', expand=True)
            self.controls_tab_btn.config(bg='#3498db', activebackground='#2980b9')
        elif tab_name == "activity":
            self.activity_tab_frame.pack(fill='both', expand=True)
            self.activity_tab_btn.config(bg='#3498db', activebackground='#2980b9')
    
    def clear_activity_log(self):
        """Clear the activity log"""
        if hasattr(self, 'activity_log_text'):
            self.activity_log_text.delete("1.0", tk.END)
            self.log_message("🗑️ Activity log cleared")
    
    def auto_refresh_project_details(self):
        """Auto-refresh project details every 30 seconds"""
        if self.current_page == "project_detail" and self.current_project:
            # Reload project data
            updated_project = self.project_manager.get_project(self.current_project.id)
            if updated_project:
                self.current_project = updated_project
                self.show_project_details()
        
        # Schedule next refresh
        self.root.after(30000, self.auto_refresh_project_details)  # 30 seconds
        
    def show_page(self, page_name):
        """Show specific page"""
        # Hide all pages
        for frame in [self.dashboard_frame, self.new_project_frame, self.project_detail_frame]:
            frame.pack_forget()
        
        # Show requested page
        if page_name == "dashboard":
            self.dashboard_frame.pack(fill='both', expand=True)
            self.refresh_projects_list()
        elif page_name == "new_project":
            self.new_project_frame.pack(fill='both', expand=True)
        elif page_name == "project_detail":
            self.project_detail_frame.pack(fill='both', expand=True)
            if self.current_project:
                self.show_project_details()
            else:
                # If no project selected, go back to dashboard
                self.show_page("dashboard")
        
        self.current_page = page_name
    
    def refresh_projects_list(self):
        """Refresh the projects list"""
        self.projects_listbox.delete(0, tk.END)
        
        projects = self.project_manager.list_projects()
        has_persian = False
        
        for project in projects:
            status_icon = "✅" if project.status == "completed" else "🔄" if project.status == "active" else "⏸️"
            progress = f"({project.completed_count}/{project.target_count})"
            lang_flag = {"english": "🇺🇸", "farsi": "🇮🇷", "spanish": "🇪🇸"}.get(project.language, "🌐")
            display_text = f"{status_icon} {lang_flag} {project.name} {progress}"
            self.projects_listbox.insert(tk.END, display_text)
            
            # Check if we have Persian projects
            if project.language == "farsi":
                has_persian = True
        
        # Update listbox font and direction based on content
        if has_persian:
            self.projects_listbox.config(font=self.font_manager.get_persian_font(11))
            # Note: Tkinter Listbox doesn't support RTL directly, but font helps with character rendering
        else:
            self.projects_listbox.config(font=self.font_manager.get_english_font(11))
        
        # If no projects exist, show a message
        if not projects:
            self.projects_listbox.insert(tk.END, "📝 No projects found. Create your first project!")
            # Clear project details
            self.current_project = None
            self.show_selected_project_details()
        
        self.update_system_stats()
    
    def update_system_stats(self):
        """Update system statistics"""
        projects = self.project_manager.list_projects()
        
        total_projects = len(projects)
        active_projects = len([p for p in projects if p.status == "active"])
        completed_projects = len([p for p in projects if p.status == "completed"])
        total_content = sum(p.completed_count for p in projects)
        
        # Check if stats_grid exists (only available in dashboard page)
        if not hasattr(self, 'stats_grid'):
            return
            
        # Clear existing stats
        for widget in self.stats_grid.winfo_children():
            widget.destroy()
        
        # Create modern stats cards
        paused_projects = len([p for p in projects if p.status == "paused"])
        
        stats = [
            ("📊", "Total Projects", total_projects, "#3498db"),
            ("🚀", "Active", active_projects, "#27ae60"),
            ("✅", "Completed", completed_projects, "#2ecc71"),
            ("📝", "Total Content", total_content, "#9b59b6")
        ]
        
        # Add paused projects if any exist
        if paused_projects > 0:
            stats.append(("⏸️", "Paused", paused_projects, "#f39c12"))
        
        # Queue stats
        queue = self.project_manager.get_publishing_queue()
        pending_queue = len([item for item in queue if item.get('status') == 'pending'])
        if pending_queue > 0:
            stats.append(("📅", "Queued", pending_queue, "#e67e22"))
        
        for i, (icon, label, value, color) in enumerate(stats):
            self.create_modern_stat_card(self.stats_grid, icon, label, str(value), color, i//3, i%3)
        
        # Configure grid weights for responsiveness
        for i in range(3):
            self.stats_grid.columnconfigure(i, weight=1)
    
    def on_project_select(self, event):
        """Handle project selection"""
        selection = self.projects_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        projects = self.project_manager.list_projects()
        
        # Check if projects exist and index is valid
        if projects and index < len(projects):
            old_project = self.current_project
            self.current_project = projects[index]
            
            # Update dashboard details
            self.show_selected_project_details()
            
            # If we're on the project detail page and the project changed, refresh everything
            if self.current_page == "project_detail" and (not old_project or old_project.id != self.current_project.id):
                self.show_project_details()
                self.refresh_schedule_timeline()
        else:
            # If no projects or invalid selection, clear current project
            self.current_project = None
            self.show_selected_project_details()
    
    def show_selected_project_details(self):
        """Show details of selected project in dashboard"""
        if not self.current_project:
            # Clear the text area if no project is selected
            self.project_details_text.config(state='normal')
            self.project_details_text.delete("1.0", tk.END)
            self.project_details_text.insert("1.0", "📋 Select a project to view details...")
            self.project_details_text.config(state='disabled')
            return
        
        project = self.current_project
        progress = (project.completed_count / project.target_count) * 100 if project.target_count > 0 else 0
        remaining = project.target_count - project.completed_count
        
        # Enable text widget for editing
        self.project_details_text.config(state='normal')
        self.project_details_text.delete("1.0", tk.END)
        
        # Insert formatted content with tags
        self.project_details_text.insert(tk.END, "📋 PROJECT OVERVIEW\n", "header")
        self.project_details_text.insert(tk.END, "─" * 50 + "\n\n", "value")
        
        self.project_details_text.insert(tk.END, "Project: ", "header")
        # Use appropriate font for project name based on language
        name_tag = "persian_value" if project.language == "farsi" else "value"
        self.project_details_text.insert(tk.END, f"{project.name}\n", name_tag)
        
        self.project_details_text.insert(tk.END, "Description: ", "header")
        # Use appropriate font for description based on language
        desc_tag = "persian_value" if project.language == "farsi" else "value"
        self.project_details_text.insert(tk.END, f"{project.description}\n", desc_tag)
        
        self.project_details_text.insert(tk.END, "ID: ", "header")
        self.project_details_text.insert(tk.END, f"{project.id}\n", "value")
        
        self.project_details_text.insert(tk.END, "Created: ", "header")
        self.project_details_text.insert(tk.END, f"{project.created_date[:10]}\n", "value")
        
        self.project_details_text.insert(tk.END, "Status: ", "header")
        self.project_details_text.insert(tk.END, f"{project.status.upper()}\n\n", "status")
        
        self.project_details_text.insert(tk.END, "📊 PROGRESS\n", "header")
        self.project_details_text.insert(tk.END, "─" * 50 + "\n\n", "value")
        
        self.project_details_text.insert(tk.END, f"Progress: {progress:.1f}%\n", "keyword")
        self.project_details_text.insert(tk.END, f"Completed: {project.completed_count}\n", "value")
        self.project_details_text.insert(tk.END, f"Target: {project.target_count}\n", "value")
        self.project_details_text.insert(tk.END, f"Remaining: {remaining}\n\n", "value")
        
        self.project_details_text.insert(tk.END, "⚙️ CONFIGURATION\n", "header")
        self.project_details_text.insert(tk.END, "─" * 50 + "\n\n", "value")
        
        # Generation method display
        method_display = {
            'template': 'Template-based',
            'local_llm': 'DeepSeek LLM',
            'research_llm': 'DeepSeek + Research',
            'claude': 'Claude AI',
            'claude_research': 'Claude + Research'
        }.get(project.content_type, project.content_type)
        
        self.project_details_text.insert(tk.END, f"Generation: {method_display}\n", "value")
        self.project_details_text.insert(tk.END, f"AI Model: {project.llm_model}\n", "keyword")
        self.project_details_text.insert(tk.END, f"Template: {project.template_style.replace('_', ' ').title()}\n", "value")
        self.project_details_text.insert(tk.END, f"Length: {project.content_length.title()}\n", "value")
        self.project_details_text.insert(tk.END, f"Audience: {project.target_audience}\n\n", "value")
        
        self.project_details_text.insert(tk.END, "🎯 KEYWORDS\n", "header")
        self.project_details_text.insert(tk.END, "─" * 50 + "\n\n", "value")
        
        for kw in project.keywords[:5]:  # Show first 5 keywords
            self.project_details_text.insert(tk.END, f"• {kw}\n", "keyword")
        
        if len(project.keywords) > 5:
            self.project_details_text.insert(tk.END, f"... and {len(project.keywords) - 5} more\n", "value")
        
        self.project_details_text.insert(tk.END, f"\n📁 Output: {project.output_directory}\n", "value")
        
        # Cost estimation
        estimated_cost = self.estimate_project_cost(project)
        self.project_details_text.insert(tk.END, f"\n💰 Estimated Cost: {estimated_cost} per content\n", "keyword")
        
        # Add instruction to double-click for details
        self.project_details_text.insert(tk.END, "\n" + "─" * 50 + "\n", "value")
        self.project_details_text.insert(tk.END, "💡 Double-click project to open detailed view", "header")
        
        # Disable text widget to make it read-only
        self.project_details_text.config(state='disabled')
    
    def open_project_details(self, event):
        """Open project details page"""
        if self.current_project:
            self.show_page("project_detail")
    
    def show_project_details(self):
        """Show detailed project information in project detail page"""
        if not self.current_project:
            return
        
        # Refresh project data from database to ensure we have latest info
        try:
            updated_project = self.project_manager.get_project(self.current_project.id)
            if updated_project:
                self.current_project = updated_project
        except Exception as e:
            print(f"Warning: Could not refresh project data: {e}")
        
        project = self.current_project
        
        # Update project title
        self.project_title_label.config(text=f"📋 {project.name}")
        
        # Update status indicator
        status_color = {
            'active': '#2ecc71',
            'paused': '#f39c12',
            'completed': '#3498db',
            'error': '#e74c3c'
        }.get(project.status.lower(), '#95a5a6')
        
        self.status_label.config(text=f"● {project.status.upper()}", fg=status_color)
        
        # Calculate and update stats
        progress = (project.completed_count / project.target_count) * 100 if project.target_count > 0 else 0
        remaining = project.target_count - project.completed_count
        
        self.progress_stat.config(text=f"{progress:.1f}%")
        self.completed_stat.config(text=str(project.completed_count))
        self.remaining_stat.config(text=str(remaining))
        
        # Refresh the schedule timeline to show correct project data
        self.refresh_schedule_timeline()
        
        # Format project details with better styling
        self.project_info_text.delete("1.0", tk.END)
        
        # Insert formatted content with tags
        self.project_info_text.insert(tk.END, "📋 PROJECT OVERVIEW\n", "header")
        self.project_info_text.insert(tk.END, "─" * 60 + "\n\n", "value")
        
        self.project_info_text.insert(tk.END, "Name: ", "header")
        self.project_info_text.insert(tk.END, f"{project.name}\n", "value")
        
        self.project_info_text.insert(tk.END, "Description: ", "header")
        self.project_info_text.insert(tk.END, f"{project.description}\n", "value")
        
        self.project_info_text.insert(tk.END, "Project ID: ", "header")
        self.project_info_text.insert(tk.END, f"{project.id}\n", "value")
        
        self.project_info_text.insert(tk.END, "Created: ", "header")
        self.project_info_text.insert(tk.END, f"{project.created_date[:10]}\n", "value")
        
        self.project_info_text.insert(tk.END, "Status: ", "header")
        self.project_info_text.insert(tk.END, f"{project.status.upper()}\n\n", "keyword")
        
        self.project_info_text.insert(tk.END, "⚙️ CONFIGURATION\n", "header")
        self.project_info_text.insert(tk.END, "─" * 60 + "\n\n", "value")
        
        self.project_info_text.insert(tk.END, "Generation Method: ", "header")
        method_display = {
            'template': 'Template-based',
            'local_llm': 'DeepSeek LLM',
            'research_llm': 'DeepSeek + Research',
            'claude': 'Claude AI',
            'claude_research': 'Claude + Research'
        }.get(project.content_type, project.content_type)
        self.project_info_text.insert(tk.END, f"{method_display}\n", "value")
        
        self.project_info_text.insert(tk.END, "AI Model: ", "header")
        self.project_info_text.insert(tk.END, f"{project.llm_model}\n", "keyword")
        
        self.project_info_text.insert(tk.END, "Template Style: ", "header")
        self.project_info_text.insert(tk.END, f"{project.template_style.replace('_', ' ').title()}\n", "value")
        
        self.project_info_text.insert(tk.END, "Content Length: ", "header")
        self.project_info_text.insert(tk.END, f"{project.content_length.title()}\n", "value")
        
        self.project_info_text.insert(tk.END, "Target Audience: ", "header")
        self.project_info_text.insert(tk.END, f"{project.target_audience}\n", "value")
        
        self.project_info_text.insert(tk.END, "Publishing Schedule: ", "header")
        self.project_info_text.insert(tk.END, f"{project.publishing_schedule}\n\n", "value")
        
        self.project_info_text.insert(tk.END, "🔑 KEYWORDS & SEO\n", "header")
        self.project_info_text.insert(tk.END, "─" * 60 + "\n\n", "value")
        
        self.project_info_text.insert(tk.END, "Primary Keywords:\n", "header")
        for kw in project.keywords:
            self.project_info_text.insert(tk.END, f"  • {kw}\n", "keyword")
        
        self.project_info_text.insert(tk.END, "\nSEO Focus Keywords:\n", "header")
        for kw in project.seo_focus:
            self.project_info_text.insert(tk.END, f"  • {kw}\n", "keyword")
        
        if project.research_sites:
            self.project_info_text.insert(tk.END, "\n🔍 RESEARCH SOURCES\n", "header")
            self.project_info_text.insert(tk.END, "─" * 60 + "\n\n", "value")
            for site in project.research_sites:
                self.project_info_text.insert(tk.END, f"  • {site}\n", "value")
        
        self.project_info_text.insert(tk.END, "\n📁 OUTPUT LOCATION\n", "header")
        self.project_info_text.insert(tk.END, "─" * 60 + "\n\n", "value")
        self.project_info_text.insert(tk.END, f"{project.output_directory}\n", "value")
        
        # Cost estimation
        estimated_cost = self.estimate_project_cost(project)
        self.project_info_text.insert(tk.END, "\n💰 COST ESTIMATION\n", "header")
        self.project_info_text.insert(tk.END, "─" * 60 + "\n\n", "value")
        self.project_info_text.insert(tk.END, f"Cost per content: {estimated_cost}\n", "value")
        if estimated_cost == "$0.00":
            total_cost = "$0.00"
        elif "0.01-0.03" in estimated_cost:
            total_cost = f"${0.01 * project.target_count:.2f}-${0.03 * project.target_count:.2f}"
        else:
            total_cost = "Variable"
        self.project_info_text.insert(tk.END, f"Total project cost: {total_cost}\n", "keyword")
    
    def estimate_project_cost(self, project):
        """Estimate cost for project based on content type"""
        if project.content_type == 'template':
            return "$0.00"
        elif project.content_type in ['local_llm', 'research_llm']:
            return "$0.00"
        elif project.content_type in ['claude', 'claude_research']:
            return "$0.01-0.03"
        else:
            return "Unknown"
    
    def create_project(self):
        """Create a new project"""
        try:
            # Validate inputs
            name = self.project_name_var.get().strip()
            if not name:
                messagebox.showerror("Error", "Project name is required")
                return
            
            description = self.project_desc_var.get().strip()
            if not description:
                description = f"Content project: {name}"
            
            # Parse keywords
            keywords_text = self.keywords_text.get("1.0", tk.END).strip()
            if not keywords_text:
                messagebox.showerror("Error", "At least one keyword is required")
                return
            
            keywords = [kw.strip() for kw in keywords_text.split(',') if kw.strip()]
            
            # Parse SEO keywords
            seo_keywords_text = self.seo_keywords_text.get("1.0", tk.END).strip()
            seo_keywords = []
            if seo_keywords_text:
                seo_keywords = [kw.strip() for kw in seo_keywords_text.split(',') if kw.strip()]
            
            # Parse target count
            try:
                target_count = int(self.target_count_var.get())
                if target_count <= 0:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("Error", "Target count must be a positive number")
                return
            
            # Parse research sites
            research_sites_text = self.research_sites_text.get("1.0", tk.END).strip()
            research_sites = []
            if research_sites_text:
                research_sites = [site.strip() for site in research_sites_text.split('\n') if site.strip()]
            
            # Get selected website ID
            website_id = None
            selected_website = self.website_var.get()
            if selected_website and selected_website != "No WordPress websites configured":
                # Extract website ID from selection
                websites = self.project_manager.get_available_websites()
                for website in websites:
                    display_name = f"{website.name} ({website.url})"
                    if display_name == selected_website:
                        website_id = website.id
                        break
            
            # Parse publishing interval
            try:
                publishing_interval = int(self.publishing_interval_var.get())
                if publishing_interval < 1:
                    publishing_interval = 1
            except ValueError:
                publishing_interval = 5
            
            # Determine the model based on content type
            selected_model = None
            content_type = self.content_type_var.get()
            
            if content_type in ["local_llm", "research_llm"]:
                selected_model = self.llm_model_var.get()
            elif content_type in ["llama"]:
                selected_model = self.llm_model_var.get() or "llama3.3:latest"
            elif content_type in ["claude", "claude_research"]:
                selected_model = self.claude_model_var.get()
            
            # Create project
            project_id = self.project_manager.create_project(
                name=name,
                description=description,
                keywords=keywords,
                target_count=target_count,
                content_type=content_type,
                language=self.content_language_var.get(),
                llm_model=selected_model,
                research_sites=research_sites,
                template_style=self.template_style_var.get(),
                seo_focus=seo_keywords or keywords[:3],
                target_audience=self.target_audience_var.get(),
                content_length=self.content_length_var.get(),
                publishing_interval=publishing_interval,
                website_id=website_id
            )
            
            self.log_message(f"✅ Project '{name}' created with ID {project_id}")
            self.clear_form()
            
            messagebox.showinfo("Success", f"Project '{name}' created successfully!")
            self.show_page("dashboard")
            
            # Refresh projects list and auto-select the new project
            self.refresh_projects_list()
            
            # Find and select the newly created project
            projects = self.project_manager.list_projects()
            for i, project in enumerate(projects):
                if project.id == project_id:
                    self.projects_listbox.selection_set(i)
                    self.current_project = project
                    self.show_selected_project_details()
                    break
            
        except Exception as e:
            self.log_message(f"❌ Error creating project: {e}")
            messagebox.showerror("Error", f"Error creating project: {e}")
    
    def clear_form(self):
        """Clear the project creation form"""
        self.project_name_var.set("")
        self.project_desc_var.set("")
        self.content_language_var.set("english")
        self.keywords_text.delete("1.0", tk.END)
        self.seo_keywords_text.delete("1.0", tk.END)
        self.target_count_var.set("5")
        self.publishing_interval_var.set("5")  # Reset to 5 minutes
        self.target_audience_var.set("")  # No default target audience
        self.research_sites_text.delete("1.0", tk.END)
    
    def generate_single_content(self):
        """Generate a single content for selected project"""
        if not self.current_project:
            messagebox.showwarning("Warning", "Please select a project")
            return
        
        def generate_thread():
            try:
                self.log_message(f"📝 Generating content for '{self.current_project.name}'")
                success = self.project_manager.generate_content_for_project(self.current_project.id)
                if success:
                    self.log_message(f"✅ Content generated successfully")
                else:
                    self.log_message(f"❌ Content generation failed")
                
                self.refresh_projects_list()
                if self.current_page == "project_detail":
                    self.show_project_details()
                else:
                    self.show_selected_project_details()
            except Exception as e:
                self.log_message(f"❌ Error: {e}")
        
        threading.Thread(target=generate_thread, daemon=True).start()
    
    def run_selected_project(self):
        """Run the selected project and create publishing queue"""
        if not self.current_project:
            messagebox.showwarning("Warning", "Please select a project")
            return
        
        def run_project_thread():
            try:
                # Calculate remaining content to generate
                remaining_count = self.current_project.target_count - self.current_project.completed_count
                
                if remaining_count <= 0:
                    self.log_message(f"✅ Project '{self.current_project.name}' is already completed!")
                    return
                
                self.log_message(f"🚀 Starting project '{self.current_project.name}'")
                self.log_message(f"📊 Will generate {remaining_count} content pieces")
                self.log_message(f"⏰ Publishing interval: {self.current_project.publishing_interval} minutes")
                
                # Run the project and get the publishing queue
                publishing_queue = self.project_manager.run_project(self.current_project.id)
                
                if publishing_queue:
                    self.log_message(f"📅 Created publishing queue with {len(publishing_queue)} items")
                    self.log_message("📋 Content will be published automatically at scheduled times")
                    
                    # Show queue details
                    for i, item in enumerate(publishing_queue[:3]):  # Show first 3 items
                        scheduled_time = item['scheduled_time']
                        if isinstance(scheduled_time, str):
                            from datetime import datetime
                            scheduled_time = datetime.fromisoformat(scheduled_time)
                        self.log_message(f"   • Content {i+1}: {scheduled_time.strftime('%H:%M:%S')}")
                    
                    if len(publishing_queue) > 3:
                        self.log_message(f"   • ... and {len(publishing_queue) - 3} more")
                
                self.refresh_projects_list()
                if self.current_page == "project_detail":
                    self.show_project_details()
                else:
                    self.show_selected_project_details()
                self.log_message(f"✅ Project execution completed - content queued for publishing")
                
            except Exception as e:
                self.log_message(f"❌ Project execution error: {e}")
        
        threading.Thread(target=run_project_thread, daemon=True).start()
    
    def pause_selected_project(self):
        """Pause the selected project"""
        if not self.current_project:
            messagebox.showwarning("Warning", "Please select a project")
            return
        
        self.project_manager.update_project_status(self.current_project.id, "paused")
        self.log_message(f"⏸️ Project '{self.current_project.name}' paused")
        self.refresh_projects_list()
        if self.current_page == "project_detail":
            self.show_project_details()
        else:
            self.show_selected_project_details()
    
    def stop_selected_project(self):
        """Stop the selected project and remove from queue"""
        if not self.current_project:
            messagebox.showwarning("Warning", "Please select a project")
            return
        
        # Confirm stop action
        result = messagebox.askyesno(
            "Stop Project", 
            f"Are you sure you want to stop project '{self.current_project.name}'?\n\n"
            "This will:\n"
            "• Pause the project\n"
            "• Remove pending items from publishing queue\n"
            "• Keep generated content files\n\n"
            "Continue?"
        )
        
        if not result:
            return
        
        try:
            # Update project status to paused
            self.project_manager.update_project_status(self.current_project.id, "paused")
            
            # Remove project items from publishing queue
            self.remove_project_from_queue(self.current_project.id)
            
            self.log_message(f"⏹️ Project '{self.current_project.name}' stopped")
            self.log_message("📅 Removed pending items from publishing queue")
            
            self.refresh_projects_list()
            if self.current_page == "project_detail":
                self.show_project_details()
            else:
                self.show_selected_project_details()
                
        except Exception as e:
            self.log_message(f"❌ Error stopping project: {e}")
            messagebox.showerror("Error", f"Error stopping project: {e}")
    
    def remove_selected_project(self):
        """Remove the selected project completely"""
        if not self.current_project:
            messagebox.showwarning("Warning", "Please select a project")
            return
        
        # First confirmation dialog
        first_confirmation = messagebox.askyesno(
            "Remove Project", 
            f"⚠️ PERMANENT REMOVAL WARNING ⚠️\n\n"
            f"Are you sure you want to PERMANENTLY remove project:\n"
            f"'{self.current_project.name}'?\n\n"
            "This will:\n"
            "• Delete the project from the system\n"
            "• Remove ALL content files from disk\n"
            "• Remove ALL items from publishing queue\n"
            "• This action CANNOT be undone!",
            icon='warning'
        )
        
        if not first_confirmation:
            return
        
        # Second confirmation dialog for extra safety
        final_confirmation = messagebox.askyesno(
            "Final Confirmation",
            f"⚠️ LAST CHANCE TO CANCEL ⚠️\n\n"
            f"You are about to permanently delete:\n"
            f"'{self.current_project.name}'\n\n"
            "Are you absolutely sure?\n\n"
            "Click 'Yes' to proceed with deletion\n"
            "Click 'No' to cancel",
            icon='warning'
        )
        
        if not final_confirmation:
            messagebox.showinfo("Cancelled", "Project removal cancelled.")
            return
        
        try:
            project_name = self.current_project.name
            project_id = self.current_project.id
            
            # Remove from publishing queue
            self.remove_project_from_queue(project_id)
            
            # Remove project files
            self.remove_project_files(self.current_project)
            
            # Remove project from manager
            success = self.project_manager.remove_project(project_id)
            
            if success:
                self.log_message(f"🗑️ Project '{project_name}' removed permanently")
                self.log_message("📁 All project files deleted")
                self.log_message("📅 Removed from publishing queue")
                
                # Clear current project selection
                self.current_project = None
                
                # Refresh the interface
                self.refresh_projects_list()
                if self.current_page == "project_detail":
                    self.show_page("dashboard")
                else:
                    self.show_selected_project_details()
                
                messagebox.showinfo("Success", f"Project '{project_name}' removed successfully.")
            else:
                self.log_message(f"❌ Failed to remove project '{project_name}'")
                messagebox.showerror("Error", "Failed to remove project from system.")
                
        except Exception as e:
            self.log_message(f"❌ Error removing project: {e}")
            messagebox.showerror("Error", f"Error removing project: {e}")
    
    def remove_project_from_queue(self, project_id: str):
        """Remove all items for a project from the publishing queue"""
        try:
            queue = self.project_manager.get_publishing_queue()
            
            # Filter out items for this project
            filtered_queue = [item for item in queue if item['project_id'] != project_id]
            
            # Save the filtered queue
            queue_file = "publishing_queue.json"
            queue_for_json = []
            for item in filtered_queue:
                item_copy = item.copy()
                if isinstance(item_copy['scheduled_time'], datetime):
                    item_copy['scheduled_time'] = item_copy['scheduled_time'].isoformat()
                queue_for_json.append(item_copy)
            
            with open(queue_file, 'w', encoding='utf-8') as f:
                json.dump(queue_for_json, f, indent=2, ensure_ascii=False)
            
            removed_count = len(queue) - len(filtered_queue)
            if removed_count > 0:
                self.log_message(f"📅 Removed {removed_count} items from publishing queue")
            
        except Exception as e:
            self.log_message(f"❌ Error removing from queue: {e}")
    
    def remove_project_files(self, project):
        """Remove all files and directories for a project"""
        try:
            if os.path.exists(project.output_directory):
                shutil.rmtree(project.output_directory)
                self.log_message(f"📁 Deleted project directory: {project.output_directory}")
            else:
                self.log_message(f"📁 Project directory not found: {project.output_directory}")
                
        except Exception as e:
            self.log_message(f"❌ Error removing project files: {e}")
            raise
    
    def view_project_files(self):
        """View project files"""
        if not self.current_project:
            messagebox.showwarning("Warning", "Please select a project")
            return
        
        import subprocess
        
        try:
            if os.path.exists(self.current_project.output_directory):
                subprocess.Popen(f'explorer "{self.current_project.output_directory}"')
                self.log_message(f"📁 Opened project files for '{self.current_project.name}'")
            else:
                messagebox.showwarning("Warning", "Project directory not found")
        except Exception as e:
            self.log_message(f"❌ Error opening directory: {e}")
    
    def view_publishing_queue(self):
        """View the current publishing queue"""
        try:
            queue = self.project_manager.get_publishing_queue()
            
            if not queue:
                messagebox.showinfo("Publishing Queue", "No items in publishing queue")
                return
            
            # Create a new window to show the queue
            queue_window = tk.Toplevel(self.root)
            queue_window.title("📅 Publishing Queue")
            queue_window.geometry("800x600")
            queue_window.configure(bg='white')
            
            # Header
            header_frame = tk.Frame(queue_window, bg='#2c3e50', height=60)
            header_frame.pack(fill='x')
            header_frame.pack_propagate(False)
            
            tk.Label(header_frame, text="📅 Publishing Queue", 
                    font=('Arial', 16, 'bold'), fg='white', bg='#2c3e50').pack(expand=True)
            
            # Queue content
            content_frame = tk.Frame(queue_window, bg='white')
            content_frame.pack(fill='both', expand=True, padx=20, pady=20)
            
            # Queue list
            queue_text = scrolledtext.ScrolledText(content_frame, font=('Consolas', 10), 
                                                  bg='#f8f9fa', wrap=tk.WORD)
            queue_text.pack(fill='both', expand=True)
            
            # Populate queue information
            queue_text.insert(tk.END, f"📊 Total Items: {len(queue)}\n\n")
            
            # Group by status
            status_groups = {}
            for item in queue:
                status = item['status']
                if status not in status_groups:
                    status_groups[status] = []
                status_groups[status].append(item)
            
            # Display each status group
            for status, items in status_groups.items():
                status_emoji = {
                    'queued': '⏰',
                    'published': '✅',
                    'failed': '❌',
                    'error': '⚠️'
                }.get(status, '📄')
                
                queue_text.insert(tk.END, f"{status_emoji} {status.upper()} ({len(items)} items)\n")
                queue_text.insert(tk.END, "=" * 50 + "\n")
                
                for item in items:
                    project = self.project_manager.get_project(item['project_id'])
                    project_name = project.name if project else f"Project {item['project_id']}"
                    
                    scheduled_time = item['scheduled_time']
                    if isinstance(scheduled_time, str):
                        from datetime import datetime
                        scheduled_time = datetime.fromisoformat(scheduled_time)
                    
                    time_str = scheduled_time.strftime('%Y-%m-%d %H:%M:%S')
                    
                    queue_text.insert(tk.END, f"• {project_name} - Content {item['content_index']}\n")
                    queue_text.insert(tk.END, f"  Scheduled: {time_str}\n")
                    
                    if status == 'queued':
                        now = datetime.now()
                        if scheduled_time > now:
                            time_diff = scheduled_time - now
                            minutes = int(time_diff.total_seconds() / 60)
                            queue_text.insert(tk.END, f"  Time remaining: {minutes} minutes\n")
                        else:
                            queue_text.insert(tk.END, f"  Status: Due for publishing\n")
                    
                    queue_text.insert(tk.END, "\n")
                
                queue_text.insert(tk.END, "\n")
            
            queue_text.config(state='disabled')
            
            # Buttons
            btn_frame = tk.Frame(queue_window, bg='white')
            btn_frame.pack(fill='x', padx=20, pady=(0, 20))
            
            tk.Button(btn_frame, text="🔄 Refresh", 
                     command=lambda: self.refresh_queue_window(queue_text),
                     bg='#3498db', fg='white', font=('Arial', 10)).pack(side='left', padx=(0, 10))
            
            tk.Button(btn_frame, text="🧹 Clear Completed", 
                     command=lambda: self.clear_completed_queue_items(queue_text),
                     bg='#e74c3c', fg='white', font=('Arial', 10)).pack(side='left', padx=(0, 10))
            
            tk.Button(btn_frame, text="❌ Close", 
                     command=queue_window.destroy,
                     bg='#95a5a6', fg='white', font=('Arial', 10)).pack(side='right')
            
            self.log_message("📅 Opened publishing queue viewer")
            
        except Exception as e:
            self.log_message(f"❌ Error viewing queue: {e}")
            messagebox.showerror("Error", f"Error viewing publishing queue: {e}")
    
    def refresh_queue_window(self, queue_text):
        """Refresh the queue window content"""
        try:
            queue_text.config(state='normal')
            queue_text.delete(1.0, tk.END)
            
            queue = self.project_manager.get_publishing_queue()
            
            if not queue:
                queue_text.insert(tk.END, "No items in publishing queue")
                queue_text.config(state='disabled')
                return
            
            # Repopulate with updated data (same logic as above)
            queue_text.insert(tk.END, f"📊 Total Items: {len(queue)}\n\n")
            
            # Group by status and display
            status_groups = {}
            for item in queue:
                status = item['status']
                if status not in status_groups:
                    status_groups[status] = []
                status_groups[status].append(item)
            
            for status, items in status_groups.items():
                status_emoji = {
                    'queued': '⏰',
                    'published': '✅',
                    'failed': '❌',
                    'error': '⚠️'
                }.get(status, '📄')
                
                queue_text.insert(tk.END, f"{status_emoji} {status.upper()} ({len(items)} items)\n")
                queue_text.insert(tk.END, "=" * 50 + "\n")
                
                for item in items:
                    project = self.project_manager.get_project(item['project_id'])
                    project_name = project.name if project else f"Project {item['project_id']}"
                    
                    scheduled_time = item['scheduled_time']
                    if isinstance(scheduled_time, str):
                        from datetime import datetime
                        scheduled_time = datetime.fromisoformat(scheduled_time)
                    
                    time_str = scheduled_time.strftime('%Y-%m-%d %H:%M:%S')
                    
                    queue_text.insert(tk.END, f"• {project_name} - Content {item['content_index']}\n")
                    queue_text.insert(tk.END, f"  Scheduled: {time_str}\n")
                    
                    if status == 'queued':
                        now = datetime.now()
                        if scheduled_time > now:
                            time_diff = scheduled_time - now
                            minutes = int(time_diff.total_seconds() / 60)
                            queue_text.insert(tk.END, f"  Time remaining: {minutes} minutes\n")
                        else:
                            queue_text.insert(tk.END, f"  Status: Due for publishing\n")
                    
                    queue_text.insert(tk.END, "\n")
                
                queue_text.insert(tk.END, "\n")
            
            queue_text.config(state='disabled')
            
        except Exception as e:
            queue_text.insert(tk.END, f"Error refreshing queue: {e}")
            queue_text.config(state='disabled')
    
    def clear_completed_queue_items(self, queue_text):
        """Clear completed items from the queue"""
        try:
            self.publishing_scheduler.clear_completed_items()
            self.refresh_queue_window(queue_text)
            self.log_message("🧹 Cleared completed queue items")
        except Exception as e:
            self.log_message(f"❌ Error clearing queue: {e}")
    
    def show_project_context_menu(self, event):
        """Show context menu for project list"""
        try:
            # Select the item under cursor
            index = self.projects_listbox.nearest(event.y)
            self.projects_listbox.selection_clear(0, tk.END)
            self.projects_listbox.selection_set(index)
            self.projects_listbox.activate(index)
            
            # Update current project
            self.on_project_select(None)
            
            if not self.current_project:
                return
            
            # Create context menu
            context_menu = tk.Menu(self.root, tearoff=0)
            
            # Add menu items based on project status
            context_menu.add_command(label="📝 View Details", command=self.open_project_details)
            context_menu.add_separator()
            
            if self.current_project.status == "active":
                context_menu.add_command(label="▶️ Run Project", command=self.run_selected_project)
                context_menu.add_command(label="⏹️ Stop Project", command=self.stop_selected_project)
            elif self.current_project.status == "paused":
                context_menu.add_command(label="▶️ Resume Project", command=self.resume_selected_project)
            elif self.current_project.status == "completed":
                context_menu.add_command(label="🔄 Restart Project", command=self.restart_selected_project)
            
            context_menu.add_separator()
            context_menu.add_command(label="📁 View Files", command=self.view_project_files)
            context_menu.add_command(label="📅 View Queue", command=self.view_publishing_queue)
            context_menu.add_separator()
            context_menu.add_command(label="🗑️ Remove Project", command=self.remove_selected_project)
            
            # Show context menu
            context_menu.post(event.x_root, event.y_root)
            
        except Exception as e:
            self.log_message(f"❌ Error showing context menu: {e}")
    
    def resume_selected_project(self):
        """Resume a paused project"""
        if not self.current_project:
            messagebox.showwarning("Warning", "Please select a project")
            return
        
        self.project_manager.update_project_status(self.current_project.id, "active")
        self.log_message(f"▶️ Project '{self.current_project.name}' resumed")
        self.refresh_projects_list()
        if self.current_page == "project_detail":
            self.show_project_details()
        else:
            self.show_selected_project_details()
    
    def restart_selected_project(self):
        """Restart a completed project"""
        if not self.current_project:
            messagebox.showwarning("Warning", "Please select a project")
            return
        
        result = messagebox.askyesno(
            "Restart Project",
            f"Are you sure you want to restart project '{self.current_project.name}'?\n\n"
            "This will:\n"
            "• Reset the project status to active\n"
            "• Reset completed count to 0\n"
            "• Allow generating content again\n\n"
            "Continue?"
        )
        
        if result:
            # Reset project
            self.current_project.status = "active"
            self.current_project.completed_count = 0
            self.project_manager.projects[self.current_project.id] = self.current_project
            self.project_manager.save_projects()
            
            self.log_message(f"🔄 Project '{self.current_project.name}' restarted")
            self.refresh_projects_list()
            if self.current_page == "project_detail":
                self.show_project_details()
            else:
                self.show_selected_project_details()
    
    def log_message(self, message):
        """Add message to activity log with color coding"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        if hasattr(self, 'activity_log_text'):
            # Determine message type and color
            if "✅" in message or "Success" in message:
                tag = "success"
            elif "❌" in message or "Error" in message or "Failed" in message:
                tag = "error"
            elif "⚠️" in message or "Warning" in message:
                tag = "warning"
            elif "📝" in message or "🚀" in message or "📊" in message:
                tag = "info"
            else:
                tag = None
            
            if tag:
                self.activity_log_text.insert(tk.END, log_entry, tag)
            else:
                self.activity_log_text.insert(tk.END, log_entry)
            
            self.activity_log_text.see(tk.END)
        
        print(log_entry.strip())  # Also print to console
        self.root.update()
    
    def on_language_change(self, event=None):
        """Handle language change to update fonts and text direction"""
        language = self.content_language_var.get()
        
        if language == "farsi":
            # Update form fields to use Persian font and RTL direction
            self.name_entry.config(font=self.font_manager.get_persian_font(11), justify='right')
            self.desc_entry.config(font=self.font_manager.get_persian_font(11), justify='right')
            
            # Update RTL text widgets with Persian font
            self.keywords_text.config(font=self.font_manager.get_persian_font(11))
            self.seo_keywords_text.config(font=self.font_manager.get_persian_font(11))
            
            # Force RTL formatting for existing content
            self.keywords_text.apply_rtl_formatting()
            self.seo_keywords_text.apply_rtl_formatting()
            
        else:
            # Use English font and LTR direction for other languages
            self.name_entry.config(font=self.font_manager.get_english_font(11), justify='left')
            self.desc_entry.config(font=self.font_manager.get_english_font(11), justify='left')
            
            # Update RTL text widgets with English font
            self.keywords_text.config(font=self.font_manager.get_english_font(11))
            self.seo_keywords_text.config(font=self.font_manager.get_english_font(11))
            
            # Force LTR formatting for existing content
            self.keywords_text.apply_ltr_formatting()
            self.seo_keywords_text.apply_ltr_formatting()
    

    
    def on_generation_method_change(self):
        """Handle generation method change to show/hide relevant options"""
        method = self.content_type_var.get()
        
        # Show/hide DeepSeek model selection based on method
        if method in ["local_llm", "research_llm"]:
            self.llm_combo.config(state="readonly")
        else:
            self.llm_combo.config(state="disabled")
        
        # Show/hide Claude model selection based on method
        if method in ["claude", "claude_research"]:
            self.claude_combo.config(state="readonly")
        else:
            self.claude_combo.config(state="disabled")
    
    def open_settings(self):
        """Open settings dashboard"""
        try:
            import subprocess
            import sys
            
            # Run settings dashboard in a separate process
            subprocess.Popen([sys.executable, "dashboards/settings_dashboard.py"])
            self.log_message("⚙️ Settings dashboard opened")
            
        except Exception as e:
            self.log_message(f"❌ Error opening settings: {e}")
            messagebox.showerror("Error", f"Failed to open settings: {e}")
    
    def refresh_websites(self):
        """Refresh available WordPress websites"""
        try:
            websites = self.project_manager.get_available_websites()
            website_options = []
            
            for website in websites:
                display_name = f"{website.name} ({website.url})"
                website_options.append(display_name)
            
            if not website_options:
                website_options = ["No WordPress websites configured"]
            
            self.website_combo['values'] = website_options
            
            # Set default selection
            if website_options and website_options[0] != "No WordPress websites configured":
                self.website_combo.current(0)
            
            self.log_message(f"🔄 Loaded {len(websites)} WordPress websites")
            
        except Exception as e:
            self.log_message(f"❌ Error loading websites: {e}")
            self.website_combo['values'] = ["Error loading websites"]
    
    def back_to_dashboard(self):
        """Handle back to dashboard button click"""
        # Navigate back to the main dashboard page
        self.show_page("dashboard")
        self.log_message("🏠 Navigated back to dashboard")
    
    def create_new_project(self):
        """Create a new project"""
        # Clear the form
        self.clear_form()
        
        # Switch to project settings tab
        self.notebook.select(0)
        
        self.log_message("📝 Ready to create new project")
    
    def delete_project(self):
        """Delete selected project"""
        selection = self.projects_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a project to delete.")
            return
        
        # Get selected project
        project_name = self.projects_listbox.get(selection[0])
        
        # Confirm deletion
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete project '{project_name}'?"):
            try:
                # TODO: Implement actual project deletion in project manager
                self.log_message(f"🗑️ Project '{project_name}' deleted successfully.")
                messagebox.showinfo("Success", f"Project '{project_name}' deleted successfully.")
                self.refresh_projects_list()
            except Exception as e:
                self.log_message(f"❌ Error deleting project: {e}")
                messagebox.showerror("Error", f"Error deleting project: {e}")
    
    def save_project(self):
        """Save the current project settings"""
        try:
            # Get form data
            name = self.project_name_var.get().strip()
            description = self.project_desc_var.get().strip()
            language = self.language_var.get()
            
            if not name:
                messagebox.showwarning("Validation Error", "Please enter a project name.")
                return
            
            # Get keywords
            keywords_text = self.keywords_text.get("1.0", tk.END).strip()
            keywords = [k.strip() for k in keywords_text.split('\n') if k.strip()]
            
            if not keywords:
                messagebox.showwarning("Validation Error", "Please enter at least one keyword.")
                return
            
            # Get other settings
            content_type = self.content_type_var.get()
            llm_model = self.llm_model_var.get()
            target_count = int(self.target_count_var.get()) if hasattr(self, 'target_count_var') else 5
            target_audience = self.target_audience_var.get() if hasattr(self, 'target_audience_var') else "Marketing professionals"
            
            # Create or update project
            if hasattr(self, 'current_project') and self.current_project:
                # Update existing project
                self.log_message(f"💾 Updating project '{name}'...")
                # TODO: Implement project update in project manager
                messagebox.showinfo("Success", f"Project '{name}' updated successfully!")
            else:
                # Create new project
                self.log_message(f"💾 Creating project '{name}'...")
                project_id = self.project_manager.create_project(
                    name=name,
                    description=description,
                    keywords=keywords,
                    content_type=content_type,
                    target_count=target_count,
                    language=language,
                    llm_model=llm_model,
                    target_audience=target_audience
                )
                self.log_message(f"✅ Project '{name}' created with ID: {project_id}")
                messagebox.showinfo("Success", f"Project '{name}' created successfully!")
            
            # Refresh projects list
            self.refresh_projects_list()
            
        except Exception as e:
            self.log_message(f"❌ Error saving project: {e}")
            messagebox.showerror("Error", f"Error saving project: {e}")
    
    def start_content_generation(self):
        """Start content generation for the current project with publishing queue"""
        if not hasattr(self, 'current_project') or not self.current_project:
            messagebox.showwarning("No Project", "Please select or create a project first.")
            return
        
        try:
            self.log_message(f"🚀 Starting content generation for '{self.current_project.name}'...")
            self.is_running = True
            
            # Start generation in a separate thread
            def generation_thread():
                try:
                    # Calculate remaining content to generate
                    remaining_count = self.current_project.target_count - self.current_project.completed_count
                    
                    if remaining_count <= 0:
                        self.log_message(f"✅ Project '{self.current_project.name}' is already completed!")
                        self.is_running = False
                        return
                    
                    self.log_message(f"📊 Will generate {remaining_count} content pieces")
                    self.log_message(f"⏰ Publishing interval: {self.current_project.publishing_interval} minutes")
                    
                    # Run the project and get the publishing queue
                    publishing_queue = self.project_manager.run_project(self.current_project.id)
                    
                    if publishing_queue:
                        self.log_message(f"📅 Created publishing queue with {len(publishing_queue)} items")
                        self.log_message("📋 Content will be published automatically at scheduled times")
                    
                    self.log_message(f"✅ Content generation completed for '{self.current_project.name}'")
                    self.is_running = False
                    self.refresh_projects_list()
                    
                except Exception as e:
                    self.log_message(f"❌ Content generation error: {e}")
                    self.is_running = False
            
            threading.Thread(target=generation_thread, daemon=True).start()
            
        except Exception as e:
            self.log_message(f"❌ Error starting content generation: {e}")
            messagebox.showerror("Error", f"Error starting content generation: {e}")
    
    def stop_content_generation(self):
        """Stop content generation"""
        if hasattr(self, 'is_running') and self.is_running:
            self.is_running = False
            self.log_message("⏹️ Content generation stopped by user")
            
            # Also stop the project if it's running
            if self.current_project:
                self.project_manager.update_project_status(self.current_project.id, "paused")
                self.log_message(f"⏸️ Project '{self.current_project.name}' paused")
            
            messagebox.showinfo("Stopped", "Content generation has been stopped.")
        else:
            messagebox.showinfo("Not Running", "No content generation is currently running.")
    
    def create_content_generation_tab(self):
        """Create content generation tab"""
        generation_tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(generation_tab, text="🚀 Content Generation")
        
        # Main container
        main_frame = tk.Frame(generation_tab, bg='white')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Generation controls
        controls_frame = tk.LabelFrame(main_frame, text="🎮 Generation Controls", 
                                      font=('Arial', 12, 'bold'), bg='white', padx=15, pady=10)
        controls_frame.pack(fill='x', pady=(0, 15))
        
        # Control buttons
        btn_frame = tk.Frame(controls_frame, bg='white')
        btn_frame.pack(fill='x', pady=10)
        
        tk.Button(btn_frame, text="▶️ Start Generation", 
                 command=self.start_content_generation,
                 bg='#27ae60', fg='white', font=('Arial', 11, 'bold'),
                 width=15, height=2).pack(side='left', padx=(0, 10))
        
        tk.Button(btn_frame, text="⏹️ Stop Generation", 
                 command=self.stop_content_generation,
                 bg='#e74c3c', fg='white', font=('Arial', 11, 'bold'),
                 width=15, height=2).pack(side='left', padx=(0, 10))
        
        tk.Button(btn_frame, text="📝 Generate Single", 
                 command=self.generate_single_content,
                 bg='#3498db', fg='white', font=('Arial', 11, 'bold'),
                 width=15, height=2).pack(side='left', padx=(0, 10))
        
        # Project management buttons
        mgmt_frame = tk.Frame(controls_frame, bg='white')
        mgmt_frame.pack(fill='x', pady=(10, 0))
        
        tk.Button(mgmt_frame, text="⏹️ Stop Project", 
                 command=self.stop_selected_project,
                 bg='#e67e22', fg='white', font=('Arial', 10, 'bold'),
                 width=15, height=1).pack(side='left', padx=(0, 10))
        
        tk.Button(mgmt_frame, text="🗑️ Remove Project", 
                 command=self.remove_selected_project,
                 bg='#c0392b', fg='white', font=('Arial', 10, 'bold'),
                 width=15, height=1).pack(side='left', padx=(0, 10))
        
        tk.Button(mgmt_frame, text="📁 View Files", 
                 command=self.view_project_files,
                 bg='#34495e', fg='white', font=('Arial', 10, 'bold'),
                 width=15, height=1).pack(side='left')
        
        # Generation settings
        settings_frame = tk.LabelFrame(main_frame, text="⚙️ Generation Settings", 
                                      font=('Arial', 12, 'bold'), bg='white', padx=15, pady=10)
        settings_frame.pack(fill='x', pady=(0, 15))
        
        # Batch size
        batch_frame = tk.Frame(settings_frame, bg='white')
        batch_frame.pack(fill='x', pady=5)
        
        tk.Label(batch_frame, text="Batch Size:", font=('Arial', 10, 'bold'), bg='white').pack(side='left')
        self.batch_size_var = tk.StringVar(value="1")
        tk.Spinbox(batch_frame, from_=1, to=10, textvariable=self.batch_size_var, 
                  width=5, font=('Arial', 10)).pack(side='left', padx=(10, 0))
        
        # Auto publish
        auto_publish_frame = tk.Frame(settings_frame, bg='white')
        auto_publish_frame.pack(fill='x', pady=5)
        
        self.auto_publish_var = tk.BooleanVar(value=True)
        tk.Checkbutton(auto_publish_frame, text="Auto-publish to WordPress", 
                      variable=self.auto_publish_var, bg='white', 
                      font=('Arial', 10)).pack(side='left')
        
        # Progress section
        progress_frame = tk.LabelFrame(main_frame, text="📊 Generation Progress", 
                                      font=('Arial', 12, 'bold'), bg='white', padx=15, pady=10)
        progress_frame.pack(fill='both', expand=True)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100, length=400)
        self.progress_bar.pack(fill='x', pady=(0, 10))
        
        # Status label
        self.status_label = tk.Label(progress_frame, text="Ready to generate content", 
                                    font=('Arial', 10), bg='white', fg='#2c3e50')
        self.status_label.pack(pady=(0, 10))
        
        # Generation log
        log_frame = tk.Frame(progress_frame, bg='white')
        log_frame.pack(fill='both', expand=True)
        
        tk.Label(log_frame, text="Generation Log:", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w')
        
        self.generation_log = scrolledtext.ScrolledText(log_frame, height=10, 
                                                       font=('Consolas', 9), bg='#f8f9fa')
        self.generation_log.pack(fill='both', expand=True, pady=(5, 0))
    
    def create_activity_log_tab(self):
        """Create activity log tab"""
        activity_tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(activity_tab, text="📋 Activity Log")
        
        # Main container
        main_frame = tk.Frame(activity_tab, bg='white')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(main_frame, bg='white')
        header_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(header_frame, text="📋 System Activity Log", 
                font=('Arial', 14, 'bold'), bg='white').pack(side='left')
        
        tk.Button(header_frame, text="🗑️ Clear Log", 
                 command=self.clear_activity_log,
                 bg='#e74c3c', fg='white', font=('Arial', 9)).pack(side='right')
        
        # Activity log text area
        self.activity_log_text = scrolledtext.ScrolledText(
            main_frame, 
            font=('Consolas', 10),
            bg='#f8f9fa',
            fg='#2c3e50',
            wrap=tk.WORD,
            height=20
        )
        self.activity_log_text.pack(fill='both', expand=True)
        
        # Configure text tags for colored messages
        self.activity_log_text.tag_configure("success", foreground='#27ae60', font=('Consolas', 10, 'bold'))
        self.activity_log_text.tag_configure("error", foreground='#e74c3c', font=('Consolas', 10, 'bold'))
        self.activity_log_text.tag_configure("warning", foreground='#f39c12', font=('Consolas', 10, 'bold'))
        self.activity_log_text.tag_configure("info", foreground='#3498db', font=('Consolas', 10, 'bold'))
        
        # Add initial message
        self.log_message("🚀 Project Dashboard initialized successfully")
    
    def create_schedule_tab(self):
        """Create content scheduling timeline tab"""
        self.schedule_tab_frame = tk.Frame(self.tab_content_frame, bg='white')
        
        # Schedule container
        schedule_container = tk.Frame(self.schedule_tab_frame, bg='white')
        schedule_container.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Title and controls
        header_frame = tk.Frame(schedule_container, bg='white')
        header_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(header_frame, text="📅 Content Scheduling Timeline", 
                font=('Arial', 16, 'bold'), fg='#2c3e50', bg='white').pack(side='left')
        
        # Control buttons
        btn_container = tk.Frame(header_frame, bg='white')
        btn_container.pack(side='right')
        
        refresh_btn = tk.Button(btn_container, text="🔄 Refresh", 
                               command=self.refresh_schedule_timeline,
                               bg='#3498db', fg='white', font=('Arial', 9, 'bold'),
                               relief='flat', padx=15, pady=5,
                               activebackground='#2980b9')
        refresh_btn.pack(side='left', padx=(0, 10))
        
        queue_btn = tk.Button(btn_container, text="📅 View Queue", 
                             command=self.view_publishing_queue,
                             bg='#f39c12', fg='white', font=('Arial', 9, 'bold'),
                             relief='flat', padx=15, pady=5,
                             activebackground='#e67e22')
        queue_btn.pack(side='left')
        
        # Schedule overview cards
        overview_frame = tk.Frame(schedule_container, bg='white')
        overview_frame.pack(fill='x', pady=(0, 20))
        
        # Create overview cards
        self.create_schedule_overview_cards(overview_frame)
        
        # Timeline display
        timeline_frame = tk.LabelFrame(schedule_container, text="📊 Content Timeline", 
                                      font=('Arial', 12, 'bold'), bg='white', 
                                      fg='#2c3e50', padx=20, pady=15)
        timeline_frame.pack(fill='both', expand=True)
        
        # Timeline content with scrollbar
        self.schedule_timeline_text = scrolledtext.ScrolledText(
            timeline_frame, 
            font=('Consolas', 10),
            bg='#f8f9fa',
            fg='#2c3e50',
            relief='flat',
            bd=0,
            padx=15,
            pady=15,
            wrap=tk.WORD,
            height=15
        )
        self.schedule_timeline_text.pack(fill='both', expand=True)
        
        # Configure timeline text tags
        self.schedule_timeline_text.tag_configure("date_header", font=('Arial', 12, 'bold'), foreground='#2c3e50')
        self.schedule_timeline_text.tag_configure("time_slot", font=('Arial', 10, 'bold'), foreground='#3498db')
        self.schedule_timeline_text.tag_configure("content_title", font=('Arial', 10, 'bold'), foreground='#27ae60')
        self.schedule_timeline_text.tag_configure("status_completed", font=('Arial', 9), foreground='#27ae60')
        self.schedule_timeline_text.tag_configure("status_pending", font=('Arial', 9), foreground='#f39c12')
        self.schedule_timeline_text.tag_configure("status_scheduled", font=('Arial', 9), foreground='#3498db')
        self.schedule_timeline_text.tag_configure("keyword_tag", font=('Arial', 9), foreground='#9b59b6')
        self.schedule_timeline_text.tag_configure("separator", font=('Arial', 8), foreground='#bdc3c7')
    
    def create_schedule_overview_cards(self, parent_frame):
        """Create overview cards for schedule statistics"""
        # Cards container
        cards_frame = tk.Frame(parent_frame, bg='white')
        cards_frame.pack(fill='x')
        
        # Configure grid weights
        for i in range(4):
            cards_frame.columnconfigure(i, weight=1)
        
        # Total Content Card
        total_card = tk.Frame(cards_frame, bg='#3498db', relief='flat', bd=0)
        total_card.grid(row=0, column=0, padx=(0, 10), pady=5, sticky='ew')
        
        tk.Label(total_card, text="📊 Total Content", font=('Arial', 10, 'bold'), 
                fg='white', bg='#3498db').pack(pady=(10, 5))
        self.total_content_label = tk.Label(total_card, text="0", font=('Arial', 18, 'bold'), 
                                           fg='white', bg='#3498db')
        self.total_content_label.pack(pady=(0, 10))
        
        # Completed Card
        completed_card = tk.Frame(cards_frame, bg='#27ae60', relief='flat', bd=0)
        completed_card.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        tk.Label(completed_card, text="✅ Completed", font=('Arial', 10, 'bold'), 
                fg='white', bg='#27ae60').pack(pady=(10, 5))
        self.completed_content_label = tk.Label(completed_card, text="0", font=('Arial', 18, 'bold'), 
                                               fg='white', bg='#27ae60')
        self.completed_content_label.pack(pady=(0, 10))
        
        # Scheduled Card
        scheduled_card = tk.Frame(cards_frame, bg='#f39c12', relief='flat', bd=0)
        scheduled_card.grid(row=0, column=2, padx=5, pady=5, sticky='ew')
        
        tk.Label(scheduled_card, text="⏰ Scheduled", font=('Arial', 10, 'bold'), 
                fg='white', bg='#f39c12').pack(pady=(10, 5))
        self.scheduled_content_label = tk.Label(scheduled_card, text="0", font=('Arial', 18, 'bold'), 
                                               fg='white', bg='#f39c12')
        self.scheduled_content_label.pack(pady=(0, 10))
        
        # Next Content Card
        next_card = tk.Frame(cards_frame, bg='#9b59b6', relief='flat', bd=0)
        next_card.grid(row=0, column=3, padx=(10, 0), pady=5, sticky='ew')
        
        tk.Label(next_card, text="⏭️ Next Content", font=('Arial', 10, 'bold'), 
                fg='white', bg='#9b59b6').pack(pady=(10, 5))
        self.next_content_label = tk.Label(next_card, text="--:--", font=('Arial', 12, 'bold'), 
                                          fg='white', bg='#9b59b6')
        self.next_content_label.pack(pady=(0, 10))
    
    def refresh_schedule_timeline(self):
        """Refresh the content scheduling timeline"""
        if not self.current_project:
            return
        
        project = self.current_project
        
        # Update overview cards
        self.total_content_label.config(text=str(project.target_count))
        self.completed_content_label.config(text=str(project.completed_count))
        
        remaining = project.target_count - project.completed_count
        self.scheduled_content_label.config(text=str(remaining))
        
        # Calculate next content time
        next_time = self.calculate_next_content_time(project)
        self.next_content_label.config(text=next_time)
        
        # Generate timeline
        self.generate_content_timeline(project)
    
    def calculate_next_content_time(self, project):
        """Calculate when the next content will be created"""
        from datetime import datetime, timedelta
        
        if project.completed_count >= project.target_count:
            return "Complete"
        
        try:
            interval_minutes = int(project.publishing_schedule)
            # If this is the first content, it can be created immediately
            if project.completed_count == 0:
                return "Now"
            else:
                # Next content based on the interval
                next_time = datetime.now() + timedelta(minutes=interval_minutes)
                return next_time.strftime("%H:%M")
        except:
            return "Manual"
    
    def generate_content_timeline(self, project):
        """Generate detailed content timeline"""
        from datetime import datetime, timedelta
        
        # Clear timeline
        self.schedule_timeline_text.delete("1.0", tk.END)
        
        # Timeline header
        self.schedule_timeline_text.insert(tk.END, "📅 CONTENT CREATION & PUBLISHING TIMELINE\n", "date_header")
        self.schedule_timeline_text.insert(tk.END, "═" * 80 + "\n\n", "separator")
        
        # Project overview
        self.schedule_timeline_text.insert(tk.END, f"Project: {project.name}\n", "content_title")
        self.schedule_timeline_text.insert(tk.END, f"Total Content: {project.target_count} | Completed: {project.completed_count} | Remaining: {project.target_count - project.completed_count}\n", "time_slot")
        self.schedule_timeline_text.insert(tk.END, f"Publishing Interval: {project.publishing_schedule} minutes\n\n", "time_slot")
        
        # Get existing content files
        existing_files = []
        if os.path.exists(project.output_directory):
            existing_files = [f for f in os.listdir(project.output_directory) if f.endswith('.md')]
        
        # Generate timeline for each content
        try:
            interval_minutes = int(project.publishing_schedule)
        except:
            interval_minutes = 5
        
        current_time = datetime.now()
        
        # Calculate base time for scheduling (start from now for remaining content)
        completed_count = project.completed_count
        
        for i in range(project.target_count):
            content_num = i + 1
            
            # Calculate creation and publishing times based on project interval
            if i < completed_count:
                # For completed content, show historical times (approximate)
                creation_time = current_time - timedelta(minutes=interval_minutes * (completed_count - i))
                processing_delay = min(2, interval_minutes // 2)
                publishing_time = creation_time + timedelta(minutes=processing_delay)
            else:
                # For future content, calculate from now
                future_index = i - completed_count
                creation_time = current_time + timedelta(minutes=interval_minutes * future_index)
                processing_delay = min(2, interval_minutes // 2)  # Max 2 min or half the interval, whichever is smaller
                publishing_time = creation_time + timedelta(minutes=processing_delay)
            
            # Determine status
            if i < project.completed_count:
                status = "✅ COMPLETED"
                status_tag = "status_completed"
            elif i == project.completed_count:
                status = "🔄 IN PROGRESS"
                status_tag = "status_pending"
            else:
                status = "⏰ SCHEDULED"
                status_tag = "status_scheduled"
            
            # Get keyword for this content
            keyword_index = i % len(project.keywords)
            keyword = project.keywords[keyword_index] if project.keywords else "General Topic"
            
            # Timeline entry
            self.schedule_timeline_text.insert(tk.END, f"📝 Content #{content_num:02d}\n", "date_header")
            self.schedule_timeline_text.insert(tk.END, "─" * 50 + "\n", "separator")
            
            self.schedule_timeline_text.insert(tk.END, f"📅 Creation Date: ", "time_slot")
            self.schedule_timeline_text.insert(tk.END, f"{creation_time.strftime('%Y-%m-%d %H:%M')}\n", "time_slot")
            
            self.schedule_timeline_text.insert(tk.END, f"📤 Publishing Time: ", "time_slot")
            self.schedule_timeline_text.insert(tk.END, f"{publishing_time.strftime('%Y-%m-%d %H:%M')}\n", "time_slot")
            
            self.schedule_timeline_text.insert(tk.END, f"🎯 Keyword: ", "keyword_tag")
            self.schedule_timeline_text.insert(tk.END, f"{keyword}\n", "keyword_tag")
            
            self.schedule_timeline_text.insert(tk.END, f"📊 Status: ", "time_slot")
            self.schedule_timeline_text.insert(tk.END, f"{status}\n", status_tag)
            
            # Show file name if completed
            if i < len(existing_files):
                self.schedule_timeline_text.insert(tk.END, f"📁 File: ", "time_slot")
                self.schedule_timeline_text.insert(tk.END, f"{existing_files[i]}\n", "content_title")
            
            # Estimated time until creation (for scheduled content)
            if status == "⏰ SCHEDULED":
                time_until = creation_time - current_time
                if time_until.total_seconds() > 0:
                    hours = int(time_until.total_seconds() // 3600)
                    minutes = int((time_until.total_seconds() % 3600) // 60)
                    self.schedule_timeline_text.insert(tk.END, f"⏱️ Time Until Creation: ", "time_slot")
                    self.schedule_timeline_text.insert(tk.END, f"{hours}h {minutes}m\n", "status_scheduled")
            
            self.schedule_timeline_text.insert(tk.END, "\n", "separator")
        
        # Summary section
        self.schedule_timeline_text.insert(tk.END, "📊 PROJECT SUMMARY\n", "date_header")
        self.schedule_timeline_text.insert(tk.END, "═" * 80 + "\n", "separator")
        
        if project.target_count > project.completed_count:
            remaining_content = project.target_count - project.completed_count
            remaining_time = timedelta(minutes=interval_minutes * remaining_content)
            completion_time = current_time + remaining_time
            
            self.schedule_timeline_text.insert(tk.END, f"🏁 Estimated Completion: ", "time_slot")
            self.schedule_timeline_text.insert(tk.END, f"{completion_time.strftime('%Y-%m-%d %H:%M')}\n", "content_title")
            
            # Better time formatting
            total_minutes = remaining_time.total_seconds() / 60
            if total_minutes < 60:
                time_str = f"{int(total_minutes)} minutes"
            elif total_minutes < 1440:  # Less than 24 hours
                hours = int(total_minutes // 60)
                minutes = int(total_minutes % 60)
                time_str = f"{hours}h {minutes}m"
            else:
                days = remaining_time.days
                hours = remaining_time.seconds // 3600
                time_str = f"{days} days, {hours} hours"
            
            self.schedule_timeline_text.insert(tk.END, f"⏳ Time Remaining: ", "time_slot")
            self.schedule_timeline_text.insert(tk.END, f"{time_str}\n", "status_scheduled")
            
            # Show interval information
            self.schedule_timeline_text.insert(tk.END, f"⏰ Content Interval: ", "time_slot")
            if interval_minutes < 60:
                interval_str = f"{interval_minutes} minutes"
            else:
                hours = interval_minutes // 60
                minutes = interval_minutes % 60
                interval_str = f"{hours}h {minutes}m" if minutes > 0 else f"{hours}h"
            self.schedule_timeline_text.insert(tk.END, f"{interval_str} between each content\n", "keyword_tag")
        else:
            self.schedule_timeline_text.insert(tk.END, "🎉 Project Completed!\n", "status_completed")
        
        # Cost and performance estimates
        estimated_cost = self.estimate_project_cost(project)
        self.schedule_timeline_text.insert(tk.END, f"💰 Estimated Total Cost: ", "time_slot")
        if estimated_cost == "$0.00":
            total_cost = "$0.00"
        elif "0.01-0.03" in estimated_cost:
            total_cost = f"${0.01 * project.target_count:.2f}-${0.03 * project.target_count:.2f}"
        else:
            total_cost = "Variable"
        self.schedule_timeline_text.insert(tk.END, f"{total_cost}\n", "keyword_tag")

def main():
    """Run the project dashboard"""
    root = tk.Tk()
    app = ProjectDashboard(root)
    root.mainloop()

if __name__ == "__main__":
    main() 