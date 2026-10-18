import sys
import logging
import platform
import threading

logger = logging.getLogger("SecureFlow.Notifier")

class DesktopNotifier:
    def __init__(self, app_name: str = "SecureFlow AI"):
        self.app_name = app_name
        self._win11_available = False
        try:
            import win11toast
            self._win11 = win11toast
            self._win11_available = True
        except Exception:
            pass

        self._plyer_available = False
        try:
            from plyer import notification
            self._plyer = notification
            self._plyer_available = True
        except Exception:
            pass

    def notify(self, title: str, message: str, urgency: str = "normal"):
        """Displays a desktop notification with audible chime and native Windows toast in background thread."""
        logger.info(f"[ALERT: {title}] {message}")

        # Play system audio chime immediately on Windows
        if platform.system() == "Windows":
            try:
                import winsound
                if "BLOCK" in title or "CRITICAL" in title or urgency == "critical":
                    winsound.MessageBeep(winsound.MB_ICONHAND)
                else:
                    winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            except Exception:
                pass

        # Trigger desktop toast in non-blocking daemon thread
        threading.Thread(
            target=self._dispatch_toast,
            args=(title, message),
            daemon=True
        ).start()

    def _dispatch_toast(self, title: str, message: str):
        # 1. Primary: Native Windows 10/11 Toast via win11toast
        if self._win11_available and platform.system() == "Windows":
            try:
                self._win11.toast(f"🛡️ {self.app_name} - {title}", message)
                return
            except Exception as e:
                logger.debug(f"win11toast failed: {e}")

        # 2. Secondary: Plyer
        if self._plyer_available:
            try:
                self._plyer.notify(
                    title=f"🛡️ {self.app_name} - {title}",
                    message=message,
                    app_name=self.app_name,
                    timeout=5
                )
                return
            except Exception as e:
                logger.debug(f"Plyer notification failed: {e}")

        # 3. Tertiary: PowerShell Balloon Tip Fallback
        if platform.system() == "Windows":
            self._windows_tray_fallback(title, message)

    def _windows_tray_fallback(self, title: str, message: str):
        try:
            import subprocess
            clean_msg = message.replace("'", "`'").replace("\n", " ")
            clean_title = title.replace("'", "`'")
            ps_cmd = (
                "[reflection.assembly]::loadwithpartialname('System.Windows.Forms') | Out-Null; "
                "$notify = new-object system.windows.forms.notifyicon; "
                "$notify.icon = [system.drawing.systemicons]::Warning; "
                "$notify.visible = $true; "
                f"$notify.showballoontip(4000, '{clean_title}', '{clean_msg}', [system.windows.forms.tooltipicon]::Warning)"
            )
            subprocess.Popen(["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", ps_cmd],
                             creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        except Exception:
            pass
