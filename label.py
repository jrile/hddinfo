from fpdf import FPDF
from barcode.writer import ImageWriter
import barcode
import time

class Label():



    def label_with_info(self, serial, f_list, username, old, new):
        pdf = FPDF(format=(80,65), unit='mm')
        pdf.add_page()
    # put barcode here
        self.create_barcode(serial)

        pdf.image('barcode.png', x=0, y=0,  h=30) # barcodes print out with height of 280px.
        pdf.set_font('Arial', '', 12) 
        pdf.ln(21)
        pdf.cell(21, 4, "Added " + time.strftime("%c"),0,2)
        pdf.cell(80, 4, "Created: " + old,0,2)
        pdf.cell(80, 4, "Modified: " + new,0,2)
        #pdf.set_font('Arial', '', 12)
        #pdf.cell(30, 10, "created: " + old + ", modified: " + new, ln=1)        
        pdf.output('barcodes/label.pdf')
        self.print_barcode('barcodes/label.pdf')

    def label_with_big_barcode(self, serial):
        pdf = FPDF(format=(60,30))
        pdf.add_page()
        self.create_barcode(serial)
        pdf.image('barcode.png', 1, 1, w=58)
        pdf.output('label_big_barcode.pdf')
        self.print_barcode('label_big_barcode.pdf')

    def label(self, serial, f_list, username, old, new):
        pdf = FPDF(format=(80,24))
        pdf.add_page()
        # put barcode here
        self.create_barcode(serial)

        pdf.image('barcode.png', 0, 0, h=24) # barcodes print out with height of 280px.
        #pdf.add_page()
        #pdf.set_font('Times','',14)
        #pdf.cell(30, 22, serial)
        pdf.output('barcodes/' + serial + '.pdf')
        self.print_barcode('barcodes/' + serial + '.pdf')

    def group_label(self, group_id, name, location, notes):
        pdf = FPDF(format=(80,65), unit='mm')
        pdf.set_margins(5, 5)
        pdf.add_page()
        self.create_barcode(group_id)
        pdf.image('barcode.png', x=0, y=0, h=30)
        pdf.set_font('Arial', '', 14)
        pdf.cell(30)
        pdf.cell(40,0, location, 0, 2)
        pdf.ln(10)
        pdf.cell(30)
        pdf.cell(21, 4, str(group_id) + ": " + name, 0, 1)
        pdf.ln(10)
        pdf.set_font('Arial', '', 8)
        pdf.multi_cell(0, 5, notes, 0, 2)
        pdf.output('barcodes/group_label.pdf')
        self.print_barcode('barcodes/group_label.pdf')
        
    def create_barcode(self, serial):
        code39 = barcode.get_barcode_class('code39')
        c39 = code39(str(serial), writer=ImageWriter())
        fullname = c39.save('barcode')


    def print_barcode(self, pdf_filename):
        # this is where we will print barcodes
        return
    

if __name__ == "__main__":
    l = Label()
    directory = ["test1", "test2", "test3", "test4"]
    l.label_with_info("helloaaa", directory, "jrile", "1-1-1999", "5-22-2014")
    l.label_with_big_barcode("serialtest")
    l.group_label(123, "NEV1", "B-52", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaThis is a drive full of stuff where we did things and some other stuff.")
