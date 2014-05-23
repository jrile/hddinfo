from fpdf import FPDF
from barcode.writer import ImageWriter
import barcode
import time

class Label():


    def labelWithInfo(self, serial, f_list, username, old, new):
        pdf = FPDF(format=(60,58))
        pdf.add_page()
    # put barcode here
        self.createBarcode(serial)

        pdf.image('barcode.png', 1, 1, h=28) # barcodes print out with height of 280px.

        pdf.set_font('Arial', 'B', 6) 
        pdf.ln(28)
        pdf.cell(0, 0, "Added " + time.strftime("%c") + " by " + username, ln=2)
        pdf.set_font('Arial', '', 12)
        pdf.cell(30, 10, "created: " + old + ", modified: " + new, ln=1)
  
        pdf.cell(30, 10, "Contains:", ln=2)
        
    # print folder directory
        pdf.set_font('Times', '', 12)
        max_folders_on_label = 15
        for f in f_list:
            if max_folders_on_label > 0:
                max_folders_on_label -= 1
                pdf.cell(0, 5, f, 0, 1)

        pdf.output('label.pdf')


    def labelWithBigBarcode(self, serial):
        pdf = FPDF(format=(60,58))
        pdf.add_page()
        self.createBarcode(serial)
        pdf.image('barcode.png'), 1, 1, w=56)
        pdf.output('label.pdf')

    def label(self, serial, f_list, username, old, new):
        pdf = FPDF(format=(80,24))
        pdf.add_page()
    # put barcode here
        self.createBarcode(serial)

        pdf.image('barcode.png', 0, 0, h=24) # barcodes print out with height of 280px.
        #pdf.add_page()
        #pdf.set_font('Times','',14)
        #pdf.cell(30, 22, serial)
        pdf.output('/home/shared/' + serial + '.pdf')

        
    def createBarcode(self, serial):
        code39 = barcode.get_barcode_class('code39')
        c39 = code39(str(serial), writer=ImageWriter())
        fullname = c39.save('barcode')
    

if __name__ == "__main__":
    l = Label()
    directory = ["test1", "test2", "test3", "test4"]
    l.labelWithInfo("helloaa", directory, "jrile", "1-1-1999", "5-22-2014")
    l.labelWithBigBarcode("serialtest")
