#### Jade Application Kit
# * https://codesardine.github.io/Jade-Application-Kit
# * Vitor Lopes Copyright (c) 2016 - 2020
# * https://vitorlopes.me

import sys
import subprocess
from JAK.Utils import Instance, bindings, getScreenGeometry
from JAK import Settings
from JAK.Widgets import JWindow
from JAK.WebEngine import JWebView
if bindings() == "PyQt5":
    print("PyQt5 Bindings")
    from PyQt5.QtCore import Qt, QCoreApplication
    from PyQt5.QtWidgets import QApplication
else:
    print("JAK_PREFERRED_BINDING environment variable not set, falling back to PySide2 Bindings.")
    from PySide2.QtCore import Qt, QCoreApplication
    from PySide2.QtWidgets import QApplication


class JWebApp(QApplication):
    #### Imports: from JAK.Application import JWebApp
    def __init__(self, config=Settings.config(), **app_config):
        super(JWebApp, self).__init__(sys.argv)
        self.config = config
        self.setAAttribute(Qt.AA_UseHighDpiPixmaps)
        self.setAAttribute(Qt.AA_EnableHighDpiScaling)
        self.applicationStateChanged.connect(self._applicationStateChanged_cb)

        for key, value in app_config.items():
            if isinstance(value, dict):
                for subkey, subvalue in app_config[key].items():
                    config[key][subkey] = subvalue
            else:
                config[key] = value

        if config["setAAttribute"]:
            for attr in config["setAAttribute"]:
                self.setAAttribute(attr)

        if config["remote-debug"] or "--remote-debug" in sys.argv:
            sys.argv.append("--remote-debugging-port=9000")

        if config["debug"] or "--dev" in sys.argv:
            print("Debugging On")
            if not config["debug"]:
                config["debug"] = True
        else:
            print("Production Mode On, use (--dev) for debugging")

        # Enable/Disable GPU acceleration
        if not config["disableGPU"]:
            # Virtual machine detection using SystemD
            detect_virtual_machine = subprocess.Popen(
                ["systemd-detect-virt"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
            detect_nvidia_pci = subprocess.Popen(
                "lspci | grep -i --color 'vga\|3d\|2d'", stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                shell=True
            )
            virtual = detect_virtual_machine.communicate()[-1]
            nvidia_pci = detect_nvidia_pci.communicate()[0].decode("utf-8").lower()

        if config["disableGPU"]:
            self.disable_opengl()
            print("Disabling GPU, Software Rendering explicitly activated")
        else:
            if virtual:
                # Detect virtual machine
                print(f"Virtual machine detected:{virtual}")
                self.disable_opengl()

            elif nvidia_pci:
                # Detect NVIDIA cards
                if "nvidia" in nvidia_pci:
                    print("NVIDIA falling back to Software Rendering")
                    self.disable_opengl()
            else:
                print(f"Virtual Machine:{virtual}")

        if not self.config['webview']['online'] and self.config['webview']['IPC']:
            if bindings() == "PyQt5":
                from PyQt5.QtWebEngineCore import QWebEngineUrlScheme
            else:
                from PySide2.QtWebEngineCore import QWebEngineUrlScheme
            QWebEngineUrlScheme.registerScheme(QWebEngineUrlScheme("ipc".encode()))

    def _applicationStateChanged_cb(self, event):
        view = Instance.retrieve("view")
        page = view.page()
        # TODO freeze view when inactive to save ram
        if event == Qt.ApplicationInactive:
            print("inactive")
        elif event == Qt.ApplicationActive:
            print("active")

    def disable_opengl(self):
        # Disable GPU acceleration
        # https://codereview.qt-project.org/c/qt/qtwebengine-chromium/+/206307
        self.setAAttribute(Qt.AA_UseSoftwareOpenGL)

    def setAAttribute(self, attr):
        QCoreApplication.setAttribute(attr, True)
        
    def run(self):
        Instance.record("view", JWebView(self.config))
        win = Instance.auto("win", JWindow(self.config))

        if self.config['window']["transparent"]:
            from JAK.Utils import JavaScript
            JavaScript.css(
                "body, html {background-color:transparent !important;background-image:none !important;}", "JAK"
            )

        if self.config['webview']["addCSS"]:
            from JAK.Utils import JavaScript
            JavaScript.css(self.config['webview']["addCSS"], "user")
            print("Custom CSS detected")

        if self.config['webview']["runJavaScript"]:
            from JAK.Utils import JavaScript
            JavaScript.send(self.config['webview']["runJavaScript"])
            print("Custom JavaScript detected")

        if self.config['window']["fullScreen"]:
            screen = getScreenGeometry()
            win.resize(int(screen.width()), int(screen.height()))
        else:
            width, height = int(win.default_size("width")), int(win.default_size("height"))
            win.resize(width, height)

        win.setFocusPolicy(Qt.WheelFocus)
        win.show()
        win.setFocus()
        win.window_original_position = win.frameGeometry()
        self.exec_()
