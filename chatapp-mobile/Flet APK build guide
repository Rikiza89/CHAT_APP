# Building ChatApp APK with Flet

## Project Structure

```
chatapp-mobile/
├── main.py              # Main Flet app
├── requirements.txt     # Python dependencies
└── assets/             # Optional: icons, images
    └── icon.png        # App icon (512x512 PNG)
```

## Setup Instructions

### 1. Install Flet

```bash
pip install flet
```

### 2. Configure API Endpoints

Edit `main.py` and update these lines:

```python
API_BASE_URL = "http://YOUR_SERVER_IP:8000/api/v1"
WS_BASE_URL = "ws://YOUR_SERVER_IP:8000/ws"
```

**Important:** 
- Use your actual server IP (Raspberry Pi or local server)
- Don't use `localhost` - it won't work on mobile
- For production, use your domain with HTTPS

### 3. Test Locally First

```bash
python main.py
```

This opens a desktop window to test the app before building APK.

## Building APK

### Option 1: Using Flet Build (Recommended)

```bash
# Install flet build tools
pip install flet

# Build APK
flet build apk --project chatapp-mobile --build-number 1 --build-version "1.0.0"
```

**Build options:**
- `--project`: Your project name
- `--build-number`: Increment for each release (1, 2, 3...)
- `--build-version`: Version string (1.0.0, 1.1.0, etc.)
- `--org`: Organization ID (e.g., com.yourcompany)

Full command with all options:
```bash
flet build apk \
  --project chatapp \
  --org com.mycompany \
  --build-number 1 \
  --build-version "1.0.0" \
  --deep-linking-url "myapp://open"
```

### Option 2: Manual Build with Android Studio

If you need more control:

```bash
# Package as Android project
flet build apk --project chatapp --android-only

# This creates an Android Studio project in:
# build/android/
```

Then open in Android Studio and build manually.

## APK Location

After successful build:
```
build/apk/app-release.apk
```

## Installing APK

### On Physical Device:
1. Transfer APK to phone via USB/email/cloud
2. Enable "Install from Unknown Sources" in Settings
3. Open APK and install

### On Emulator:
```bash
adb install build/apk/app-release.apk
```

## Customization

### 1. App Icon

Create a 512x512 PNG icon and place in `assets/icon.png`:

```bash
flet build apk --icon assets/icon.png
```

### 2. App Name

In `main.py`, change:
```python
page.title = "Your App Name"
```

### 3. Permissions

Create `AndroidManifest.xml` in project root:

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
</manifest>
```

Then build with:
```bash
flet build apk --android-manifest AndroidManifest.xml
```

## Backend Requirements

Your Django backend needs these endpoints working:

### REST API:
- `POST /api/v1/token/` - Login (returns JWT)
- `POST /api/v1/register/` - Registration
- `GET /api/v1/rooms/` - List chat rooms
- `POST /api/v1/rooms/` - Create room

### WebSocket:
- `ws://server/ws/chat/{room_id}/` - Chat room WebSocket

## Common Issues

### "Can't connect to server"
- Check `API_BASE_URL` is correct
- Ensure phone is on same network as server
- Check Django `ALLOWED_HOSTS` includes server IP
- Verify firewall allows port 8000

### WebSocket not working
- Use `ws://` not `wss://` for local network
- Check Django Channels is running
- Verify no proxy blocking WebSocket

### Build fails
```bash
# Update flet
pip install --upgrade flet

# Clean build
rm -rf build/
flet build apk --clean
```

## Production Deployment

For production (not local network):

1. **Get a domain and SSL certificate**
2. **Update endpoints:**
   ```python
   API_BASE_URL = "https://your-domain.com/api/v1"
   WS_BASE_URL = "wss://your-domain.com/ws"
   ```
3. **Configure Django for HTTPS**
4. **Rebuild APK**

## Testing Checklist

- [ ] Login works
- [ ] Registration works
- [ ] Room list loads
- [ ] Can create new room
- [ ] Messages send in real-time
- [ ] Messages received from other users
- [ ] Logout works
- [ ] App reconnects after network interruption

## Development Workflow

```bash
# 1. Make changes to main.py
# 2. Test locally
python main.py

# 3. Test on device (hot reload)
flet run --android

# 4. Build final APK when ready
flet build apk --build-number 2
```

## File Sizes

- Typical APK size: 15-40 MB
- First build takes 5-10 minutes
- Subsequent builds: 1-2 minutes

## Next Steps

After successful build, consider:
1. Add push notifications
2. Add file/image sharing
3. Add user search
4. Implement offline message queue
5. Add biometric authentication
6. Publish to Google Play Store

## Publishing to Play Store

1. Create Google Play Developer account ($25 one-time)
2. Build signed APK:
   ```bash
   flet build apk --release
   ```
3. Create app listing
4. Upload APK
5. Submit for review

## Support

- Flet docs: https://flet.dev
- Django Channels: https://channels.readthedocs.io
- Issues: Check logs with `adb logcat`
