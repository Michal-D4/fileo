# Fileo

This application is about the files, your files.

Fileo[fɑɪlɔ] - could be FileOrganizer, but that doesn't matter.

The graphical interface is shown in the image below.

![fileo](img/fileo.jpg)

## The GUI elements:

1. the application mode
2. the menu button to hide/show the left pane widgets: folders, tags, file extensions, authors
3. the name of current file
4. menu button to select which fields will be visible in the file list
5. the name of the current database
6. the branch of folder tree from the root to the current folder
7. the left toolbar, it contains the following buttons from top to bottom:
   1. button to chose/create the data base file
   2. selection of the "DIR" mode of application, the file list shows the files from the current folder
   3. selection of the "FILTER" mode, the list of files shows the files according to the filter settings
   4. open the filter settings dialog, switch application into "FILTER_SETUP" mode
   5. open dialog to scan the file system to load files into the database
   6. hide/show left pane
   7. menu button   &mdash;   do nothing yet
8. the dialog to start scan the file system folders for files
9. the panel to show/edit file data: comments(notes), tags, authors(for books), locations - the folder branches where the current file can be found - file may reside in the several folders.

The application works in three main modes: DIR, FILTER and FILTER_SETUP. In DIR mode, files are selected by the current directory in the "Folders" widget.

In the FILTER mode, the list of files depends on the parameters of the filter set in FILTER_SETUP mode.

## How it's done

As said, the app is about files. Files have a number of attributes:

1. name
2. path, the user will almost never see it, only by opening a directory or copying the full filename and in the "File info" page
3. extension
4. tags
5. rating
6. author(s) - usually for books
7. dates
   1. modified
   2. opened
   3. created
   4. published (books)
8. rating
9. how many times the file has been opened
10. size
11. pages - usually for books

The following attributes are used in filter: all dates (but only one can be used at a time), extension, tags, rating, authors, and folder which was intentionally not included in the file attributes.

Folders are not associated with file system directories, the path is used for that. You can freely create, move, copy and delete folders in the folder tree, the files will remain intact. You can, for example, create multiple folder hierarchies, this can be handy. Of course, if you delete all folders it will be impossible to access files using folder tree, but they remain accessible by filter. The next time the **`@@Lost`** folder will appear, it can be used to access files that are not in any other folder.
You can also copy/move files from one folder to another. **Copying** is carried out by dragging *with the left mouse button pressed*, **moving** - *with the left mouse button and Shift key pressed*.

## How it works

### How to add files?

There are two method to add files:

1. Open "Search for files..." dialog with the button ![image-20230210145215938](img/image-20230210145215938.png)

   ![image-20230210145404623](img/image-20230210145404623.png)

2. drag files from the file explorer (or similar application) to the folder in the folder tree.

> **Note**. Scanning the file system can be quite lengthy, so it is performed in a separate thread.
> The red circle in the lower left corner is a sign that the thread is working:
>
> ![image-20230213184306153](img/image-20230213184306153.png)
>
> Only one thread can run at time. The user interface is not blocking but you should avoid to perform operation that make changes in the database, for example, drag-drop operations. But you can change the list of files by changing a current folder or filter, or you can open files.

3. You can export the selected files (with all their attributes) from one database using the file list context menu

   ![export-files](img/export-files.jpg)

   and then import them to another database

   ![import-files](img/import-files.jpg)

   to the folder "New folder" in this case.

### How to work with filters

Firstly you should setup the filter:

![image-20230213185910924](img/image-20230213185910924.png)

With filter defined on the picture the file list will include files from folders `DB`, `ML` and `Rust`, that has at least one of tags `Math`, `ML` or `package`, has rating greater than 4, and opened after `2022-09-14`.

> **Note** Here "after" and "before" include the date in the input fields 2022-09-14 and 2022-11-14. That is, if "after"and "before" are equal then the filter includes files with a date equal to this date.

The Apply button applies a specified filter without closing the Filter Setup dialog box.

The button Done applies a filter, closing dialog and switch application into "Filter mode". In this mode when you change selection in one of the widgets in the left pane (Folders, Tags, Extensions, Authors) the list of files is changing accordingly.

### How to make notes to the file

![fileo-comments](img/fileo-comments.jpg)

1. "+"  plus button - add new note and open it in the editor
6. "x" button - delete the note
8.  the button to open the note in the editor

#### Note editor

![edit-comment](C:\Users\mihal\OneDrive\Documents\pyprj\fileo\img\edit-comment.jpg)

1. the save changes button
2. the button to discard changes

Note is a markdown text.