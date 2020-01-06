import os
import PIL
import shutil
import ntpath
import os.path
from tkinter import *
from io import BytesIO
from mutagen.id3 import ID3
from PIL import Image, ImageTk
from tkinter.ttk import Progressbar
from tkinter import filedialog, messagebox


# File formats dictionary
FILE_FORMATS = {
    "Image": [".jpeg", ".jpg", ".tiff", ".gif", ".bmp", ".png"],
    "Video": [".avi", ".flv", ".wmv", ".mov", ".mp4", ".webm", ".vob", ".mng", ".qt", ".mpg", ".mpeg", ".3gp", ".mkv"],
    "Document": [".oxps", ".epub", ".pages", ".fdf", ".ods", ".odt", ".pwi", ".xsn", ".xps", ".dox", ".rvg", ".rtf",
                 ".rtfd", ".wpd", ".ppt", "pptx"],
    "Archive": [".a", ".ar", ".cpio", ".iso", ".tar", ".gz", ".rz", ".7z", ".dmg", ".rar", ".xar", ".zip"],
    "Audio": [".aac", ".aa", ".aac", ".dvf", ".m4a", ".m4b", ".m4p", ".msv", ".ogg", ".oga", ".raw", ".vox", ".wav", ".wma"],
    "Plaintext": [".txt", ".in", ".out"],
    "MP3": [".mp3"],
    "PDF": [".pdf"],
    "Word": [".docx", ".doc", ".dotx", ".docm"],
    "Excel": [".xls", ".xlsx"]
}
# Defualt thumbnail file name dictionary
DEFUALT_THUMBNAILS = {
    "Image": "Image.png", "Video": "Video.png", "Document": "Document.png", "Archive": "Archive.png",
    "Audio": "Audio.png", "Plaintext": "Plaintext.png", "MP3": "MP3.png", "PDF": "PDF.png",
    "Word": "Word.png", "Excel": "Excel.png", "File": "File.png"
}
# Make a dictionary for every extension to have a file format
EXTENSIONS = {extension: file_format
              for file_format, extensions in FILE_FORMATS.items()
              for extension in extensions}
# Get the thumbnails folder path
THUMBNAILS_DIR = os.path.abspath(os.curdir) + "\Thumbnails data\\"
DEFAULT_THUMBNAILS_DIR = os.path.abspath(os.curdir) + "\Thumbnails\\"
# Global variables
FILES = []
FOLDERS = []
SELECTED = 0
LARGE_SIZE = (130, 130)
SMALL_SIZE = (60, 60)
KEY_STATE = "None"
ROW = COLUMN = 0
COPY = {}
MOVE = {}
MAINFRAME = BOTTOMFRAME = SONG_NAME = None
CO_SHORT = "w"
MV_SHORT = "s"
NXT_SHORT = "d"
PRV_SHORT = "a"


# Add files to FILES
def browse_for_files():
    # Browse for files and list them
    files = root.splitlist(filedialog.askopenfilenames(parent=root, title='Choose files'))
    # Iterate over every item in the list and add it to FILES if it's not in it (avoid duplicates)
    for file in files:
        if file not in FILES:
            FILES.append(file)


# Update the first page label text
def add_files(label, button):
    browse_for_files()
    # If there are items in FILES show there number on the label
    if FILES:
        label["text"] = "Selected " + str(len(FILES)) + " Files"
        # And if there are selected folders activate the Next button
        if FOLDERS:
            button["state"] = "normal"


def add_files_to_page(count, prev, label, next):
    browse_for_files()
    update_file_frames(count, prev, label, next)


def browse_for_all_files():
    path = ""
    folder = filedialog.Directory(initialdir=os.path.dirname(path))
    path = folder.show()
    for entry in os.scandir(path):
        if entry.is_file():
            entry = entry.path.replace("\\", "/")
            if entry not in FILES:
                FILES.append(entry)


def add_all_files(label, button):
    browse_for_all_files()
    # If there are items in FILES show there number on the label
    if FILES:
        label["text"] = "Selected " + str(len(FILES)) + " Files"
        # And if there are selected folders activate the Next button
        if FOLDERS:
            button["state"] = "normal"


def add_all_files_to_page(count, prev, label, next):
    browse_for_all_files()
    update_file_frames(count, prev, label, next)


# Add folders to FOLDERS
def browse_for_folders(coming_from):
    folder_path = ""
    # Keep browsing for folders
    while True:
        folder = filedialog.Directory(initialdir=os.path.dirname(folder_path))
        folder_path = folder.show()
        # Break if the user doesn't provide directory (presses cancel)
        if not folder_path:
            break
        # If the selected folder isn't in FOLDERS add it to the list
        if folder_path not in FOLDERS:
            FOLDERS.append(folder_path)
    if coming_from == "Page":
        load_bottomFrame()


# Update the first page label text
def add_folders(label, button):
    browse_for_folders("Start")
    # If there are items in FOLDERS show there number on the label
    if FOLDERS:
        label["text"] = "Selected " + str(len(FOLDERS)) + " Folders"
        # And if there are selected files activate the Next button
        if FILES:
            button["state"] = "normal"


# Go to the next page
def next_page(master):
    global page_1
    # Unpack the first page, class the second and pack it
    start_page.pack_forget()
    page_1 = Page_1(master)
    page_1.pack()


# Get the file's name from it's full path
def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


# Get an image from path to add to the window with the given x and y lengths
def image_out(path, x, y):
    image = Image.open(path)
    return ImageTk.PhotoImage(image.resize((x, y), Image.ANTIALIAS))


# Get the defualt thumbnail for given the file format and the frame place
def defualt_thumbnail(file, place):
    # Open the Image and get it's size (for the thumbnail function)
    img = Image.open(DEFAULT_THUMBNAILS_DIR + file)
    width, height = img.size
    # Check the given frame place 
    # And thumbnail the image by setting it's size and getting it's path accordingly
    if place == "Left":
        img.thumbnail(SMALL_SIZE)
        new_img_path = THUMBNAILS_DIR + "Left thumbnail.png"
    elif place == "Middle":
        img.thumbnail(LARGE_SIZE)
        new_img_path = THUMBNAILS_DIR + "Middle thumbnail.png"
    if place == "Right":
        img.thumbnail(SMALL_SIZE)
        new_img_path = THUMBNAILS_DIR + "Right thumbnail.png"
    # Save the thumbnail image at the path set before and return the "label-able" form of it
    img.save(new_img_path)
    return ImageTk.PhotoImage(Image.open(new_img_path))


# Create and return the thumbnail for the given file and it's frame place
def create_thumbnail(path, place):
    # Get the global variable SONG_NAME
    global SONG_NAME
    # Get the file's extension from it's path 
    file_name = path_leaf(path)
    extension = os.path.splitext(file_name)[1].lower()
    # Check if the extinsion is in the preset EXTENSIONS
    if extension in EXTENSIONS:
        # Get the file format and try to get it's thumbnail accordingly
        file_format = EXTENSIONS[extension]
        # Check if it's an image
        if file_format == "Image":
            # Try to open the image and get it's thumbnail
            try:
                img = Image.open(path)
                width, height = img.size
                if place == "Left":
                    img.thumbnail(SMALL_SIZE)
                    new_img_path = THUMBNAILS_DIR + "Left thumbnail" + extension
                elif place == "Middle":
                    img.thumbnail(LARGE_SIZE)
                    new_img_path = THUMBNAILS_DIR + "Middle thumbnail" + extension
                if place == "Right":
                    img.thumbnail(SMALL_SIZE)
                    new_img_path = THUMBNAILS_DIR + "Right thumbnail" + extension
                img.save(new_img_path)
                return ImageTk.PhotoImage(Image.open(new_img_path))
            # If not return the defualt thumbnail for "Image"
            except:
                return defualt_thumbnail(DEFUALT_THUMBNAILS[file_format], place)
        # Check if it's an MP3 file
        elif file_format == "MP3":
            # Try to get the song name using ID3
            try:
                tags = ID3(path)
                SONG_NAME = tags.get("TIT2")
            except:
                pass
            # Try to get the song's album art as the thumbnail using ID3 and saving it as a JPG file
            try:
                tags = ID3(path)
                pict = tags.get("APIC:").data
                img = Image.open(BytesIO(pict))
                width, height = img.size
                if place == "Left":
                    img.thumbnail(SMALL_SIZE)
                    new_img_path = THUMBNAILS_DIR + "Left thumbnail.jpg"
                elif place == "Middle":
                    img.thumbnail(LARGE_SIZE)
                    new_img_path = THUMBNAILS_DIR + "Middle thumbnail.jpg"
                if place == "Right":
                    img.thumbnail(SMALL_SIZE)
                    new_img_path = THUMBNAILS_DIR + "Right thumbnail.jpg"
                img.save(new_img_path)
                return ImageTk.PhotoImage(Image.open(new_img_path))
            # If not return the defualt thumbnail for "MP3"
            except:
                return defualt_thumbnail(DEFUALT_THUMBNAILS[file_format], place)
        # For the rest file formats in EXTENSIONS get their Defualt thumbnail
        elif file_format in DEFUALT_THUMBNAILS:
            return defualt_thumbnail(DEFUALT_THUMBNAILS[file_format], place)
    # The extinsion isn't in the preset EXTENSIONS. Return the defualt thumbnail for "File"
    else:
        return defualt_thumbnail(DEFUALT_THUMBNAILS["File"], place)


# Empty the THUMBNAILS_DIR path
def empty_thumbnails():
    # Iterate over every file in the folder, join it with the folder's path and delete it
    for file_object in os.listdir(THUMBNAILS_DIR):
        file_object_path = os.path.join(THUMBNAILS_DIR, file_object)
        if os.path.isfile(file_object_path) or os.path.islink(file_object_path):
            os.unlink(file_object_path)


def update_file_frames(count, prev, label, next):
    global SELECTED, SONG_NAME
    count["text"] = (str(SELECTED + 1) + "/" + str(len(FILES)))
    # Update the middle frame label
    try:
        curr_file_path = FILES[SELECTED]
        curr_file = path_leaf(curr_file_path)
        middle_thumb = create_thumbnail(curr_file_path, "Middle")
    except:
        curr_file = "No selected files"
    # Check if a song name was set
    if SONG_NAME:
        # Set the label text to the song name and reset SONG_NAME to None again
        label["text"] = SONG_NAME
        SONG_NAME = None
    # If no avaliable song name set the label text to the file's name
    else:
        label["text"] = curr_file
    # If there is a middle thumbnail set it to the label's image and check it
    if middle_thumb:
        label["image"] = middle_thumb
        label.image = middle_thumb
    else:
        label["image"] = ""
    # Unpack the previous file label if the the user is at the first file
    if SELECTED < 1:
        prev.place_forget()
    # The user is at a later file
    else:
        # Pack the previous file name label
        prev.place(x=37.5, y=37.5, anchor="center")
        # Update the previous file label
        try:
            prev_file_path = FILES[SELECTED-1]
            prev_file = path_leaf(prev_file_path)
            left_thumb = create_thumbnail(prev_file_path, "Left")
        except:
            pass
        if SONG_NAME:
            prev["text"] = SONG_NAME
            SONG_NAME = None
        else:
            prev["text"] = prev_file
        if left_thumb:
            prev["image"] = left_thumb
            prev.image = left_thumb
        else:
            prev["image"] = ""
    # Check if the user isn't at the last file
    if SELECTED < len(FILES) - 1:
        # Pack the next file name label
        next.place(x=37.5, y=37.5, anchor="center")
        # Update the next file label
        try:
            next_file_path = FILES[SELECTED+1]
            next_file = path_leaf(next_file_path)
            right_thumb = create_thumbnail(next_file_path, "Right")
        except:
            pass
        if SONG_NAME:
            next["text"] = SONG_NAME
            SONG_NAME = None
        else:
            next["text"] = next_file
        if right_thumb:
            next["image"] = right_thumb
            next.image = right_thumb
        else:
            next["image"] = ""
    # The user is at the last file (unpack the label)
    else:
        next.place_forget()


# Navigate between files
def nav_file(count, prev, label, next, pressed):
    # Get the global variable of the current selected file
    global SELECTED
    # Check if the pressed key is Next
    if pressed == "Next":
        # Only go forward if there is space, reload the bottom frame and empty the thumbnails path
        if SELECTED < len(FILES) - 1:
            SELECTED += 1
            load_bottomFrame()
            empty_thumbnails()
        else:
            return
    # The pressed key is Prev
    else:
        # Only go backward if there is space, reload the bottom frame and empty the thumbnails path
        if SELECTED > 0:
            SELECTED -= 1
            load_bottomFrame()
            empty_thumbnails()
        else:
            return
    update_file_frames(count, prev, label, next)
    

# Open the current selected file
def open_file(event=None):
    os.startfile(FILES[SELECTED])


# Deselect a button when selected twice
def press(var, button, event):
    # Get the global variable of the current key state 
    global KEY_STATE
    # If a shortcut gets pressed select the corresponding button
    if event == "Shortcut":
        button.select()
    # Copy button is pressed
    if var == 1:
        # Check if the last pressed key was Copy too
        if KEY_STATE == "Copy":
            # Deselect the Copy key and update the key state
            button.deselect()
            KEY_STATE = "None"
        else:
            # Update the key state
            KEY_STATE = "Copy"
    # Move button is pressed
    else:
        if KEY_STATE == "Move":
            button.deselect()
            KEY_STATE = "None"
        else:
            KEY_STATE = "Move"


def delete(count, prev, label, next):
    MsgBox = messagebox.askquestion('Delete file', 'Are you sure you want to permanently delete this file?', icon='warning')
    if MsgBox == 'yes':
        curr_file = FILES[SELECTED]
        if curr_file in MOVE:
            del MOVE[curr_file]
        if curr_file in COPY:
            del COPY[curr_file]
        FILES.remove(curr_file)
        try:
            os.remove(curr_file)
            messagebox.showinfo('Deleted', 'This file was permanetly deleted.')
        except:
            messagebox.showinfo('Error', "This file doesn't exist anymore.")
        update_file_frames(count, prev, label, next)


def done():
    global COPY, MOVE
    items = len(MOVE)
    for file in COPY:
        for dest in COPY[file]:
            items += 1
    prog = Toplevel(root)
    prog.minsize(200, 70)
    progFrame = Frame(prog, bg="#333333", width=250, height=70)
    progFrame.pack(expand=TRUE, fill='both')
    progFrame.pack_propagate(0)
    progress_label = Label(progFrame, text="Processing...", bg="#333333", fg="#ffffff", font="Verdana 10 bold")
    progress_label.pack(pady=5)
    progress = Progressbar(progFrame, orient=HORIZONTAL, maximum=items, length=200, mode='determinate')
    progress.pack(pady=5)
    #x = threading.Thread(target=add_progress, args=(progress))
    for file in COPY:
        for dest in COPY[file]:
            try:
                shutil.copy2(file, dest)
            except shutil.SameFileError:
                messagebox.showinfo('Error', "Unable to copy " + path_leaf(file) + " to " +
                                    dest + " which has a file with the same name.")
                pass
            progress['value'] += 1
            progress.update()        
    for file in MOVE:
        try:
            shutil.move(file, MOVE[file])
        except shutil.Error:
            messagebox.showinfo('Error', "Unable to move " + path_leaf(file) + " to " +
                                MOVE[file] + " which has a file with the same name.")
            pass
        progress['value'] += 1
        progress.update()
    messagebox.showinfo('Done', 'Done!')
    root.destroy()


def add_progress(progress):
    progress['value'] += 1


# Class for folder frames
class Folder(Frame):
    def __init__(self, frame, path):
        self.state = "None"
        Frame.__init__(self, frame)
        # Get the global variable of rows and columns
        global ROW, COLUMN
        # Create the frame and grid it
        self = Frame(frame, bg="#333333", bd=0, relief=RIDGE, width=75, height=75)
        self.grid(row=ROW, column=COLUMN, sticky="nswe", padx=2, pady=2)
        self.pack_propagate(0)
        # Go to the next row every 5 columns
        if COLUMN < 4:
            COLUMN += 1
        else:
            ROW += 1
            COLUMN = 0
        # Create a path attribute
        self.path = path
        # Frame event tracker
        self.bind("<Button-1>", lambda label: destination(self))
        # Folder label
        folder_image = image_out(DEFAULT_THUMBNAILS_DIR + "Folder.png", 60, 60)
        folder_lbl = Label(self, image=folder_image, text=path_leaf(path),
                           bg="#333333", fg="#ffffff", font="Verdana 6", compound=TOP)
        folder_lbl.image = folder_image
        folder_lbl.place(x=35.5, y=35.5, anchor="center")
        folder_lbl.bind("<Button-1>", lambda label: destination(self))
        # Check if there are selected files
        if FILES:
            # Get the current file path
            curr_file = FILES[SELECTED]
            # Check if the folder's path is in the file's copy destinations
            if curr_file in COPY:
                if path in COPY[curr_file]:
                    # Make a green frame on the folder frame as an indicator for copying and pack it
                    for_copy = Frame(self, bg="#00ff00", bd=3, relief=RIDGE, width=12, height=12)
                    for_copy.pack(anchor="nw", padx=6)
            # Check if the folder's path is the file's move destination
            if curr_file in MOVE:
                if MOVE[curr_file] == path:
                    # Make a blue frame on the folder frame as an indicator for moving and pack it
                    for_move = Frame(self, bg="#0000ff", bd=3, relief=RIDGE, width=12, height=12)
                    for_move.pack(anchor="nw", padx=6)


# Class for adding folder frames
class AddFolder(Frame):
    def __init__(self, frame):
        self.state = "None"
        Frame.__init__(self, frame)
        # Get the global variable of rows and columns
        global ROW, COLUMN
        # Create the frame and grid it
        self = Frame(frame, bg="#333333", bd=0, relief=RIDGE, width=75, height=75)
        self.grid(row=ROW, column=COLUMN, sticky="nswe", padx=2, pady=2)
        self.pack_propagate(0)
        # Go to the next row every 5 columns
        if COLUMN < 4:
            COLUMN += 1
        else:
            ROW += 1
            COLUMN = 0
        # Frame event tracker
        self.bind("<Button-1>", lambda label: browse_for_folders("Page"))
        # Add Folders label
        add_folders_image = image_out(DEFAULT_THUMBNAILS_DIR + "Add folders transparent.png", 50, 50)
        add_folders_lbl = Label(self, image=add_folders_image, bg="#333333")
        add_folders_lbl.image = add_folders_image
        add_folders_lbl.place(x=35.5, y=35.5, anchor="center")
        add_folders_lbl.bind("<Button-1>", lambda label: browse_for_folders("Page"))


# Remove a file path from COPY if it equals the entered path
def remove_from_Copy(file, path):
    if file in COPY:
        if path in COPY[file]:
            COPY[file].remove(path)


# Remove a file path from MOVE if it equals the entered path
def remove_from_MOVE(file, path):
    if file in MOVE:
        if MOVE[file] == path:
            del MOVE[file]


# Fill COPY and MOVE dictionaries
def destination(folder):
    # Get the selected file and the clicked folder's path
    curr_file = FILES[SELECTED]
    path = folder.path
    destinations = []
    # Check if the Copy button or nothing was pressed when the folder was selected
    if KEY_STATE == "Copy" or KEY_STATE == "None":
        # Check if there is a key with the file's path in COPY
        if curr_file in COPY:
            # Iterate over the paths in the already existing COPY and append it to destinations
            for destination in COPY[curr_file]:
                destinations.append(destination)
            # If the selected folder path already exists in destinations remove it
            if path in destinations:
                destinations.remove(path)
            # Check if the Copy button was pressed
            elif KEY_STATE == "Copy":
                # Add the folder path to destinations remove it from MOVE if it's in it
                destinations.append(path)
                remove_from_MOVE(curr_file, path)
            # Update COPY
            COPY.update({curr_file: destinations})
            # If there is no destinations for the selected file delete it from COPY
            if len(COPY[curr_file]) == 0:
                del COPY[curr_file]
        # There is no key with the file's path in COPY and the Copy button was pressed
        elif KEY_STATE == "Copy":
            # Add the folder path to destinations, update COPY and remove it from MOVE if it's in it
            destinations.append(path)
            COPY.update({curr_file: destinations})
            remove_from_MOVE(curr_file, path)
    # Check if the MOVE or nothing button was pressed when the folder was selected
    if KEY_STATE == "Move" or KEY_STATE == "None":
        # Check if there is a key with the file's path in MOVE
        if curr_file in MOVE:
            # Delete the key if it's value already equals the selected folder path
            if MOVE[curr_file] == path:
                del MOVE[curr_file]
            # Check if the Move button was pressed
            elif KEY_STATE == "Move":
                # Set the key's value to the selected folder's path and remove it from COPY if it's in it
                MOVE.update({curr_file: path})
                remove_from_Copy(curr_file, path)
        # Check if the Move button was pressed
        elif KEY_STATE == "Move":
            # Set the key's value to the selected folder's path and remove it from COPY if it's in it
            MOVE.update({curr_file: path})
            remove_from_Copy(curr_file, path)
    # Reload the bottom frame
    load_bottomFrame()


# Load and reload the bottom frame
def load_bottomFrame():
    # Get the global variables and reinitialize ROW and COLUMN
    global BOTTOMFRAME, ROW, COLUMN
    ROW = COLUMN = 0
    # If there is a bottom frame destroy it
    if BOTTOMFRAME:
        BOTTOMFRAME.destroy()
    # Make a bottom frame and pack it
    BOTTOMFRAME = Frame(MAINFRAME, bg="#333333", bd=3, relief=RIDGE, width=403, height=400)
    BOTTOMFRAME.pack(expand=TRUE, side=BOTTOM)
    BOTTOMFRAME.grid_propagate(0)
    # Create a folder frame for each item in FOLDERS
    for i in range(len(FOLDERS)):
        folderFrame = Folder(BOTTOMFRAME, FOLDERS[i])
    add_folder_frame = AddFolder(BOTTOMFRAME) 


def validate(P):
    if P:
        P = P[-1]
    if str.isdecimal(P) or P == "" or str.isalpha(P):
        return True
    else:
        return False


def character_limit(entry_text):
    text = str(entry_text.get())
    if len(text) > 0:
        entry_text.set(text[-1])       


def apply_shortcuts(left, right, copy, move, window):
    global CO_SHORT, MV_SHORT, PRV_SHORT, NXT_SHORT
    shorts = [left, right, copy, move]
    for short in shorts:
        if shorts.count(short) > 1:
            messagebox.showinfo('Error', "Please use different shortcut buttons for every button")
            return
        if not short:
            messagebox.showinfo('Error', "Please make sure to fill all the shortcuts")
            return
    page_1.co_button.unbind_all(CO_SHORT)
    page_1.mv_button.unbind_all(MV_SHORT)
    page_1.next_file_lbl.unbind_all(NXT_SHORT)
    page_1.prev_file_lbl.unbind_all(PRV_SHORT)
    PRV_SHORT = str(left)
    NXT_SHORT = str(right)
    CO_SHORT = str(copy)
    MV_SHORT = str(move)
    page_1.co_button.bind_all(CO_SHORT, lambda label: press(1, page_1.co_button, "Shortcut"))
    page_1.mv_button.bind_all(MV_SHORT, lambda label: press(2, page_1.mv_button, "Shortcut"))
    page_1.next_file_lbl.bind_all(NXT_SHORT, lambda label: nav_file(page_1.file_count_lbl, page_1.prev_file_lbl,
                                                                    page_1.file_lbl, page_1.next_file_lbl, "Next"))
    page_1.prev_file_lbl.bind_all(PRV_SHORT, lambda label: nav_file(page_1.file_count_lbl, page_1.prev_file_lbl,
                                                                    page_1.file_lbl, page_1.next_file_lbl, "Prev"))
    window.destroy()


class Shortcut_Label:
    def __init__(self, parent, text, row, column):
        self = Label(parent, text=text, bg="#333333", fg="#ffffff", font="Verdana 10 bold")
        self.grid(row=row, column=column, sticky="w", padx=5, pady=5)


class Shortcut_Entry:
    def __init__(self, parent, validate, text, row, column):
        self = Entry(parent, width="1", font="Verdana 10 bold", validate='all',
                        validatecommand=(validate, '%P'), textvariable=text)
        text.trace("w", lambda *args: character_limit(text))
        self.grid(row=row, column=column, padx=5, pady=5, ipadx=2)


def shortcuts():
    global CO_SHORT, MV_SHORT, NXT_SHORT, PRV_SHORT
    short = Toplevel(root)
    short.title("Shortcuts")
    short.configure(bg="#333333", width=250, height=140)
    short.minsize(330, 140)

    shortcuts_label = Label(short, text="Shortcuts:", bg="#333333", fg="#ffffff", bd=0, relief=RIDGE, font="Verdana 10 bold")
    shortcuts_label.pack(side=TOP, padx=5, pady=5)

    shortFrame = Frame(short, bg="#333333", width=210, height=70)
    shortFrame.pack(expand=TRUE, fill='both', padx=20)
    shortFrame.grid_propagate(0)

    left_label =Shortcut_Label(shortFrame, "Previous file:", 0, 0)
    right_label = Shortcut_Label(shortFrame, "          Next file:", 0, 2)
    copy_label = Shortcut_Label(shortFrame, "Copy:", 1, 0)
    move_label = Shortcut_Label(shortFrame, "          Move:", 1, 2)

    vcmd = (root.register(validate))

    left_text = StringVar()
    right_text = StringVar()
    copy_text = StringVar()
    move_text = StringVar()
    
    left_entry = Shortcut_Entry(shortFrame, vcmd, left_text, 0, 1)
    right_entry = Shortcut_Entry(shortFrame, vcmd, right_text, 0, 3)
    copy_entry = Shortcut_Entry(shortFrame, vcmd, copy_text, 1, 1)
    move_entry = Shortcut_Entry(shortFrame, vcmd, move_text, 1, 3)

    apply_btn = Button(short, text="Apply", bg="#cccccc", command=lambda: apply_shortcuts(
                       left_text.get(), right_text.get(), copy_text.get(), move_text.get(), short))
    apply_btn.pack(side=RIGHT, padx=5, pady=5)

    cancel_btn = Button(short, text="Cancel", bg="#cccccc", command=short.destroy)
    cancel_btn.pack(side=RIGHT, padx=5, pady=5)


# Configure the application's root
root = Tk()
root.title("Messillizer")
root.configure(bg="#222222")
root.iconbitmap(DEFAULT_THUMBNAILS_DIR + "Icon.ico")
root.minsize(420, 620)

# Menu bar
menu = Menu(root, bg="#444444")
root.configure(menu=menu)
# File menu
fileMenu = Menu(menu, tearoff=0, bg="#555555", fg="#ffffff")
menu.add_cascade(label="File", menu=fileMenu)
fileMenu.add_command(label="Add Files")
fileMenu.add_command(label="Add all files from a directory")
fileMenu.add_separator()
fileMenu.add_command(label="Add Folders")
fileMenu.add_separator()
fileMenu.add_command(label="Exit", command=root.destroy)
# Options menu
preferencesMenu = Menu(menu, tearoff=0, bg="#555555", fg="#ffffff")
menu.add_cascade(label="Preferences", menu=preferencesMenu)
preferencesMenu.add_command(label="Shortcuts", command=shortcuts)


# Make a starting page class inheriting Frame
class StartPage(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)

        # Frames
        # The mainframe
        mainFrame_1 = Frame(self, bg="#222222", width=420, height=620)
        mainFrame_1.pack(expand=TRUE, fill='both')
        mainFrame_1.pack_propagate(0)
        # The top frame
        topFrame_1 = Frame(mainFrame_1, bg="#333333", bd=3, relief=RIDGE, width=380, height=275)
        topFrame_1.pack(expand=TRUE, side=TOP)
        topFrame_1.pack_propagate(0)
        # The bottom frame
        bottomFrame_1 = Frame(mainFrame_1, bg="#333333", bd=3, relief=RIDGE, width=380, height=275)
        bottomFrame_1.pack(expand=TRUE)
        bottomFrame_1.pack_propagate(0)

        # Labels
        # Files label
        files_image = image_out(DEFAULT_THUMBNAILS_DIR + "Add files.png", 100, 100)
        files_label = Label(topFrame_1, image=files_image, text="Add Files", bg="#333333",
                            fg="#ffffff", font="Verdana 10 bold", compound=TOP)
        files_label.image = files_image
        files_label.place(x=186, y=133.5, anchor="center")
        # Folders label
        folders_image = image_out(DEFAULT_THUMBNAILS_DIR + "Add folders.png", 100, 100)
        folders_label = Label(bottomFrame_1, image=folders_image, text="Add Folders",
                              bg="#333333", fg="#ffffff", font="Verdana 10 bold", compound=TOP)
        folders_label.image = folders_image
        folders_label.place(x=186, y=133.5, anchor="center")

        # Event trackers
        # Add files button
        topFrame_1.bind("<Button-1>", lambda label: add_files(files_label, next_page_btn))
        files_label.bind("<Button-1>", lambda label: add_files(files_label, next_page_btn))
        # Add folders button
        bottomFrame_1.bind("<Button-1>", lambda label: add_folders(folders_label, next_page_btn))
        # Next page button
        next_page_btn = Button(mainFrame_1, text="Next >>", bg="#555555", command=lambda: next_page(root), foreground="#ffffff",
                               activebackground="#cccccc", font="Verdana 10", state=DISABLED)
        next_page_btn.pack(side=BOTTOM, padx=25, pady=5, ipadx=157)
        # Menu bar update
        fileMenu.entryconfigure(0, command=lambda: add_files(files_label, next_page_btn))
        fileMenu.entryconfigure(1, command=lambda: add_all_files(files_label, next_page_btn))
        fileMenu.entryconfigure(3, command=lambda: add_folders(folders_label, next_page_btn))


# Make the second page class inheriting Frame
class Page_1(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)

        # Frames
        global MAINFRAME, BOTTOMFRAME
        # The mainframe
        MAINFRAME = Frame(self, bg="#222222", width=420, height=620)
        MAINFRAME.pack(expand=TRUE, fill='both')
        MAINFRAME.pack_propagate(0)
        # The top frame
        topFrame_2 = Frame(MAINFRAME, bg="#333333", bd=3, relief=RIDGE, width=403, height=220)
        topFrame_2.pack(expand=TRUE, side=TOP)
        topFrame_2.pack_propagate(0)
        # The navigation frame
        navFrame = Frame(topFrame_2, bg="#333333", bd=0, relief=RIDGE, width=403, height=170)
        navFrame.pack(expand=TRUE, side=TOP, anchor="n")
        navFrame.pack_propagate(0)
        # The files frames
        LeftFilesFrame = Frame(navFrame, bg="#333333", bd=0, relief=RIDGE, width=75, height=75)
        MidFilesFrame = Frame(navFrame, bg="#333333", bd=0, relief=RIDGE, width=170, height=150)
        RightFilesFrame = Frame(navFrame, bg="#333333", bd=0, relief=RIDGE, width=75, height=75)
        # The buttomFrame
        load_bottomFrame()

        # Navigation frame widgets
        # Try to get the current and next file's name
        try:
            curr_file = path_leaf(FILES[SELECTED])
            next_file = path_leaf(FILES[SELECTED + 1])
        except:
            curr_file = "No selected files"
            next_file = ""
        # File count label
        self.file_count_lbl = Label(navFrame, text=(str(SELECTED + 1) + "/" + str(len(FILES))),
                                    bg="#333333", fg="#ffffff", font="Verdana 8")
        self.file_count_lbl.pack(side=TOP)
        # Previous file button
        prev_btn = Frame(navFrame, bg="#333333", bd=0, relief=RIDGE, width=35, height=35)
        prev_btn.pack(expand=True, side=LEFT)
        prev_btn.pack_propagate(0)
        prev_image = image_out(DEFAULT_THUMBNAILS_DIR + "Prev.png", 35, 35)
        prev_btn_lbl = Label(prev_btn, image=prev_image, bg="#333333")
        prev_btn_lbl.image = prev_image
        prev_btn_lbl.bind("<Button-1>", lambda label: nav_file(self.file_count_lbl, self.prev_file_lbl,
                                                               self.file_lbl, self.next_file_lbl, "Prev"))
        prev_btn_lbl.pack(side=LEFT)
        # Pack the files frames
        LeftFilesFrame.pack(expand=True, side=LEFT)
        LeftFilesFrame.pack_propagate(0)
        MidFilesFrame.pack(expand=True, side=LEFT)
        MidFilesFrame.pack_propagate(0)
        RightFilesFrame.pack(expand=True, side=LEFT)
        RightFilesFrame.pack_propagate(0)
        # Open the selected file when double clicking the middle file frame and navigate by clicking on the others
        LeftFilesFrame.bind("<Button-1>", lambda label: nav_file(self.file_count_lbl, self.prev_file_lbl,
                                                                 self.file_lbl, self.next_file_lbl, "Prev"))
        MidFilesFrame.bind("<Double-Button-1>", open_file)
        RightFilesFrame.bind("<Button-1>", lambda label: nav_file(self.file_count_lbl, self.prev_file_lbl,
                                                                  self.file_lbl, self.next_file_lbl, "Next"))
        # Next file button
        next_btn = Frame(navFrame, bg="#333333", bd=0, relief=RIDGE, width=35, height=35)
        next_btn.pack(expand=True, side=LEFT)
        next_btn.pack_propagate(0)
        next_image = image_out(DEFAULT_THUMBNAILS_DIR + "Next.png", 35, 35)
        next_btn_lbl = Label(next_btn, image=next_image, bg="#333333")
        next_btn_lbl.image = next_image
        next_btn_lbl.bind("<Button-1>", lambda label: nav_file(self.file_count_lbl, self.prev_file_lbl,
                                                               self.file_lbl, self.next_file_lbl, "Next"))
        next_btn_lbl.pack(side=RIGHT)
        
        # Files frame widgets
        # Prev file frame
        self.prev_file_lbl = Label(LeftFilesFrame, bg="#333333", fg="#ffffff", font="Verdana 6", compound=TOP)
        self.prev_file_lbl.place(x=37.5, y=37.5, anchor="center")
        self.prev_file_lbl.bind("<Button-1>", lambda label: nav_file(self.file_count_lbl, self.prev_file_lbl,
                                                                     self.file_lbl, self.next_file_lbl, "Prev"))
        # Current file frame
        self.file_lbl = Label(MidFilesFrame, text=curr_file,
                              bg="#333333", fg="#ffffff", font="Verdana 10", compound=TOP)
        self.file_lbl.place(x=85, y=75, anchor="center")
        self.file_lbl.bind("<Double-Button-1>", open_file)
        # Next file frame
        self.next_file_lbl = Label(RightFilesFrame, text=next_file,
                                   bg="#333333", fg="#ffffff", font="Verdana 6", compound=TOP)
        self.next_file_lbl.place(x=37.5, y=37.5, anchor="center")
        self.next_file_lbl.bind("<Button-1>", lambda label: nav_file(self.file_count_lbl, self.prev_file_lbl,
                                                                     self.file_lbl, self.next_file_lbl, "Next"))
        # Check if there are selected files
        if FILES:
            # Create the initial thumbnails and assign them to the labels
            left_thumb = create_thumbnail(FILES[SELECTED - 1], "Left")
            mid_thumb = create_thumbnail(FILES[SELECTED], "Middle")
            right_thumb = create_thumbnail(FILES[SELECTED + 1], "Right")
            self.file_lbl["image"] = mid_thumb
            self.file_lbl.image = mid_thumb
            self.next_file_lbl["image"] = right_thumb
            self.next_file_lbl.image = right_thumb
        # Top frame widgets
        v = IntVar()
        # Copy button
        self.co_button = Radiobutton(topFrame_2, text="Copy", variable=v, value=1, bg="#cccccc",
                                     indicatoron=0, command=lambda: press(v.get(), self.co_button, "Button"))
        self.co_button.pack(side=LEFT, anchor='s', expand=True, padx=5, pady=10, ipadx=25, ipady=15)
        # Move button
        self.mv_button = Radiobutton(topFrame_2, text="Move", variable=v, value=2, bg="#cccccc",
                                     indicatoron=0, command=lambda: press(v.get(), self.mv_button, "Button"))
        self.mv_button.pack(side=LEFT, anchor='s', expand=True, padx=5, pady=10, ipadx=25)
        # Delete button
        del_button = Button(topFrame_2, text="Delete", bg="#cccccc", command=lambda: delete(
                            self.file_count_lbl, self.prev_file_lbl, self.file_lbl, self.next_file_lbl))
        del_button.pack(side=LEFT, anchor='s', expand=True, padx=5, pady=10, ipadx=25)
        # Done button
        done_button = Button(topFrame_2, text="Done", bg="#cccccc", command=done)
        done_button.pack(side=LEFT, anchor='s', expand=True, padx=5, pady=10, ipadx=25)
        # Keyboard shortcuts
        self.co_button.bind_all(CO_SHORT, lambda label: press(1, self.co_button, "Shortcut"))
        self.mv_button.bind_all(MV_SHORT, lambda label: press(2, self.mv_button, "Shortcut"))
        self.next_file_lbl.bind_all(NXT_SHORT, lambda label: nav_file(
                                    self.file_count_lbl, self.prev_file_lbl, self.file_lbl, self.next_file_lbl, "Next"))
        self.prev_file_lbl.bind_all(PRV_SHORT, lambda label: nav_file(
                                    self.file_count_lbl, self.prev_file_lbl, self.file_lbl, self.next_file_lbl, "Prev"))
        # Menu bar update
        fileMenu.entryconfigure(0, command=lambda: add_files_to_page(
                                self.file_count_lbl, self.prev_file_lbl, self.file_lbl, self.next_file_lbl))
        fileMenu.entryconfigure(1, command=lambda: add_all_files_to_page(
                                self.file_count_lbl, self.prev_file_lbl, self.file_lbl, self.next_file_lbl))
        fileMenu.entryconfigure(3, command=lambda: browse_for_folders("Page"))

    
# Class the root to be the starting page and pack it
start_page = StartPage(root)
page_1 = Page_1(root)
start_page.pack()


# Run the program
def main(): 
    root.mainloop()


if __name__ == '__main__':
    main()