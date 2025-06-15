"""
AI Content Management System - Dashboards Package
Provides web-based dashboards for project management, content creation, and system settings.
"""

__version__ = "0.1.1"
__author__ = "AI Content Management System"

# Import main dashboard classes
try:
    from .project_dashboard import ProjectDashboard
    from .content_dashboard import ContentDashboard  
    from .settings_dashboard import SettingsDashboard
except ImportError:
    # Graceful fallback if dashboard modules are not available
    pass 