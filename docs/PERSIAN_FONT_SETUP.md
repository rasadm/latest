# Persian Font & RTL Support Setup Guide

## Overview
The Project Dashboard now includes comprehensive Persian font support using **Vazirmatn** font family and **RTL (Right-to-Left) text direction** for optimal display and input of Persian/Farsi content.

## Font Hierarchy
The system uses the following font preference order for Persian content:

1. **Vazirmatn** (Primary choice - modern, clean Persian font)
2. **Vazir** (Fallback option)
3. **IRANSans** (Alternative Persian font)
4. **Tahoma** (System fallback)
5. **Arial Unicode MS** (Universal fallback)

## Installation Instructions

### Windows
1. Download Vazirmatn font from: https://github.com/rastikerdar/vazirmatn
2. Extract the font files
3. Right-click on `Vazirmatn-Regular.ttf` and select "Install"
4. Install additional weights if needed (Bold, Light, etc.)

### macOS
1. Download Vazirmatn font from the same repository
2. Double-click the font file to open Font Book
3. Click "Install Font"

### Linux
1. Download the font files
2. Copy to `~/.fonts/` or `/usr/share/fonts/`
3. Run `fc-cache -fv` to refresh font cache

## Features

### Enhanced Persian Character Recognition
- Improved detection of Persian characters including ی (yeh) without Arabic dots
- Extended Persian character set recognition: پچژگکیهءآأإئؤ
- Proper distinction between Persian and Arabic text
- Weighted character detection for better accuracy

### Dynamic Font & Direction Switching
- **Project List**: Automatically uses Persian font when Persian projects are present
- **Form Fields**: Updates font and text direction when language is changed to "farsi"
- **Project Details**: Uses appropriate font and RTL direction based on project language
- **Text Areas**: Supports Persian text input with automatic RTL direction detection
- **Entry Fields**: Right-aligned text input for Persian content with real-time font switching

### Keyboard Shortcuts Support
- **Ctrl+A**: Select all text (works with Persian text)
- **Ctrl+C**: Copy selected text to clipboard
- **Ctrl+X**: Cut selected text to clipboard
- **Ctrl+V**: Paste text from clipboard with automatic RTL detection
- **Ctrl+Z**: Undo last action (Text widgets only)
- **Ctrl+Y**: Redo last undone action (Text widgets only)
- All shortcuts work seamlessly with Persian, English, and mixed-language content

### Supported Elements
- Project names and descriptions (with keyboard shortcuts)
- Keywords and SEO text (with full text editing support)
- Project details display
- Form input fields (RTL Entry widgets with shortcuts)
- Text areas (RTL Text widgets with undo/redo)
- List displays

## Usage

### Creating Persian Projects
1. Open the Project Dashboard
2. Click "New Project"
3. Select "farsi" from the Content Language dropdown
4. Form fields will automatically switch to Persian font and RTL direction
5. Enter Persian text in project name, description, and keywords
6. Text will automatically align right-to-left as you type Persian characters

### Viewing Persian Projects
- Persian projects display with 🇮🇷 flag in the project list
- Project details use Persian font for Persian content
- Mixed-language project lists are supported

## Technical Implementation

### RTLText Class
```python
class RTLText(tk.Text):
    """Custom Text widget with RTL support for Persian/Arabic text"""
    
    def __init__(self, parent, font_manager, **kwargs):
        super().__init__(parent, **kwargs)
        self.font_manager = font_manager
        self.setup_rtl_support()
    
    def setup_rtl_support(self):
        # Configure RTL and LTR tags
        self.tag_configure("rtl", justify='right')
        self.tag_configure("ltr", justify='left')
        
        # Bind events for automatic RTL detection
        self.bind('<KeyRelease>', self.on_text_change)
```

### FontManager Class
```python
class FontManager:
    def __init__(self):
        self.font_preferences = {
            'persian': ['Vazirmatn', 'Vazir', 'IRANSans', 'Tahoma', 'Arial Unicode MS'],
            'arabic': ['Vazirmatn', 'Vazir', 'Arabic Typesetting', 'Tahoma', 'Arial Unicode MS'],
            'english': ['Segoe UI', 'Arial', 'Helvetica', 'sans-serif'],
            'default': ['Segoe UI', 'Arial', 'Helvetica', 'sans-serif']
        }
    
    def is_rtl_text(self, text):
        """Check if text requires RTL direction"""
        language = self.detect_text_language(text)
        return language in ['persian', 'arabic']
```

### Language Detection & RTL Support
The system detects Persian text using Unicode ranges:
- Persian/Farsi: `\u0600-\u06FF`, `\uFB50-\uFDFF`, `\uFE70-\uFEFF`
- Specific Persian characters: `پچژگ`
- **Automatic RTL Detection**: Text direction switches automatically when Persian characters are detected
- **Real-time Direction**: Text alignment changes as you type Persian content

### Font Caching
- Fonts are cached for performance
- Cache key format: `{language}_{size}_{weight}`
- Automatic fallback to available system fonts

## Troubleshooting

### Font Not Displaying Correctly
1. Verify Vazirmatn is installed on your system
2. Check font cache (run `fc-cache -fv` on Linux)
3. Restart the application
4. Check console for font-related warnings

### Mixed Language Issues
- The system prioritizes Persian font if any Persian projects exist
- Individual text elements use appropriate fonts based on content
- Form fields update when language selection changes

### Performance Considerations
- Font detection is cached for better performance
- Language detection runs only when needed
- Minimal impact on application startup time

### Keyboard Shortcuts Issues
- If shortcuts don't work, ensure the text widget has focus (click on it first)
- Persian text selection works from right to left
- Copy/paste preserves text direction and formatting
- Undo/redo is available in text areas but not single-line entry fields

## Customization

### Adding Custom Fonts
Edit the `font_preferences` in `FontManager` class:
```python
'persian': ['YourCustomFont', 'Vazirmatn', 'Vazir', 'IRANSans', 'Tahoma']
```

### Adjusting Detection Sensitivity
Modify the character ratio thresholds in `detect_text_language()` method.

## Best Practices

1. **Install Vazirmatn**: For best results, install the complete Vazirmatn font family
2. **Test Mixed Content**: Verify both Persian and English content display correctly
3. **Check Fallbacks**: Ensure fallback fonts are available on target systems
4. **Regular Updates**: Keep font files updated for latest improvements

## Support

For font-related issues:
1. Check system font installation
2. Verify Unicode support in your terminal/environment
3. Test with simple Persian text first
4. Check application logs for font warnings

## Resources

- **Vazirmatn Font**: https://github.com/rastikerdar/vazirmatn
- **Persian Typography**: https://github.com/rastikerdar
- **Unicode Persian Range**: https://unicode.org/charts/PDF/U0600.pdf 