import launch

if not launch.is_installed("bs4"):
    launch.run_pip("install bs4", "Required by gdown")
