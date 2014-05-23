from main import *
from label import *
import sys

class Organization:



    def prompt(self):
        while 1:
            print "n - new group location"
            print "a - add to existing group location"
            print "r - return to main program"
            print "q - quit"
            option = raw_input("Please select: ")
            if option.lower() == 'n':
                self.new_location()
            elif option.lower() == 'a':
                self.add_to_location()
            elif option.lower() == 'r':
                break
            elif option.lower() == 'q':
                sys.exit()

    def add_to_location(self):
        location = raw_input("Scan location: ")
        if not group_exists(location):
            print "Group does not exist in our system! Please add it first."
            self.new_location()
        else:
            self.scan_items(location)

    def scan_items(self, group_id): 
        items = []
        try:
            while 1:
                item = raw_input("Scan items (press CTRL+C to quit): ")
                if not hdd_exists(item):
                    raise HDDSystemException("Drive does not exist in our system! Please add it first.")
                items.append(item)
            
        except KeyboardInterrupt:
            print "\nAdding items to location..."
            for item in items:
                add_to_group(item, group_id)      

    def new_location(self, barcode=None):
        name = raw_input("Enter descriptive name: ")
        while not name:
            name = raw_input("Enter descriptive name: ")
        location = raw_input("Enter location: ")
        notes = raw_input("Enter notes: ")
        
        add_group(name, notes, location)
        
        # print group barcode here.
        l = Label()
        l.group_label(get_last_group_id(), name, location, notes)

        while True:
            option = raw_input("Group successfully added! Would you like to add items to this group now? [y/n]: ")
            if option.lower() == 'y':
                group_id = get_last_group_id()
                self.scan_items(group_id)
                break
            if option.lower() == 'n':
                break        



if __name__ == "__main__":
    o = Organization()
    o.new_location()
        
            


