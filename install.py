import launch

if not launch.is_installed("bs4"):
    launch.run_pip("install bs4", "bs4 requirement for GDick links parsing")

if not launch.is_installed("firebase-admin"):
    launch.run_pip("install firebase-admin==4.5.0", "firebase-admin requirement for the Firestore usage")
