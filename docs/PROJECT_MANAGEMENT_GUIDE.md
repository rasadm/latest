# 🛠️ Project Management Guide

## Overview

The Project Management System now includes comprehensive stop and remove functionality, allowing you to control project execution and clean up unwanted projects safely.

## 🔧 New Features Added

### 1. Stop Project Functionality

**Purpose**: Pause a running project and remove its items from the publishing queue while keeping all generated content.

**How to Use**:
- Click **"⏹️ Stop Project"** button in the dashboard
- Or right-click on a project and select **"⏹️ Stop Project"**
- Or use the stop button in the project detail page

**What It Does**:
- ✅ Pauses the project (changes status to "paused")
- ✅ Removes pending items from publishing queue
- ✅ Keeps all generated content files
- ✅ Stops any ongoing content generation

### 2. Remove Project Functionality

**Purpose**: Permanently delete a project and all its associated data.

**How to Use**:
- Click **"🗑️ Remove Project"** button in the dashboard
- Or right-click on a project and select **"🗑️ Remove Project"**
- Or use the remove button in the project detail page

**Safety Features**:
- ⚠️ **Double Confirmation**: Requires clicking "Yes" and typing "DELETE"
- 📋 **Clear Warning**: Shows exactly what will be deleted
- 🔒 **Case Sensitive**: Must type "DELETE" exactly

**What It Does**:
- 🗑️ Deletes project from the system
- 📁 Removes ALL content files from disk
- 📅 Removes ALL items from publishing queue
- ⚠️ **PERMANENT** - Cannot be undone!

### 3. Context Menu (Right-Click)

**Purpose**: Quick access to project actions based on project status.

**How to Use**:
- Right-click on any project in the list
- Select the desired action from the context menu

**Available Actions**:
- **📝 View Details**: Open project detail page
- **▶️ Run Project**: Start content generation (active projects)
- **⏹️ Stop Project**: Stop and pause project (active projects)
- **▶️ Resume Project**: Resume paused project (paused projects)
- **🔄 Restart Project**: Reset completed project (completed projects)
- **📁 View Files**: Open project directory
- **📅 View Queue**: View publishing queue
- **🗑️ Remove Project**: Permanently delete project

### 4. Enhanced Project Controls

**Project Detail Page**:
- Added **"⏹️ Stop Project"** button
- Added **"🗑️ Remove Project"** button
- Added **"📁 View Files"** button
- Organized controls into logical groups

**Main Dashboard**:
- Added **"⏹️ Stop Project"** button
- Added **"🗑️ Remove Project"** button
- Enhanced queue status display

## 📊 Project Status Management

### Project Statuses

1. **🟢 Active**: Project is running or ready to run
2. **🟡 Paused**: Project is stopped but can be resumed
3. **🔵 Completed**: Project has generated all target content

### Status Transitions

```
Active ──────► Paused (Stop Project)
  │               │
  │               ▼
  │           Active (Resume Project)
  │               │
  ▼               ▼
Completed ──► Active (Restart Project)
  │
  ▼
Deleted (Remove Project)
```

## 🛡️ Safety Features

### Stop Project Safety
- **Non-Destructive**: Keeps all generated content
- **Reversible**: Can resume or restart later
- **Queue Cleanup**: Removes pending publishing items
- **Immediate Effect**: Stops generation immediately

### Remove Project Safety
- **Double Confirmation**: Two-step confirmation process
- **Clear Warnings**: Detailed explanation of consequences
- **Type Verification**: Must type "DELETE" to confirm
- **Complete Cleanup**: Removes all traces of the project

### Publishing Queue Safety
- **Automatic Cleanup**: Removes project items when stopped/removed
- **Status Tracking**: Maintains queue integrity
- **Error Handling**: Graceful handling of queue operations

## 🔄 Workflow Examples

### Example 1: Stop a Running Project
1. Project is generating content (status: Active)
2. Click **"⏹️ Stop Project"**
3. Confirm the action
4. Project status changes to "Paused"
5. Queue items are removed
6. Content generation stops
7. Generated files remain intact

### Example 2: Remove an Unwanted Project
1. Right-click on project in list
2. Select **"🗑️ Remove Project"**
3. Read the warning carefully
4. Click "Yes" to proceed
5. Type "DELETE" in the confirmation box
6. Project is permanently removed
7. All files and queue items deleted

### Example 3: Resume a Paused Project
1. Right-click on paused project
2. Select **"▶️ Resume Project"**
3. Project status changes to "Active"
4. Can run the project again
5. Will continue from where it left off

### Example 4: Restart a Completed Project
1. Right-click on completed project
2. Select **"🔄 Restart Project"**
3. Confirm the restart
4. Completed count resets to 0
5. Status changes to "Active"
6. Can generate all content again

## 🚨 Important Warnings

### Before Stopping a Project
- ✅ Generated content will be preserved
- ✅ Can resume later from where it stopped
- ⚠️ Pending publishing will be cancelled
- ⚠️ May interrupt ongoing content generation

### Before Removing a Project
- ⚠️ **ALL DATA WILL BE LOST**
- ⚠️ **CANNOT BE UNDONE**
- ⚠️ All content files will be deleted
- ⚠️ All queue items will be removed
- ⚠️ Project configuration will be lost

## 🔧 Technical Details

### Files Affected by Stop
- `projects.json` - Project status updated
- `publishing_queue.json` - Queue items removed
- Content files - **NOT AFFECTED**

### Files Affected by Remove
- `projects.json` - Project entry deleted
- `publishing_queue.json` - Queue items removed
- `projects/project_[id]_[name]/` - **ENTIRE DIRECTORY DELETED**

### Queue Management
- **Stop**: Removes only pending items for the project
- **Remove**: Removes all items for the project
- **Resume**: Does not restore queue items (must run project again)

## 🎯 Best Practices

### When to Stop a Project
- ✅ Need to pause content generation temporarily
- ✅ Want to modify project settings
- ✅ Need to free up system resources
- ✅ Experiencing errors that need investigation

### When to Remove a Project
- ✅ Project was created by mistake
- ✅ No longer need the content
- ✅ Want to start completely fresh
- ✅ Project has wrong configuration that can't be fixed

### Before Removing
1. **Backup Important Content**: Copy any valuable content files
2. **Check Queue Status**: Ensure no important publishing is pending
3. **Verify Project**: Make sure you're removing the right project
4. **Consider Stopping**: Maybe stopping is sufficient instead of removing

## 🆘 Troubleshooting

### Stop Project Issues
- **Problem**: Stop button doesn't work
- **Solution**: Check if project is actually running, try refreshing the list

- **Problem**: Queue items not removed
- **Solution**: Check `publishing_queue.json` file, restart the dashboard

### Remove Project Issues
- **Problem**: Can't type "DELETE"
- **Solution**: Make sure caps lock is on, type exactly "DELETE"

- **Problem**: Files not deleted
- **Solution**: Check file permissions, close any open files in the directory

### General Issues
- **Problem**: Buttons are grayed out
- **Solution**: Select a project first, check project status

- **Problem**: Context menu doesn't appear
- **Solution**: Right-click directly on a project name in the list

## 📞 Support

If you encounter issues with stop/remove functionality:

1. Check the **Activity Log** for error messages
2. Verify **Project Status** in the dashboard
3. Check **File Permissions** for project directories
4. Restart the **Project Dashboard** if needed
5. Manually check `projects.json` and `publishing_queue.json` files

The system is designed to be safe and reliable, with multiple confirmations for destructive actions and comprehensive error handling. 