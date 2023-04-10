import launch

if not launch.is_installed("notion_client"):
    launch.run_pip("install notion_client", "requirements for Organizer")