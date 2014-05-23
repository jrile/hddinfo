import os
import os.path
import datetime
import sys
import commands
import re
import mysql.connector
from optparse import OptionParser
from label import *
from organization import *
connection = mysql.connector.connect(user='root', database='hdds')
cursor = connection.cursor()


def main(argv):
    """Flag options, automatically adds a -h/--help flag with this information."""
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename", help="read mountpoints from FILE", metavar="FILE")
    parser.add_option("-o", "--output", dest="output", help="dump drive information to FILE", metavar="FILE")
    parser.add_option("-p", "--prompt", dest="prompt", help="specify drive information before adding to database", action="store_true")
    parser.add_option("-l", "--location", dest="location", help="add hard drives to groups (boxes)", action="store_true")

    (options, args) = parser.parse_args()

    filename = options.filename
    try: 
        if options.location:
            o = Organization()
            o.prompt()

        if filename == None:
            # default file to read drives from
            filename = "drives.in"


#TODO: add username/password table
        username = raw_input("Enter username: ")
        while not username:
            username = raw_input("Enter username: ")
        

        parse_drives(filename, username, options.output, options.prompt)


    except IOError:
        print "No file to read drives from. Please create a \'drives.in\' file to place the drives in, or specify a file with the -f flag."
            


def parse_drives(f, username, output, prompt):
    if output:
        output = open(output, 'w')

    lines = open(f).read().splitlines()
    for drive in lines:
        try:
            print "\n####################################"
            print "Starting to parse drive: " + drive
            print "####################################\n"
            # in case drive has been automatically mounted
            command = "sudo umount /mnt"
            os.system(command)
            # mount drive
            command = "sudo mount -t auto " + drive + " /mnt 2>/dev/null" #ignore output that may occur if nothing is mounted here.
            os.system(command)
        
            # get drive serial #. assuming serial is unique.
            serial = commands.getoutput("sudo smartctl -i " + drive[:8] + " | grep \"Serial Number:\"").split()[2]

            label = None
            location = None
            notes = None

            if prompt:
                label = raw_input("Enter label: ")
                location = raw_input("Enter location: ")
                notes = raw_input("Enter notes for drive: ")

            add_drive(label, location, serial, notes, username)

            if output:
                output.write("\nSerial: " + serial + "\n")
                if label:
                    output.write("Label: " + label + "\n")

            l = Label()
            #l.label(serial, ["test1", "test2", "test3"], username, "1-1-1999", "5-22-2014") #testing

            folders = parse_folders("/mnt", serial, out=output, prompt=prompt)

            old = get_oldest_file_date(serial) or "N/A" 
            new = get_newest_file_date(serial) or "N/A"
            
            l.label_with_info(serial, folders, username, old.strftime("%m-%d-%y"), new.strftime("%m-%d-%y"))
            
            print "Sucessfully parsed drive: " + drive
            print

        except IndexError:
            print "Error! Could not parse drive: " + drive
            print "Can't get serial number from drive: " + drive
    
           
        except mysql.connector.errors.IntegrityError:
            print "Error! This drive already exists in the database: " + drive

        except KeyboardInterrupt:
            print "\nUser interrupt! Cancelling parsing drive " + drive + "!"
            #remove_all(serial)

            
        finally:
            print "Program ending... unmounting " + drive
            if output:
                output.close()
            command = "sudo umount /mnt"
            os.system(command)

def parse_folders(path, serial, level=1, out=None, prompt=False):
    folders = []
    if level == 1:
        # add a 'root' folder for all the files on on the top-most directory.
        add_folder(serial, "root")
        folder_sequence = get_last_folder_sequence()
        parse_files(path, folder_sequence, serial, 1, out, prompt)

    for f in os.listdir(path):
        if os.path.isdir(os.path.join(path,f)):
            folders.append(f)
            print ("---" * level) + "Folder found: " + f
            if out:
                out.write(("---" * level) + f + "/\n")
            add_folder(serial, f)
            folder_sequence = get_last_folder_sequence()
            parse_files(os.path.join(path, f), folder_sequence, serial, level=level+1, out=out, prompt=prompt)
            parse_folders(os.path.join(path, f), serial, level=level+1, out=out, prompt=prompt)
    return folders
        


def parse_files(path, folder_sequence, serial, level=2, out=None, prompt=False):
    for filename in os.listdir(path):

        if not os.path.isdir(os.path.join(path, filename)):
            print ("---" * level) + "File found: " + filename
            if out:
                out.write(("---" * level) + filename + "\n")
            date = os.path.getmtime(os.path.join(path, filename))
            dt = datetime.datetime.fromtimestamp(date)
            notes = None
            if prompt:
                notes = raw_input("---" * level + "Enter notes for file " + filename + ": ")
            add_file(filename, folder_sequence, dt.strftime('%Y-%m-%d %H:%M:%S'), notes)
            


# MySQL queries
def add_drive(label, location, serial, notes, username):
    query = "insert into drives (label, location, serial, notes, username) values (%s, %s, %s, %s, %s)"
    cursor.execute(query, (label, location, serial, notes, username))

def remove_hdd(serial):
    cursor.execute("delete from drives where serial = \'%s\'" % serial)

def update_hdd(label, location, serial, notes):
    query = "update drives set label = %s, location = %s, notes = %s where serial = %s"
    cursor.execute(query, (label, location, notes, serial))

def hdd_exists(serial):
    query = "select 1 from drives where serial = \'%s\'" 
    cursor.execute(query % serial)
    if cursor.fetchone() is None:
        return False
    return True

def add_folder(serial, folder_name):
    query = "insert into folders (serial, folder_name) values (%s, %s)"
    cursor.execute(query, (serial, folder_name))

def get_last_folder_sequence():
    cursor.execute("select max(folder_sequence) from folders")
    return cursor.fetchone()[0]

def update_folder(folder_sequence, serial, folder_name):
    query = "update folders set serial = %s, folder_name = %s where folder_sequence = %s"
    cursor.execute(query, (serial, folder_name, folder_sequence))

def remove_folder(folder_sequence):
    cursor.execute("delete from folders where folder_sequence = \'%s\'" % folder_sequence)

def add_file(name, folder_sequence, created, notes):
    query = "insert into files (name, folder_sequence, created, notes) values (%s, %s, %s, %s)"
    cursor.execute(query, (name, folder_sequence, created, notes))

def update_file(file_sequence, name, folder_sequence, created, notes):
    query = "update files set name = %s, folder_sequence = %s, created = %s, notes = %s where file_sequence = %s"
    cursor.execute(query, (name, folder_sequence, created, notes, file_sequence))

def remove_file(file_sequence):
    cursor.execute("delete from files where file_sequence = \'%s\'" % file_sequence)

def add_group(name, notes, location):
    query = "insert into drive_group (name, notes, location) values (%s, %s, %s)"
    cursor.execute(query, (name, notes, location))

def update_group(group_id, name, notes, location):
    query = "update drive_group set name = %s, notes = %s, location = %s where id = %s"
    cursor.execute(query, (name, notes, location, group_id))

def delete_group(group_id):
    query = "delete from drive_group where id = \'%s\'"
    cursor.execute(query % group_id)

def add_to_group(serial, group_id):
    query = "update drives set drive_group = %s where serial = %s"
    cursor.execute(query, (group_id, serial))

def group_exists(group_id):
    query = "select 1 from drive_group where id = \'%s\'"
    cursor.execute(query % group_id)
    if cursor.fetchone() is None:
        return False
    return True

def get_last_group_id():
    cursor.execute("select max(id) from drive_group")
    return cursor.fetchone()[0]

def remove_all(serial):
    query = "delete from files where folder_sequence = (select folder_sequence from folders where serial = %s)" 
    cursor.execute(query % serial)
    query = "delete from folders where serial = %s"
    cursor.execute(query % serial)
    remove_hdd(serial)
    print serial + " has been removed from the database."

def get_oldest_file_date(serial):
    query = "select min(created) from files join folders using (folder_sequence) join drives using (serial) where serial = \'%s\'"
    cursor.execute(query % serial)
    print serial
    return cursor.fetchone()[0]

def get_newest_file_date(serial):
    query = "select max(created) from files join folders using (folder_sequence) join drives using (serial) where serial = \'%s\'"
    cursor.execute(query % serial)
    return cursor.fetchone()[0]


class HDDSystemException(Exception):
    pass



if __name__ == "__main__":
    main(sys.argv[1:])
