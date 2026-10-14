import logging
import platform

logger = logging.getLogger("SecureFlow.Notifier")

class DesktopNotifier:
    def __init__(self, app_name: str = "SecureFlow AI"):
        self.app_name = app_name
        self._plyer_available = False
        try:
            from plyer import notification
            self._plyer = notification
            self._plyer_available = True
        except Exception as e:
            logger.debug(f"Plyer notifications not available: {e}")

    def notify(self, title: str, message: str, urgency: str = "normal"):
        """Displays a desktop notification with cross-platform fallback."""
        logger.info(f"[ALERT: {title}] {message}")
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

        # Windows-specific fallback using ctypes/MessageBox or powershell if needed
        if platform.system() == "Windows":
            self._windows_tray_fallback(title, message)

    def _windows_tray_fallback(self, title: str, message: str):
        try:
            import subprocess
            # Non-blocking PowerShell balloon tip
            clean_msg = message.replace("'", "`'")
            ps_cmd = (
                "[reflection.assembly]::loadwithpartialname('System.Windows.Forms') | Out-Null; "
                "$notify = new-object system.windows.forms.notifyicon; "
                "$notify.icon = [system.drawing.systemicons]::Information; "
                "$notify.visible = $true; "
                f"$notify.showballoontip(4000, '{title}', '{clean_msg}', [system.windows.forms.tooltipicon]::Warning)"
            )
            subprocess.Popen(["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", ps_cmd],
                             creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        except Exception:
            pass
