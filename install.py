import launch

if not launch.is_installed("bs4"):
    launch.run_pip("install bs4", "bs4 requirement for GDisk links parsing")

if not launch.is_installed("requests-cache"):
    launch.run_pip("install requests-cache", "requests-cache requirement disabling download cache")

# Make this installation optional only for Firebase storage due to incompatible
# protobuf (4.22.0) version dependency of latest (6.1.0) firebase-admin version. But tensorboard requires 3.20.0
# Firebase version that should work fine is 4.5.0

# if not launch.is_installed("firebase-admin"):
#     launch.run_pip("install firebase-admin==4.5.0", "firebase-admin requirement for the Firestore usage")
