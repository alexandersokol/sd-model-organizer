# SD Model Organizer

SD Model Organizer is a [Stable Diffusion WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui]) extension
that allows users to store information about different models
needed for Stable Diffusion WebUI, add information, description, own notes and download them.

![readme_home.png](pic/readme_home.png)

## 🚀 Core features

- Sort model records by time added, name, model types, groups and search by name.
- Downloads model with single click
- Downloads batch of models regarding to the filter applied on home screen.
- Downloads models to the model type predefined path or manually selected.
- Downloads models into subdirectories.
- Downloads model's preview.
- Add model preview.
- Add model description and own notes with rich text editor (TinyMCE)
- Stores model records in local SQLite database.
- Stores model records in remote Firebase Firestore.
- Export/import existing model as json files.
- Dark/Light theme support.




## Home Screen

- Shows model records added by users with cards or table layout
- Allows one-click download of a model
- Enables filtering of added model records by name, group, and model type
- Allows sorting by time added or name
- Enables exporting/importing model records to/from a JSON file
- Allows downloading all models that are listed on the home screen

## Model Add/Edit Screen

- Requires name field to be filled in, which will be displayed in the model record
- Requires a model type selection, which currently supports Checkpoint, VAE, Lora, Hyper Network, Embedding, and Other
- Requires a download URL to download the model
- Supports a preview image URL that will be displayed in the model record preview, and will also be downloaded with the
  model
- Supports adding a model page URL that will be displayed in model details
- Allows for adding groups to a model record, which can be used as tags. Groups are either taken from already existing
  records or can be added through the "Add groups" section
- Allows the user to control where the downloaded file will be placed, including options such
  as `Download Path`, `Download File Name`, and `Subdir`
- Includes a "Prompts" section containing two fields: `Positive Prompts` and `Negative Prompts`
- Supports a `Description` field that uses a WYSWYG TinyMCE editor for adding and editing text with rich text formatting

## Model Details Screen

- Contains the same fields as the add/edit screen but without the ability to edit them. Empty fields in the model record
  will not be displayed.

## Removal Screen

- Allows for removing a model or files related to that model, if such files exist.

## Download Screen

- Contains cards, one for each model record added for downloading
- Each card displays a status (Pending, In Progress, Exists, Complete, or Error) in a different color. While a card is
  in "In Progress" state, the download progress is displayed.
- Displays a general download status at the top.

🎉🎉🎉

SD Model Organizer
The SD Model Organizer is an extension for the Stable Diffusion WebUI that allows users to store and manage information
about different models used with the Stable Diffusion system. With this extension, users can easily add, edit, and
download models, as well as organize them by group, type, or other attributes.

## 🚀 Features

The SD Model Organizer extension includes the following features:

Home Screen
Model Records Display: Shows model records added by user with cards or table layout.
One-click Download: Download a model with one click.
Filtering: Filter added model records by name, group, model type.
Sorting: Sort by time added or name.
Export/Import: Export/import model records to/from json file.
Bulk Download: Download all models that are listed in the home screen.
Model Add/Edit Screen
Name: Name field (required) - Name of the model record displayed.
Model Type: Model type, currently supports Checkpoint, VAE, Lora, Hyper Network, Embedding and Other. (required) - Model
type, shows badge and takes path were the model will be downloaded.
Download URL: An url to the model for download (required).
Preview Image URL: Image url that will be displayed in model record preview, also will be downloaded with a model.
Model Page URL: An url to the model page, displayed in model details.
Groups: A list of groups that can be added by user to model record and used as tags. Groups are taken from already
existing records or can be added via the next section.
Add Groups Section: Allows adding new groups for models that don't exist yet.
Download Options Section: Allows users to control where downloaded file will be placed. Contains options such as
Download Path, Download File Name, and Subdir.
Prompts Section: Contains two fields Positive Prompts and Negative Prompts.
Description Field: Supports WYSWYG tinyMCE editor that allows adding and editing text using rich text formatting.
Model Details Screen
Same Fields as Add/Edit Screen: Contains the same fields as add/edit screen but without the ability to edit them. Empty
fields of the model record are not displayed.
Removal Screen
Removal of Models: Allows users to remove models or files related to those models if such files exist.
Download Screen
Model Download Cards: Contains cards, one per each model record added for downloading.
Download Status: Each card might have status "Pending", "In Progress", "Exists", "Complete", "Error" colored
differently. While the card is in "In Progress" state, the download progress is displayed.
General Download Status: Shows the general download status on top.
📦 Installation
The SD Model Organizer can be installed from the Stable Diffusion WebUI. Simply navigate to the Extensions page and
search for "SD Model Organizer". Click the Install button to add it to your WebUI.

🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check out the issues page if you want to
contribute.

📝 License
This project is licensed under the MIT License. Feel free to use, modify, and distribute it as you wish.