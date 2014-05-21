import os, os.path, mysql.connector, datetime, sys, commands, re
from optparse import OptionParser

connection = mysql.connector.connect(user='root', database='hdds')
cursor = connection.cursor()


def main(argv):
    """Flag options, automatically adds a -h/--help flag with this information."""
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename", help="read mountpoints from FILE", metavar="FILE")
    parser.add_option("-o", "--output", dest="output", help="dump drive information to FILE", metavar="FILE")
    parser.add_option("-p", "--prompt", dest="prompt", help="specify drive information before adding to database", action="store_true")

    (options, args) = parser.parse_args()

    filename = options.filename
    if filename == None:
        # default file to read drives from
        filename = "drives.in"


    #TODO: add username/password table
    username = raw_input("Enter username: ")
    while not username:
        username = raw_input("Enter username: ")
        
    parse_drives(filename, username, options.output, options.prompt)


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
            command = "sudo mount " + drive + " /mnt -t auto"
            os.system(command)
        
            # get drive serial #. assuming serial is unique.
            serial = commands.getoutput("sudo smartctl -i " + drive + " | grep \"Serial Number:\"").split()[2]
            print serial
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

            parse_folders("/mnt", serial, out=output, prompt=prompt)

            print "Sucessfully parsed drive: " + drive
            print

        except IndexError:
            print "Error! Could not parse drive: " + drive
            print "Can't get serial number from drive: " + drive
    
           
        except mysql.connector.errors.IntegrityError:
            print "Error! This drive already exists in the database: " + drive
            
        finally:
            if output:
                output.close()

def parse_folders(path, serial, level=1, out=None, prompt=False):
    if level == 1:
        # add a 'root' folder for all the files on on the top-most directory.
        add_folder(serial, "root")
        folder_sequence = get_folder_sequence("root", serial)
        parse_files(path, folder_sequence, serial, 1, out, prompt)

    for f in os.listdir(path):
        if os.path.isdir(os.path.join(path,f)):
            print ("---" * level) + "Folder found: " + f
            if out:
                out.write(("---" * level) + f + "/\n")
            add_folder(serial, f)
            folder_sequence = get_folder_sequence(f, serial)
            parse_files(os.path.join(path, f), folder_sequence, serial, level=level+1, out=out, prompt=prompt)
            parse_folders(os.path.join(path, f), serial, level=level+1, out=out, prompt=prompt)

        


def parse_files(path, folder_sequence, serial, level=2, out=None, prompt=False):
    for filename in os.listdir(path):

        if not os.path.isdir(os.path.join(path, filename)):
            print ("---" * level) + "File found: " + filename
            if out:
                out.write(("---" * level) + filename + "\n")
            date = os.path.getmtime(os.path.join(path, filename))
            dt = datetime.datetime.fromtimestamp(date)
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

def add_folder(serial, folder_name):
    query = "insert into folders (serial, folder_name) values (%s, %s)"
    cursor.execute(query, (serial, folder_name))

def get_folder_sequence(folder_name, serial):
    query = "select folder_sequence from folders where folder_name = %s and serial = %s"
    cursor.execute(query, (folder_name, serial))
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




if __name__ == "__main__":
    main(sys.argv[1:])
