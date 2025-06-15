# 📅 Publishing Queue System Guide

## Overview

The Publishing Queue System automatically schedules and publishes your content at specified intervals, ensuring consistent content delivery without manual intervention.

## How It Works

### 1. Content Generation & Scheduling

When you click **"Run Project"**, the system:

1. **Generates All Content**: Creates all remaining content pieces for the project
2. **Creates Publishing Queue**: Schedules each content piece based on your publishing interval
3. **Saves Queue**: Stores the schedule in `publishing_queue.json`

### 2. Automatic Publishing

The **Publishing Scheduler** runs in the background and:

1. **Monitors Queue**: Checks every minute for content due for publishing
2. **Publishes Content**: Automatically publishes content to WordPress at scheduled times
3. **Updates Status**: Tracks publishing success/failure for each item

### 3. Publishing Schedule Logic

- **First Content**: Publishes immediately after generation
- **Subsequent Content**: Publishes at intervals you specified (e.g., every 5 minutes)
- **Example**: If interval is 5 minutes:
  - Content 1: Publishes now
  - Content 2: Publishes in 5 minutes
  - Content 3: Publishes in 10 minutes
  - Content 4: Publishes in 15 minutes

## Using the System

### Step 1: Create a Project

1. Click **"✨ New Project"**
2. Set your **Publishing Interval** (minutes between posts)
3. Choose your **WordPress Website**
4. Add your **Keywords** and settings
5. Click **"💾 Save Project"**

### Step 2: Run the Project

1. Select your project from the list
2. Click **"▶️ Run Project"**
3. Watch as content is generated and queued
4. Check the **Publishing Queue Status** in the dashboard

### Step 3: Monitor Publishing

1. Click **"📅 View Queue"** to see scheduled content
2. Monitor the **Queue Status** in the main dashboard
3. Check the **Activity Log** for publishing updates

## Queue Status Indicators

- **⏰ Queued**: Content scheduled for future publishing
- **✅ Published**: Content successfully published to WordPress
- **❌ Failed**: Publishing failed (will retry automatically)
- **⚠️ Error**: System error occurred

## Background Scheduler

### Starting the Scheduler

The scheduler starts automatically when you open the Project Dashboard. You can also run it separately:

```bash
python publishing_scheduler.py
```

Or use the batch file:
```bash
start_publishing_scheduler.bat
```

### Scheduler Features

- **Automatic Retry**: Failed publications are retried automatically
- **Error Handling**: Graceful handling of network issues and API errors
- **Status Tracking**: Real-time status updates for all queue items
- **Queue Management**: Automatic cleanup of completed items

## Queue Management

### Viewing the Queue

1. Click **"📅 View Queue"** in the main dashboard
2. See all scheduled content with timestamps
3. Check status and time remaining for each item

### Queue Actions

- **🔄 Refresh**: Update queue display with latest status
- **🧹 Clear Completed**: Remove successfully published items
- **📅 Reschedule**: Manually reschedule failed items (via scheduler)

## File Structure

```
publishing_queue.json    # Queue data storage
publishing_scheduler.py  # Background scheduler service
project_dashboard.py     # Main GUI with queue integration
project_manager.py       # Queue creation and management
```

## Troubleshooting

### Content Not Publishing

1. **Check WordPress Credentials**: Ensure settings are correct
2. **Verify Queue Status**: Use "📅 View Queue" to check item status
3. **Check Activity Log**: Look for error messages
4. **Restart Scheduler**: Close and reopen the dashboard

### Publishing Errors

- **401 Unauthorized**: Check WordPress credentials and user permissions
- **Network Errors**: Check internet connection
- **File Not Found**: Ensure content files exist in project directory

### Queue Issues

- **Empty Queue**: Run the project again to regenerate queue
- **Stuck Items**: Use "🧹 Clear Completed" to clean up
- **Wrong Times**: Check project publishing interval settings

## Best Practices

1. **Set Realistic Intervals**: Don't publish too frequently (minimum 1-5 minutes)
2. **Monitor Queue Status**: Check regularly for failed items
3. **Keep Scheduler Running**: Don't close the dashboard during publishing
4. **Backup Content**: Content files are saved locally as backup
5. **Test Settings**: Start with small projects to test your configuration

## Advanced Features

### Custom Scheduling

You can modify `publishing_queue.json` manually to:
- Change publishing times
- Reorder content
- Add custom metadata

### Integration with Other Tools

The queue system can be extended to:
- Send notifications when content is published
- Integrate with social media scheduling
- Generate publishing reports

## Support

If you encounter issues:

1. Check the **Activity Log** for error details
2. Review the **Queue Status** for stuck items
3. Restart the **Publishing Scheduler**
4. Verify your **WordPress Settings**

The system is designed to be robust and handle most issues automatically, but manual intervention may be needed for complex WordPress configuration problems. 