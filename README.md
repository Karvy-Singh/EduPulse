# EduPulse - Multilingual PA System

<div align="center">

![EduPulse Banner](https://img.shields.io/badge/Agora-X-blue?style=for-the-badge&logo=agora)
![GDG Hackfest 2025](https://img.shields.io/badge/GDG-Hackfest%202025-orange?style=for-the-badge)
![Problem Statement](https://img.shields.io/badge/Problem-LA--04-green?style=for-the-badge)

[Features](#-features) • [Demo](#-demo) • [Installation](#-installation) • [Usage](#-usage) • [Architecture](#-architecture)

</div>

---

## Problem Statement

**LA-04: PA System**

Public announcements must be quickly localized into many languages during festivals or crises. The challenge is to build a system that:

- Converts a single announcement into multiple languages
- Provides both text and audio outputs
- Supports instant deployment for public safety and inclusivity

## Solution: EduPulse

EduPulse is an intelligent, real-time public announcement system that automatically monitors multiple communication channels (email and Google Classroom), translates announcements into multiple languages, and broadcasts them via high-quality text-to-speech audio.

### Key Highlights

- **Multi-channel monitoring**: Automatically polls Gmail and Google Classroom for new announcements
- **Real-time audio broadcasting**: Powered by Agora's Conversational AI with OpenAI TTS
- **Multilingual support**: Supports English, Hindi, Tamil, Telugu, and Bengali
- **Auto-broadcast**: Critical announcements can be automatically played
- **Modern UI**: Clean, intuitive PyQt6 interface with dark theme
- **Persistent settings**: All configurations saved in `settings.json`

---

## Features

### Automatic Monitoring
- **Gmail Integration**: Polls email inbox for official announcements
- **Google Classroom Integration**: Monitors classroom announcements across all courses
- **Configurable intervals**: Set custom polling frequencies (5-3600 seconds)

### Multilingual Support
- Real-time language selection
- Support for 5+ Indian languages
- Automatic translation of announcement text
- Language-specific TTS output

### Audio Broadcasting
- **Agora RTC Integration**: Low-latency, high-quality audio
- **OpenAI TTS**: Natural-sounding voice synthesis
- **Smart truncation**: Limits broadcasts to first 60 words for clarity
- **Manual or automatic playback**: User-controlled or auto-broadcast mode

### User Interface
- **Feed View**: Real-time announcement cards with source, timestamp, and content
- **Settings Panel**: Complete configuration management
- **Status Monitoring**: Live connection and polling status
- **Dark Theme**: Modern, easy-on-the-eyes design

---

## Demo

https://github.com/user-attachments/assets/0b3be601-721f-4fde-8e77-293ad37608e4




### Main Feed

![WhatsApp Image 2025-11-14 at 21 20 19](https://github.com/user-attachments/assets/88b64103-49f7-4f19-98a6-631ab86874dc)
*Real-time announcement feed with play audio controls*

### Settings Panel

![WhatsApp Image 2025-11-15 at 09 23 45](https://github.com/user-attachments/assets/65a3a8ed-991f-40b1-a8b6-974c93790e2c)

*Comprehensive settings for all integrations*

### Audio Playback
- Announcements are broadcast with natural-sounding voice
- Visual feedback during playback
- Quick manual replay option

---

## Installation

### Prerequisites

- **Python 3.8+**
- **Chrome/Chromium browser** (for Agora voice client)
- **ChromeDriver** (matching your Chrome version)
- **Agora account** ([Sign up free](https://www.agora.io))
- **OpenAI API key** ([Get API key](https://platform.openai.com))
- **Google Cloud Project** (for Gmail and Classroom APIs)

### Step 1: Clone the Repository

```bash
git clone https://github.com/codelif/edupulse.git
cd edupulse
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**requirements.txt:**
```txt
PyQt6>=6.6.0
requests>=2.31.0
selenium>=4.15.0
google-auth>=2.23.0
google-auth-oauthlib>=1.1.0
google-api-python-client>=2.108.0
python-dotenv>=1.0.0
```

### Step 3: Set Up Agora

1. Create an Agora account at [agora.io](https://www.agora.io)
2. Create a new project
3. Get your **App ID**
4. Generate an **RTC Token** for your channel
5. Get your **Basic Authorization** header (Base64 encoded credentials)


### Step 4: Gmail API
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Enable **Gmail API**
4. Create OAuth 2.0 credentials
5. Download credentials as `credentials.json` (place in project root)

### Step 5: Google Classroom API Setup (One-Time Configuration)

To enable Google Classroom functionality in this project, each user must perform a one-time OAuth setup and download a `credentials.json` file. Follow the steps below.

---

#### 1. Enable APIs and Configure OAuth Consent Screen

1. Open **Google Cloud Console**.
2. Go to **APIs & Services → Credentials**.
3. Click **Configure Consent Screen**.
4. Select **External** as the user type (unless you specifically require Internal).
5. Fill out the required application information.
6. Add your email address under Audience-> **Test Users**.
7. Save and proceed through the remaining steps.

---

#### 2. Create OAuth Client

1. Inside **APIs & Services → Credentials**, click **Create Credentials**.
2. Select **OAuth Client ID**.
3. Choose **Desktop App** as the application type.
4. Create the client.
5. Download the generated **credentials JSON** file.
6. Place the file in the root directory of the project and rename it to:


### Step 6: Get OpenAI API Key

1. Sign up at [OpenAI](https://platform.openai.com)
2. Generate an API key
3. Ensure you have credits available

---

##  Usage

### First Run

1. **Start the application:**
   ```bash
   python main.py
   ```

2. **Configure Settings:**
   - Click **Settings** in the sidebar
   - Fill in all required fields:
     - **Email Settings**: Gmail credentials
     - **Agora Settings**: App ID, Channel, Token, OpenAI Key, Authorization
     - **Polling Settings**: Set intervals for email and classroom polling
   - Click **Save Settings**
   - **Restart the application**

3. **Initial Setup:**
   - On first Gmail access, browser will open for OAuth authentication
   - On first Classroom access, grant necessary permissions
   - These tokens are saved for future use

### Running the System

1. **Monitor Feed:**
   - The feed page shows all incoming announcements
   - New announcements appear at the top
   - Each card shows source, timestamp, and content

2. **Audio Playback:**
   - **Manual**: Click "Play Audio" on any announcement card
   - **Automatic**: Enable "Enable auto broadcast" checkbox
   - Audio limited to first 60 words for clarity

3. **Language Selection:**
   - Select output language from dropdown (English, Hindi, Tamil, etc.)
   - Future announcements will use selected language

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                         EduPulse                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐   ┌──────────────┐  │
│  │   Gmail      │    │  Classroom   │   │   Settings   │  │
│  │   Poller     │    │   Poller     │   │   Manager    │  │
│  └──────┬───────┘    └──────┬───────┘   └──────────────┘  │
│         │                   │                               │
│         └───────────┬───────┘                               │
│                     ▼                                       │
│         ┌────────────────────────┐                         │
│         │   Announcement Feed    │                         │
│         │      (UI Layer)        │                         │
│         └───────────┬────────────┘                         │
│                     ▼                                       │
│         ┌────────────────────────┐                         │
│         │   Agora Manager        │                         │
│         │   - Voice Client       │                         │
│         │   - TTS Integration    │                         │
│         └────────────────────────┘                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
           │                    │                    │
           ▼                    ▼                    ▼
    ┌───────────┐      ┌──────────────┐     ┌─────────────┐
    │   Gmail   │      │ Google       │     │   Agora     │
    │    API    │      │ Classroom    │     │ RTC + AI    │
    └───────────┘      │     API      │     └─────────────┘
                       └──────────────┘
```

### Technology Stack

**Frontend:**
- PyQt6 - Modern GUI framework
- Custom dark theme with responsive design

**Backend:**
- Python 3.8+
- Threading for concurrent polling
- JSON-based settings management

**Integrations:**
- **Agora RTC**: Real-time communication
- **Agora Conversational AI**: Agent orchestration
- **OpenAI GPT-4**: Language processing
- **OpenAI TTS**: Text-to-speech synthesis
- **Gmail API**: Email monitoring
- **Google Classroom API**: Classroom announcements
- **Selenium WebDriver**: Agora voice client automation

### Data Flow

1. **Polling**: Gmail and Classroom pollers run in background threads
2. **Detection**: New announcements detected via UID/timestamp tracking
3. **Processing**: Announcement text extracted and formatted
4. **Translation**: Text translated to selected language (future enhancement)
5. **Display**: Announcement card added to feed UI
6. **Broadcasting**: 
   - Manual: User clicks "Play Audio"
   - Auto: If auto-broadcast enabled
7. **TTS**: First 60 words sent to Agora agent
8. **Audio**: Agent uses OpenAI TTS to synthesize speech
9. **Playback**: Audio streamed via Agora RTC to speakers

---

## ⚙️ Configuration

### Settings File (`settings.json`)

```json
{
    "email": {
        "imap_host": "imap.gmail.com",
        "username": "announcements@school.edu",
        "password": "your_app_password"
    },
    "agora": {
        "app_id": "your_agora_app_id",
        "channel": "pa_channel",
        "token": "your_rtc_token",
        "openai_key": "sk-proj-...",
        "authorization": "Basic base64_encoded_credentials",
        "headless": true
    },
    "polling": {
        "email_interval": 60,
        "classroom_interval": 60
    },
    "audio": {
        "default_language": "English",
        "auto_broadcast": false
    }
}
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. "Failed to initialize Agora"

**Causes:**
- Invalid authorization header
- Expired RTC token
- Invalid App ID
- OpenAI API key issues

**Solutions:**
- Regenerate RTC token from Agora console
- Verify authorization is Base64 encoded: `customer_id:customer_secret`
- Check OpenAI API key has credits
- Ensure App ID matches your Agora project

#### 2. "Gmail credentials not configured"

**Solutions:**
- Fill in email settings in Settings panel
- Use App Password for Gmail (not regular password)
- Enable "Less secure app access" or use OAuth

#### 3. Chrome driver issues

**Solutions:**
- Install ChromeDriver matching your Chrome version
- Add ChromeDriver to PATH
- Or specify path in code

#### 4. No announcements appearing

**Solutions:**
- Check polling intervals in settings
- Verify Gmail/Classroom credentials
- Check console for error messages
- Ensure first-run OAuth completed successfully

#### 5. Audio not playing

**Solutions:**
- Check system audio settings
- Verify Agora token is valid
- Set `headless: false` in settings to see browser
- Check OpenAI TTS model availability

---


---

<div align="center">

**Built with ❤️ for Agora X GDG Hackfest 2025**

</div>
