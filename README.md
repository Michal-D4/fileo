# Fileo

This application is about the files, your files.

Fileo[fɑɪlɔ] - could be FileOrganizer, but that doesn't matter.

The graphical interface is shown in the image below.

![fileo](https://github.com/Michal-D4/fileo/raw/main/img/fileo.jpg)

## The GUI elements:

1. shows application mode
2. the button to display menu to hide/show the widgets("Folders", "Tags", "File Extensions", "Authors") on the left pane. All menu items checked in the image &ndash; this means that all widgets are visible.
3. the name of current file
4. a button to search files by name, and a button to select fields to be visible in the file list
5. a group of buttons for working with the folder tree: previous-next folder in the history of visited folders; show hidden folder; collapse all branches/expand the last branch
6. the left toolbar, it contains the following buttons from top to bottom:
   1. button to chose/create the data base file
   2. switch to "DIR" mode, the file list displays files from the current folder
   3. switch to the "FILTER" mode, the file list displays files according to the filter settings
   4. open filter settings dialog, switch to "FILTER_SETUP" mode
   5. open a dialog to upload files to the application from  the selected root folder and all its subfolders
   6. hide/show left pane
   7. menu button
7. list of selected files (by filter, folder, etc.)
8. current database name
9. folder tree branch from root to current folder
10. panel for displaying/editing file data: notes, tags, authors (for books), links (links to a file locations, file can be located in several folders).

The application works in three main modes: DIR, FILTER and FILTER_SETUP. In DIR mode, files are selected by the current directory in the "Folders" widget.

In FILTER mode, the list of files depends on the filter options set in FILTER_SETUP mode. The filter may depend on the selected folders, selected tags, and selected authors in the boxes in the left pane. In FILTER_SETUP mode, the list of files does not change when changing the selected folders, tags, authors. But in FILTER mode, any changes are immediately displayed in the list of files.

## How it's done

As said, the app is about files. Files have a number of attributes:

1. name
2. path, the user practically does not see it, only by opening the directory or copying the full file name and on the "File Info" page
3. file extension
4. tags
5. rating
6. author(s) - usually for books
7. dates of:
    1. modification
    2. last opening
    3. creation
    4. publication (books)
    5. date of last created/modified note to the file
8. number of file openings
9. size in bytes
10. number of pages - usually for books

The following attributes are used in filter: all dates (but only one can be used at a time), extension, tags, rating, authors, and folder which was intentionally not included in the file attributes.

Folders are not associated with file system directories, the path is used for that. You can freely create, move, copy and delete folders in the folder tree, the files will remain intact. You can, for example, create multiple folder hierarchies, this can be handy. Of course, if you delete all folders it will be impossible to access files using folder tree, but they remain accessible by filter. The next time the **`@@Lost`** folder will appear, it can be used to access files that are not in any other folder.
You can also *copy/move files from one folder to another*  by dragging *with the left or right mouse button pressed*.



## How it works

### How to add files?

There are two method to add files:

1. Open "Search for files..." dialog with the button ![image-20230210145215938](https://github.com/Michal-D4/fileo/raw/main/img/image-20230210145215938.png)

   ![image-20230210145404623](https://github.com/Michal-D4/fileo/raw/main/img/image-20230210145404623.png)

2. drag files from the file explorer (or similar application) to the folder in the folder tree.

> **Note**. Scanning the file system can be quite lengthy, so it is performed in a separate thread.
> The red circle in the lower left corner is a sign that the thread is working:
>
> ![image-20230213184306153](https://github.com/Michal-D4/fileo/raw/main/img/image-20230213184306153.png)
>
> Only one background thread can run at a time - this is the design of the application. The user interface is not blocking but you should avoid to perform operation that make changes in the database, for example, drag-drop operations. But you can change the list of files by changing a current folder or filter, or you can open files.

3. You can export the selected files (with all their attributes) from the database using the context menu of the file list:

   ![export-files](https://github.com/Michal-D4/fileo/raw/main/img/export-files.jpg)

   and then import them to another database

   ![import-files](https://github.com/Michal-D4/fileo/raw/main/img/import-files.jpg)

   to the folder "New folder" in this case.

### How to work with filters

First you should setup the filter:

![image-20230213185910924](https://github.com/Michal-D4/fileo/raw/main/img/image-20230213185910924.png)

With the filter set in the picture, the list of files will include files from the any of `DB`, `ML` or `Rust` folders that have at least one of the `Math`, `ML` or `package` tags, have a rating higher than 4 and are open after `2022-09-14 00:00:00`.

> **Note.** In case of before &mdash; the date before or equal to `2022-11-14 23:59:59`.

The Apply button applies a specified filter without closing the Filter Setup dialog box.

The Done button applies the filter, closes the dialog, and switches the application to "**Filter Mode**". In this mode, when you change the selection in any of the fields on the left panel (Folders, Tags, Extensions, Authors), the list of files immediately changes.

### How to find files by name

![image-20230428203253627](https://github.com/Michal-D4/fileo/raw/main/img/find_file.jpg)

The search is performed by pressing the Enter key. "Aa" is a case sensitive search, if checked, "ab" - exact search, but you can use wildcards: "*" - any number of any letters, or "?" - any single letter.

### How to make notes to the file

![fileo-comments](https://github.com/Michal-D4/fileo/raw/main/img/file-notes.jpg)

1. "+"  plus button - add new note and open it in the editor
8.  the button to open the note in the editor
3. start editing of the note
4. "x" button - delete the note
5. external (http) reference, can be open in the system web browser

#### Note editor

![edit-comment](https://github.com/Michal-D4/fileo/raw/main/img/edit-comment.jpg)

1. the save changes button, save changes and close editor
2. the button to discard changes

> pressing any of these buttons closes the editor

Note is a markdown text. You can insert web links here, but the links to files in the application are not implemented (and not planned yet)

### Tag selector

![tag-selector](https://github.com/Michal-D4/fileo/raw/main/img/tag-selector.jpg)

1. The list of tags associated with the current file. You can input here a list of tags separated by commas. *It is the only place where the new tag can be created.* The new tags will appear in the list 2 and 4.
2. The list of tags. The tags selected in this list apply to the file filter.
3. The context menu in the list of tags. Selected tags are highlighted ('Linux' and 'package'). The tag  'package' is a current tag (last selected).
4. The tag selector. The tags selected here will appear in the list 1.

### Author selector

![author-selector](https://github.com/Michal-D4/fileo/raw/main/img/author-selector.jpg)

1. The list of authors associated with the current file. You can input here a list of authors separated by commas (in square brackets if author name contains comma as in "Vaughan, Lee", otherwise it may be entered without brackets, but new authors without brackets must be in the end of list). It is the only place where the new author can be created. The new authors will appear in the list 2 and 4.
2. The list of authors. The authors selected in this list apply to the file filter.
3. The context menu in the list of authors. The current tag is highlighted - "Vijay  Pande" in this case.
4. The author selector. The authors selected here will appear in the list 1.

### Locations

![Locations](https://github.com/Michal-D4/fileo/raw/main/img/Locations.jpg)

1-4 are locations of the current file, 5 is a context menu.

The location marked with bullet is a current location.

All 4 locations end with the Poetry folder. This means that the file exists only in this folder (Poetry), the folder Poetry is presented in 4 branches. That's why the file has 4 locations.

The letters "L" and "H" in brackets means "Link" and "Hidden". "Link" and "Hidden" are attributes of folder. For example, the folder "fileo" in the branch 2 is a link to the folder "fileo"[^1] in the branch 1; the folder "A folder"  in folder "my" is "Hidden", but it is shown in the picture below because of the "FOLDERS" widget is in "Show hidden folders" mode:

![Folders](https://github.com/Michal-D4/fileo/raw/main/img/Folders.jpg)

1. The current folder (Poetry).
2. The check box. It is used to switch the "FOLDERS" widget to the "Show hidden folders" mode. The folders "@@Lost" and "Linux" are hidden; "A folder" and "fileo" in the folder "my" are links. The only difference between folder and link to it is that when you delete folder all its links and all its children will be deleted too, whereas deletion of any link of folder does not impact any other folder.
3. The current file. "Environment Variables in Linux.md"

[^1]: A folder link always has the same name as the folder itself, because the link is a simple pair of folder IDs: the first is the folder ID, the second is the parent folder ID. A folder can have many parent folders. The first parent is set when the folder is created, all the others are set when the folder is copied to another folder. This other folder becomes its parent.

### File info

![file-info](https://github.com/Michal-D4/fileo/raw/main/img/file-info.jpg)

The "File rating" and "Pages" can be edited here. But they also can be edited directly in the file list if visible:

![file-list-fields](https://github.com/Michal-D4/fileo/raw/main/img/file-list-fields.jpg)

1. The file list
2. Menu to select fields visible in the file list. The checked fields are visible, the field "File Name" is always visible.

### File operations



![file_context_menu](https://github.com/Michal-D4/fileo/raw/main/img/file_context_menu.png)

Almost all operations with files are shown in the context menu on the picture.

Besides them you can copy / move files from one folder to another.

You can also open files by double clicking on "File name". If the file is executable, it will be executed, not opened. Thus, the application can be used as a "Start Menu", it can be even more convenient than the standard "Start Menu".

> **Note:** If you delete a file from a folder, the file will still remain in the DB, even if you delete it from all folders, you can find it by searching by name or part of the name, or with a filter, or at least it will appear in (hidden) folder "@@Lost".
> If you delete a file from the DB, it will be deleted from all folders, and all notes for this file and its links to tags and authors will be lost.