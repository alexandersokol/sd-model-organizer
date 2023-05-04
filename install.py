import launch

if not launch.is_installed("bs4"):
    launch.run_pip("install bs4", "Required to parse GDisk links")

if not launch.is_installed("firebase-admin"):
    launch.run_pip("install firebase-admin", "Required for Firebase Storage")
