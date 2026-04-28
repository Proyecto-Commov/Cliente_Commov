# 🚀 Quick Start Guide

## 5-Minute Setup (Same Machine)

### Step 1: Install Dependencies (2 min)

```bash
cd c:\CLIENTE_COMMOV
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed Flask-2.3.0 Flask-Sock-0.2.9 Werkzeug-2.3.0
```

### Step 2: Verify FFmpeg (1 min)

```bash
ffmpeg -version
```

**Expected output:**
```
ffmpeg version X.X ...
```

If not found: Download from https://ffmpeg.org/download.html

### Step 3: Start the System (1 min)

```bash
cd c:\SERVIDOR_COMMOV
python iniciar_todo.py
```

**Expected output:**
```
============================================================
🚀 Iniciando Sistema Commov (Emisor + Receptor Web)
============================================================
📡 Iniciando Receptor Web (Puerto 8080)...
✅ Receptor Web iniciado correctamente
   Accede a: http://localhost:8080
   WebSocket: ws://localhost:8080/video

📸 Iniciando Cámara y Transmisión...
✅ Emisor iniciado

============================================================
🎬 SISTEMA EN FUNCIONAMIENTO
============================================================
Abre tu navegador en: http://localhost:8080
Presiona Ctrl+C para detener el sistema
============================================================
```

### Step 4: Open Browser (1 min)

Open: **http://localhost:8080**

You should see:
- Video title "Streaming en Directo"
- Status: "Reproduciendo..." (Green)
- Live video from your webcam

---

## Verify System is Working

### ✅ Test Checklist

- [ ] `iniciar_todo.py` shows "✅ Receptor Web iniciado correctamente"
- [ ] `iniciar_todo.py` shows "✅ Emisor iniciado"
- [ ] Browser opens without error
- [ ] Status shows "Conectado - Esperando video..."
- [ ] Video starts playing after 2-3 seconds
- [ ] Status changes to "Reproduciendo..." (Green)

### ❌ If Something's Wrong

**No video showing?**
```bash
# Check server is running
curl http://localhost:8080

# Check health
curl http://localhost:8080/health
```

Expected health response:
```json
{
  "status": "ok",
  "h264_connected": true,
  "queue_size": 10
}
```

**If `h264_connected` is false:** Emitter didn't connect. Check terminal output.

**If `queue_size` is 0:** No data flowing. Check that camera is working.

---

## Different Machine Setup (Client ≠ Server)

### On Server Machine:
```bash
cd c:\SERVIDOR_COMMOV
python emisor_directo.py
```

### On Client Machine:

1. **Edit** `c:\SERVIDOR_COMMOV\emisor_directo.py` (Line ~20):
```python
IP_RECEPTOR = "192.168.1.X"  # Server's IP address
```

2. **Start client:**
```bash
cd c:\CLIENTE_COMMOV
pip install -r requirements.txt
python receptor_web.py
```

3. **Open browser:**
```
http://localhost:8080
```

---

## Configuration Quick Reference

| Setting | File | Line | Default | Purpose |
|---------|------|------|---------|---------|
| Receiver IP | `emisor_directo.py` | ~20 | `127.0.0.1` | Where to send video |
| Video Width | `emisor_directo.py` | ~9 | `640` | Resolution width |
| Video Height | `emisor_directo.py` | ~10 | `480` | Resolution height |
| FPS | `emisor_directo.py` | ~11 | `30` | Frames per second |
| Bitrate | `emisor_directo.py` | ~12 | `1500k` | Video quality |
| Preset | `emisor_directo.py` | ~13 | `ultrafast` | Speed vs quality |
| Web Port | `receptor_web.py` | ~112 | `8080` | Access address |

---

## Common Issues & Quick Fixes

### "Connection refused"
```python
# In emisor_directo.py, change:
IP_RECEPTOR = "127.0.0.1"  # ← Make sure this is correct
```

### "FFmpeg not found"
```bash
ffmpeg -version
# If not found, download from ffmpeg.org
```

### "Port 8080 already in use"
```bash
# Windows
netstat -ano | findstr :8080
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8080
kill -9 <PID>
```

### "Video very laggy"
```python
# In emisor_directo.py:
preset="ultrafast"  # or "superfast"
bitrate="1500k"     # Keep it low for wifi
fps=30              # or reduce to 15-24
```

### "Firefox not working"
Use Chrome, Edge, or Safari instead (Firefox doesn't support H.264).

---

## Next Steps

After confirming it works:

1. **For production:** Read `INTEGRATION_GUIDE.md` → Security section
2. **For customization:** Edit `emisor_directo.py` config section
3. **For remote setup:** Change `IP_RECEPTOR` and configure firewall
4. **For debugging:** Check `COMPATIBILITY_CHECK.md`

---

## Need Help?

**See detailed documentation:**
- `INTEGRATION_GUIDE.md` - Full setup & troubleshooting
- `COMPATIBILITY_CHECK.md` - Technical validation

**Quick test commands:**
```bash
# Server health
curl http://localhost:8080/health

# Browser console errors
Press F12 → Console tab

# Check what's using the ports
netstat -ano | findstr :5000
netstat -ano | findstr :8080
```

---

**Good luck! 🎬**

